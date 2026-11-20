# Releases (Velisa ADR-022, ADR-023 and its addendum; D36, D37)

Release workflows are per repository (ADR-022 does not unify them). Read the repository's `.github/workflows/release.yml` (or `release-please.yml`) before acting: its `on:` block says whether it runs on a push to `main`, after CI (`workflow_run`), on a tag push, or also by hand (`workflow_dispatch`).

## Methods

| Method | Repositories (2026-11-20) | How a release happens |
|---|---|---|
| Release on push | audio-production, color-grading, detection, diarization, dubbing, imagemagick, ingest, media-analysis, motion-graphics, nle-bridge, publish, qc, remotion-ffmpeg, slide-sync, sound-design, subtitle, thumbnail, transcription, video-editing, voice-enhance; Velisa itself | merging a releasable pull request to `main`; the job resolves the version, writes the CHANGELOG section and contract, tests the commit, pushes commit and tag with `GITHUB_TOKEN` |
| After CI on main (`workflow_run`) | hyperframes | the same, once CI on `main` is green |
| Bump pull request | artifacts | merge the `chore(release): vX.Y.Z` pull request the workflow opens |
| release-please | blender (`blender-skill-vX.Y.Z`), stepcap | merge the release-please pull request |
| Version bumped by hand | bdmvkit, dvdcc, udfkit, vtskit (PyPI trusted publishing), oncemore | bump the version in a pull request; on the push to `main` (or by hand where `workflow_dispatch` exists) the job tags a version that has no tag yet. oncemore: the owner pushes the `v*` tag |

ffmpeg-skill and video-production-agent are outside these ADRs; read their own workflow.

## Which pull requests release (ADR-023 rule 2, D37 addendum)

In auto mode (the version file still equals the latest tag), a push releases only if a pull request merged since the tag qualifies:

| Pull request carries | Result |
|---|---|
| a release-level label (`feature` / `minor` / `enhancement`, `fix` / `bug` / `patch`, `major` / `breaking`, or what the repository's `version-resolver` maps) | releases at that level |
| `dependencies` (Dependabot) | releases, as a patch, in every Skill decided by labels or paths (addendum, 2026-11-19); a Dependabot `major` / `minor` label is about the dependency, not the Skill |
| no label at all | releases, as a patch (remotion-ffmpeg: nothing) |
| only `contract:none` / `contract:additive` / `contract:breaking` (the contract-diff bot's label) | as if it had no label: `release_gate.py` does not count `contract:*` labels (D37, addendum of 2026-11-20) |
| `contract:breaking` without a major label (`major`, or what `version-resolver` maps to major), on a Skill whose latest tag is 1.0.0 or later | nothing: the release job fails, and `release_gate.py` prints the pull request (ADR-031 section 5, D46 addendum). The pull request's own `major-label-check` fails first. It goes if the release is major anyway: another merged pull request carries `major`, or the major version was bumped by hand. On 0.x the rows above apply unchanged |
| only `chore`, `ci`, `docs` / `documentation`, `test`, `maintenance`, `refactor` | nothing |

A commit that came from no pull request is judged by its subject: `chore:`, `ci:`, `docs:`, `test:`, `build:`, `refactor:`, `style:` release nothing. A version bumped by hand in a pull request is released as written, whatever the labels.

- In the release-drafter repositories `.github/scripts/release_gate.py` decides "release or not" (output `releasable`) before release-drafter picks the level. It reads the release-level labels from the same repository's `release-drafter.yml` `version-resolver`, so the two cannot disagree. The file is identical in the 17 repositories that have it; change it everywhere or nowhere.
- hyperframes: `release.mjs plan` (same rule in JavaScript). imagemagick, remotion-ffmpeg: `resolve_version.py`. transcription: paths changed since the tag (its ADR-036) plus `dependencies` labels (its ADR-049).
- The autolabeler turns a conventional-commit title into a label (`feat:` → `feature`, `fix:` → `fix`, `docs:` → `docs`, `ci:` → `ci`, `chore:` → `chore`). `major` is never added automatically; only the owner adds it.

## The release commit is tested first (ADR-023 rule 1)

The job commits and tags locally, then the step "Test the release commit before pushing it" runs the fast tests (those that need no FFmpeg, ffmpeg-skill, ImageMagick or browser, always including the CHANGELOG, version and contract tests). A failure pushes nothing: `main` and the tags stay as they were, and the next qualifying push tries again. A test in each repository keeps that step between the commit and every `git push`.

CHANGELOG headings keep the repository's own form (`## X.Y.Z - date` or `## vX.Y.Z - date`). `changelog-check.yml` checks the headings and that a pull request moving the version adds its heading; `release-guard.yml` checks, after the tag exists, that the tag's `contract/contract.json` says the tag's version.

## Explaining "why did nothing release?"

1. Latest tag: `gh api repos/kajisho5/<repo>/tags -q '.[0].name'` (sort by version if tags are not in order).
2. Pull requests merged since: `gh api 'repos/kajisho5/<repo>/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=30' -q '.[] | select(.merged_at) | {number, title, merged_at, labels: [.labels[].name]}'`, keep those merged after the tag's commit date.
3. Apply the table above. Then read the last run: `gh api 'repos/kajisho5/<repo>/actions/workflows/release.yml/runs?branch=main&per_page=1'`, and its job log for "Nothing to release", a failed "Test the release commit" step, or a failed gate step naming a `contract:breaking` pull request. For that last case, add `major` to the pull request (only the owner does), or, when every breaking change is in an `EXPERIMENTAL` entry, have the reviewer remove `contract:breaking`. Then run the release again.

## Releasing from a session

- Never push a tag (refused from sessions, and it bypasses the tests). Never bump major.
- To release a change that carries only maintenance labels, add a release-level label to the next pull request, or bump the version in a pull request (`fix:` / `feat:` title).
- Where `release.yml` has `workflow_dispatch`, it can be run by hand: `gh api -X POST repos/kajisho5/<repo>/actions/workflows/release.yml/dispatches -f ref=main` (add `-f 'inputs[<name>]=<value>'` for its inputs). Dispatching does not change the gate: with nothing releasable it releases nothing.
- After a release, video-production-agent sees the new tag at its next re-pin (repin.md).
