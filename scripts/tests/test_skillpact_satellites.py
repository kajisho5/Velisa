"""scripts/skillpact-satellites.py finds the repositories with a SkillPact contract and summarises their
conformance runs (ADR-014). Offline: the raw.githubusercontent.com lookup is faked.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location("skillpact_satellites", ROOT / "scripts" / "skillpact-satellites.py")
sat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sat)

MANIFEST = {
    "org": "kajisho5",
    "components": [
        {"repo": "imagemagick-skill", "status": "active"},
        {"repo": "qc-skill", "status": "active"},
        {"repo": "nle-bridge-skill", "status": "planned"},
        {"repo": "broken-skill", "status": "scaffold"},
    ],
}
IM_CONTRACT = {"requirements": {"binaries": [{"name": "magick", "alternatives": ["convert", "sips"]},
                                             {"name": "unknown-tool"}]}}


def fake_get(seen):
    def get(url):
        seen.append(url)
        if url.endswith("/imagemagick-skill/HEAD/skill.contract.json"):
            return json.dumps(IM_CONTRACT)
        if url.endswith("/broken-skill/HEAD/skill.contract.json"):
            return "{not json"
        return None
    return get


class SatellitesTests(unittest.TestCase):
    def test_lists_repos_with_a_contract_and_skips_planned(self):
        seen = []
        found = sat.satellites(MANIFEST, fake_get(seen))
        self.assertEqual(found, [{"repo": "imagemagick-skill", "apt": "imagemagick"},
                                 {"repo": "broken-skill", "apt": ""}])
        self.assertFalse(any("nle-bridge-skill" in u for u in seen), "planned repositories are not looked up")
        self.assertIn("https://raw.githubusercontent.com/kajisho5/qc-skill/HEAD/skill.contract.json", seen)

    def test_apt_packages_follow_alternatives_and_skip_unknown(self):
        self.assertEqual(sat.apt_packages({"requirements": {"binaries": [{"name": "sips", "alternatives": ["ffprobe"]}]}}),
                         ["ffmpeg"])
        self.assertEqual(sat.apt_packages({}), [])

    def test_lookup_failure_other_than_404_is_not_swallowed(self):
        def boom(url):
            raise OSError("network down")
        with self.assertRaises(OSError):
            sat.satellites(MANIFEST, boom)

    def test_main_list_prints_a_matrix(self):
        with tempfile.TemporaryDirectory() as d:
            m = Path(d) / "ecosystem.json"
            m.write_text(json.dumps(MANIFEST), encoding="utf-8")
            import contextlib, io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(sat.main(["list", "--manifest", str(m)], get=fake_get([])), 0)
            self.assertEqual(json.loads(buf.getvalue())["include"][0]["repo"], "imagemagick-skill")

    def test_summary_table(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "a").mkdir()
            (p / "a" / "result-imagemagick-skill.json").write_text(
                json.dumps({"repo": "imagemagick-skill", "level": "L2-tested", "outcome": "success"}))
            (p / "result-broken-skill.json").write_text(
                json.dumps({"repo": "broken-skill", "level": "none", "outcome": "failure"}))
            out = sat.summary(p)
        self.assertIn("| `imagemagick-skill` | `L2-tested` | pass (L1 or better) | not reported | not reported |", out)
        self.assertIn("| `broken-skill` | `none` | below L1 or failed | not reported | not reported |", out)
        self.assertIn("No Skill declares progress events or error classes yet.", out)

    def test_summary_reports_what_each_skill_declares(self):
        # The Action's `declares` output (skillpact 0.8.1), as the matrix job records it: a compact JSON string.
        dec = {"capabilities": 3, "progress": ["image.resize", "video.encode"],
               "error_classes": {"BAD_INPUT": "input", "NO_BINARY": "environment", "TIMEOUT": "transient",
                                 "UNSUPPORTED": "input"},
               "idempotency": {"bit_exact": ["image.resize"], "content_equivalent": [], "none": []}}
        none = {"capabilities": 2, "progress": [], "error_classes": {},
                "idempotency": {"bit_exact": [], "content_equivalent": [], "none": []}}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            for repo, raw in (("imagemagick-skill", json.dumps(dec, separators=(",", ":"))),
                              ("qc-skill", json.dumps(none)), ("ingest-skill", ""), ("odd-skill", "[1, 2]"),
                              ("broken-skill", "{not json")):
                (p / f"result-{repo}.json").write_text(
                    json.dumps({"repo": repo, "level": "L2-tested", "outcome": "success", "declares": raw}))
            out = sat.summary(p)
        self.assertIn("| `imagemagick-skill` | `L2-tested` | pass (L1 or better) | 2 of 3 "
                      "| 4 code(s): environment 1, input 2, transient 1 |", out)
        self.assertIn("| `qc-skill` | `L2-tested` | pass (L1 or better) | 0 of 2 | none |", out)
        for repo in ("ingest-skill", "odd-skill", "broken-skill"):
            self.assertIn(f"| `{repo}` | `L2-tested` | pass (L1 or better) | not reported | not reported |", out)
        self.assertIn("- `imagemagick-skill`: progress events from `image.resize`, `video.encode`; error classes "
                      "`BAD_INPUT` input, `NO_BINARY` environment, `TIMEOUT` transient, `UNSUPPORTED` input", out)
        self.assertNotIn("- `qc-skill`", out)

    def test_parse_declares(self):
        self.assertEqual(sat.parse_declares('{"progress":["a"]}'), {"progress": ["a"]})
        self.assertEqual(sat.parse_declares({"progress": []}), {"progress": []})
        for bad in ("", "   ", None, "{x", "[]", "3"):
            self.assertIsNone(sat.parse_declares(bad))

    def test_summary_with_no_results(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("No repository", sat.summary(Path(d)))


if __name__ == "__main__":
    unittest.main()
