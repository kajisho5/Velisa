# ADR-023: The Release Job Tests Its Commit Before Pushing It; Chore / CI / Docs / Test Pull Requests Release Nothing

Status: Accepted (decision D37)

## Context

On 2026-11-19 most Skills moved to a release job that runs on every push to main (ADR-022, method 1). That job writes the release commit (version, CHANGELOG section, contract file) and pushes it with `GITHUB_TOKEN`. GitHub starts no workflow for a push made with that token. So main's CI never runs on the release commit, and nothing checks it before the next pull request does. Two mains broke this way on the same day:

- **sound-design-skill**: the v0.3.4 release commit (ce12090) wrote `## v0.3.4 - 2026-11-19`. Every hand-written section of its CHANGELOG reads `## X.Y.Z - date`, and `test_docs_give_the_vram_guidance` looks for `## 0.3.4`. The shared `render_changelog.sh` had been copied from video-editing-skill, whose CHANGELOG does use `## vX.Y.Z`. Seven more Skills (detection, diarization, dubbing, nle-bridge, publish, slide-sync, voice-enhance) got the same wrong form that day, though no test of theirs looked. Their first release sections also repeated the whole history under a second heading for a version that already had one.
- **hyperframes-skill**: the v0.10.3 release commit (2c02b62) released a `ci:` pull request that wrote no `## Unreleased` entry. `release.mjs bump` only renames that section, so CHANGELOG.md got no `## 0.10.3` section, and two tests in `tests/release.test.mjs` failed.

Both releases shipped only a CI change. With `version-resolver.default: patch`, and with chore / ci / docs mapped to a patch, every merged pull request cut a release. imagemagick-skill already released nothing for chore / ci / docs / test-only pull requests (its own `resolve_version.py`).

release-drafter cannot express "no release" itself. Its schema (v7.10.0) accepts only `major`, `minor` or `patch` for both `version-resolver.default` and a category's `semver-increment`.

## Decision

