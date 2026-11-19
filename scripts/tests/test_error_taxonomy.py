"""The error taxonomy (docs/specs/error-taxonomy.json) and its report-only check, scripts/error_taxonomy.py
(ADR-027, decision D41). Offline: the contracts are small inline examples of every shape the ecosystem uses.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import error_taxonomy as et  # noqa: E402

SCRIPT = ROOT / "scripts" / "error_taxonomy.py"
MAP = ROOT / "docs" / "specs" / "error-taxonomy-map.md"

# one contract per shape found in the ecosystem (2026-11-20)
LIST_SHAPE = {"skill_id": "list-shape", "version": "1.0.0", "errors": {
    "codes": ["INVALID_REQUEST", "TOOL_ERROR", "CANCELLED"],
    "exit_codes": {"INVALID_REQUEST": 2, "TOOL_ERROR": 12, "CANCELLED": 15},
    "retryable": {"INVALID_REQUEST": False, "TOOL_ERROR": True, "CANCELLED": True}}}
NON_RETRYABLE_SHAPE = {"skill_id": "nonretry-shape", "errors": {
    "codes": ["INVALID_INPUT", "INTERNAL_ERROR"], "non_retryable": ["INVALID_INPUT"]}}
CLASSES_SHAPE = {"skill_id": "classes-shape", "errors": {
    "codes": ["ANALYZER_TIMEOUT", "CACHE_MISS"], "classes": {"ANALYZER_TIMEOUT": "RETRYABLE", "CACHE_MISS": "FATAL"}}}
MAP_SHAPE = {"skill": {"id": "map-shape"}, "errors": {
    "ENGINE_TIMEOUT": {"exit_code": 4, "retryable": True}, "INPUT_NOT_FOUND": {"exit_code": 2, "retryable": False}}}
KINDS_SHAPE = {"skill_id": "kinds-shape", "error": {"kinds": {"input": "INPUT_INVALID", "timeout": "TIMEOUT"}, "retryable": False}}
EXIT_KIND_SHAPE = {"skill_id": "exit-kind-shape", "conventions": {"errors": {"failed": 1, "input": 2, "missing_tool": 3}}}
TOOLS_SHAPE = {"skill_id": "tools-shape", "tools": [{"name": "a", "errors": ["ARTIFACT_INPUT_NOT_FOUND"]},
                                                     {"name": "b", "errors": ["ARTIFACT_INPUT_NOT_FOUND", "ARTIFACT_TOO_MANY_PAGES"]}]}
NO_CODES = {"skill_id": "no-codes", "tools": [{"name": "x"}]}


class Taxonomy(unittest.TestCase):
    def setUp(self):
        self.tax = et.load_taxonomy()

    def test_every_class_says_meaning_retry_and_message(self):
        for name, c in self.tax["classes"].items():
            self.assertTrue(re.match(r"^[A-Z_]+$", name))
            for key in ("meaning", "retry", "user_message"):
                self.assertTrue(c.get(key), f"{name}.{key}")
            self.assertIn(c["retry"], self.tax["retry_policies"])

    def test_every_code_and_kind_maps_to_a_class(self):
        for table in ("codes", "kinds"):
            for name, cls in self.tax[table].items():
                self.assertIn(cls, self.tax["classes"], f"{table}.{name}")

    def test_spec_page_lists_every_class(self):
        page = (ROOT / "docs" / "specs" / "error-taxonomy.md").read_text(encoding="utf-8")
        for name in self.tax["classes"]:
            self.assertIn(f"| `{name}` |", page)

    def test_the_committed_map_matches_the_taxonomy(self):
        rows = [r.split("|") for r in MAP.read_text(encoding="utf-8").splitlines() if r.startswith("| ") and "---" not in r][1:]
        self.assertGreater(len(rows), 250)
        for r in rows:
            name, cls = r[2].strip(), r[3].strip()
            table = "kinds" if name.startswith("kind `") else "codes"
            key = name[6:-1] if table == "kinds" else name
            self.assertEqual(self.tax[table].get(key), cls, name)

    def test_a_bad_class_is_refused(self):
        d = Path(tempfile.mkdtemp(prefix="velisa-test-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        bad = json.loads(json.dumps(self.tax))
        bad["codes"]["X"] = "NO_SUCH_CLASS"
        (d / "t.json").write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(ValueError):
            et.load_taxonomy(d / "t.json")


class Declared(unittest.TestCase):
    def names(self, contract):
        return {(e["name"], e["type"]): e["retryable"] for e in et.declared(contract)}

    def test_list_shape_with_retryable_map(self):
        self.assertEqual(self.names(LIST_SHAPE), {("INVALID_REQUEST", "code"): False, ("TOOL_ERROR", "code"): True,
                                                  ("CANCELLED", "code"): True})

    def test_non_retryable_list(self):
        self.assertEqual(self.names(NON_RETRYABLE_SHAPE), {("INVALID_INPUT", "code"): False, ("INTERNAL_ERROR", "code"): True})

    def test_classes_map(self):
        self.assertEqual(self.names(CLASSES_SHAPE), {("ANALYZER_TIMEOUT", "code"): True, ("CACHE_MISS", "code"): False})

    def test_code_map(self):
        self.assertEqual(self.names(MAP_SHAPE), {("ENGINE_TIMEOUT", "code"): True, ("INPUT_NOT_FOUND", "code"): False})

    def test_kinds_with_codes(self):
        self.assertEqual(self.names(KINDS_SHAPE), {("input", "kind"): None, ("timeout", "kind"): None,
                                                   ("INPUT_INVALID", "code"): False, ("TIMEOUT", "code"): False})

    def test_kinds_by_exit_code(self):
        self.assertEqual(set(self.names(EXIT_KIND_SHAPE)), {("failed", "kind"), ("input", "kind"), ("missing_tool", "kind")})

    def test_per_tool_lists_once_each(self):
        self.assertEqual(self.names(TOOLS_SHAPE), {("ARTIFACT_INPUT_NOT_FOUND", "code"): None, ("ARTIFACT_TOO_MANY_PAGES", "code"): None})

    def test_identity(self):
        self.assertEqual(et.skill_id(MAP_SHAPE, "f"), "map-shape")
        self.assertEqual(et.skill_id({}, "fallback"), "fallback")


class Check(unittest.TestCase):
    def setUp(self):
        self.tax = et.load_taxonomy()

    def test_known_shapes_have_no_unknown_codes(self):
        contracts = {et.skill_id(c, "?"): c for c in (LIST_SHAPE, NON_RETRYABLE_SHAPE, CLASSES_SHAPE, MAP_SHAPE, KINDS_SHAPE,
                                                       EXIT_KIND_SHAPE, TOOLS_SHAPE, NO_CODES)}
        report = et.check(self.tax, contracts)
        self.assertEqual(report["unknown"], {})
        self.assertEqual(report["no_codes"], ["no-codes"])
        self.assertEqual(report["retry_differs"], {"list-shape": ["CANCELLED"], "nonretry-shape": ["INTERNAL_ERROR"]})

    def test_unknown_code_is_reported(self):
        c = {"skill_id": "new", "errors": {"codes": ["INVALID_REQUEST", "BRAND_NEW_CODE"]}}
        report = et.check(self.tax, {"new": c})
        self.assertEqual(report["unknown"], {"new": ["BRAND_NEW_CODE"]})
        self.assertIn("BRAND_NEW_CODE", et.markdown(report))

    def test_override_wins(self):
        tax = json.loads(json.dumps(self.tax))
        tax["overrides"] = {"new": {"TOOL_ERROR": "INTERNAL"}}
        self.assertEqual(et.classify(tax, "new", "TOOL_ERROR", "code"), "INTERNAL")
        self.assertEqual(et.classify(tax, "other", "TOOL_ERROR", "code"), "ENGINE_FAILED")


class Cli(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="velisa-test-"))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60)

    def test_report_only_by_default_and_strict_on_request(self):
        tools = self.dir / "tools" / "new_skill"
        tools.mkdir(parents=True)
        (tools / "contract_1.0.0.json").write_text(json.dumps({"skill_id": "new", "errors": {"codes": ["NOPE"]}}), encoding="utf-8")
        out = self.run_cli("--contracts", str(self.dir / "tools"), "--json", str(self.dir / "r.json"), "--table")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("new: NOPE", out.stdout)
        self.assertEqual(json.loads((self.dir / "r.json").read_text())["unknown"], {"new": ["NOPE"]})
        self.assertEqual(self.run_cli("--contracts", str(self.dir / "tools"), "--strict").returncode, 1)

    def test_checkouts_layout(self):
        c = self.dir / "some-skill" / "contract"
        c.mkdir(parents=True)
        (c / "contract.json").write_text(json.dumps(LIST_SHAPE), encoding="utf-8")
        out = self.run_cli("--checkouts", str(self.dir), "--strict")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("Every declared code and kind maps to a class.", out.stdout)

    def test_nothing_found(self):
        self.assertEqual(self.run_cli("--contracts", str(self.dir)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
