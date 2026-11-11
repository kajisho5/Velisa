"""scripts/ecosystem-health.py reports what is broken across the ecosystem and nobody has looked at.
Offline: the REST calls are faked and the clock is fixed.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("ecosystem_health", ROOT / "scripts" / "ecosystem-health.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

NOW = datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc)


def run(name, conclusion, day, event="push", branch="main", sha="a", minutes=5):
    return {"name": name, "conclusion": conclusion, "status": "completed", "event": event, "head_branch": branch, "head_sha": sha,
            "created_at": f"2026-11-{day:02d}T06:00:00Z", "run_started_at": f"2026-11-{day:02d}T06:00:00Z",
            "updated_at": f"2026-11-{day:02d}T06:{minutes:02d}:00Z", "html_url": f"https://example.invalid/{name}/{day}"}


class FakeAPI:
    """repos: {name: {"runs": [...newest first...], "pulls": [...]}}; issues are kept in memory."""

    def __init__(self, repos, issue=None):
        self.repos, self.issue, self.comments, self.calls = repos, issue, [], []

    def __call__(self, method, path, body=None):
        self.calls.append((method, path))
        parts = path.split("?")[0].strip("/").split("/")
        if parts[3:4] == ["issues"]:
            if method == "GET":
                return [self.issue] if self.issue else []
            if method == "POST" and parts[-1] == "comments":
                self.comments.append(body["body"])
                return {}
            if method == "POST":
                self.issue = {"number": 7, "body": body["body"]}
                return self.issue
            self.issue["body"] = body["body"]
            return self.issue
        repo = self.repos.get(parts[2])
        if repo is None:
            return None
        if len(parts) == 3:
            return {"default_branch": "main"}
        if parts[3] == "actions":
            runs = repo.get("runs", [])
            return {"workflow_runs": [r for r in runs if r["head_branch"] == "main"] if "branch=" in path else runs}
        return repo.get("pulls", [])


class RedWorkflows(unittest.TestCase):
    def test_latest_failure_is_red_with_the_start_of_the_streak(self):
        runs = [run("nightly", "failure", 10, "schedule"), run("nightly", "failure", 9, "schedule"), run("nightly", "failure", 6, "schedule"),
                run("nightly", "success", 5, "schedule"), run("nightly", "failure", 1, "schedule")]
        red = health.red_workflows(runs, "main")
        self.assertEqual([(w["workflow"], w["since"], w["runs"]) for w in red], [("nightly", "2026-11-06T06:00:00Z", 3)])

    def test_a_failure_followed_by_a_success_is_not_red(self):
        self.assertEqual(health.red_workflows([run("tests", "success", 10), run("tests", "failure", 9)], "main"), [])

    def test_only_the_default_branch_and_not_pull_request_runs_count(self):
        runs = [run("tests", "failure", 10, branch="feature"), run("tests", "failure", 10, event="pull_request"), run("tests", "success", 9)]
        self.assertEqual(health.red_workflows(runs, "main"), [])

    def test_cancelled_runs_inside_a_streak_do_not_end_it(self):
        runs = [run("tests", "failure", 10), run("tests", "cancelled", 9), run("tests", "failure", 8), run("tests", "success", 7)]
        self.assertEqual(health.red_workflows(runs, "main")[0]["runs"], 2)


class Inspect(unittest.TestCase):
    def test_manual_only_ci_is_flagged(self):
        api = FakeAPI({"agent": {"runs": [run("tests", "success", 7, event="workflow_dispatch", branch="fix")]}})
        s = health.inspect(api, "o", "agent", NOW)
        self.assertTrue(s["manual"])
        self.assertFalse(s["no_ci"])

    def test_a_repository_without_any_run_is_flagged(self):
        s = health.inspect(FakeAPI({"r": {}}), "o", "r", NOW)
        self.assertTrue(s["no_ci"])
        self.assertFalse(s["manual"])

    def test_duplicate_runs_for_one_pull_request_commit(self):
        runs = [run("ci", "success", 9, "push", "feature", "s1"), run("ci", "success", 9, "pull_request", "feature", "s1"),
                run("ci", "success", 8, "pull_request", "other", "s2"), run("ci", "success", 7, "push", "main", "s3")]
        self.assertEqual(health.inspect(FakeAPI({"r": {"runs": runs}}), "o", "r", NOW)["duplicate"], 1)

    def test_average_pull_request_minutes_and_stale_pull_requests(self):
        runs = [run("ci", "success", 9, "pull_request", "f", "s1", minutes=10), run("ci", "success", 8, "pull_request", "g", "s2", minutes=30)]
        pulls = [{"number": 1, "created_at": "2026-10-01T00:00:00Z", "title": "old", "user": {"login": "bot"}},
                 {"number": 2, "created_at": "2026-11-09T00:00:00Z", "title": "new", "user": {"login": "me"}}]
        s = health.inspect(FakeAPI({"r": {"runs": runs, "pulls": pulls}}), "o", "r", NOW)
        self.assertEqual(s["minutes"], 20)
        self.assertEqual(s["open"], 2)
        self.assertEqual([(p["number"], p["days"]) for p in s["stale"]], [(1, 41)])


class Issue(unittest.TestCase):
    RED = {"sub": {"runs": [run("compat", "failure", 10, "schedule"), run("compat", "failure", 9, "schedule")]},
           "ok": {"runs": [run("tests", "success", 10)]}}

    def test_first_run_opens_the_issue_and_reports_what_is_red(self):
        api = FakeAPI(dict(self.RED))
        text, rc = health.run_issue(api, "o", ["sub", "ok", "gone"], "o/hub", "owner", NOW)
        self.assertEqual(rc, 0)
        self.assertIn("**compat** failing for 2 day(s), 2 run(s) in a row", text)
        self.assertIn("gone: not found", text)
        self.assertEqual(json.loads(health.STATE_RE.search(api.issue["body"]).group(1)), ["sub:compat"])
        self.assertEqual(len(api.comments), 1)
        self.assertTrue(api.comments[0].startswith("@owner "))

    def test_the_same_red_is_not_announced_twice_and_a_new_one_is(self):
        api = FakeAPI(dict(self.RED))
        health.run_issue(api, "o", ["sub", "ok"], "o/hub", "owner", NOW)
        health.run_issue(api, "o", ["sub", "ok"], "o/hub", "owner", NOW)
        self.assertEqual(len(api.comments), 1)
        api.repos["ok"] = {"runs": [run("tests", "failure", 11)]}
        health.run_issue(api, "o", ["sub", "ok"], "o/hub", "owner", NOW)
        self.assertEqual(len(api.comments), 2)
        self.assertIn("ok:tests", api.comments[1])
        self.assertNotIn("sub:compat", api.comments[1])

    def test_a_recovery_and_a_second_failure_is_announced_again(self):
        api = FakeAPI(dict(self.RED))
        health.run_issue(api, "o", ["sub"], "o/hub", "owner", NOW)
        api.repos["sub"] = {"runs": [run("compat", "success", 11, "schedule")]}
        text, _ = health.run_issue(api, "o", ["sub"], "o/hub", "owner", NOW)
        self.assertIn("Nothing is red", text)
        api.repos["sub"] = {"runs": [run("compat", "failure", 12, "schedule"), run("compat", "success", 11, "schedule")]}
        health.run_issue(api, "o", ["sub"], "o/hub", "owner", NOW)
        self.assertEqual(len(api.comments), 2)

    def test_nothing_readable_is_an_error_and_writes_no_issue(self):
        api = FakeAPI({})
        _, rc = health.run_issue(api, "o", ["a", "b"], "o/hub", "owner", NOW)
        self.assertEqual(rc, 1)
        self.assertIsNone(api.issue)


class Roster(unittest.TestCase):
    def test_the_hub_is_checked_too_and_planned_components_are_not(self):
        manifest = {"components": [{"repo": "a"}, {"repo": "b", "status": "planned"}]}
        self.assertEqual(health.repos(manifest, "Velisa"), ["a", "Velisa"])
        self.assertEqual(health.repos(manifest, None), ["a"])


if __name__ == "__main__":
    unittest.main()
