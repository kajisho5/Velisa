# ADR-029: Monorepo or Polyrepo: the Repositories Stay Separate

Status: Accepted (decision D44). No migration.

## Context

Velisa is 33 components in 33 GitHub repositories (`ecosystem.json`, 2026-11-20): one engine (ffmpeg-skill), 27 Skills, two apps (oncemore, stepcap), two governance tools (skillpact, system-intelligence) and the agent (video-production-agent), with this repository as the catalogue, the marketplace and the home of the shared checks. Together they hold about 150 MB of history (GitHub's size figures; ffmpeg-skill 42 MB, skillpact 20 MB, stepcap 17 MB, oncemore 12 MB).

The cost of keeping them apart was visible in November 2026:

- **Rollouts are one pull request per repository.** The reusable checks went to 26 repositories in 26 pull requests (ADR-022), the release gate to 21 (ADR-023), the `dependencies` rule to 17 copies of the same `release_gate.py` (ADR-023 addendum). Each copy can drift.
- **Contracts cross repositories by pin.** The agent pins each Skill's `contract/contract.json` byte for byte. Re-pins were made by hand and went stale within hours until the agent automated them (its ADR-117); the first automated re-pin was red for a test that quoted an old release.
- **A change that spans repositories cannot be one commit.** The timebase work (ADR-026) left video-editing-skill and the agent to change their rate reading "together", which separate repositories can only do in two coordinated pull requests.

The question is whether one repository (a monorepo) would remove these costs, and at what price.

## Options

| | Polyrepo (today) | Monorepo |
|---|---|---|
| A change across Skills | one pull request per repository; reusable workflows (`@main`) and copied scripts | one pull request, one review, one CI run |
| Contract between Skill and agent | a pin per release, re-pinned by a workflow (ADR-117); the agent can lag a release | the agent reads the Skill's contract at the same commit; no pin, but also no independent release boundary |
| Releases | per repository, six methods (ADR-022), tags `vX.Y.Z` | per-package tags (`qc-skill-v1.4.5`) and a tool that releases only what changed; every release method rewritten |
| Installing one Skill | `pip install`, `npm`, a checkout, or `/plugin install <skill>@velisa` from a GitHub source per repository | the marketplace entries would have to point into subdirectories of one repository, and `pip install git+...` would need `#subdirectory=`; neither was tried here |
| Licences | per repository: MIT (most), LGPL-3.0 (bdmvkit, vtskit), Apache-2.0 (udfkit, dvdcc), GPL-3.0 (oncemore), skillpact's own | one repository carrying four licences, per directory, with the copyleft boundaries explained in one place |
| Engine | ffmpeg-skill is maintained apart: Velisa hands it proposals and never changes it (ROADMAP, proposals 5-14) | the engine either stays outside (so the main cross-repository dependency is still a pin) or its maintainers accept a shared repository |
| CI | each repository's CI is small and fast; a red Skill does not block another | one pipeline that must select tests by path to stay fast; one red test can hold every merge |
| History, issues, links | as they are | 33 histories merged, issues and pull request numbers moved or left behind, every link in every roadmap, ADR and the dashboard rewritten |
| Agent sessions | one repository per task, small checkout (disk is tight in cloud sessions) | one large checkout (about 150 MB of history before any build output) for every task |

## Decision

1. **Stay polyrepo.** Do not merge the repositories, in whole or in part.
2. **Reduce the costs above where they are, instead:**
   - shared logic is a reusable workflow in this repository (ADR-020, ADR-022), or one file kept identical by a test where a reusable workflow cannot hold it (`release_gate.py`);
   - contracts reach the agent by automated re-pin from release tags (video-production-agent ADR-117), and integration runs the siblings at the pinned releases, with their mains in a nightly canary;
   - shared data formats are specs, schemas and fixtures here that Skills copy into their tests (ADR-024), and shared rules are specs with vectors and reference code here (ADR-026, ADR-027);
   - a cross-repository change is planned in one roadmap entry here, with one pull request per repository linked from it.

## Why

- **Independence is the product.** Every Skill works alone and installs alone (`/plugin install <skill>@velisa`, `pip install`), and the agent works with whichever Skills are installed (the `wakeup` routing skill falls back when one is missing). A repository per Skill is the simplest way to keep that true: its own contract, its own release, its own tests that do not import a sibling.
- **The release boundary is useful.** The agent pins a release, not a commit on a sibling's main. A Skill's unreleased change cannot turn the agent red (the reason for ADR-117's pinned integration). A monorepo would trade that for atomic commits and need a new way to stop a half-finished Skill change from reaching the agent.
- **The licences differ**, including LGPL and GPL components. Separate repositories keep each one's terms obvious to whoever installs it.
- **The engine is not ours to move.** ffmpeg-skill is the largest dependency and is maintained apart; the main cross-repository coupling would remain a pin either way.
- **The measured costs are bounded and already automated.** The rollouts were one-off; the re-pin is now a workflow; copies of shared scripts are checked by tests. A migration would cost far more once (history, releases, marketplace, every link) and add a permanent cost (one large CI and one large checkout).

## When to revisit

Open this question again when one of these holds, measured over a month:

- more than a quarter of merged pull requests are one change split across three or more repositories;
- re-pins regularly need a hand fix (more than one `repin: needs review` a week that is not a real breaking change), or the agent stays more than a week behind a Skill's release;
- a shared script is copied into more than five repositories and the copies drift despite the tests;
- the marketplace and `pip` are shown (by a trial) to install a single plugin and a single package from a subdirectory of one repository, keeping per-Skill installs;
- the components gain a second team of maintainers who need to change many Skills at once, or the engine's maintainers ask to share a repository;
- the number of repositories doubles.

A partial step (for example, moving the governance tools or the disc kits into one repository each) is decided the same way, on these measures, in a new ADR.

## Consequences

- Cross-repository work keeps costing one pull request per repository; the reusable workflows and the maintainer plugin's commands (ADR-028) keep that cheap to do.
- The pins and the re-pin workflow stay a central mechanism and must keep working.
- Nothing is migrated, archived or renamed by this decision.
