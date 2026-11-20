# Re-pin (video-production-agent ADR-117)

The agent keeps one pin per sibling Skill: the Skill's `contract/contract.json` at a release tag, byte for byte. ffmpeg-skill has no pin (no committed contract).

## What the workflow does

`.github/workflows/repin.yml` in kajisho5/video-production-agent runs at 02:11 and 14:11 UTC and on `workflow_dispatch`. It runs `scripts/repin.py`:

1. `update`: for each sibling, the latest release tag (`vX.Y.Z`; blender-skill `blender-skill-vX.Y.Z`). When it is newer than the pin, the tag's `contract/contract.json` replaces the pin (`tools/<skill>/contract_<new>.json`, `skills/pins/<package>_<new>.json`), the pin's readers under `src/`, `tests/`, `evals/` move with it (never `docs/`), and `si contract-diff OLD NEW --json` (system-intelligence v0.7.0) classifies the change. Then `integration/siblings.lock.json` is written.
2. `check`: the lock names every sibling and agrees with the pins (offline).
3. `verify` (addendum 1): the unit job's commands (read from `tests.yml`) and the evals run on the re-pinned tree. A failure makes the re-pin a `review` one.

Decision per sibling:

| Classification | Decision |
|---|---|
| none / additive, inside the adapter's `SUPPORTED_SKILL_VERSIONS` | `auto`: the pin moves |
| none / additive, a new minor of a 0.x / 1.x line outside the gate | `widen`: the gate takes the `X.Y.` prefix, with a dated comment; the refusal probes move to `X.(Y+1).0` |
| breaking, a major change (other than a first 1.0.0 after 0.x with a `none` / `additive` diff, which widens the gate to `1.0.`: agent ADR-117 addendum 3, ADR-031), a minor outside the gate on 2.x+, a tag not newer than the pin, or `verify` failed | `review`: the pin moves, the gate does not |

## The pull request

- One pull request per run, always from `bot/repin`, rebuilt from `main` and force-pushed with a lease (that branch only). An open one is updated in place; when `main` already has every latest release (and nothing was skipped), the open one is closed with a comment.
- The branch is not overwritten once anyone else has pushed to it: every commit past `main` must be the workflow's. A person's fix on the branch survives the next run; the run then exits with a warning, and the next re-pin waits until that pull request is merged or closed.
- Label `repin` always. A `review` re-pin is opened as a draft, labelled `repin: needs review`, and gets a comment listing the reasons. The body opens with the failing tests and "Check before merging": lines the rewrite left in `tests/` / `evals/` (history, or an expectation that should read the pin through `tests/pinned_versions.py`).
- The `repin review` check (`repin-review.yml`) is red while `repin: needs review` is on. To clear it, a person reviews, fixes the adapter, tests or gate on the branch if needed, removes the label and marks the pull request ready.

## The workflow_dispatch CI behaviour

A pull request opened with the workflow's `GITHUB_TOKEN` starts no workflow. Without a `REPIN_TOKEN` secret the repin job therefore runs `gh workflow run tests.yml --ref bot/repin` and `gh workflow run repin-review.yml --ref bot/repin` itself:

- the results are on the branch's head commit (`gh api repos/kajisho5/video-production-agent/commits/bot/repin/check-runs`), not in the pull request's checks list, so the pull request page can look as if no CI ran;
- the draft state is the merge gate for a `review` re-pin;
- the dispatched `repin review` finds the pull request by its head branch and reads its labels.

With `REPIN_TOKEN` (a token that may push and open pull requests) the push starts them on the pull request as usual.

## Doing it from a session

1. Dispatch: `gh api -X POST repos/kajisho5/video-production-agent/actions/workflows/repin.yml/dispatches -f ref=main` (or `/repin`).
2. Find the run: `gh api 'repos/kajisho5/video-production-agent/actions/workflows/repin.yml/runs?event=workflow_dispatch&per_page=1' -q '.workflow_runs[0] | {id, status, conclusion, html_url}'`, and wait until `status` is `completed`.
3. The pull request: `gh api 'repos/kajisho5/video-production-agent/pulls?head=kajisho5:bot/repin&state=open' -q '.[0] | {number, title, draft, labels: [.labels[].name], html_url}'`. No result after a successful run: nothing new was released, or the branch had someone else's commits (see the run's summary).
4. CI: the `tests` and `repin review` runs dispatched on `bot/repin` (step 2's query with `workflow_dispatch` on those workflows, or the check runs on the branch's head).
5. Merge an `auto` / `widen` re-pin when its tests are green (`gh api -X PUT repos/kajisho5/video-production-agent/pulls/N/merge -f merge_method=squash -f sha=<head>`). A draft cannot be merged; a `review` re-pin waits for the owner to mark it ready (a session cannot, see session-limits.md).

Do not hand-edit pins on another branch while a `bot/repin` pull request is open; push the fix to `bot/repin` instead, or let the next run rebuild it.
