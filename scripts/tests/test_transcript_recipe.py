"""The routing skill's transcript recipe (transcript.md) against ecosystem.json.

The page names an owner for each job it describes; ownership lives in ecosystem.json, so a move there must show up
here instead of leaving the page pointing at the old owner.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "plugins/video-production-os/skills/video-production-os"
PAGE = SKILL_DIR / "transcript.md"
MANIFEST = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))
# The jobs the page names, each followed (within a sentence) by the repository that owns it.
JOBS = ["文字起こしの語句検索", "言い直し・重複の候補提示", "無音・フィラー除去"]


def owner(job: str) -> str:
    owners = [c["repo"] for c in MANIFEST["components"] if job in c["owns"]]
    assert len(owners) == 1, f"{job}: owners {owners}"
    return owners[0]


class TranscriptRecipeTests(unittest.TestCase):
    def setUp(self):
        self.text = PAGE.read_text(encoding="utf-8")

    def test_skill_links_the_page(self):
        self.assertIn("](transcript.md)", (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))

    def test_named_owners_match_ecosystem_json(self):
        for job in JOBS:
            with self.subTest(job=job):
                at = self.text.find(job)
                self.assertGreaterEqual(at, 0, f"{job} is not named on the page")
                self.assertIn(f"`{owner(job)}`", self.text[at:at + 160], f"{job}: owner is {owner(job)}")

    def test_speaker_switching_points_at_the_diarization_owner(self):
        self.assertIn(f"`{owner('話者識別')}`", self.text)

    def test_nothing_is_cut_without_confirmation(self):
        self.assertIn("CONFIRM", self.text)
        self.assertRegex(self.text, r"--filler-extra 啊")
        # every cut example is frame-accurate: word-level ranges must not snap to keyframes
        for line in re.findall(r"cut\.py [^`\n]*", self.text):
            with self.subTest(line=line):
                self.assertIn("--accurate", line)


if __name__ == "__main__":
    unittest.main()
