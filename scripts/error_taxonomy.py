"""Check Skill contracts against the ecosystem's error taxonomy (docs/specs/error-taxonomy.md, ADR-027,
decision D41). Report only: it exits 0 unless --strict is given and a contract declares a code the
taxonomy does not know.

    # the contracts video-production-agent pins (as contract-shape.yml checks them)
    python3 scripts/error_taxonomy.py --contracts ../video-production-agent/src/video_agent/tools
    # each Skill's own contract/contract.json, from sibling checkouts
    python3 scripts/error_taxonomy.py --checkouts ..
    # one file; the per-code mapping table as Markdown; a JSON report
    python3 scripts/error_taxonomy.py path/to/contract.json --table --json report.json

What is read from a contract (every shape found in the ecosystem on 2026-11-20):
- `errors.codes` (a list), with `errors.retryable` / `errors.retryable_default` (code -> bool),
  `errors.non_retryable` (a list) or `errors.classes` (code -> FATAL | RETRYABLE | BLOCKED);
- `errors` as a map of code -> {exit_code, retryable};
- `errors` / `error` with `kinds` (kind -> code), and `errors` / `conventions.errors` as a map of
  lower-case kind -> exit code;
- `tools[].errors` (lists of codes).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "docs" / "specs" / "error-taxonomy.json"
RETRY_ALLOWED = {"once", "once_longer", "later"}
_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_KIND = re.compile(r"^[a-z][a-z0-9_]*$")


def load_taxonomy(path: Path = TAXONOMY) -> Dict[str, Any]:
    tax = json.loads(path.read_text(encoding="utf-8"))
    classes = tax["classes"]
    for table in ("codes", "kinds"):
        for name, cls in tax[table].items():
            if cls not in classes:
                raise ValueError(f"{path}: {table}.{name} maps to unknown class {cls}")
    for skill, table in tax.get("overrides", {}).items():
        for name, cls in table.items():
            if cls not in classes:
                raise ValueError(f"{path}: overrides.{skill}.{name} maps to unknown class {cls}")
    for name, c in classes.items():
        if c["retry"] not in tax["retry_policies"]:
            raise ValueError(f"{path}: class {name} has unknown retry policy {c['retry']}")
    return tax


def skill_id(contract: Dict[str, Any], fallback: str) -> str:
    for key in ("skill_id", "id", "skill", "name"):
        v = contract.get(key)
        if isinstance(v, dict):
            v = v.get("id") or v.get("name")
        if isinstance(v, str) and v:
            return v
    return fallback


def _retry_table(errs: Dict[str, Any], codes: Iterable[str]) -> Dict[str, Optional[bool]]:
    out: Dict[str, Optional[bool]] = {c: None for c in codes}
    for key in ("retryable", "retryable_default"):
        if isinstance(errs.get(key), dict):
            out.update({c: bool(v) for c, v in errs[key].items() if c in out})
            return out
    if isinstance(errs.get("non_retryable"), list):
        nr = {str(x) for x in errs["non_retryable"]}
        return {c: c not in nr for c in out}
    if isinstance(errs.get("classes"), dict):
        return {c: (errs["classes"].get(c) == "RETRYABLE") if c in errs["classes"] else None for c in out}
    if isinstance(errs.get("retryable"), bool):
        return {c: errs["retryable"] for c in out}
    return out


def declared(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every error a contract declares: [{name, type: code | kind, retryable: bool | None}], sorted, once each."""
    found: Dict[Tuple[str, str], Optional[bool]] = {}

    def add(name: str, typ: str, retryable: Optional[bool] = None) -> None:
        key = (typ, name)
        if key not in found or found[key] is None:
            found[key] = retryable

    def read_block(errs: Any) -> None:
        if not isinstance(errs, dict):
            return
        if isinstance(errs.get("codes"), list):
            codes = [str(c) for c in errs["codes"]]
            retry = _retry_table(errs, codes)
            for c in codes:
                add(c, "code", retry[c])
            return
        if isinstance(errs.get("kinds"), dict):
            for kind, code in errs["kinds"].items():
                add(str(kind), "kind")
                if isinstance(code, str):
                    add(code, "code", errs["retryable"] if isinstance(errs.get("retryable"), bool) else None)
            return
        for name, v in errs.items():
            if isinstance(v, dict) and _CODE.match(str(name)):
                add(str(name), "code", v["retryable"] if isinstance(v.get("retryable"), bool) else None)
            elif isinstance(v, int) and not isinstance(v, bool) and _KIND.match(str(name)):
                add(str(name), "kind")

    read_block(contract.get("errors"))
    read_block(contract.get("error"))
    read_block((contract.get("conventions") or {}).get("errors") if isinstance(contract.get("conventions"), dict) else None)
    for tool in contract.get("tools") or []:
        if isinstance(tool, dict) and isinstance(tool.get("errors"), list):
            for c in tool["errors"]:
                if isinstance(c, str) and _CODE.match(c):
                    add(c, "code")
    return [{"name": n, "type": t, "retryable": r} for (t, n), r in sorted(found.items(), key=lambda x: (x[0][1], x[0][0]))]


