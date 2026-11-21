---
description: Explain how a Velisa repository releases and what the next release would contain; dispatch it where the workflow allows
argument-hint: "<repo> [dispatch]"
allowed-tools: Bash(gh api:*)
---

Repository: the first word of "$ARGUMENTS" (a name under kajisho5, e.g. `qc-skill`; default `Velisa`). Read the velisa-maintainer skill's `references/releases.md` first if you have not.

1. Find the release workflow: `gh api repos/kajisho5/<repo>/actions/workflows -q '.workflows[] | {name, path, state}'`, then read the one that releases (`release.yml`, `release-please.yml`, `publish.yml` ...) with `gh api repos/kajisho5/<repo>/contents/<path> -q .content | base64 -d`. From its `on:` block and steps, say which method it is (push to main, after CI, bump pull request, release-please, hand bump, tag push) and whether it has `workflow_dispatch` (and its inputs).
2. The current state:
   - the latest tag and the version file on main (`VERSION`, `pyproject.toml`, `package.json`);
   - the pull requests merged since that tag, with their labels (`gh api 'repos/kajisho5/<repo>/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=50'`, keep `merged_at` after the tag's commit date);
   - the last run of the release workflow and its result.
3. Apply the gate (ADR-023 and its addendum): would the next push to main release, and at which level? Name the pull requests that decide it. If the version file is ahead of the tag, it releases as written.
4. Only if the second word of the arguments is `dispatch` and the workflow has `workflow_dispatch`: run it with `gh api -X POST repos/kajisho5/<repo>/actions/workflows/<file>/dispatches -f ref=main` (inputs as `-f 'inputs[name]=value'`, asking the user for any required input), wait for it, and report the tag and release it made (`gh api repos/kajisho5/<repo>/releases/latest`). Otherwise explain what would make it release (a release-level label on the next pull request, a version bump in a pull request, merging the release pull request).

Never push a tag and never bump a major version. Report in the user's language.
