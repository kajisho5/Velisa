---
description: Dispatch video-production-agent's repin workflow and report the pull request it opened or updated
argument-hint: "[--no-wait]"
allowed-tools: Bash(gh api:*)
---

Re-pin video-production-agent to the sibling Skills' latest releases (ADR-117). Read the velisa-maintainer skill's `references/repin.md` first if you have not.

1. Dispatch the workflow on `main`:
   `gh api -X POST repos/kajisho5/video-production-agent/actions/workflows/repin.yml/dispatches -f ref=main`
2. Find the run it started (the newest `workflow_dispatch` run created after step 1):
   `gh api 'repos/kajisho5/video-production-agent/actions/workflows/repin.yml/runs?event=workflow_dispatch&per_page=3' -q '.workflow_runs[] | {id, status, conclusion, created_at, html_url}'`
   Unless the arguments say `--no-wait` ($ARGUMENTS), wait for `status: completed` (poll every 30 s or so; a run takes a few minutes). If it failed, read the failed step's log (`gh api repos/kajisho5/video-production-agent/actions/runs/<id>/jobs`, then `.../actions/jobs/<job id>/logs`) and report it.
3. The pull request:
   `gh api 'repos/kajisho5/video-production-agent/pulls?head=kajisho5:bot/repin&state=open' -q '.[0] | {number, title, draft, labels: [.labels[].name], html_url, head: .head.sha}'`
   None: either nothing new was released (the run's summary says so, and an open re-pin would have been closed) or `bot/repin` has commits by someone else and was not rebuilt (a warning in the run). Say which.
4. Its CI: without a `REPIN_TOKEN` the workflow dispatches `tests` and `repin review` on `bot/repin`, so they are not in the pull request's checks list. Read the head commit's check runs:
   `gh api repos/kajisho5/video-production-agent/commits/<head>/check-runs -q '.check_runs[] | {name, status, conclusion}'`
5. Report, in the user's language:
   - the pull request (number, link, draft or ready, labels) and each sibling with its new version and its decision (`auto`, `widen`, `review`) from the body;
   - for a `review` re-pin (draft, `repin: needs review`): the reasons from its comment, the failing tests and the "Check before merging" lines from the head of the body; it waits for the owner to review, remove the label and mark it ready;
   - the CI state from step 4, and what is still running.

Do not merge from this command. Do not push to `bot/repin` unless asked: a push by anyone else stops the workflow from rebuilding the branch until that pull request is merged or closed.