def classify(tax: Dict[str, Any], skill: str, name: str, typ: str) -> Optional[str]:
    over = tax.get("overrides", {}).get(skill, {})
    if name in over:
        return over[name]
    return tax["codes" if typ == "code" else "kinds"].get(name)


def check(tax: Dict[str, Any], contracts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """The report: per Skill its rows {name, type, class, retry, skill_retryable, note}, its unknown codes,
    and the Skills that declare no error code at all."""
    skills: Dict[str, Any] = {}
    for sid, contract in sorted(contracts.items()):
        rows, unknown = [], []
        for e in declared(contract):
            cls = classify(tax, sid, e["name"], e["type"])
            row = {"name": e["name"], "type": e["type"], "class": cls,
                   "retry": tax["classes"][cls]["retry"] if cls else None, "skill_retryable": e["retryable"], "note": ""}
            if cls is None:
                unknown.append(e["name"])
                row["note"] = "unknown: not in the taxonomy"
            elif e["retryable"] is True and row["retry"] not in RETRY_ALLOWED:
                row["note"] = f"the Skill says retryable; the class says {row['retry']}"
            rows.append(row)
        skills[sid] = {"version": str(contract.get("version") or ""), "errors": rows, "unknown": unknown}
    return {
        "taxonomy": tax["spec"],
        "skills": skills,
        "unknown": {s: v["unknown"] for s, v in skills.items() if v["unknown"]},
        "no_codes": sorted(s for s, v in skills.items() if not v["errors"]),
        "retry_differs": {s: [r["name"] for r in v["errors"] if r["note"].startswith("the Skill says")]
                          for s, v in skills.items() if any(r["note"].startswith("the Skill says") for r in v["errors"])},
    }


def find_contracts(contract_dirs: Sequence[Path], checkouts: Sequence[Path], files: Sequence[Path]) -> Dict[str, Dict[str, Any]]:
    paths: List[Path] = list(files)
    for d in contract_dirs:
        paths += sorted(p for p in d.rglob("contract*.json") if p.is_file())
    for d in checkouts:
        paths += sorted(d.glob("*/contract/contract.json"))
    out: Dict[str, Dict[str, Any]] = {}
    for p in paths:
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict):
            out[skill_id(doc, p.parent.name)] = doc
    return out


def markdown(report: Dict[str, Any], table: bool = False) -> str:
    lines = [f"## Error taxonomy check ({report['taxonomy']})", ""]
    n = len(report["skills"])
    lines.append(f"{n} contracts read. Report only: nothing here fails a build.")
    lines.append("")
    if report["unknown"]:
        lines.append("**Codes the taxonomy does not know** (add them to docs/specs/error-taxonomy.json or rename them):")
        lines += [f"- {s}: {', '.join(codes)}" for s, codes in sorted(report["unknown"].items())]
    else:
        lines.append("Every declared code and kind maps to a class.")
    lines.append("")
    if report["no_codes"]:
        lines.append("**Contracts that declare no error code**: " + ", ".join(report["no_codes"]))
        lines.append("")
    if report["retry_differs"]:
        lines.append("**The Skill calls it retryable, the class does not**:")
        lines += [f"- {s}: {', '.join(codes)}" for s, codes in sorted(report["retry_differs"].items())]
        lines.append("")
    if table:
        lines += ["| Skill | code / kind | class | retry (class) | retryable (Skill) | note |", "|---|---|---|---|---|---|"]
        for s, v in sorted(report["skills"].items()):
            for r in v["errors"]:
                name = r["name"] if r["type"] == "code" else f"kind `{r['name']}`"
                sr = "" if r["skill_retryable"] is None else ("yes" if r["skill_retryable"] else "no")
                lines.append(f"| {s} | {name} | {r['class'] or '?'} | {r['retry'] or ''} | {sr} | {r['note']} |")
        lines.append("")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("files", nargs="*", type=Path, help="contract JSON files")
    p.add_argument("--contracts", action="append", type=Path, default=[], help="a folder searched for contract*.json")
    p.add_argument("--checkouts", action="append", type=Path, default=[], help="a folder of checkouts: */contract/contract.json")
    p.add_argument("--taxonomy", type=Path, default=TAXONOMY)
    p.add_argument("--table", action="store_true", help="also print every code with its class")
    p.add_argument("--json", type=Path, help="write the report as JSON")
    p.add_argument("--strict", action="store_true", help="exit 1 when a code is unknown")
    a = p.parse_args(argv)
    tax = load_taxonomy(a.taxonomy)
    contracts = find_contracts(a.contracts, a.checkouts, a.files)
    if not contracts:
        print("no contract found", file=sys.stderr)
        return 2
    report = check(tax, contracts)
    print(markdown(report, a.table))
    if a.json:
        a.json.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 1 if a.strict and report["unknown"] else 0


if __name__ == "__main__":
    sys.exit(main())
