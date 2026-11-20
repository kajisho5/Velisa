# ADR-030: What 1.0 Means for a Skill, and the Order the Skills Get There

Status: Accepted (decision D45). The owner approved moving the 0.x Skills to 1.0, one Skill at a time.

## Context

On 2026-11-20, 24 of the 27 Skills in `ecosystem.json` were still on a 0.x release. Three were already on 1.x (color-grading-skill 1.1.4, audio-production-skill 1.4.3, qc-skill 1.4.5). They reached 1.0 before this ADR, with no stated promise. ffmpeg-skill, the engine, is not a Skill here and is not touched. video-production-agent is the consumer: it pins each Skill's `contract/contract.json` byte for byte and gates each one by a version prefix (`SUPPORTED_SKILL_VERSIONS`, for example `("0.1.",)`).

Before 1.0, `si contract-diff` (ADR-020) recommends a minor bump for a breaking change and a patch bump for an additive one. That means a dependent cannot tell from the version alone whether a release breaks it. Every per-tool lifecycle in every committed contract is `EXPERIMENTAL`. That includes the three 1.x Skills, so no Skill yet says which parts it stands behind.

## Measurements (2026-11-20, every Skill on 0.x)

Sources, per repository, all read from `origin/main` and the release tags:

- **Releases:** the release tags.
- **Tag diffs:** `si contract-diff` (system-intelligence v0.7.0) between consecutive tags, over the last 10 tags that commit `contract/contract.json`. Tags cut before the contract was committed cannot be compared.
- **PR labels:** the `contract:*` labels on the last 30 merged pull requests (ADR-020's contract-diff caller).
- **Bugs:** open issues labelled `bug`. There were none in any repository. Known defects are listed from the open issues instead: CodeRabbit follow-ups labelled `fix`, and failing scheduled checks.
- **Tests:** test functions on main (`def test_`, `it(` / `test(`). No repository sets a coverage threshold.
- **Open steps:** unticked steps in `ECOSYSTEM_ROADMAP.md`, read for whether they would change the contract.
- **Agent:** whether video-production-agent pins and gates the Skill.

The ranking is most stable first. It is ordered by these criteria, in this order:

1. no breaking change in the tag diffs or the PR labels;
2. no open roadmap step that would change the contract;
3. no known open defect;
4. at least five releases;
5. the number of tests.

| # | Skill | Version (releases) | Tag diffs | PR labels | Open steps that change the contract | Known defects / open issues | Tests | Agent |
|---|---|---|---|---|---|---|---|---|
| 1 | thumbnail-skill | 0.1.22 (23) | 3 none | 4 none | none | none | 219 | pinned, gate `0.1.` |
| 2 | imagemagick-skill | 0.10.1 (17) | contract only in v0.10.1 | 4 none | none | #44: `contract --json` not byte-identical to the file; a brandkit OSError outside the JSON error path | 207 | pinned |
| 3 | motion-graphics-skill | 0.4.4 (31) | 3 none | 6 none | none (issue #10 asks to re-investigate `shape`) | #53 (docs wording) | 431 | pinned |
| 4 | subtitle-skill | 0.10.3 (29) | 2 none | 4 none | none | #45: karaoke accepts overlapping cue ranges; #37: scheduled ffmpeg-skill compatibility check failing | 280 | pinned |
| 5 | publish-skill | 0.2.5 (7) | 4 none | 4 none | none (step 7 is a field test) | 1 issue | 458 | pinned |
| 6 | vtskit | 0.4.2 (8) | 1 none | 3 none | none | none | 120 | not pinned |
| 7 | ingest-skill | 0.1.3 (4) | 3 none | 5 none | none | none | 116 | pinned |
| 8 | dubbing-skill | 0.2.4 (4) | 2 none | none labelled | none | 1 issue | 334 | pinned |
| 9 | diarization-skill | 0.3.5 (4) | 3 none | 4 none | none (step 6 is a field test) | 1 issue | 84 | pinned |
| 10 | voice-enhance-skill | 0.1.3 (4) | 2 none | none labelled | none (step 10 is a field test); every op measured on synthetic fixtures only | none | 174 | pinned |
| 11 | media-analysis-skill | 0.1.23 (24) | 3 none | 6 none | step 6 (incremental measurement: new inputs) | 1 issue | 147 | pinned |
| 12 | transcription-skill | 0.13.1 (35) | contract only in v0.13.1 | 4 none | steps 8 (script alignment), 12 (per-channel) | 1 issue | 428 | pinned |
| 13 | video-editing-skill | 0.8.8 (38) | 5 none, 2 additive (v0.8.7, v0.8.8) | 2 additive, 4 none | step 20 (`propose` candidates) | 2 issues | 348 | pinned |
| 14 | sound-design-skill | 0.3.6 (5) | 3 none | none labelled | steps 8 (tempo map), 12 (licence record spec) | none | 258 | pinned |
| 15 | udfkit | 0.2.1 (3) | contract not in tags | 2 none | none | 1 issue | 59 | not pinned |
| 16 | dvdcc | 0.2.1 (4) | contract not in tags | 3 none | none | 2 issues | 38 | not pinned |
| 17 | bdmvkit | 0.7.1 (7) | contract only in v0.7.1 | 3 none | step 2 (bitrate planner) | none | 65 | not pinned |
| 18 | artifacts-skill | 0.4.0 (4) | contract not in tags | 3 none | step 6 (event documents) | 10 issues | 700 | pinned |
| 19 | slide-sync-skill | 0.1.3 (3) | 1 none, **breaking** at v0.1.3 | none labelled | none | none | 102 | pinned |
| 20 | detection-skill | 0.2.7 (5) | 3 none, **breaking** at v0.2.7 | 1 breaking | none | 1 issue; an agent gate change open (agent #177) | 141 | pinned |
| 21 | nle-bridge-skill | 0.1.4 (5) | 3 none, **breaking** at v0.1.4 | 1 breaking | none (step 8 is a field test) | none | 117 | pinned |
| 22 | remotion-ffmpeg-skill | 0.14.4 (21) | 2 none, **breaking** at v0.14.4 | 1 breaking | steps 6, 7, 8, 9, 11 (new compositions and inputs) | none | 150 | pinned |
| 23 | hyperframes-skill | 0.11.1 (20) | 3 none, **breaking** at v0.11.0 and v0.11.1 | 2 breaking | steps 7–11, 14; `contract_version` still 0.1 | 1 issue | 161 | pinned |
| 24 | blender-skill | 0.31.1 (33, two tag prefixes) | contract not in tags | 2 none | steps 6–9 (deferred scenes, passes) | 91 issues | 170 | pinned, no gate |

Reasons for the top of the order:

- **thumbnail-skill** has no breaking or additive change in its last measured releases, no open step, no open issue and 23 releases.
- **imagemagick-skill** has the same history. It ranks below thumbnail-skill only because of the two open CodeRabbit follow-ups in #44, and because its history before v0.10.1 cannot be compared.
- **motion-graphics-skill** has the longest history and the most tests, but an old issue that may add a `shape` element.
- **subtitle-skill** has an open input-validation defect (#45). The fix would refuse input that is accepted today. Its compatibility check is also red (#37).
- Breaking changes in the last release put slide-sync, detection, nle-bridge, remotion-ffmpeg and hyperframes near the end.
- Open contract-changing steps put remotion-ffmpeg, hyperframes and blender at the end.

## Decision

### 1. The compatibility promise

From a Skill's 1.0.0:

- A change that `si contract-diff` classifies as `breaking`, to any part of the contract the promise covers, ships only in a major release (X+1.0.0).
- An `additive` change ships in a minor or major release.
- A release with no contract change can be a patch.

These are si's own recommended bumps from 1.0 (ADR-020). The promise covers:

- every `provides[]` entry whose `lifecycle` is `STABLE`, and the tool it maps to;
- the request, response and error shapes those tools use;
- the top-level contract fields that are not tied to a capability.

`contract_version` stays a separate axis (VERSIONING section 1). 1.0 is the release version, not a contract-shape bump.

### 2. What stays experimental

A `provides[]` entry whose `lifecycle` is `EXPERIMENTAL` (or `PROPOSED`) is outside the promise. Its tool may still change in a minor release, including in ways si calls breaking.

Such a change is named in the pull request and in the CHANGELOG entry. The agent's re-pin still sees it as breaking and asks a person to review it (agent ADR-117), so nothing floats across it silently.

When a Skill goes to 1.0, it marks as `STABLE` only the entries it is ready to keep. Everything else stays `EXPERIMENTAL`. A tool without a `provides[]` entry is covered only if the Skill's README says so.

Promoting an entry from `EXPERIMENTAL` to `STABLE` is metadata, not a shape change: VERSIONING section 3, and si's `lifecycle-promoted` rule, classify it as none. It can happen in any release.

### 3. Deprecation

To retire a `STABLE` entry or a parameter:

1. Mark it `DEPRECATED` in a minor release. The CHANGELOG entry and the README name its replacement, or say there is none.
2. Keep it working for at least one further minor release and at least 30 days.
3. Remove it, or mark it `RETIRED`, only in the next major release.

Removing a `DEPRECATED` entry in a minor release breaks the promise. An `EXPERIMENTAL` entry can be removed in a minor release, with a CHANGELOG line.

### 4. How a Skill goes to 1.0

1. **Prepare**, in one pull request:
   - choose the `STABLE` entries;
   - write the promise in the README and an ADR in the Skill's repository.
2. **Release**, through the repository's own release flow. In the release-drafter Skills, a person puts the `major` label on that pull request: release-drafter resolves 1.0.0 from 0.x, and `release_gate.py` treats `major` as release-level. Where a flow cannot express a major bump, it is changed as little as possible, in the same pull request. `release-guard` (ADR-022) only checks that the tag's contract states the tag's version. The contract-diff caller (ADR-020) reports and does not block. So a 1.0 promotion with no breaking change needs neither of them changed.
3. **Re-pin**: the agent's `repin.yml` picks the tag up. A 0.x → 1.0.0 release whose contract diff is `none` or `additive` widens the gate to `1.0.`, like any other minor. Every other major change still goes to review.

   One Skill is landed (released, re-pinned, re-pin merged) before the next starts. The order is the ranking above. Skills the agent does not pin (the disc kits) skip the re-pin step.

## Consequences

- A dependent that floats across 1.x minors can rely on the `STABLE` entries. The version says when it must look again.
- Until a Skill marks an entry `STABLE`, its 1.x promise covers no capability. A Skill can therefore reach 1.0 with a small stable core and grow it.
- The three Skills already on 1.x adopt the promise with their first release that marks `STABLE` entries. Until then, everything in them is `EXPERIMENTAL`.
- Repositories are moved and their results recorded one at a time. This ADR does not change any Skill repository.
