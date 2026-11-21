"""The reusable contract-diff workflow (ADR-020, decision D34) keeps its promises: callable, report only by
default, three labels, System Intelligence pinned to a full SHA. Offline, text only.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
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

    def test_label_and_comment_wait_for_the_head_to_still_be_the_compared_commit(self):
        # Minor (a): an older run that finishes last must not overwrite a newer result.
        self.assertIn('current="$(gh api "repos/$REPO/pulls/$PR" --jq .head.sha)"', WORKFLOW)
        for step in ("Label the pull request", "Comment on the pull request"):
            block = WORKFLOW.split(f"- name: {step}", 1)[1].split("\n      - ", 1)[0]
            self.assertIn("steps.fresh.outputs.current == 'true'", block, step)
        self.assertIn("group: contract-diff-${{ github.event.pull_request.number }}", WORKFLOW)
        self.assertIn("cancel-in-progress: true", WORKFLOW)

    def test_the_comment_says_whether_it_fails(self):
        # Minor (b): with fail-on-breaking the comment no longer says "report only".
        block = WORKFLOW.split("- name: Comment on the pull request", 1)[1]
        self.assertIn('if [ "$FAIL_ON_BREAKING" = "true" ]; then', block)
        self.assertIn("This check fails the pull request on a breaking change", block)
        self.assertIn("FAIL_ON_BREAKING: ${{ inputs.fail-on-breaking }}", block)

    @unittest.skipUnless(shutil.which("jq"), "jq is not installed")
    def test_only_the_workflows_own_comment_is_updated(self):
        # Minor (c): a person's comment that starts with the marker is not taken over.
        program = re.search(r'--jq "(\.\[\] \| select\(\.user\.login.*?\.id)"', WORKFLOW).group(1)
        program = program.replace('\\"', '"').replace("$AUTHOR", "github-actions[bot]")
        program = program.replace("$marker", "<!-- velisa:contract-diff -->")
        comments = [
            {"id": 1, "user": {"login": "someone"}, "body": "<!-- velisa:contract-diff -->\nquoted"},
            {"id": 2, "user": {"login": "github-actions[bot]"}, "body": "unrelated"},
            {"id": 3, "user": {"login": "github-actions[bot]"}, "body": "<!-- velisa:contract-diff -->\n### Contract diff"},
        ]
        out = subprocess.run(["jq", program], input=json.dumps(comments), capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout.split(), ["3"])


if __name__ == "__main__":
    unittest.main()