1. **The release job tests its commit before pushing it.** Every release workflow that pushes a commit to main does the same thing. It commits (and tags) locally, then a step named **"Test the release commit before pushing it"** runs the repository's fast tests on that commit. Only after that step does the job push. A failure pushes nothing, so main and the tags stay as they were. The fast tests are the ones that need no FFmpeg, ffmpeg-skill, ImageMagick or browser. They always include the tests that read CHANGELOG.md, the version and the contract file. A test in each repository keeps the step between the commit and every `git push`.
2. **Chore / ci / docs / test pull requests release nothing.** This is imagemagick-skill's rule, now the ecosystem's. On a push to main where the version still equals the latest tag (auto mode), the job releases only if one pull request merged since that tag qualifies. A pull request qualifies when it carries a release-level label (feature / minor / enhancement, fix / bug / patch, major / breaking, or whatever the repository's `version-resolver` maps to a bump) or carries no label at all; an unlabelled one still ships as a patch. A pull request labelled only chore, ci, documentation, docs, test, maintenance or refactor does not qualify. A commit that came from no pull request is judged by its subject (`chore:`, `ci:`, `docs:`, `test:`, `build:`, `refactor:`, `style:` do not release).
   - In the release-drafter repositories, `.github/scripts/release_gate.py` decides this before release-drafter runs, and it reads the release-level labels from that repository's `release-drafter.yml`. Each `version-resolver` no longer maps chore / ci / docs / test to a patch. `default: patch` stays, because the schema allows nothing else, and only an unlabelled pull request reaches it.
   - A version bumped by hand in a pull request is still released as written, whatever its labels.
   - `dependencies` keeps the meaning each repository gave it. It still maps to a patch in color-grading, media-analysis and qc.
3. **The CHANGELOG heading is the repository's own form.** `render_changelog.sh` writes `## X.Y.Z - date` where the CHANGELOG uses that form, and `## vX.Y.Z - date` where it already used the `v`. A test checks the rendered heading. hyperframes-skill's `bump` writes a `## X.Y.Z` section from the commit subjects when no pull request wrote `## Unreleased`.

## How each repository does it (2026-11-19)

| Repositories | Gate (rule 2) | Test before the push (rule 1) |
|---|---|---|
| sound-design, detection, diarization, dubbing, ingest, nle-bridge, publish, slide-sync, voice-enhance, video-editing, audio-production (`render_changelog.sh` family) | `release_gate.py` → `RELEASABLE` in `compute_version.sh` | `python -m unittest discover -s tests` (plus `contract/generate.py --check` where CI runs it). video-editing runs CI's module list; audio-production runs the four test files that need no FFmpeg |
| color-grading, media-analysis, motion-graphics, qc, subtitle, thumbnail | `release_gate.py`, read by each repository's own decision step | the contract, contract-file, release and version-source test files (color-grading and motion-graphics clone ffmpeg-skill main for the CLI contract tests) |
| hyperframes | `release.mjs plan` (same rule, in JavaScript) | `tests/release.test.mjs`, `contract.test.mjs`, `contract-file.test.mjs` |
| imagemagick | its `resolve_version.py` (unchanged; the rule's origin) | the suite of its no-ImageMagick CI job, and `contract/generate.py --check` |
| remotion-ffmpeg | its `resolve_version.py` (unchanged; stricter: unlabelled changes release nothing too) | `python -m unittest discover -s tests`, and `contract/generate.py --check` |
| transcription | ADR-036 (unchanged): decides by the paths changed since the tag. Changes only under `.github/`, `docs/`, `tests/`, release tooling or in Markdown release nothing | the CI unit list without the three modules that need FFmpeg |
| artifacts, blender | not applicable: the release goes through a pull request (a bump PR, release-please), so CI runs on the release commit before it reaches main. Conventional-commit `ci` / `docs` / `chore` already cut no release there | not applicable |

ffmpeg-skill and video-production-agent are not covered by this change.

## Rollout results (2026-11-19)

- **Before**: each Skill's main was tested locally at its newest commit. Two failed because of a release commit: sound-design-skill (`test_docs_give_the_vram_guidance`) and hyperframes-skill (2 tests in `tests/release.test.mjs`). The others passed. Some needed ffmpeg-skill or FFmpeg, as their CI provides. Seven more had release-written `## vX.Y.Z` headings in a `## X.Y.Z` CHANGELOG, and four of those had a duplicated first-release section. No test of theirs checked this.
- **After**: 21 pull requests merged, one per repository. The release run on each merge took one of three paths:
  - Releases with the new steps, the test before the push passing: sound-design v0.3.5 (and v0.3.6 for #29), hyperframes v0.10.4, detection v0.2.5, diarization v0.3.5, dubbing v0.2.4, nle-bridge v0.1.2, publish v0.2.5, slide-sync v0.1.2, voice-enhance v0.1.3, ingest v0.1.2, video-editing v0.8.6, audio-production v1.4.3, thumbnail v0.1.22. Pull requests on a `fix/` branch were labelled `fix` by the autolabelers, so they released.
  - "Nothing to release", because the merged pull request carried only maintenance labels: media-analysis, qc, subtitle, imagemagick, remotion-ffmpeg. transcription released nothing too, under its ADR-036.
  - Stopped by the new step before any push: color-grading and motion-graphics. Their contract tests need an ffmpeg-skill checkout that the release runner did not have. Nothing was pushed, and main and the tags were unchanged. A follow-up gives the step a clone of ffmpeg-skill main.
- Every new release heading has the repository's own form (for example sound-design `## 0.3.5 - 2026-11-19`, hyperframes `## 0.10.4`).

## Consequences

- A release commit that would fail the repository's fast tests is never pushed. The next push to main tries again.
- A push that merges only maintenance work no longer makes a tag, a GitHub Release or a package upload. That work ships with the next qualifying change.
- The gate reads labels, so a mislabelled pull request can be held back. A person who wants it released adds a release-level label before the next merge, or bumps the version by hand.
- The fast tests are a subset. Integration tests that need FFmpeg or ffmpeg-skill still run only in CI on pull requests.
- `release-guard.yml` (ADR-022) still checks a tag after it is made. This ADR adds the check before the push.
