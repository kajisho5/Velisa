# ADR-018: Contract-Shape Check and the Weekly Read-Only Reports

Status: Accepted

## Context

Decision D31 ([DECISION_LOG](../ecosystem/DECISION_LOG.md), 2026-11-12) gives each contract check one owner:

- The OS contract shape belongs to system-intelligence, and Velisa CI calls it.
- Side effects, signatures and isolation tests belong to skillpact (ADR-014).
- Runtime version gates belong to the agent.

Until now no Velisa workflow checked any contract against `registry/capability_contract.schema.json`. The two weekly System Intelligence calls were `si watch` (`scripts/ecosystem-audit.sh`) and `si diagnose .` (`dashboard.yml`). system-intelligence also had two read-only commands that nothing here ran (its ECOSYSTEM_ROADMAP.md step 8):

- `si roadmap-drift` (its ADR-015).
- `si diagnose --field` (its ADR-016). The ownership audit's gap G5 recommended running both weekly.

The Skills' contracts are produced by running each Skill. video-production-agent pins a copy of each one, byte for byte (`src/video_agent/tools/<name>/contract_<version>.json`). These pinned copies are the contracts the ecosystem runs on. D32 also generates the capability maps from them.

## Decision

1. **`.github/workflows/contract-shape.yml`** runs `si contract-check` (system-intelligence ADR-017). It runs over `ecosystem.json`, with the agent's pinned contracts and the schema from this repository's `registry/`, which is the reference definition. The workflow runs:
   - on pull requests and pushes that change `ecosystem.json`, the schema, the baseline or the workflow;
   - weekly, because the agent re-pins without any change here;
   - on demand.
2. **Each contract is matched to its component by its own identity.** The check matches `skill_id`, `id`, `skill.id` or `skill.package`. A match is either exact or with `-skill` added, never by similarity. A component with no pinned contract is listed as `no_contract` and is not checked. This applies, for example, to ffmpeg-skill, whose pin is a contract check rather than a JSON copy.
3. **It blocks on a break.** The job fails when a contract breaks the schema or is not JSON. It is a red check, not a required one, like the other ecosystem workflows.
4. **Known violations are listed, with a reason.** `registry/contract-shape-baseline.json` names each one by its component and a JSON Pointer; a pointer covers everything below it. A listed violation does not fail the job. Any other violation does. An entry that matches nothing is reported as stale, and should then be deleted. On 2026-11-13 the list holds six components: detection, diarization, dubbing, slide-sync, sound-design and voice-enhance. In each:
   - `dependencies[]` name every dependency under `id` (skills, packages and binaries alike), where the schema expects skill dependencies with `skill_id` and `version_range`;
   - `skill` is a string where the schema expects an object.

   Fixing these is a decision for the Skill (its contract) or for the registry owner (the schema), not for this workflow.
5. **The weekly ecosystem audit adds two reports.** `ecosystem-audit.yml` now also runs:
   - `si roadmap-drift ecosystem.json --github`, which reads the roadmaps and merged pull requests through the REST API, GET only, with the workflow's own token;
   - `si diagnose --field --ownership-map ecosystem.json`, which reads the CI config from the audit's clones and uses the agent's pinned contracts.

   Both are read-only (`SI_READ_ONLY=1`) and run with `continue-on-error`. They are added to the job summary, and their JSON reports go in the artifact. Like the rest of the audit, they report and never fail the build.
6. **Pinning.** Both workflows install System Intelligence at a full commit SHA, with its tag in a comment. This is the same way skillpact-conformance.yml pins the skillpact Action.

## Consequences

- A newly pinned contract that breaks the OS shape fails a Velisa check within a week, or at once when the schema or the list changes here.
- Coverage is what the agent pins: 21 of 33 components today. A Skill whose contract is not pinned as JSON is visible as `no_contract`, not silently passed.
- The weekly audit now shows roadmap drift and field readiness next to `si watch`, without anyone running them by hand.
- Moving System Intelligence to a newer version is a one-line change of the SHA in each workflow.
