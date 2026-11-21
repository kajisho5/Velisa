# ADR-020: Contract Changes Are Classified on Every Pull Request

Status: Accepted (report only; see "When it starts to fail")

## Context

Every Skill commits its contract as `contract/contract.json` (ADR-019-committed-contract-file), and video-production-agent pins those files byte for byte. `docs/VERSIONING.md` section 3 says which contract changes are breaking and which are not, but nothing applied it: whether a pull request only added to a contract or broke it, and so which release bump it needs, was left to whoever read the diff. The contract shape (ADR-018) and the direction of calls (ADR-019-layers-and-dependency-direction) are already checked by System Intelligence; the change between two versions of one contract was not.

## Decision

1. **The classifier is System Intelligence's `si contract-diff`** (its ADR-019, from v0.7.0). It compares two contracts key by key and gives every change an effect (`breaking`, `additive` or `info`) and a rule, the whole a classification (`none`, `additive` or `breaking`), and the release bump it needs: before 1.0, breaking is a minor bump and additive a patch; from 1.0, breaking is major and additive minor. The rules implement VERSIONING section 3; this repository does not keep a second copy of them.
2. **One reusable workflow, `.github/workflows/contract-diff.yml`** (`workflow_call`). On a pull request it compares `contract/contract.json` at the merge base with the one at the head, then:
   - puts one label on the pull request, `contract:none`, `contract:additive` or `contract:breaking`, and removes the other two (the labels are created on first use);
   - keeps one comment, updated in place, with the classification, the recommended bump and every change;
   - writes the same table to the job summary and the JSON report to an artifact.
   A pull request with no contract on either side is reported as nothing to compare. Inputs: `contract-path`, `fail-on-breaking` (default `false`), `label`, `comment`; outputs: `classification`, `recommended-bump`.
3. **A Skill opts in with a short caller** that runs on pull requests touching `contract/contract.json` and grants `issues: write` and `pull-requests: write`. It calls `kajisho5/Velisa/.github/workflows/contract-diff.yml@main`, so a change to the workflow reaches every caller; System Intelligence inside it is pinned to a full commit SHA, like `layering.yml`.
4. **Report only.** The job stays green whatever it finds. A pull request from a fork has a read-only token, so its label and comment steps may fail without failing the job; the summary and artifact still carry the result.
5. **First caller: qc-skill.** The other Skills are not wired yet; they are listed in decision D34.

## When it starts to fail

A caller sets `fail-on-breaking: true` once the owner decides that a breaking contract change needs an explicit acknowledgement (for example a `contract:breaking-accepted` label, or a `contract_version` bump checked by the same report). Until then the label and the comment are the signal.

## Consequences

- A reviewer sees on the pull request itself whether dependents can float across the change, and the bump the release needs.
- The classification is as good as the contract is explicit: a parameter that keeps its name and type but changes its meaning is not seen (VERSIONING section 3's silent break).
- ffmpeg-skill commits no contract file (ADR-019-committed-contract-file) and is not covered.
- The weekly re-pin in video-production-agent can use the same command on two tags (`si contract-diff --base-ref <old tag> --head-ref <new tag>`); that is the agent's decision, not this one.
