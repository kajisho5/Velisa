# ADR-022: Reusable Checks for Skills, and the Release Methods Left as They Are

Status: Accepted (contract-diff on every Skill with a contract; changelog-check and release-guard on trial)

## Context

ADR-020 gave the Skills one reusable workflow, `contract-diff.yml`, first called by qc-skill. Three smaller problems were known in it: two runs on one pull request could finish in the wrong order and leave the older result; with `fail-on-breaking: true` the comment still said "report only"; and the comment it updates was found by its first line alone, so a person's comment that quoted that line could be overwritten.

Other checks are written once per repository and drift apart: whether `contract/contract.json` is still what the code prints, whether `CHANGELOG.md` has a heading for the version a pull request ships, and whether a release tag's contract says the tag's version. The release workflows themselves differ more (table below), and each one is already tested in its own repository.

## Decision

1. **contract-diff.yml** (ADR-020) gains three fixes:
   - Callers set `concurrency: {group: contract-diff-<pull request number>, cancel-in-progress: true}`. The workflow also asks GitHub for the pull request's current head before it writes. When the head is no longer the commit it compared, it leaves the label and the comment to the newer run.
   - The comment says "This check fails the pull request on a breaking change" when `fail-on-breaking` is set, and "Report only" otherwise.
   - The comment it updates must be one posted by `comment-author` (default `github-actions[bot]`, the account of the workflow token).
2. **Three more reusable workflows** (`workflow_call`, read-only token, inputs reach scripts only through `env:`):
   - **`contract-file-check.yml`** runs the repository's own generator with `--check`: `python contract/generate.py --check` or `node contract/generate.mjs --check` (`runtime: python | node`). It installs the package first (`install`, default `pip install -e .` or `npm ci`).
   - **`changelog-check.yml`** checks two things. First, every level-2 heading of `CHANGELOG.md` is a version heading or an allowed other heading, each version appears once, and versions run newest first. Second, on a pull request that changes the version in `version-file`, the head has a heading for the new version and the version does not go down. The default heading pattern accepts every form the Skills use. Inputs cover the rest: `other-headings` for headings that are not versions, and `stop-at` for history older than an automated changelog.
   - **`release-guard.yml`** checks that `git show <tag>:contract/contract.json` says the tag's version. The tag is the given tag, else the pushed tag, else the newest tag matching `tag-pattern`. It releases nothing.
3. **The release workflows are not unified.** The table records the methods. The one step they all share is checked by `release-guard.yml`: the release commit regenerates the contract file, so a tag's file is that tag's own contract output.
4. **A check that already runs is not added twice.** `contract-file-check.yml` is for a repository whose test suite does not run the generator. Today every Skill below already runs `generate --check` from a unit test in CI on pull requests (`tests/test_contract_file.py`, blender-skill's `tests/test_all.py`, hyperframes-skill's `tests/contract-file.test.mjs`), so no Skill calls it yet.
5. **Rollout** (decision D36):
   - `contract-diff.yml`, with the concurrency group, goes on every Skill with a committed contract, except those whose contract shape is being reworked (dubbing, sound-design, voice-enhance, slide-sync).
   - `changelog-check.yml` and `release-guard.yml` are on trial in qc-skill (release on every push to main), publish-skill (hand-pushed tag) and blender-skill (release-please).

## Release methods (2026-11-19, updated the same day)

| Method | Repositories | Who makes the tag |
|---|---|---|
| A release job on every push to main. It resolves the version from the labels of the merged pull requests (release-drafter or its own resolver), writes the CHANGELOG section, regenerates the contract, and pushes the release commit and tag | audio-production, color-grading, media-analysis, motion-graphics, qc, subtitle, thumbnail, transcription, video-editing (release-drafter); publish, detection, diarization, ingest, nle-bridge (moved to this method on 2026-11-19); imagemagick, remotion-ffmpeg (own resolver, which also takes a version bumped by hand in the pull request) | the job, with `GITHUB_TOKEN` |
| The same, but run on the completion of CI on main (`workflow_run`) | hyperframes | the job |
| A bump pull request (`chore(release): vX.Y.Z`) opened by a workflow; merging it releases | artifacts | the release job after CI |
| release-please pull request | blender (tags `blender-skill-vX.Y.Z`), stepcap | release-please |
| The version is bumped by hand in a pull request. On the push to main, the release job tags a version that has no tag yet; it also runs on a tag push or by hand. PyPI trusted publishing | bdmvkit, dvdcc, udfkit, vtskit | the job, or a person |
| A person pushes `v*` on the main commit that carries the version; the job checks the version and creates the GitHub Release | oncemore (also builds the Mac app) | a person |

GitHub starts no workflow for a tag pushed with the default `GITHUB_TOKEN`. So where a job makes the tag, `release-guard.yml` is called on that workflow's completion (`workflow_run`); where a person pushes the tag, it is called on the tag push.

## Measured before the rollout

- **release-guard**: 26 tags across the 25 Skill repositories carry `contract/contract.json`, and all 26 say their tag's version (0 mismatches). For artifacts-skill (v0.4.0) and oncemore (v1.4.0), the newest tag is older than the file (`allow-missing-contract` lets the check pass with a warning). The four Skills that have no tags have nothing to check.
- **changelog-check**: 19 of the 25 repositories have a CHANGELOG, and the default settings pass 14 of them. The other five need an input:
  - blender-skill and stepcap have an old `## Changelog` section (`stop-at: ^## Changelog$`).
  - video-editing-skill has a "Before release automation" section (`stop-at`).
  - thumbnail-skill's release-drafter notes use level-2 headings inside each entry (`other-headings: ^## `).
  - audio-production-skill lists v0.4.0 four times and v0.3.0 twice in its history (`stop-at: ^## v0\.4\.0 `).
  bdmvkit, dvdcc, ingest, oncemore, udfkit and vtskit have no CHANGELOG.

## Rollout results (2026-11-19)

- **contract-diff**: 25 Skill repositories call it, with the concurrency group. On each caller's own pull request it labelled `contract:none` and posted one comment.
  - udfkit runs it on every pull request, not only on those that touch the contract, so that a pull request that changes the contract and then reverts it gets `contract:none` again. The other callers keep the path filter. Such a pull request keeps its old label there until a later run.
- **changelog-check** passed on its own pull request in qc-skill, publish-skill and blender-skill (`stop-at: ^## Changelog$`).
- **release-guard** passed by hand and on the release workflow's completion (`workflow_run`):
  - qc-skill checked v1.4.4 and publish-skill checked v0.2.3, the releases made by merging the trial;
  - blender-skill checked `blender-skill-v0.31.1` (`tag-pattern`; its stray `v0.0.1` tag is ignored).
- 16 release tags were made after these merges, the first in each repository to contain one. Every one carries a contract that says its tag's version.

## Consequences

- A fix to one of these checks reaches every caller through `@main`, as with ADR-020.
- The changelog check reads the version from a file. It cannot judge a version computed only at release time (method 1 before the release commit). There it checks the heading format, and the version heading is checked once the release commit exists.
- `release-guard.yml` finds a wrong tag after it is made; it does not stop it. The release jobs that check before tagging (publish-skill) keep doing so.
- ffmpeg-skill commits no contract file and calls none of these workflows.
- ADR-023 adds two rules to method 1 (and hyperframes, imagemagick and remotion-ffmpeg): the release commit is tested before it is pushed, and chore / ci / docs / test pull requests release nothing.
