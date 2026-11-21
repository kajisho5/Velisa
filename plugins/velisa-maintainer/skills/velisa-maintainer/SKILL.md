---
name: velisa-maintainer
description: Maintain the Velisa repositories (kajisho5/Velisa, video-production-agent and the Skill repositories) - re-pin sibling contracts, cut or explain a release, read a contract diff, apply the timebase and error-taxonomy specs, update the shared JSON schemas and conformance fixtures, read a roadmap, and know what a Claude Code session cannot do on GitHub. Use when asked to re-pin, release, bump a version, label a pull request for release, review a contract change, check timecode or error codes against the specs, export schemas to a Skill, or plan maintenance work across these repositories. Not for producing video (that is the velisa plugin's wakeup skill).
---

# Velisa maintenance

Velisa is one repository per component (listed in Velisa's `ecosystem.json`), held together by contracts, pins and shared checks. Work in a git worktree per change, branch from `main`, never force-push and never rewrite history. ffmpeg-skill is maintained apart: report its bugs, do not change it.

## Which reference to read

| Task | Read |
|---|---|
| Re-pin the agent to new Skill releases; a `repin: needs review` pull request | [references/repin.md](references/repin.md) |
| Release a repository, choose labels, a release that did not happen | [references/releases.md](references/releases.md) |
| A `contract:*` label or the contract-diff comment on a pull request | [references/contract-diff.md](references/contract-diff.md) |
| Frame rates, timecode, rounding; error codes and retries | [references/specs.md](references/specs.md) |
| `registry/schemas/`, conformance fixtures, exporting them to a Skill | [references/schemas.md](references/schemas.md) |
| A GitHub call that was refused from this session | [references/session-limits.md](references/session-limits.md) |

## Commands

- `/repin` dispatches video-production-agent's `repin` workflow and reports the pull request it opened or updated.
- `/release <repo>` says how that repository releases and what the next push to main would release; it dispatches only where the workflow has `workflow_dispatch`.
- `/roadmap <repo>` lists the open steps of that repository's `ECOSYSTEM_ROADMAP.md` with their "Done when".

## Rules that hold everywhere

- Decisions are recorded: an ADR in the repository it concerns, and a `D<n>` entry in Velisa's `docs/ecosystem/DECISION_LOG.md` for a cross-repository call. Take the next free number after checking `main` and the open pull requests.
- A contract change is additive unless the owner decided otherwise. The agent pins contracts byte for byte; a Skill release reaches it only through a re-pin.
- A release is made by the repository's release workflow, never by a tag pushed from a session. Pick the bump with the pull request's label (or its conventional-commit title, which the autolabeler turns into one). Never a major bump without the owner.
- A measurement that was not made is unknown. Say what was verified, by what, and what was not.
- Use the REST API (`gh api repos/...`). GraphQL, and every `gh` command built on it, fails here.
