"""The reusable contract-diff workflow (ADR-020, decision D34) keeps its promises: callable, report only by
default, three labels, System Intelligence pinned to a full SHA. Offline, text only.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github" / "workflows" / "contract-diff.yml").read_text(encoding="utf-8")


class ContractDiffWorkflowTests(unittest.TestCase):
    def test_it_is_a_reusable_workflow(self):
        self.assertRegex(WORKFLOW, r"(?m)^on:\n  workflow_call:")
        for name in ("contract-path:", "fail-on-breaking:", "label:", "comment:"):
            self.assertIn(f"      {name}", WORKFLOW)

    def test_it_reports_only_by_default(self):
        block = WORKFLOW.split("      fail-on-breaking:", 1)[1].split("      label:", 1)[0]
        self.assertIn("default: false", block)
        self.assertIn("if: inputs.fail-on-breaking && steps.diff.outputs.classification == 'breaking'", WORKFLOW)

    def test_the_three_labels(self):
        self.assertIn("for kind in none additive breaking; do", WORKFLOW)
        self.assertIn('"labels[]=contract:$CLASSIFICATION"', WORKFLOW)

    def test_system_intelligence_is_pinned_to_a_full_sha(self):
        pins = re.findall(r"kajisho5/system-intelligence@([0-9a-zA-Z_]+)\" # (v\d+\.\d+\.\d+)", WORKFLOW)
        self.assertEqual(len(pins), 1, pins)
        self.assertRegex(pins[0][0], r"^[0-9a-f]{40}$")

    def test_it_compares_from_the_merge_base(self):
        self.assertIn('git merge-base "$BASE_SHA" "$HEAD_SHA"', WORKFLOW)
        self.assertIn("fetch-depth: 0", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
