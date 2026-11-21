---
description: Show the open roadmap steps of a Velisa repository, with what "done" means for each
argument-hint: "<repo> [--all]"
allowed-tools: Bash(python3:*), Bash(gh api:*)
---

Run:

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py" $ARGUMENTS`

The argument is a repository under kajisho5 (it reads `ECOSYSTEM_ROADMAP.md`, else `docs/ecosystem/ROADMAP.md`, else `ROADMAP.md`, through the REST API) or a local roadmap file. `--all` also lists the steps that are done; `--json` gives the steps as data.

Show the result as it is, then in two or three lines, in the user's language: which open step looks next (the lowest number with nothing under "Needs" that is still missing), which steps need real hardware or real media (Velisa's `docs/field-test/` covers those), and any step that another repository must do first. Do not tick or edit a roadmap from this command.
