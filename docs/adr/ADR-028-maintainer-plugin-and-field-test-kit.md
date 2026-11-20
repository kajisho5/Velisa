# ADR-028: A Maintainer Plugin Beside the OS Plugin, and a Kit for Steps That Need Real Hardware or Media

Status: Accepted (decisions D42, D43)

## Context

- **Maintenance knowledge is spread out.** How a re-pin works (video-production-agent ADR-117 and its addendum), how each Skill releases (ADR-022, ADR-023 and its addendum), what the contract-diff label means (ADR-020), the timebase and error-taxonomy rules (ADR-026, ADR-027) and the schemas (ADR-024, ADR-025) are each in a long ADR. A session that maintains the repositories re-reads them every time, and learns the limits of its own GitHub access (no tag push, no branch deletion, no GraphQL, no draft to ready, no settings change, no `@coderabbitai` comment) by being refused.
- **The marketplace has one local plugin**, `velisa`, which installs the whole OS for people producing video. Maintenance tools in it would reach every user.
- **Some roadmap steps cannot be finished by CI.** Their "Done when" needs a GPU with weights, Premiere Pro or DaVinci Resolve, a test account per platform, a set-top disc player, or consented recordings of people. Nine are open (or ticked with "still to do") across seven repositories on 2026-11-20. No roadmap marks them with 確認待ち or "awaiting confirmation"; they were found by reading each step. Nothing told the owner what to run, what to measure, or how to bring the numbers back.

## Decision

1. **A second local plugin, `velisa-maintainer`** (`plugins/velisa-maintainer/`), listed in the marketplace right after `velisa` by `scripts/marketplace.py` (category `maintenance`). It is not a dependency of `velisa`, so installing the OS does not install it.
   - One skill, `velisa-maintainer`: a short `SKILL.md` (which reference to read for which task, the commands, the rules that hold everywhere) and six references: `repin.md`, `releases.md`, `contract-diff.md`, `specs.md`, `schemas.md`, `session-limits.md`.
   - Three commands, following the plugin layout (`commands/*.md`): `/repin` dispatches video-production-agent's `repin.yml` and reports the pull request, its decision per sibling and its CI (which, without `REPIN_TOKEN`, is on the branch's commit, not in the pull request's checks); `/release <repo>` reads the repository's release workflow, applies the ADR-023 gate to the pull requests merged since the latest tag, and dispatches only where the workflow has `workflow_dispatch`; `/roadmap <repo>` runs `scripts/roadmap.py`, which lists the open steps of `ECOSYSTEM_ROADMAP.md` with their "Done when" through the REST API.
   - Every GitHub call in it is REST (`gh api`). None pushes a tag, merges, or marks a draft ready.
2. **A field test kit** in `docs/field-test/`: `steps.json` lists the nine steps with what each needs, the conditions to run and the metrics to record; `README.md` is the procedure (consent, accounts, running, committing); `scripts/field_test.py record` writes a JSON record (`velisa/field-test-result@1`) and a Markdown page into `docs/field-test/results/`. Media are hashed and never copied, and their paths are not written. A step whose media shows people refuses media without `--consent`. A value that looks like a credential is refused. `check` validates the committed results, and the scripts tests run it.
3. The step's own repository is updated from the committed result (its report or fixture, then the tick), not by the kit.

## Consequences

- A maintenance session loads one short skill and reads one reference, instead of five ADRs. The references copy facts from the ADRs; when an ADR changes, its reference changes in the same pull request (a test checks each reference still names its ADRs and key terms).
- The steps list goes stale as roadmaps change; a new hardware step is added by hand.
- The kit records what a person measured; it does not run the Skills. A result is evidence for the step's own repository, which keeps its "Done when".
- Not done: running any of the nine steps (no hardware, software, accounts or consented media here); a check that the plugin's commands run in Claude Code (their files are checked, the commands were not invoked from an installed plugin).
