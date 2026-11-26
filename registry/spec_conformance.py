"""Shared data-format specs (docs/specs/), checked: JSON Schemas and conformance fixtures (ADR-024, D38).

    registry/schemas/<spec>.schema.json         the shape, JSON Schema draft 2020-12
    registry/conformance/<spec>/valid/*.json    documents the spec accepts
    registry/conformance/<spec>/invalid/*.json  documents it refuses, each for one reason (the file name says which)
    registry/conformance/manifest.json          every schema and fixture with its sha256, and how each one fails

A fixture fails either the schema (`schema`) or a rule JSON Schema cannot state (`rules`: a time on a frame, a cut
point inside its cover, frame numbers agreeing with seconds). `rules()` below is the reference for those; a Skill that
validates with the schema alone takes the `schema` fixtures from the manifest.

    python3 -m registry.spec_conformance            check every fixture; print one line per fixture
    python3 -m registry.spec_conformance --check    also fail when manifest.json is out of date (CI)
    python3 -m registry.spec_conformance --write-manifest
    python3 -m registry.spec_conformance --export title stinger --to <skill>/tests/fixtures/velisa
                                                    copy those specs' schemas, fixtures and manifest entries into a
                                                    Skill's tests, with the Velisa commit they came from

Needs the `jsonschema` package (4.18 or later); registry/ itself stays dependency-free, so it is imported here only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "conformance"
MANIFEST = FIXTURE_DIR / "manifest.json"

# spec name -> (schema file, the spec document it formalizes)
SPECS: Dict[str, tuple] = {
    "pacing-profile": ("pacing-profile.schema.json", "docs/adr/ADR-035-reference-pacing.md"),
    "protect-ranges": ("protect-ranges.schema.json", "docs/adr/ADR-035-reference-pacing.md"),
    "kit": ("kit.schema.json", "docs/specs/kit.md"),
    "title": ("title.schema.json", "docs/specs/title-and-stinger.md"),
    "stinger": ("stinger.schema.json", "docs/specs/title-and-stinger.md"),
    "licence-record": ("licence-record.schema.json", "docs/specs/licence-record.md"),
    "sidecar-envelope": ("sidecar-envelope.schema.json", "docs/specs/sidecar-envelope.md"),
}

ON_FRAME = 1e-3  # "t * frame_rate within 1/1000 of a whole frame" (docs/specs/title-and-stinger.md, Times)


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rate(doc: Dict[str, Any]) -> Optional[Fraction]:
    fr = doc.get("frame_rate")
    if not isinstance(fr, str) or "/" not in fr:
        return None
    num, den = fr.split("/", 1)
    return Fraction(int(num), int(den))


def _frames(t: float, rate: Fraction) -> float:
    return t * float(rate)


def _on_frame(t: float, rate: Fraction) -> bool:
    f = _frames(t, rate)
    return abs(f - round(f)) <= ON_FRAME


def rules(spec: str, doc: Any) -> List[str]:
    """Problems JSON Schema cannot state, for a document that already passed the schema. Empty when it holds."""
    out: List[str] = []
    if spec == "pacing-profile":
        low, high = doc["silence_detection"]["analysis_bandpass_hz"]
        if low >= high:
            out.append("analysis band must increase")
        if doc["pacing"]["target_keep_silence_ms"] > doc["pacing"]["max_keep_silence_ms"]:
            out.append("pause target exceeds maximum")
        if doc["probe_meta"]["analysis_count"] != len(doc["probe_meta"]["sample_names"]):
            out.append("analysis count differs from sample names")
    elif spec == "protect-ranges":
        if any(r["end_ms"] <= r["start_ms"] for r in doc):
            out.append("end must follow start")
    elif spec == "stinger":
        c, cover = doc["cut_point"], doc["cover"]
        if not cover["start"] <= c < cover["end"]:
            out.append(f"cut_point {c} is not inside cover [{cover['start']}, {cover['end']})")
        rate = _rate(doc)
        if rate is not None:
            for name, t in (("cut_point", c), ("cover.start", cover["start"]), ("cover.end", cover["end"])):
                if not _on_frame(t, rate):
                    out.append(f"{name} {t} is not on a frame at {doc['frame_rate']} ({_frames(t, rate):.6f} frames)")
            if "cut_point_frame" in doc and doc["cut_point_frame"] != round(_frames(c, rate)):
                out.append(f"cut_point_frame {doc['cut_point_frame']} is not round(cut_point * frame_rate) = {round(_frames(c, rate))}")
            if "cover_frames" in doc:
                for k in ("start", "end"):
                    if doc["cover_frames"][k] != round(_frames(cover[k], rate)):
                        out.append(f"cover_frames.{k} {doc['cover_frames'][k]} does not match cover.{k}")
        if "cover_frames" in doc and "frames" in doc and doc["cover_frames"]["end"] > doc["frames"]:
            out.append(f"cover_frames.end {doc['cover_frames']['end']} is past the last frame ({doc['frames']} frames)")
    elif spec == "title":
        seg = doc["segments"]
        rate = _rate(doc)
        if rate is not None:
            for k in ("in", "loop", "out"):
                if not _on_frame(seg[k], rate):
                    out.append(f"segments.{k} {seg[k]} is not a whole number of frames at {doc['frame_rate']}")
                elif "segment_frames" in doc and doc["segment_frames"][k] != round(_frames(seg[k], rate)):
                    out.append(f"segment_frames.{k} {doc['segment_frames'][k]} does not match segments.{k}")
    return out


def _validator(schema: Dict[str, Any]):
    from jsonschema import Draft202012Validator  # optional dependency, see the module docstring
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def check_fixture(spec: str, validator: Any, path: Path) -> Dict[str, Any]:
    """{expect, fails: [] | ["schema"] | ["rules"], problems} for one fixture."""
    doc = load_json(path)
    expect = path.parent.name
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        problems = [f"{'/'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in errors]
        return {"expect": expect, "fails": ["schema"], "problems": problems}
    problems = rules(spec, doc)
    return {"expect": expect, "fails": ["rules"] if problems else [], "problems": problems}


def run() -> Dict[str, Any]:
    """Check every schema and fixture. Returns the manifest and the list of failures."""
    manifest: Dict[str, Any] = {
        "description": "Velisa shared data-format specs: schemas and conformance fixtures (registry/README.md, ADR-024). "
                       "Generated by `python3 -m registry.spec_conformance --write-manifest`; do not edit.",
        "on_frame_tolerance": ON_FRAME,
        "specs": {},
    }
    failures: List[str] = []
    for spec, (schema_file, doc_path) in SPECS.items():
        schema_path = SCHEMA_DIR / schema_file
        validator = _validator(load_json(schema_path))
        fixtures = []
        for kind in ("valid", "invalid"):
            for path in sorted((FIXTURE_DIR / spec / kind).glob("*.json")):
                r = check_fixture(spec, validator, path)
                rel = path.relative_to(ROOT).as_posix()
                ok = (kind == "valid") == (not r["fails"])
                if not ok:
                    failures.append(f"{rel}: expected {kind}, " + ("; ".join(r["problems"]) if r["problems"] else "but it passed"))
                fixtures.append({"path": rel, "sha256": sha256_file(path), "expect": kind, "fails": r["fails"]})
        if not any(f["expect"] == "valid" for f in fixtures) or not any(f["expect"] == "invalid" for f in fixtures):
            failures.append(f"{spec}: needs at least one valid and one invalid fixture")
        manifest["specs"][spec] = {"spec": doc_path, "schema": f"schemas/{schema_file}",
                                   "schema_sha256": sha256_file(schema_path), "fixtures": fixtures}
    return {"manifest": manifest, "failures": failures}


def manifest_text(manifest: Dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _head_commit() -> Optional[str]:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def export(specs: List[str], to: Path, source: Optional[str] = None) -> Dict[str, Any]:
    """Copy the named specs' schemas and fixtures into `to` (the same layout as registry/: schemas/, conformance/<spec>/)
    with a manifest.json of those specs and the Velisa commit they came from. Files of other specs in `to` are left alone;
    the named specs' fixture directories are replaced, so a fixture removed here is removed there."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    unknown = [s for s in specs if s not in manifest["specs"]]
    if unknown:
        raise SystemExit(f"spec_conformance: unknown spec(s) {unknown}; known: {sorted(manifest['specs'])}")
    out_manifest = {"description": "Copied from Velisa registry/ by `python3 -m registry.spec_conformance --export`; do not edit. "
                                   "Update by exporting again (registry/README.md, Conformance fixtures).",
                    "source": {"repository": "kajisho5/Velisa", "commit": source or _head_commit()},
                    "on_frame_tolerance": manifest["on_frame_tolerance"],
                    "specs": {s: manifest["specs"][s] for s in specs}}
    (to / "schemas").mkdir(parents=True, exist_ok=True)
    for s in specs:
        entry = manifest["specs"][s]
        shutil.copyfile(ROOT / entry["schema"], to / entry["schema"])
        dest = to / "conformance" / s
        if dest.exists():
            shutil.rmtree(dest)
        for f in entry["fixtures"]:
            (to / f["path"]).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / f["path"], to / f["path"])
    existing = to / "manifest.json"
    if existing.exists():  # keep the specs exported earlier that were not named this time
        old = json.loads(existing.read_text(encoding="utf-8")).get("specs", {})
        out_manifest["specs"] = {**{k: v for k, v in old.items() if k not in specs}, **out_manifest["specs"]}
    existing.write_text(manifest_text(out_manifest), encoding="utf-8")
    return out_manifest


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m registry.spec_conformance", description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="also fail when registry/conformance/manifest.json is out of date")
    ap.add_argument("--write-manifest", action="store_true", help="write registry/conformance/manifest.json")
    ap.add_argument("--export", nargs="+", metavar="SPEC", help="copy these specs' schemas and fixtures (needs --to)")
    ap.add_argument("--to", type=Path, help="the directory --export writes into")
    ap.add_argument("--source", help="the Velisa commit to record with --export (default: git rev-parse HEAD)")
    a = ap.parse_args(argv)
    if a.export:
        if not a.to:
            ap.error("--export needs --to")
        out = export(a.export, a.to, a.source)
        print(f"exported {', '.join(a.export)} to {a.to} (Velisa {out['source']['commit']})")
        return 0
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print("spec_conformance: the jsonschema package is needed (pip install 'jsonschema>=4.18')", file=sys.stderr)
        return 2
    result = run()
    for spec, entry in result["manifest"]["specs"].items():
        for f in entry["fixtures"]:
            print(f"{f['path']}: {f['expect']}" + (f" (fails: {', '.join(f['fails'])})" if f["fails"] else ""))
    text = manifest_text(result["manifest"])
    if a.write_manifest:
        MANIFEST.write_text(text, encoding="utf-8")
        print(f"wrote {MANIFEST.relative_to(ROOT.parent).as_posix()}")
    elif a.check and (not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != text):
        result["failures"].append("registry/conformance/manifest.json is out of date: run python3 -m registry.spec_conformance --write-manifest")
    for f in result["failures"]:
        print(f"FAIL {f}", file=sys.stderr)
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
