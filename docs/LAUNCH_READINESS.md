# Launch readiness

What has to be true before Velisa is announced as released, how each item is checked, and how the work
between now and then is run so that time goes into the product and not into finding out late that
something broke. Status tags as elsewhere: **CURRENT** (exists, verified), **PROPOSED** (not built).

This document is a gate, not a roadmap: features are in each repository's `ECOSYSTEM_ROADMAP.md`. An item
here is either checked by a machine every day or it names the person who has to check it.

## 1. Gates

A launch is go when every row is true on the same day.

| # | Gate | Checked by | How |
|---|---|---|---|
| G1 | No workflow is red on any default branch | machine, daily | `scripts/ecosystem-health.py` → issue `ecosystem-health` (**CURRENT**) |
| G2 | Every repository tests a change automatically (pull request and default branch) | machine, daily | same report, "No automatic CI" (**CURRENT**) |
| G3 | The agent runs against every Skill's default branch every night and against the last supported engine line | machine, nightly | `video-production-agent` `tests.yml` schedule (**CURRENT** once its schedule is merged) |
| G4 | Every pinned contract in the agent equals the Skill's latest release | machine, nightly | G3's integration legs fail on fatal drift; a failure opens an issue |
| G5 | One command installs the whole set on a clean macOS, Windows and Linux machine | machine, per change | `.github/workflows/install.yml` (**CURRENT**) |
| G6 | The reference productions finish end to end from real footage with the review checkpoints | owner | §3, P1–P3 |
| G7 | The four roadmap steps that need real material are confirmed | owner | §3, R1–R4 |
| G8 | No open security finding of high severity; dependency updates no older than 14 days | machine, daily | CodeQL where a repository runs it; stale pull requests in the health report |
| G9 | README, install instructions and the plugin marketplace name the same versions | machine, daily | `scripts/marketplace.py --check` in `skill-updates.yml` (**CURRENT**) |

G1–G5, G8 and G9 need no meeting: the health issue is the answer. G6 and G7 are the only gates that wait on
a person, so they are the critical path and should start first, not last.

## 2. How the work is run until launch

Measured on 2026-11-11 over the last 30–50 workflow runs of each of the 34 repositories:

- Four workflows had been red on a default branch for four days or more without anyone being told
  (a nightly compatibility check, a macOS test, a documentation deploy, and the agent's own tests).
- The agent's tests ran only when started by hand, so a Skill release that changed a pinned contract was
  found at the next manual run. Several re-pin rounds in one week came from this.
- Five repositories ran the same workflow twice for each pull-request commit.
- Thirteen dependency-update pull requests and three release pull requests were open in the Skill
  repositories, the oldest for 60 days.

The rules that follow from it:

1. **A failure is announced once, the morning after.** The health issue comments only when something turns
   red. Nothing else needs to be watched. A scheduled workflow in a single repository that can fail should
   also open an issue there (subtitle-skill's compatibility check and the agent's nightly do).
2. **Contracts are re-pinned by the night, not by the feature.** A Skill may release whenever it is ready.
   The agent's nightly run reports the drift; one re-pin pull request covers everything that drifted that
   day. A Skill change that touches a block a consumer pins says so in its pull request, so the re-pin is
   expected and not a surprise.
3. **One pull request, one automatic run.** `push` is limited to the default branch and tags; pull-request
   runs cancel the superseded commit. Scheduled and default-branch runs are never cancelled.
4. **Reproduce before the third push.** When a failure only shows in CI (an FFmpeg major the workstation
   does not have, another OS), the first follow-up commit adds the diagnostics the failure message lacked;
   it is not a guess at the fix. Tolerances are not loosened to get green.
5. **Dependency updates merge in the week they arrive** when their checks pass. Major bumps get their
   release notes read; a bump that needs a change gets it in the same pull request.
6. **Review is spent where it finds things.** The automated reviewer is limited to about one review an
   hour for the whole account. It is asked once per pull request, on the commit that is believed final,
   and the work does not wait for it once the checks are green and its findings are answered.
7. **Parallel work is split by repository, never inside one.** Two changes to the same repository at the
   same time cost a merge; two repositories cost nothing.

## 3. What only the owner can check

These need real footage, real accounts or a real editing application. Each takes under an hour once the
material is at hand; they are listed in the order that unblocks the most.

| # | What | Repository and step | Material |
|---|---|---|---|
| R1 | A hand-off opens correctly in a real editing application | nle-bridge-skill, step 8 | DaVinci Resolve or Premiere Pro, one finished project |
| R2 | Voice clean-up measured on real venue recordings | voice-enhance-skill, step 10 | two or three lectern or lavalier recordings with room noise |
| R3 | Speaker turns measured on real conference recordings | diarization-skill, step 6 | one panel discussion with three or more speakers |
| R4 | A first real upload on a test account | publish-skill, step 7 | a throw-away channel or account |
| P1 | Reference production: a recorded lecture with slides to a published video with captions | whole set | one lecture recording and its slide file |
| P2 | Reference production: a multi-camera panel to a cut with speaker names and loudness to standard | whole set | two or more camera files of one session |
| P3 | Reference production: a short promotional cut with graphics, music bed and a thumbnail | whole set | any event footage |

For P1–P3 the record to keep is the `ProductionReceipt` the agent writes, the time each step took, and
every place a person had to step in. Those three lists are the launch notes and the first known-issues
page.

## 4. Not gates

Left out on purpose, so they do not hold the date: optional engines (they are opt-in and checked by their
own tests), steps in a roadmap that are not ticked and are not in §3, and anything outside the scope in
`NEGATIVE_ARCHITECTURE.md`.
