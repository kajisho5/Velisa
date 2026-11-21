"""The field test kit (docs/field-test/, scripts/field_test.py, decision D43). Offline.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("field_test", ROOT / "scripts" / "field_test.py")
ft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ft)

NOW = dt.datetime(2026, 11, 20, 9, 30, tzinfo=dt.timezone.utc)


class CatalogueTests(unittest.TestCase):
    steps = ft.load_catalogue()

    def test_every_step_is_complete(self):
        self.assertGreaterEqual(len(self.steps), 9)
        for sid, s in self.steps.items():
            self.assertRegex(sid, ft.ID)
            for key in ("repo", "step", "roadmap", "title", "done_when", "needs", "media", "how", "report_goes_to"):
                self.assertTrue(s.get(key), f"{sid}: {key}")
            self.assertIsInstance(s["consent"], bool)
            self.assertTrue(s["conditions"] and s["metrics"], sid)
            for c in s["conditions"]:
                self.assertRegex(c, r"^[a-z0-9][a-z0-9-]*$")
            for m in s["metrics"]:
                self.assertRegex(m, r"^[a-z0-9_]+$")

    def test_readme_lists_every_step(self):
        text = (ROOT / "docs/field-test/README.md").read_text(encoding="utf-8")
        for sid, s in self.steps.items():
            self.assertIn(f"`{sid}`", text)
            self.assertIn(s["repo"], text)

    def test_committed_results_are_well_formed(self):
        self.assertEqual(ft.main(["check"]), 0)


class RecordTests(unittest.TestCase):
    steps = ft.load_catalogue()

    def test_record_hashes_media_and_keeps_no_path(self):
        with tempfile.TemporaryDirectory(prefix="velisa-field-test-") as d:
            clip = Path(d) / "Speaker Name - hall.wav"
            clip.write_bytes(b"\x00" * 1000)
            rec = ft.build(self.steps["voice-enhance-venue"], verdict="partial",
                           measures=["lecture-hall:dereverb.wer_after_pct=12.4", "lecture-hall:dereverb.minutes=11"],
                           media=[f"hall={clip}"], env=["gpu=RTX 4060"], versions=["voice-enhance-skill=0.1.3"],
                           consent=True, now=NOW)
            self.assertEqual(rec["format"], "velisa/field-test-result@1")
            self.assertEqual(rec["media"], [{"label": "hall", "sha256": "541b3e9daa09b20bf85fa273e5cbd3e80185aa4ec298e765db87742b70138a53", "bytes": 1000}])
            self.assertEqual(rec["measurements"], {"lecture-hall:dereverb.wer_after_pct": 12.4, "lecture-hall:dereverb.minutes": 11})
            self.assertEqual(rec["missing_conditions"], ["lapel", "handheld-pa-bleed", "panel-3-mics"])
            self.assertTrue(rec["consent_stated"])
            self.assertFalse(rec["done_when_met"])
            j, m = ft.write(rec, self.steps["voice-enhance-venue"], Path(d) / "out")
            self.assertEqual(j.name, "2026-11-20-voice-enhance-venue.json")
            for f in (j, m):
                body = f.read_text(encoding="utf-8")
                self.assertNotIn("Speaker Name", body)
                self.assertNotIn(d, body)
            self.assertIn("| lecture-hall (dereverb) | wer_after_pct | 12.4 |", m.read_text(encoding="utf-8"))
            self.assertEqual(ft.validate(json.loads(j.read_text(encoding="utf-8")), self.steps), [])
            j2, _ = ft.write(rec, self.steps["voice-enhance-venue"], Path(d) / "out")
            self.assertEqual(j2.name, "2026-11-20-voice-enhance-venue-2.json", "a second run never overwrites the first")

    def test_yes_no_and_numbers(self):
        rec = ft.build(self.steps["publish-real-upload"], verdict="pass", now=NOW,
                       measures=["youtube.uploaded=yes", "youtube.processed_resolution=1920x1080", "youtube.processed_duration_s=12.5", "youtube.captions_accepted=no"])
        self.assertEqual(rec["measurements"], {"youtube.uploaded": True, "youtube.processed_resolution": "1920x1080",
                                               "youtube.processed_duration_s": 12.5, "youtube.captions_accepted": False})
        self.assertIsNone(rec["consent_stated"])
        self.assertTrue(rec["done_when_met"])
        self.assertIn("| youtube | uploaded | yes |", ft.markdown(rec, self.steps["publish-real-upload"]))

    def test_refusals(self):
        s = self.steps["diarization-der"]
        with tempfile.NamedTemporaryFile(prefix="velisa-field-test-") as f:
            with self.assertRaisesRegex(ft.FieldTestError, "--consent"):
                ft.build(s, verdict="partial", measures=["panel.der_pct=21"], media=[f"panel={f.name}"])
        cases = [
            (dict(verdict="pass"), "a pass needs"),
            (dict(verdict="partial", measures=["kitchen.der_pct=1"]), "condition 'kitchen'"),
            (dict(verdict="partial", measures=["panel.wer=1"]), "metric 'wer'"),
            (dict(verdict="partial", measures=["der_pct=1"]), "not <condition>.<metric>"),
            (dict(verdict="partial", measures=["panel.der_pct=1", "panel.der_pct=2"]), "twice"),
            (dict(verdict="partial", media=["x=/no/such/file"], consent=True), "no such file"),
            (dict(verdict="partial", env=["auth=token: abc"]), "credential"),
            (dict(verdict="partial", notes=["password=hunter2"]), "credential"),
            (dict(verdict="maybe"), "verdict"),
        ]
        for kwargs, msg in cases:
            with self.assertRaisesRegex(ft.FieldTestError, msg):
                ft.build(s, **kwargs)

    def test_validate_flags_a_hand_edited_record(self):
        rec = ft.build(self.steps["nle-bridge-real-nle"], verdict="fail", measures=["resolve-studio.imports=no"], now=NOW)
        self.assertEqual(ft.validate(rec, self.steps), [])
        bad = dict(rec, done_when_met=True)
        self.assertIn("done_when_met disagrees with the verdict", ft.validate(bad, self.steps))
        bad = dict(rec, media=[{"label": "x", "sha256": "0" * 64, "bytes": 1, "path": "/home/someone/x.mov"}])
        self.assertTrue(any("label, sha256 and bytes only" in e for e in ft.validate(bad, self.steps)))
        self.assertEqual(ft.validate(dict(rec, format="other"), self.steps), ["format is not velisa/field-test-result@1"])

    def test_cli(self):
        with tempfile.TemporaryDirectory(prefix="velisa-field-test-") as d:
            rc = ft.main(["record", "transcription-haas-gpu", "--verdict", "blocked", "--note", "no NVIDIA GPU here", "--out", d])
            self.assertEqual(rc, 0)
            files = sorted(p.name for p in Path(d).iterdir())
            self.assertEqual(len(files), 2)
            self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}-\d{2}-transcription-haas-gpu\.(json|md)", n) for n in files))
            self.assertEqual(ft.main(["check", *[str(p) for p in Path(d).glob("*.json")]]), 0)
        self.assertEqual(ft.main(["record", "no-such-step", "--verdict", "pass"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
