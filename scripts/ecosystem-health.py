#!/usr/bin/env python3
"""One daily answer to "is anything in the ecosystem broken and nobody has looked?" for every repository in
ecosystem.json (and this one). Standard library only; reads the GitHub REST API (GITHUB_TOKEN / GH_TOKEN).

Per repository it reports:
  red        a workflow whose latest completed run on the default branch failed, and since when
             (push, schedule and workflow_dispatch runs; a nightly check that fails counts)
  manual     no run in the recent history was started by a push, a pull request or a schedule, so nothing
             tests a change unless someone starts a run by hand
  duplicate  the same workflow ran more than once for the same pull-request commit (wasted minutes)
  slow       pull-request runs take longer than SLOW_MINUTES on average
  stale      open pull requests older than STALE_DAYS

Modes:
  (default)  print the report (Markdown)
  --issue    keep one open issue labelled `ecosystem-health` in GITHUB_REPOSITORY: its body is replaced with
             the current report on every run, and a comment mentioning NOTIFY (default: the repository owner)
             is added only when something turned red since the previous run. Needs issues: write.
             Used by .github/workflows/ecosystem-health.yml.

Usage:
  python3 scripts/ecosystem-health.py [--report FILE]
  python3 scripts/ecosystem-health.py --issue [--report FILE]
Exit codes: 0 checked (healthy or not), 1 no repository could be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"
LABEL = "ecosystem-health"
TITLE = "Ecosystem health"
STATE_RE = re.compile(r"<!-- ecosystem-health-state\n(.*?)\n-->", re.S)
RUNS = 50
STALE_DAYS = 14
SLOW_MINUTES = 15
BAD = {"failure", "timed_out", "startup_failure"}
AUTOMATIC = {"push", "pull_request", "pull_request_target", "schedule", "merge_group"}

Fetch = Callable[[str, str, Optional[Dict[str, Any]]], Any]


def github(token: Optional[str]) -> Fetch:
    def fetch(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "velisa-ecosystem-health",
                                              "X-GitHub-Api-Version": "2022-11-28", **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
    return fetch


def when(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def repos(manifest: Dict[str, Any], hub: Optional[str]) -> List[str]:
    names = [c["repo"] for c in manifest["components"] if c.get("status") != "planned"]
    return names + ([hub] if hub and hub not in names else [])


def red_workflows(runs: List[Dict[str, Any]], branch: str) -> List[Dict[str, Any]]:
    """Workflows whose latest completed run on the default branch failed, with the start of the failing streak.
    `runs` is newest first, as the API returns it."""
    by_name: Dict[str, List[Dict[str, Any]]] = {}
    for r in runs:
        if r.get("head_branch") == branch and r.get("status") == "completed" and r.get("event") != "pull_request":
            by_name.setdefault(r.get("name") or "?", []).append(r)
    out = []
    for name, rs in sorted(by_name.items()):
        if rs[0].get("conclusion") not in BAD:
            continue
        streak = 0
        for r in rs:
            if r.get("conclusion") in BAD:
                streak += 1
            elif r.get("conclusion") == "success":
                break
        out.append({"workflow": name, "since": rs[streak - 1]["created_at"], "runs": streak, "url": rs[0].get("html_url")})
    return out


def inspect(fetch: Fetch, org: str, repo: str, now: datetime) -> Dict[str, Any]:
    info = fetch("GET", f"/repos/{org}/{repo}", None)
    if not info:
        return {"error": "not found"}
    branch = info.get("default_branch") or "main"
    runs = (fetch("GET", f"/repos/{org}/{repo}/actions/runs?per_page={RUNS}", None) or {}).get("workflow_runs") or []
    on_branch = (fetch("GET", f"/repos/{org}/{repo}/actions/runs?branch={branch}&per_page={RUNS}", None) or {}).get("workflow_runs") or []
    pulls = fetch("GET", f"/repos/{org}/{repo}/pulls?state=open&per_page=100", None) or []
    pr_runs = [r for r in runs if r.get("event") == "pull_request" and r.get("status") == "completed" and r.get("run_started_at")]
    minutes = sum((when(r["updated_at"]) - when(r["run_started_at"])).total_seconds() for r in pr_runs) / 60 / len(pr_runs) if pr_runs else None
    same = Counter((r.get("head_sha"), r.get("name")) for r in runs
                   if r.get("event") in ("push", "pull_request") and r.get("head_branch") != branch)
    return {
        "branch": branch,
        "red": red_workflows(on_branch, branch),
        "manual": bool(runs) and not any(r.get("event") in AUTOMATIC for r in runs),
        "no_ci": not runs,
        "duplicate": sum(1 for n in same.values() if n > 1),
        "minutes": minutes,
        "open": len(pulls),
        "stale": sorted(({"number": p["number"], "days": (now - when(p["created_at"])).days, "title": p.get("title") or "",
                          "author": (p.get("user") or {}).get("login") or "?"}
                         for p in pulls if (now - when(p["created_at"])).days >= STALE_DAYS), key=lambda p: -p["days"]),
    }


def collect(fetch: Fetch, org: str, names: List[str], now: datetime) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    state: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []
    for repo in names:
        try:
            state[repo] = inspect(fetch, org, repo, now)
        except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
            errors.append(f"{repo}: {e}")
            continue
        if state[repo].get("error"):
            errors.append(f"{repo}: {state[repo].pop('error')}")
            del state[repo]
    return state, errors


def red_keys(state: Dict[str, Dict[str, Any]]) -> List[str]:
    return sorted(f"{repo}:{w['workflow']}" for repo, s in state.items() for w in s["red"])


def report(org: str, state: Dict[str, Dict[str, Any]], errors: List[str], now: datetime) -> str:
    link = lambda repo: f"[{repo}](https://github.com/{org}/{repo})"   # noqa: E731
    red = [(r, w) for r, s in sorted(state.items()) for w in s["red"]]
    manual = sorted(r for r, s in state.items() if s["manual"] or s["no_ci"])
    dup = sorted((r for r, s in state.items() if s["duplicate"]), key=lambda r: -state[r]["duplicate"])
    slow = sorted((r for r, s in state.items() if (s["minutes"] or 0) > SLOW_MINUTES), key=lambda r: -state[r]["minutes"])
    stale = [(r, p) for r, s in sorted(state.items()) for p in s["stale"]]
    lines = [f"## Ecosystem health ({now:%Y-%m-%d}) — {len(state)} repositories",
             f"{len(red)} red workflow(s), {len(manual)} without automatic CI, {len(stale)} stale pull request(s), "
             f"{sum(s['open'] for s in state.values())} open pull request(s) in total.", ""]
    lines.append("### Red on the default branch" if red else "### Nothing is red on a default branch")
    for repo, w in red:
        days = (now - when(w["since"])).days
        lines.append(f"- {link(repo)} — **{w['workflow']}** failing for {days} day(s), {w['runs']} run(s) in a row"
                     + (f" ([latest]({w['url']}))" if w.get("url") else ""))
    if manual:
        lines += ["", "### No automatic CI (a change is tested only when someone starts a run)"] + [f"- {link(r)}" for r in manual]
    if stale:
        lines += ["", f"### Pull requests open for {STALE_DAYS}+ days"]
        lines += [f"- {link(r)} #{p['number']} ({p['days']} days, {p['author']}): {p['title'][:80]}" for r, p in stale]
    if dup:
        lines += ["", "### The same workflow ran twice for one pull-request commit"]
        lines += [f"- {link(r)} — {state[r]['duplicate']} time(s) in the last {RUNS} runs" for r in dup]
    if slow:
        lines += ["", f"### Pull-request runs slower than {SLOW_MINUTES} minutes on average"]
        lines += [f"- {link(r)} — {state[r]['minutes']:.0f} min" for r in slow]
    if errors:
        lines += ["", "### Could not read"] + [f"- {e}" for e in errors]
    return "\n".join(lines) + "\n"


def run_issue(fetch: Fetch, org: str, names: List[str], repository: str, notify: Optional[str], now: datetime) -> Tuple[str, int]:
    found = fetch("GET", f"/repos/{repository}/issues?labels={LABEL}&state=open&per_page=10", None) or []
    issue = next((i for i in found if "pull_request" not in i), None)
    m = STATE_RE.search(issue["body"] or "") if issue else None
    before = set(json.loads(m.group(1))) if m else set()
    state, errors = collect(fetch, org, names, now)
    if not state:
        return report(org, state, errors, now), 1
    text = report(org, state, errors, now)
    keys = red_keys(state)
    body = (text + "\nUpdated daily by `.github/workflows/ecosystem-health.yml`. A comment is added only when something turns red.\n\n"
            "<!-- ecosystem-health-state\n" + json.dumps(keys) + "\n-->\n")
    if issue is None:
        issue = fetch("POST", f"/repos/{repository}/issues", {"title": TITLE, "body": body, "labels": [LABEL]})
    else:
        fetch("PATCH", f"/repos/{repository}/issues/{issue['number']}", {"body": body})
    fresh = [k for k in keys if k not in before]
    if fresh:
        fetch("POST", f"/repos/{repository}/issues/{issue['number']}/comments",
              {"body": (f"@{notify} " if notify else "") + "Turned red since the last check:\n" + "\n".join(f"- {k}" for k in fresh)})
    return text, 0


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issue", action="store_true", help="keep the report in the ecosystem-health issue of GITHUB_REPOSITORY")
    ap.add_argument("--report", help="also write the report (Markdown) to this file")
    a = ap.parse_args(argv)
    manifest = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))
    org = manifest["org"]
    repository = os.environ.get("GITHUB_REPOSITORY") or f"{org}/Velisa"
    names = repos(manifest, repository.split("/")[1] if repository.split("/")[0] == org else None)
    fetch = github(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    now = datetime.now(timezone.utc)
    if a.issue:
        text, rc = run_issue(fetch, org, names, repository, os.environ.get("NOTIFY") or repository.split("/")[0], now)
    else:
        state, errors = collect(fetch, org, names, now)
        text, rc = report(org, state, errors, now), (0 if state else 1)
    if a.report:
        Path(a.report).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
