# Contract diff (Velisa ADR-020, ADR-022; D34, D36)

`kajisho5/Velisa/.github/workflows/contract-diff.yml@main` is a reusable workflow every Skill with a committed `contract/contract.json` calls on pull requests (25+ callers; ffmpeg-skill and video-production-agent do not call it).

## What it does

- Compares `contract/contract.json` at the merge base with the head using System Intelligence's `si contract-diff` (pinned to a commit SHA, v0.7.0). Every change gets an effect (`breaking`, `additive`, `info`) and a rule from `docs/VERSIONING.md` section 3.
- Puts exactly one label on the pull request: `contract:none`, `contract:additive` or `contract:breaking`.
- Keeps one comment, updated in place, posted by `comment-author` (default `github-actions[bot]`): the classification, the recommended bump and every change. It also writes the table to the job summary and the JSON report to an artifact.
- Recommended bump: before 1.0, breaking → minor and additive → patch; from 1.0, breaking → major and additive → minor.
- Report only: green whatever it finds, unless the caller sets `fail-on-breaking: true` (then the comment says the check fails on a breaking change). No caller sets it yet.

Callers group runs with `concurrency: {group: contract-diff-<pull request number>, cancel-in-progress: true}`, and the workflow checks the pull request's current head before writing, so an older run never writes last. Most callers filter on the contract path; udfkit runs on every pull request so a change that is reverted gets `contract:none` again.

## Reading it as a maintainer

- `contract:additive` is the normal state for a contract change (the ecosystem rule: additive unless the owner decided otherwise). Label the pull request so the release takes at least the recommended level (`feature` for a minor).
- `contract:breaking` needs the owner. Report it with the changes listed in the comment; do not merge on your own.
- A meaning change with the same name and type is not seen (VERSIONING section 3's silent break). Say so when you know of one.
- The agent's re-pin runs the same command on two tags; a breaking classification there is a `review` re-pin (repin.md).

## Run it locally

```bash
pip install "system-intelligence @ git+https://github.com/kajisho5/system-intelligence@32e087fb3aa499d054e71338e27bcf967eed91cc"
git show origin/main:contract/contract.json > /tmp/old.json
si contract-diff /tmp/old.json contract/contract.json --json
```

Related reusable checks (ADR-022): `contract-file-check.yml` (the generator's `--check`; no Skill calls it because each runs it in its own tests), `changelog-check.yml`, `release-guard.yml` (releases.md).
