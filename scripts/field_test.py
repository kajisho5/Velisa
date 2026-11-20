#!/usr/bin/env python3
"""Record the result of a field test: a roadmap step that needs real hardware, software, accounts or media
(docs/field-test/README.md, decision D43).

    python3 scripts/field_test.py list
    python3 scripts/field_test.py show nle-bridge-real-nle
    python3 scripts/field_test.py record nle-bridge-real-nle --verdict pass \\
        --env nle="Premiere Pro 25.1" --version nle-bridge-skill=0.1.2 \\
        --measure premiere-pro.imports=yes --measure premiere-pro.start_timecode_kept=yes \\
        --media export=out/edit.xml --note "markers kept, colours lost"
    python3 scripts/field_test.py check [docs/field-test/results/*.json]

`record` writes two files the owner can commit: docs/field-test/results/<date>-<id>.json (the record,
`velisa/field-test-result@1`) and the same name with .md (for people and for the step's own repository).
Media files are hashed (sha256 and size) and never copied; only the label given on the command line is
written, never the path. A step whose media shows people needs --consent. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "docs" / "field-test" / "steps.json"
RESULTS = ROOT / "docs" / "field-test" / "results"
FORMAT = "velisa/field-test-result@1"
VERDICTS = ("pass", "fail", "partial", "blocked")
ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
KEY = re.compile(r"^(?P<cond>[a-z0-9][a-z0-9-]*)(?::(?P<detail>[a-z0-9][a-z0-9_-]*))?\.(?P<metric>[a-z0-9_]+)$")
# never written into a result, whatever the person types: a value that looks like a secret is refused
SECRETISH = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|bearer)\s*[=:]|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}")


class FieldTestError(Exception):
    """A request the recorder refuses; the message says what to change."""


def load_catalogue(path: Path = CATALOGUE) -> Dict[str, Dict[str, Any]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    steps = {s["id"]: s for s in doc["steps"]}
    if len(steps) != len(doc["steps"]):
        raise FieldTestError("duplicate step id in the catalogue")
    return steps


def pair(text: str, what: str) -> Tuple[str, str]:
    if "=" not in text:
        raise FieldTestError(f"{what} must be key=value: {text!r}")
    k, v = text.split("=", 1)
    k, v = k.strip(), v.strip()
    if not k or not v:
        raise FieldTestError(f"{what} needs a key and a value: {text!r}")
    if SECRETISH.search(text):
        raise FieldTestError(f"{what} looks like a credential and is not recorded: {k}")
    return k, v


def value(text: str) -> Any:
    """A number stays a number; yes / no become booleans; anything else is text."""
    low = text.lower()
    if low in ("yes", "true"):
        return True
    if low in ("no", "false"):
        return False
    try:
        return int(text) if re.fullmatch(r"-?[0-9]+", text) else float(text) if re.fullmatch(r"-?[0-9]*\.[0-9]+", text) else text
    except ValueError:
        return text


def check_measure(step: Dict[str, Any], key: str) -> None:
    m = KEY.match(key)
    if not m:
        raise FieldTestError(f"measurement key {key!r} is not <condition>.<metric> (or <condition>:<detail>.<metric>)")
    if m.group("cond") not in step["conditions"]:
        raise FieldTestError(f"{key}: condition {m.group('cond')!r} is not one of {', '.join(step['conditions'])}")
    if m.group("metric") not in step["metrics"]:
        raise FieldTestError(f"{key}: metric {m.group('metric')!r} is not one of {', '.join(step['metrics'])}")


def sha256(path: Path) -> Tuple[str, int]:
    h, n = hashlib.sha256(), 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def build(step: Dict[str, Any], *, verdict: str, measures: Sequence[str] = (), media: Sequence[str] = (),
          env: Sequence[str] = (), versions: Sequence[str] = (), notes: Sequence[str] = (), consent: bool = False,
          tester: Optional[str] = None, now: Optional[dt.datetime] = None) -> Dict[str, Any]:
    if verdict not in VERDICTS:
        raise FieldTestError(f"verdict must be one of {', '.join(VERDICTS)}")
    if step.get("consent") and media and not consent:
        raise FieldTestError(f"{step['id']} uses recordings of people: pass --consent to state that every person "
                             "recorded agreed to this use (the result keeps no names and no media)")
    measurements: Dict[str, Any] = {}
    for item in measures:
        k, v = pair(item, "--measure")
        check_measure(step, k)
        if k in measurements:
            raise FieldTestError(f"{k} given twice")
        measurements[k] = value(v)
    if verdict == "pass" and not measurements:
        raise FieldTestError("a pass needs the measurements that show the 'Done when' is met")
    files = []
    for item in media:
        label, p = pair(item, "--media")
        path = Path(p)
        if not path.is_file():
            raise FieldTestError(f"--media {label}: no such file")
        digest, size = sha256(path)
        files.append({"label": label, "sha256": digest, "bytes": size})
    for n in notes:
        if SECRETISH.search(n):
            raise FieldTestError("a note looks like it holds a credential; it is not recorded")
    now = now or dt.datetime.now(dt.timezone.utc)
    environment = {"os": f"{platform.system()} {platform.release()}".strip(), "machine": platform.machine(),
                   "python": platform.python_version()}
    environment.update(dict(pair(e, "--env") for e in env))
    record: Dict[str, Any] = {
        "format": FORMAT,
        "step": {k: step[k] for k in ("id", "repo", "step", "roadmap", "title", "done_when")},
        "recorded_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "done_when_met": verdict == "pass",
        "environment": environment,
        "versions": dict(pair(v, "--version") for v in versions),
        "media": files,
        "consent_stated": bool(consent) if step.get("consent") else None,
        "measurements": measurements,
        "missing_conditions": [c for c in step["conditions"]
                               if not any(KEY.match(k).group("cond") == c for k in measurements)],  # type: ignore[union-attr]
        "notes": list(notes),
    }
    if tester:
        record["tester"] = tester
    return record


def markdown(record: Dict[str, Any], step: Dict[str, Any]) -> str:
    s = record["step"]
    yesno = {True: "yes", False: "no"}
    lines = [
        f"# Field test: {s['title']}",
        "",
        f"- Step: {s['repo']} {s['roadmap']} step {s['step']} (`{s['id']}`)",
        f"- Done when: {s['done_when']}",
        f"- Verdict: **{record['verdict']}** (recorded {record['recorded_at']}{', by ' + record['tester'] if record.get('tester') else ''})",
    ]
    if record["consent_stated"] is not None:
        lines.append(f"- Consent of the people recorded: {'stated' if record['consent_stated'] else 'not stated'}")
    lines += ["", "## Environment", ""]
    lines += [f"- {k}: {v}" for k, v in record["environment"].items()]
    lines += [f"- {k} {v}" for k, v in record["versions"].items()]
    lines += ["", "## Measurements", ""]
    if record["measurements"]:
        lines += ["| Condition | Metric | Value | Meaning |", "|---|---|---|---|"]
        for k, v in record["measurements"].items():
            m = KEY.match(k)
            cond = m.group("cond") + (f" ({m.group('detail')})" if m.group("detail") else "")  # type: ignore[union-attr]
            metric = m.group("metric")  # type: ignore[union-attr]
            lines.append(f"| {cond} | {metric} | {yesno.get(v, v) if isinstance(v, bool) else v} | {step['metrics'][metric]} |")
    else:
        lines.append("None recorded.")
    if record["missing_conditions"]:
        lines += ["", f"Not measured: {', '.join(record['missing_conditions'])}."]
    if record["media"]:
        lines += ["", "## Media (hashes only; the files are not in this repository)", ""]
        lines += [f"- {m['label']}: sha256 `{m['sha256']}`, {m['bytes']} bytes" for m in record["media"]]
    if record["notes"]:
        lines += ["", "## Notes", ""] + [f"- {n}" for n in record["notes"]]
    return "\n".join(lines) + "\n"


def write(record: Dict[str, Any], step: Dict[str, Any], out: Path) -> Tuple[Path, Path]:
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{record['recorded_at'][:10]}-{step['id']}"
    n = 1
    while (out / f"{stem}.json").exists() or (out / f"{stem}.md").exists():
        n += 1
        stem = f"{record['recorded_at'][:10]}-{step['id']}-{n}"
    j, m = out / f"{stem}.json", out / f"{stem}.md"
    j.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    m.write_text(markdown(record, step), encoding="utf-8")
    return j, m


def validate(record: Dict[str, Any], steps: Dict[str, Dict[str, Any]]) -> List[str]:
    """What is wrong with a result file; empty when it is a well-formed record of a known step."""
    errs: List[str] = []
    if record.get("format") != FORMAT:
        return [f"format is not {FORMAT}"]
    sid = (record.get("step") or {}).get("id")
    step = steps.get(sid)
    if step is None:
        return [f"unknown step {sid!r}"]
    if record.get("verdict") not in VERDICTS:
        errs.append("verdict")
    if record.get("done_when_met") != (record.get("verdict") == "pass"):
        errs.append("done_when_met disagrees with the verdict")
    for k in record.get("measurements") or {}:
        try:
            check_measure(step, k)
        except FieldTestError as e:
            errs.append(str(e))
    for m in record.get("media") or []:
        if not re.fullmatch(r"[0-9a-f]{64}", str(m.get("sha256", ""))) or set(m) - {"label", "sha256", "bytes"}:
            errs.append(f"media entry {m.get('label')!r}: label, sha256 and bytes only")
    if step.get("consent") and record.get("media") and record.get("consent_stated") is not True:
        errs.append("media of people without stated consent")
    if SECRETISH.search(json.dumps(record, ensure_ascii=False)):
        errs.append("something in the record looks like a credential")
    return errs


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="the steps in the catalogue")
    a = sub.add_parser("show", help="one step: what it needs and what to measure")
    a.add_argument("id")
    a = sub.add_parser("record", help="write a result file (JSON and Markdown)")
    a.add_argument("id")
    a.add_argument("--verdict", required=True, choices=VERDICTS)
    a.add_argument("--measure", action="append", default=[], metavar="COND.METRIC=VALUE")
    a.add_argument("--media", action="append", default=[], metavar="LABEL=PATH", help="hashed, never copied; the path is not written")
    a.add_argument("--env", action="append", default=[], metavar="KEY=VALUE", help="hardware or software, e.g. gpu=..., nle=...")
    a.add_argument("--version", action="append", default=[], metavar="TOOL=VERSION")
    a.add_argument("--note", action="append", default=[])
    a.add_argument("--consent", action="store_true", help="every person in the media agreed to this use")
    a.add_argument("--tester", help="optional; written as given")
    a.add_argument("--out", type=Path, default=RESULTS)
    a = sub.add_parser("check", help="validate result files")
    a.add_argument("files", nargs="*", type=Path)
    args = ap.parse_args(argv)
    try:
        steps = load_catalogue()
        if args.cmd == "list":
            for s in steps.values():
                print(f"{s['id']:<28} {s['repo']} step {s['step']}: {s['title']}")
            return 0
        if args.cmd in ("show", "record") and args.id not in steps:
            raise FieldTestError(f"unknown step {args.id!r}; `list` shows the ids")
        if args.cmd == "show":
            s = steps[args.id]
            print(f"{s['title']} ({s['repo']} {s['roadmap']} step {s['step']})\nDone when: {s['done_when']}\nNeeds:")
            print("\n".join(f"  - {n}" for n in s["needs"]))
            print(f"Media: {s['media']}\nConsent needed: {'yes' if s['consent'] else 'no'}\nHow: {s['how']}")
            print(f"Conditions: {', '.join(s['conditions'])}\nMetrics:")
            print("\n".join(f"  {k}: {v}" for k, v in s["metrics"].items()))
            return 0
        if args.cmd == "record":
            step = steps[args.id]
            rec = build(step, verdict=args.verdict, measures=args.measure, media=args.media, env=args.env,
                        versions=args.version, notes=args.note, consent=args.consent, tester=args.tester)
            for p in write(rec, step, args.out):
                print(f"wrote {p}")
            return 0
        files = args.files or sorted(RESULTS.glob("*.json"))
        bad = 0
        for f in files:
            errs = validate(json.loads(f.read_text(encoding="utf-8")), steps)
            for e in errs:
                print(f"{f}: {e}")
            bad += bool(errs)
        print(f"{len(files) - bad} of {len(files)} result files are well formed")
        return 1 if bad else 0
    except FieldTestError as e:
        print(f"field_test: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
