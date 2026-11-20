# Decision Log — cross-repository / ecosystem-level judgment calls

**Status: CURRENT / IMPLEMENTED** (this document; a real log of decisions actually made).

This is not `docs/adr/` (this repo's own formal architecture ADRs — numbered, one
proposal/decision/consequence each) and not `docs/ECOSYSTEM_CHANGELOG.md` (what changed,
factually, in which PR). This is the smaller set of judgment calls made *while operating*
this project autonomously across repositories — the kind of thing a fresh session needs to
know so it doesn't re-litigate a question already thought through, or reverse a decision
without realizing one was made.

## D1 — Do not touch `video-production-agent`'s `SkillRegistry` yet

**Context**: discovered (2026-09-05, this session) that `video-production-agent` already
has a working, tested, independently-designed Skill→Tool selection mechanism
(`SkillRegistry.select_tool`), solving a problem this project's own `docs/ROADMAP.md`
Phase 4 describes as unbuilt future work.

**Decision**: do not rewrite, extend, or "upgrade" `video-production-agent`'s registry to
consume this project's `provides`/`registry/` mechanism without a separate, explicit
investigation and plan. Record the discovery in `CURRENT_STATE.md` and queue the
investigation in `WORK_QUEUE.md` instead of acting on it immediately.

**Why**: `video-production-agent`'s registry is real, tested (187 tests), and underlies a
working end-to-end pipeline already in production use by its own author. It is not this
project's repository to rewrite unilaterally (per this project's own cross-repository rule:
"the smallest coherent change," "each repository remains independently maintainable").
Its own ADRs (028–032) are explicit and repeated on one point: "no shortcuts" between
layers — replacing a working, deliberately-static registration model with a dynamic one
is exactly the kind of "architecture inflation" this project has been told to avoid
introducing without genuine necessity. The right first step is investigation (does the
static model actually need to change, or does it already satisfy the spirit of "Capability
Discovery" well enough with a thinner connecting layer?), not a rewrite.

## D2 — Merge conflicts on Skill PRs are resolved with a `main` merge, not a rebase

**Context**: `ffmpeg-skill#24` (this project's own PR, on branch
`claude/add-capability-provides-field`) developed a real merge conflict after
`ffmpeg-skill#23` (a human-authored PR, typed colour correction) merged to `main` first.

**Decision**: merged `main` into the PR branch (one merge commit), resolved the one real
conflict (`CHANGELOG.md`, both sides added a section — kept both), verified both changes
still work together, pushed, and left one PR comment explaining what happened.

**Why**: matches this project's own standing PR-maintenance rules (merge, don't rebase, on
a conflict; never force-push over a shared branch) and the general principle that a PR this
project opened is this project's to keep green — a conflict is work now, not something to
wait out.

## D3 — `media-analysis-skill`'s five previously-unassigned Capability ids were resolved by direct code comparison, not by guessing

**Context**: the Phase 2 `provides` rollout initially left `media_probe`, `stream_layout`,
`video_format`, `audio_format`, `duration` unassigned because `CAPABILITY_MATRIX.md` §8c
hadn't pinned individual ids for them, and two real collision risks were unresolved
(`video_format` vs. `qc-skill`'s `measure.video.format`; `ffmpeg-skill`'s own `probe` tool).

**Decision**: resolved both risks by reading the actual implementations (not by inference
from names or descriptions) before assigning five new ids (`measure.media.probe`,
`measure.media.stream_layout`, `measure.video.probe`, `measure.audio.probe`,
`measure.media.duration`).

**Why**: this project's own repeated principle — never invent a capability id assignment
without verifying it against real code, because a wrong assignment (a false collision, or a
missed real one) is worse than leaving the gap open and documented. See
`CAPABILITY_MATRIX.md` §8c's "RESOLVED 2026-09-05" annotations for the specific evidence
each id's assignment rests on.

## D4 — This project maintains its own `provides`-based `registry/`, distinct from and not yet wired into `video-production-agent`'s registry

**Context**: two Skill/Provider selection mechanisms now coexist in the ecosystem — this
project's `registry/` (Capability-id-based, generic, not agent-specific) and
`video-production-agent`'s `SkillRegistry` (production-skill-name-based, hand-registered,
proven in production).

**Decision**: keep both, for now, rather than forcing a premature merge or deprecating
either. `registry/`'s README already states plainly what it is not ("not Phase 3", "not a
live registry") — this decision doesn't change that scope, it just makes explicit that
"connect the two" is deliberately deferred, not forgotten.

**Why**: per D1, a real investigation (which parts of `video-production-agent`'s selection
logic could be *expressed* in terms of `provides` without changing its behavior, versus
which parts depend on assumptions `provides` doesn't capture, like declared-order fallback
policy) needs to happen before either mechanism should change. Forcing convergence before
that investigation risks breaking the one thing in this whole ecosystem that is a real,
working, end-to-end system today.

## D5 — `workspace_confinement`/`no_clobber_input` were redesigned around observable behavior, not the originally-planned request-mutation shape

**Context**: these two `SKILL_SPEC.md` §8 checks were originally scoped the same way as
`forbidden_keys_rejected` — submit a request with a bad value (an output path outside the
workspace, or equal to an input path) and confirm the Skill rejects it. Live testing
against `qc-skill` (the only Skill this conformance harness currently exercises against a
real process) found that shape doesn't fit: `qc-skill`'s `run` request schema has no
output-path field at all — its operations (`validate`/`inspect`/`check`) are read-only
measurement returning a report on stdout, and its on-disk report cache writes to a fixed
path under the workspace via a code path (`PathPolicy.resolve_output()`) that exists but
is never actually called anywhere in the real codebase (confirmed by `grep -rn` finding
zero call sites).

**Decision**: redesigned both checks around properties observable from outside the
process, real for any Skill regardless of whether it exposes a request-level output-path
field: `workspace_confinement` snapshots directories outside the declared workspace
before/after one real, synchronous run and fails if any gained a file;
`no_clobber_input` hashes the input fixture before/after and fails if its content
changed.

**Why**: this project's rule against unearned claims applies as much to a conformance
check's own design as to a status label — a check whose only test target doesn't have
the field the check assumes would either be permanently `NotImplementedError` (true but
stalled) or would need a synthetic fake to exercise (proving nothing about a real Skill).
The observable-behavior redesign is answerable against `qc-skill` as it actually exists
today, and the property it verifies (no stray writes outside the workspace; the input is
never mutated) is the same real safety guarantee `SKILL_SPEC.md` §8 items 4-5 are meant
to protect, reached by a different, equally valid route.

## D6 — `no_unsafe_shell_out` uses a full AST walk, not a text/regex scan, after the regex draft produced two real false positives

**Context**: the first implementation of this check scanned each Skill's source files
as raw text for patterns like `shell=True`, `eval(`, `exec(`. Run against the real
ecosystem (all 9 Python Skills' actual cloned source), it immediately produced two false
FAILs: `qc-skill`'s `rules.py` has a comment literally reading "no eval()/exec()... or
shell" (documenting the constraint, not violating it), and `subtitle-skill`'s
`engine.py` module docstring says "no shell=True" for the same reason — plus a related,
distinct false positive where the AST-level check itself flagged the safe, explicit
`shell=False` keyword as if any `shell=` presence were dangerous.

**Decision**: rewrote the check to walk the parsed AST exclusively, with no text/regex
fallback: `eval`/`exec` are only flagged as an `ast.Call` whose `func` is a bare
`ast.Name`, `os.system`/`os.popen` only as an `ast.Attribute` call, and a `shell=`
keyword's `ast.Constant` value is inspected directly — `False` clears, `True` fails, and
anything else (a variable, a dynamic expression) fails conservatively as "cannot
statically prove this is never True."

**Why**: a comment or docstring is a string literal in the AST, never a `Call` node, so
switching from text to AST structure eliminates the false-positive class entirely rather
than trying to special-case comment syntax on top of a fundamentally text-based
approach. This is the same principle D5 already established for `workspace_confinement`/
`no_clobber_input`: test the actual, real behavior of real ecosystem code before
trusting a check's first design, and fix the check's *design* rather than special-casing
away an inconvenient real finding. Verified: all 9 real Python Skills now correctly PASS
(`registry/tests/test_no_unsafe_shell_out.py` also carries both false positives as
permanent regression tests).

## D7 — The Ecosystem Dashboard's data flow is aggregate-in-CI, serve-static, never live-fetch-from-browser

**Context**: a user request to build a web dashboard over the ecosystem's GitHub state
explicitly required (a) never exposing a GitHub token to a browser, and (b) never
creating a second competing source of truth. Two architectures were possible: a live
backend service the browser calls per-request (needs a always-on server, and a
server-side proxy to hide the token), or a scheduled batch job that pre-computes one
static JSON file the browser fetches directly.

**Decision**: batch aggregation in CI (`dashboard/aggregator/`, run only by
`.github/workflows/dashboard.yml`), producing one static JSON snapshot
(`dashboard/web/public/data/ecosystem-snapshot.json`) that the static frontend
(`dashboard/web/`) fetches with a plain same-origin `GET` — no live backend service, no
token ever reachable from client code. Two new structured files
(`docs/ecosystem/registry.json`, `docs/ecosystem/capability-status.json`) restate facts
already required to exist in this project's prose docs, rather than inventing an
independent tracking database.

**Why**: this is the smallest architecture that satisfies both hard constraints at once
— no server to operate, patch, or scale (GitHub Actions + GitHub Pages are both already
free at this project's scale), and the token literally never exists in any code path a
browser executes, which is a stronger guarantee than "the server hides it from the
client" (there is no server to compromise). The tradeoff — data is only as fresh as the
last aggregation run (hourly, or on-demand via `workflow_dispatch`) — is an explicit,
accepted, documented cost (`dashboard/README.md`'s "Known gaps"), not a hidden one. See
`docs/adr/ADR-011-ecosystem-dashboard.md` for the full decision record.

## D7 — Merge-conflict resolutions on `color-grading-skill#4`/`qc-skill#5` fixed real gaps, not just text collisions

**Context**: both PRs developed real merge conflicts (2026-09-06) because sibling
feature PRs in the same repos merged first: `color-grading-skill#5` (PRIMARY_CORRECTION)
before `#4` (provides); `qc-skill#2/#3/#4/#6` (delivery_package/cross_artifact/
timeline_integrity/luminance checks) before `#5` (provides). In both cases the textual
conflict was superficial (both sides had independently claimed the next ADR number in
`docs/decisions.md`), but resolving it purely as text would have shipped a real bug: in
`color-grading-skill`, `contract.capability_provides()` would `KeyError` on
`PRIMARY_CORRECTION` (no entry in `CAPABILITY_IDS`); in `qc-skill`,
`tests/test_contract_completeness.py`'s own completeness invariant would fail on 7 new
checks unaccounted for in `CAPABILITY_CHECK_GROUPS`/`UNGROUPED_CHECKS`.

**Decision**: resolved both by (1) renumbering the losing side's ADR to the next free
number rather than picking one arbitrarily, and (2) fixing the actual code gap the merge
exposed — a provisional Capability id for `PRIMARY_CORRECTION` (`color.
primary_correction`, following the matrix's own `<domain>.<verb>` convention, same
pattern as motion-graphics-skill's `bug`/`chapter` ids) and adding the 7 new qc-skill
checks to `UNGROUPED_CHECKS` (each real, run against a fresh clone of the merged `main`
to confirm the same failure/error counts reproduce there too, so the resolution wasn't
mistaken for something the merge itself broke).

**Why**: this project's repeated principle — a merge conflict is a signal to actually
read both sides' code, not just to make text combine cleanly. A conflict that resolves
without error is not the same as a conflict that resolves *correctly*; here, git's
auto-merge of `contract.py`/`tests/test_contract_completeness.py` succeeded with no
marked conflict at all, yet still left behind a real defect only running the code (not
just `git merge`) would catch. Mid-resolution, an exploratory `git checkout origin/main
-- .` followed by `git checkout HEAD -- .` (meant only to compare against a clean
baseline) instead corrupted the in-progress merge's working tree — recovered cleanly via
`git merge --abort` and redoing the resolution from scratch, since nothing had been
committed or pushed yet. Recorded here so a future session doesn't repeat either
mistake: don't use `git checkout <ref> -- .` for read-only comparison during an
in-progress merge (a separate clone or worktree is the safe way), and always run the
affected code (not just diff it) after resolving a Capability-contract-shaped conflict.

## D8 — `docs/ROADMAP.md` Phase 4 stays as scoped; the Agent-integration investigation's output is a proposed diagnostic, not a rewrite

**Context**: `docs/ecosystem/WORK_QUEUE.md` item 1 asked whether Phase 4 ("Cross-Skill
Execution/Artifact model") is still needed as scoped, or should be rewritten as "a thin
connecting layer," once `video-production-agent`'s registry could be checked against real
`provides[]` data from all 10 merged rollout PRs (2026-09-06). Ran every one of the
42 `SkillSpec.tools` candidates in `default_registry()` against every real Skill's actual
`capability_provides()` (executed live from a detached worktree per repo, not from pinned
adapter fixtures) — see the item's own "Investigated 2026-09-06 (exhaustive)" section for
the full findings.

**Decision**: Phase 4's text is unchanged — the investigation found nothing that
contradicts its premise. `video_agent/service.py`'s `Service.adapter()` → `tools/
router.py`'s `ToolRouter` is still the actual hardcoded execution-routing path Phase 4
targets; `SkillRegistry.select_tool()` is a separate, declarative availability/fallback
layer that does not drive real execution today. What *is* new: concrete, evidenced support
for building a small, separate, read-only `--check-provides`-shaped diagnostic (now item 8
in `WORK_QUEUE.md`) — the investigation surfaced two real self-declared-tool-id cases
(`qc_check`, `subtitle_generation`/`subtitle_burn_in`) that such a diagnostic must join on
Capability id, never tool-id string, to avoid false-positiving, plus two real
published-but-unconsumed capabilities (`video-editing-skill`'s `video.trim`,
`audio-production-skill`'s five extra operations) worth a future `SkillSpec` each. That
diagnostic is new, additive tooling for `video-production-agent`'s own repository to build
when its own maintainers choose to — not something this investigation implemented, per the
item's own Boundary ("investigation and, if warranted, an additive diagnostic — not a
rewrite... Do not change Agent selection behavior as part of this item").

**Why**: distinguishing "the registry-driven execution model Phase 4 describes" from "a
read-only compliance report over the registry that already exists" avoids two mistakes at
once — prematurely rewriting Phase 4 away from real, still-valid future work on the
strength of a same-day finding, and conflating a low-risk, immediately buildable
diagnostic with the actual execution-path rewrite (moderate-to-high risk, touches 187 unit
/ 90 adapter tests per Phase 4's own risk section) that Phase 4's dependency chain
(Phase 3's collision-resolution policy) is not ready for yet.

## D9 — `qc-skill`'s tool-id "mismatch" is not drift to fix; `subtitle-skill`'s is real but wider-blast-radius than a rename

**Context**: `video-production-agent`#27's own diagnostic (item 8) reported both
`qc-skill` (10/10 Capability ids) and `subtitle-skill` (2/2) as `PROVIDES_MISMATCH`.
2026-09-06's initial write-up treated both the same way ("self-declared, not a live
bug"). Traced each Skill's actual CLI transport and the Agent's own adapter code to go
one level deeper, at the user's explicit direction to act on findings rather than only
report them.

**Finding, `qc-skill`**: its real CLI has exactly one operational subcommand, `qc run`
("run inspect/check/validate against a request document"); `check`/`inspect` are a field
*inside* that one request, not separate commands. `provides[]`'s single tool id
(`qc/run`) for all 10 Capability ids is therefore the *correct* granularity for what the
Skill actually exposes at the CLI level. The Agent's own `TOOL_CHECK`/`TOOL_INSPECT`
(`tools/qc/adapter.py`) are a deliberately *finer* identifier space of the Agent's own
choosing, correctly translated to the real `"check"`/`"inspect"` request field via
`TOOL_OPERATIONS` before any request is sent. Collapsing the Agent's two ids to match the
Skill's one would be a **regression** — it would erase the one distinction the Agent
needs to build the right request.

**Decision, `qc-skill`**: no fix. `PROVIDES_MISMATCH` is technically accurate (the
strings differ) but this specific shape — one real Skill-side command, several
Agent-side operation ids atop it — should be read as expected granularity difference,
not drift. Recorded so a future session doesn't "fix" this into a real bug.

**Finding, `subtitle-skill`**: unlike `qc-skill`, this really is a simple 1:1 naming
difference (`subtitle-skill/generate`/`render` vs. this Agent's `subtitle/generate`/
`render`) — reconcilable in principle. But `SKILL_ID = "subtitle"`
(`tools/subtitle/adapter.py`) does triple duty: the package-registry key, the required
tool-id prefix (`SkillPackage.validate()`), and a `ToolSpec.required_capabilities` entry
that must exactly match the *independently* named `CapabilityResolver` environment
capability (`capabilities/resolver.py`'s `_finishing_skill(caps, "subtitle", ...)`) and
two `SkillSpec.required_capabilities=["subtitle"]` entries in `registry.py`. Renaming
`SKILL_ID` for the tool-id fix without updating all three in lockstep would silently
break availability detection (the package would require a capability name
`CapabilityResolver` never populates, and `subtitle_generation`/`subtitle_burn_in` would
report `UNAVAILABLE` in every real environment).

**Decision, `subtitle-skill`**: not attempted. A correct fix touches
`tools/subtitle/adapter.py`, `capabilities/resolver.py`, two spots in `registry.py`, and
`tests/test_adapter_subtitle.py`'s literal tool-id references, together — real,
coordinated, testable work, scoped precisely enough now to execute confidently in a
follow-up, but a behavior-affecting rename this diagnostic's own PR should not bundle in
unasked.

**Why this belongs in the log**: distinguishing "the join key doesn't match" from "this
is actually wrong" is exactly the kind of judgment call that gets silently lost if only
the diagnostic's raw `PROVIDES_MISMATCH` label is trusted at face value next time.

**Update (2026-10-30), `subtitle-skill` half resolved**: fixed on the Skill side without renaming the Agent's
`SKILL_ID`. `subtitle-skill`#20 (v0.2.1) changed `provides[].tool_id` to `subtitle/generate` /
`subtitle/render`; `video-production-agent`#84 pins that contract and its diagnostics test asserts
`PROVIDES_VALID` for both. The `qc-skill` half is unchanged (no fix, by design).

## D10 — The Dashboard and Control Room take the landing page's visual language, not their own

**Context**: the Dashboard (`/`) and Control Room (`/control-room.html`) were styled as a
dark-only "control surface" (blue for in-progress, uppercase labels, boxed cards), while the
landing page (`/lp/`) served from the same site had its own light/dark system. A visitor
moving between them saw two unrelated products.

**Decision**: restyle both pages to the landing page's system (tokens copied from
`dashboard/web/public/lp/index.html` into `dashboard/web/src/styles/tokens.css`): light and
dark schemes, Manrope, sticky plain header with a Dashboard / Control Room switch and a link
to `lp/`, hairline-separated rows instead of card grids. Status chips map onto the four
verdict colors only (ok / warn / fail / unknown); "in progress" stays non-verdict (graphite
outline). Chip text uses slightly darker/lighter "ink" variants of the same hues so 12px text
keeps 4.5:1 contrast in both schemes. Data, sections, behavior, the PWA manifest/workbox
config and the token-safety checks are unchanged; the UI stays Japanese (no i18n yet).

**Why**: one site, one visual language; the verdict colors already mean pass/warn/fail/unknown
on the landing page's QC report, so reusing them keeps "green" meaning the same thing on every
page.

## D11 — The Dashboard and Control Room are English by default, with the landing page's EN/JA switch

**Context**: the landing page (site root) became English by default with a Japanese toggle,
but the Dashboard and Control Room under `/dashboard/` were Japanese only (D10: "no i18n
yet"). A visitor who chose English or Japanese on the landing page lost that choice one
click later.

**Decision**: the same rule and storage key as the landing page: `?lang=` in the URL first,
then `localStorage["avos-lang"]`, then English; toggling writes the key and rewrites the URL
with `history.replaceState`. A small in-repo layer (`dashboard/web/src/lib/i18n.ts`, a React
context plus `en`/`ja` dictionaries) instead of an i18n library: two languages and about 160
strings do not justify a dependency. `en` is the source and `ja` is typed against its
keys, so a missing translation is a type error; the existing Japanese wording is kept as the
`ja` strings. Header links carry `?lang=ja` while Japanese is active. Dates go through `Intl`
with the active locale. The initial HTML and the PWA manifest are English.

**Not translated**: snapshot data (repo names, roles, PR titles, roadmap and WORK_QUEUE.md
text, evidence strings, System Intelligence findings). It mirrors the project's English docs
(ADR-011), the same scope `lib/labels.ts` already drew.

**Why**: one site, one language rule; a link shared in Japanese opens in Japanese.

## D12 — Animated overlays: hyperframes-skill makes the material, motion-graphics-skill places it

**Context**: the ownership audit (2026-11-12, `docs/ecosystem/ownership-audit/`) found no owner for animated
overlays. ffmpeg-skill#425 (typed keyframes on `overlay`) was on hold until one was named.

**Decision** (owner, 2026-11-12): the material is made by `hyperframes-skill` (IN / LOOP / OUT segments, alpha) and
placed by `motion-graphics-skill`'s `rendered_layer` element. ffmpeg-skill#425 is not needed for this.

**Why**: both ends already ship (hyperframes-skill 0.8.0 segments and alpha, motion-graphics-skill ADR-25, agent
ADR-102). Keyframes in the engine would widen `overlay`'s responsibility, and the Remotion route carries licence
conditions.

**Evidence**: `ownership-audit/A-visual.md` §8 O1, §9(b).

**What follows**: video-production-agent needs one path that RUNS hyperframes-skill (today a handoff-only
SkillSpec) and passes its output to `motion.layer`. That output must be ProRes 4444 or another yuva format:
`rendered_layer` refuses a VP9 alpha WebM.

## D13 — One definition of `status`; voice-enhance, dubbing, sound-design and publish are `active`

**Context**: the four said `scaffold` while each has working operations wired into the agent. `scaffold` had three
meanings (README "an empty repository", MATURITY_MODEL "Scaffolded", the agent's "no package").

**Decision** (owner, 2026-11-12): the four become `active`. `status` has one definition, written in
`ecosystem.json`'s `$comment` and used everywhere: `active` = the repository ships working operations behind its
contract, released or not; `scaffold` = the repository exists, but no operation works yet; `planned` = the
repository does not exist yet. Release state (git tags, GitHub Releases) is tracked separately.

**Why**: the old label described none of the four, and three definitions meant every reader picked a different one.

**Evidence**: `ownership-audit/B-audio-recognition.md` §9(h); `ownership-audit/D-delivery-utility-governance-docs.md`
§5 (rows 1-2), §6.2, §9(f).

**What follows**: done in `ecosystem.json`, the routing skill's owner table and the org charts (both regenerated),
and README's sentence on `scaffold`. A release step goes on each of the four repositories' roadmaps. Their
`plugin` flag (each has a root SKILL.md) was not part of this decision and is unchanged.

## D14 — Platform duration and file-size limits: publish-skill's values are authoritative

**Context**: the limits live in ffmpeg-skill `_platforms.py` and in publish-skill `limits.py`, with different values
(X: 140 s against 1200 s). The 2026-10-30 decision gave the upload-side limits to publish-skill but left
ffmpeg-skill's table unchanged.

**Decision** (owner, 2026-11-12): publish-skill's values are authoritative (it owns アップロード制限). ffmpeg-skill
`check`'s duration and size rows are guidance only, and `publish plan` does not use them for its verdict.

**Why**: publish-skill's values carry a source URL and a date; ffmpeg-skill's are constants without one. This
extends the 2026-10-30 split instead of reopening it.

**Evidence**: `ownership-audit/D-delivery-utility-governance-docs.md` §3 O1, §8 O1, §9(b).

**What follows**: ffmpeg-skill is asked, in an issue there, to label those rows as guidance. Pending until they land:
publish-skill's `plan` stops using those rows for its verdict (at the audited revision it still includes every
ffmpeg-skill check row), and video-production-agent's QA, which copies the same rows into its own verdict, does the
same, so an X delivery over 140 s is not failed against publish-skill's 1200 s limit. `docs/ecosystem/registry.json` no longer calls publish-skill the owner of platform
delivery specs (D32).

## D15 — No motion-titles-skill; title and stinger material go to hyperframes-skill, the metadata to a Velisa spec

**Context**: the 2026-11-05 field review proposed `motion-titles-skill` for animated title and stinger files.

**Decision** (owner, 2026-11-12): not created. Folded into `hyperframes-skill` (stinger templates and
`stinger.json`, typesetting, brand input), which gains `テロップ・スティンガー・ループ素材`. The metadata shapes
`title.json` and `stinger.json` become a Velisa spec: [docs/specs/title-and-stinger.md](../specs/title-and-stinger.md).

**Why**: most of the draft already exists in hyperframes-skill 0.8.0 (templates, CSV batch, segments, alpha) and in
ffmpeg-skill `export`; the draft itself said the pictures are drawn by hyperframes-skill. A new repository would be
a thin layer over it.

**Evidence**: `ownership-audit/A-visual.md` §9(c).

**What follows**: the spec documents the fields video-editing-skill, motion-graphics-skill, qc-skill and the agent
already read (`cut_point`, `cover`, segments), and marks the rest as proposed. hyperframes-skill steps 15, 8 and 14
carry the work.

## D16 — No design-system-skill; `kit@1` is a Velisa spec

**Context**: three brand formats exist side by side (ffmpeg-skill `brand.json`, motion-graphics `theme@1` and
`brand_kit`); only motion-graphics-skill and remotion-ffmpeg-skill read one.

**Decision** (owner, 2026-11-12): not created. A Velisa spec only: `kit@1`, a superset of ffmpeg-skill `brand.json`,
with a mapping table to each renderer's existing input: [docs/specs/kit.md](../specs/kit.md). Revisit as a skill once
three or more renderers read `kit@1`.

**Why**: with two readers, deriving per-renderer files has few places to go; the spec costs nothing and keeps the
door open.

**Evidence**: `ownership-audit/A-visual.md` §9(d).

**What follows**: the agent can expand a kit into the inputs each skill already takes. hyperframes-skill step 14 and
thumbnail-skill are the next readers to watch.

## D17 — No asset-library-skill; the licence record is a Velisa spec

**Context**: fetching (ingest-skill `fetch`), the audio ledger (sound-design-skill library), indexing
(media-analysis-skill `library`) and credit checking (artifacts-skill `credits_attribution`) exist. Missing: a licence
record for video and images, and API search.

**Decision** (owner, 2026-11-12): not created. A Velisa spec only: the shared licence-record shape (licence, author,
source URL, attribution line, sha256, content_id) that sound-design-skill already writes, extended to video and
images: [docs/specs/licence-record.md](../specs/licence-record.md). Project credits keep using artifacts-skill
`credits_attribution`.

**Why**: the shape is the missing part; API search needs each service's terms checked first.

**Evidence**: `ownership-audit/C-command-ingest-engine-verification.md` §9(f);
`ownership-audit/B-audio-recognition.md` §8 D16, §9(g).

**What follows**: a stock API is not wired until its terms are read and recorded.

## D18 — No generative-media-skill; an ADR first

**Context**: the only generator today is thumbnail-skill's background (FLUX.2 [klein] 4B). No video generation exists.

**Decision** (owner, 2026-11-12): not created. An ADR in Velisa comes first: candidate engines, code and weight
licences, VRAM, commercial terms, and whether thumbnail-skill's `BackgroundProvider` can be reused.
[ADR-016](../adr/ADR-016-generative-media.md) is that ADR, status Proposed.

**Why**: weight licences decide what is possible, and the audit could not confirm them from primary sources.

**Evidence**: `ownership-audit/A-visual.md` §9(e).

**What follows**: no wiring or engine request until ADR-016 is accepted.

## D19 — Restoration: the no-weights baseline first; a skill only after an ADR on weight licences

**Context**: super-resolution and frame interpolation were proposed as a new area.

**Decision** (owner, 2026-11-12): no new skill. Wire the no-weights baseline first (ffmpeg-skill scaling,
`minterpolate`, `denoise`). A skill comes only after an ADR records the weights' licences:
[ADR-017](../adr/ADR-017-restoration.md), status Proposed.

**Why**: the baseline needs no new dependency and stays deterministic; the candidate weights' licences are unverified.

**Evidence**: `ownership-audit/C-command-ingest-engine-verification.md` §9(g).

**What follows**: an archive-preparation path in the agent (`deinterlace` → `denoise` → `stabilize` → `fit`), which
needs a `denoise` SkillSpec there.

## D20 — Titles: three makers, three roles

**Decision** (owner, 2026-11-12): `motion-graphics-skill` keeps `タイトル・テロップ` (burned into a programme);
`hyperframes-skill` gains `テロップ・スティンガー・ループ素材` (title and stinger material files);
`remotion-ffmpeg-skill`'s titles stay inside its own compositions.

**Why**: titles could be made in three places; the split follows what each output is, not which tool draws it.
Moving hyperframes' templates into motion-graphics-skill would add Node and Chromium to a dependency-free skill.

**Evidence**: `ownership-audit/A-visual.md` §8 O2, §9(a).

**What follows**: `ecosystem.json` updated. The agent defaults to motion-graphics-skill and uses D12's path when
motion is needed.

## D21 — Overlays: still compositing, graphics placement and the engine

**Decision** (owner, 2026-11-12): `video-editing-skill` keeps `静止画オーバーレイ` (plain still compositing as part of
an edit). `motion-graphics-skill` gains `ロゴ・PiP・クロマキー合成` and `動くグラフィックの配置`. ffmpeg-skill's
`Bロール・画面合成` becomes `Bロール合成`; ffmpeg-skill stays the engine underneath.

**Why**: the jobs were split by name only; PiP and chroma key had no stated owner although motion-graphics-skill's
`video_overlay` does them.

**Evidence**: `ownership-audit/A-visual.md` §8 O3, §9(g).

**What follows**: wiring unchanged. The agent's SkillSpec descriptions can say when `edit.overlay` and `motion.image`
apply.

## D22 — Animated subtitles: from cues to subtitle-skill, word-timed effects to remotion-ffmpeg-skill

**Decision** (owner, 2026-11-12): everything generated from subtitle cues belongs to `subtitle-skill`, which gains
`動く字幕(字幕キュー由来)` and passes ffmpeg-skill `caption --animate/--karaoke` through. Word-timed effects belong to
`remotion-ffmpeg-skill`, which gains `語の時刻に合わせた字幕演出`.

**Why**: splitting by input keeps animated captions available without Node; the engine flags already exist.

**Evidence**: `ownership-audit/A-visual.md` §8 O4, §9(h).

**What follows**: a subtitle-skill step to expose the flags, then a re-pin in the agent.

## D23 — Loudness: audio-production-skill owns it; the agent's routing is not changed now

**Decision** (owner, 2026-11-12): `audio-production-skill` owns loudness (`音量・ラウドネス`, unchanged); ffmpeg-skill
is the engine. The agent's video path keeps `ffmpeg-skill/loudness`.

**Why**: the audit's two halves disagreed (move the route, or record it). Changing it needs evidence first.

**Evidence**: `ownership-audit/B-audio-recognition.md` §8 D1; `ownership-audit/C-command-ingest-engine-verification.md`
§8 S2; the README's "where the recommendations split".

**What follows**: a later change of routing needs a measured comparison of `loudnorm` against `ebur128` on the same
files.

## D24 — Compliance checking: the split is recorded, the wiring is not changed

**Decision** (owner, 2026-11-12): ffmpeg-skill `check` is the engine's preflight, so its `owns`
`書き出し規格の検査` becomes `書き出し前の規格点検`; `qc-skill` is judgement against the plan or spec.

**Why**: the two looked like a collision but do different jobs: fixed thresholds with fix commands, against rules
the caller supplies with UNKNOWN as a result.

**Evidence**: `ownership-audit/C-command-ingest-engine-verification.md` §8 S1, §9(c).

**What follows**: Velisa issue #36 can be closed with this record.

## D25 — Measurement and cut detection are layers, not collisions

**Decision** (owner, 2026-11-12): fast list = ffmpeg-skill `scenes`; observation = `media-analysis-skill`, which gains
`発話区間` (speech_regions); frame-accurate shot table = `detection-skill` `shots`, which gains `ショット検出`;
judgement only = `qc-skill`; slides = `slide-sync-skill`. Default providers stay as the agent has them.

**Why**: five scene detectors and three measurement paths serve different uses; the agent's `DEFAULT_PROVIDERS`
already has this shape.

**Evidence**: `ownership-audit/C-command-ingest-engine-verification.md` §8 S2, S3, §9(d);
`ownership-audit/B-audio-recognition.md` §8 D8/D9, D12.

**What follows**: `ecosystem.json` updated. Wiring `detection/shots` or `speech_regions` into the agent is a separate
step there.

## D26 — `owns` brought in line with what each repository does

**Decision** (owner, 2026-11-12):
- `video-editing-skill` gains `言い直し・重複の候補計算`; the agent's `言い直し・重複の候補提示` becomes
  `言い直し・重複の候補の提示と承認`.
- `transcription-skill` keeps `文字起こしの語句検索` and implements it (`find` / `search`).
- ffmpeg-skill keeps `納品レポート` (the tool exists; no consumer yet).
- ffmpeg-skill gains `カットリスト書き出し` (FCPXML / EDL / OTIO); `nle-bridge-skill` keeps the NLE round trip.

**Why**: the candidate computation already lives in video-editing-skill; the search was owned but not built; the
timeline export existed in two places with no stated split.

**Evidence**: `ownership-audit/C-command-ingest-engine-verification.md` §5, §8 S4, S6, S7;
`ownership-audit/D-delivery-utility-governance-docs.md` §3 O3, §8 O3.

**What follows**: WORK_QUEUE item 26 records the moved half; item 25 (the search) stands. The routing skill's
transcript recipe and its test follow the new names. Velisa issue #34 can be closed with the timeline split.

## D27 — Speaker ids: diarization-skill owns the assignment rule

**Decision** (owner, 2026-11-12): `diarization-skill` owns the rule that assigns speaker ids and gains
`話者IDの付与規則`. transcription-skill's merge is a copy of the same rule; both share conformance fixtures.

**Why**: two implementations of one rule drift unless one is named the source and a shared test holds them together.
Removing either would break a pinned contract.

**Evidence**: `ownership-audit/B-audio-recognition.md` §8 D10, §9(d).

**What follows**: the shared fixtures, in both repositories; the agent's wiring is unchanged.

## D28 — Kinetic typography, visualizers and Three.js: one owner each

**Decision** (owner, 2026-11-12): `hyperframes-skill` gains `キネティックタイポ・幾何学モーション`.
`remotion-ffmpeg-skill` gains `オーディオビジュアライザー` and keeps the measured (beat / lyric) versions. `blender-skill`
stays 3D only; its overlapping roadmap steps are deferred to these two.

**Why**: three roadmaps planned the same work while almost none of it is built; deciding before anyone starts avoids
building it twice.

**Evidence**: `ownership-audit/A-visual.md` §9(f).

**What follows**: remotion-ffmpeg-skill's Three.js step waits for hyperframes-skill's generative layer; blender-skill's
overlapping steps are marked deferred in its roadmap.

## D29 — Disc family: five entries, one agent SkillSpec

**Decision** (owner, 2026-11-12): `ecosystem.json` keeps the five (bdmvkit, vtskit, udfkit, dvdcc, oncemore). The agent
keeps ONE disc SkillSpec (`disc_author` via oncemore) and drops the four kit SkillSpecs, which name tool ids that do not
exist.

**Why**: five is right for installation and licences (the kits ship separately on PyPI); for the agent only
`disc_author` means anything.

**Evidence**: `ownership-audit/D-delivery-utility-governance-docs.md` §5 row 6, §8 O4, §9(a).

**What follows**: the SkillSpec change is in video-production-agent; nothing changes in `ecosystem.json`.

## D30 — stepcap and oncemore are listed as stand-alone apps

**Decision** (owner, 2026-11-12): add `"kind": "app"` to both. Other components need no `kind`; the default is
skill.

**Why**: neither is a production step the agent calls; both are applications with their own contract.

**Evidence**: `ownership-audit/D-delivery-utility-governance-docs.md` §9(d).

**What follows**: `scripts/tests/test_ecosystem_manifest.py` accepts `kind` (`skill` or `app`); the marketplace tags
stepcap `app`; the routing skill's owner table and the org charts show both as apps.

## D31 — Contract checks: one role each

**Decision** (owner, 2026-11-12):
- OS contract shape = `system-intelligence` (Velisa CI calls it).
- Side effects, signatures and isolation tests = `skillpact`.
- Runtime version gates = the agent.
- Velisa `registry/` = the reference definition of the collision policy.

**Why**: the same checks ran in three or four places under the same names with different content.

**Evidence**: `ownership-audit/D-delivery-utility-governance-docs.md` §8 O5, §9(e).

**What follows**: no wiring change; this entry is the written record.

## D32 — Stale documents are frozen; two maps are to be generated

**Decision** (owner, 2026-11-12):
- `HANDOFF.md`, `CROSS_REPO_STATUS.md` and `CURRENT_STATE.md` carry a header "2026-09 record, frozen; the current
  state is docs/ecosystem/ROADMAP.md".
- `docs/CAPABILITY_MATRIX.md` and `docs/REPOSITORY_MAP.md` are to be generated from the pinned contracts; only factual
  errors are fixed now.

**Why**: the three files still say 9 to 12 repositories and 21 tools; correcting them by hand would drift again.

**Evidence**: `ownership-audit/D-delivery-utility-governance-docs.md` §6 (54 rows), §8 O7;
`ownership-audit/A-visual.md` §8 O9.

**What follows**: headers added. Fixed now: `docs/ecosystem/registry.json` publish-skill row (not the owner of platform
delivery specs) and the "no package yet" notes on eight repositories that have packages; nle-bridge's `planned` in
ROADMAP.md; ROADMAP proposals 5-7 and 9-11 marked done (ffmpeg-skill #417, #418, #419, #421, #422, #423 closed
completed on 2026-11-06). The generator is WORK_QUEUE item 27.

## D33 — Layers: calls go down; same-layer calls are listed exceptions

**Decision** (owner, 2026-11-19, details delegated): every `ecosystem.json` component gets a `layer`. The five
layers, lowest first, are `engine` (ffmpeg-skill), `skill` (the 27 production skills and disc kits), `app`
(stepcap, oncemore), `orchestrator` (video-production-agent) and `governance` (skillpact, system-intelligence). A
component calls only lower layers. A same-layer or upward call is allowed only when `registry/layering.json` lists
it with its reason. Data contracts and clones made only in CI are not calls. One exception today:
thumbnail-skill → qc-skill (text legibility of thumbnail variants). The check is `si layer-check` (system-intelligence
ADR-018), which Velisa CI runs report-only (`layering.yml`).

**Why**: D21, D23, D24, D25 and D31 already describe an engine underneath, measurement layers and one owner per
check. Nothing recorded the layers or checked the direction of calls, so a skill-to-skill call could appear unseen.

**Evidence**: [ADR-019](../adr/ADR-019-layers-and-dependency-direction.md), whose inventory covers every edge with
its repository, SHA, file and line. The first run over the agent's pinned contracts found 15 declared calls: 14 go
down to ffmpeg-skill, 1 is excepted and 0 are violations.

**What follows**: the check starts to fail once the owner has accepted the exception list and every layer, two
weekly runs are clean, and the contract-shape baseline no longer lists `/dependencies` (ADR-019, "When the check
starts to fail"). `owns` is unchanged.

## D34 — Contract changes are classified on pull requests, report-only

**Decision** (owner, 2026-11-19, details delegated): a pull request that changes a Skill's `contract/contract.json`
is classified `none`, `additive` or `breaking` with System Intelligence's `si contract-diff` (its ADR-019), with the
release bump that needs (before 1.0: breaking minor, additive patch; from 1.0: breaking major, additive minor). The
reusable workflow `.github/workflows/contract-diff.yml` puts a `contract:none` / `contract:additive` /
`contract:breaking` label and one comment on the pull request. It reports only; a caller may opt in to failing
with `fail-on-breaking`.

**Why**: VERSIONING.md section 3 defines breaking and non-breaking contract changes, and every Skill commits its
contract (ADR-019-committed-contract-file), but nothing applied the definition, so the bump a contract change needs
was decided by eye.

**Evidence**: [ADR-020](../adr/ADR-020-contract-diff-on-pull-requests.md). Over the committed contract histories of
13 Skill repositories, every release-only change (the version repeated in the contract) reads `none`.

**What follows**: qc-skill calls the workflow first. Not yet wired, each with a committed contract: ingest,
video-editing, color-grading, motion-graphics, subtitle, thumbnail, blender, remotion-ffmpeg, hyperframes,
audio-production, transcription, diarization, detection, media-analysis, artifacts, publish, nle-bridge,
imagemagick, bdmvkit, vtskit, udfkit, dvdcc, stepcap, oncemore. No committed contract (nothing to compare):
ffmpeg-skill, voice-enhance, dubbing, sound-design, slide-sync. The check starts to fail only by a later decision
(ADR-020, "When it starts to fail"). `owns` is unchanged.

## D35 — Temporary directories: prefixed, always removed, movable, kept only on request

**Decision** (owner, 2026-11-19, details delegated): every temporary directory a component makes, in product code or tests, follows five rules:

- its name carries the component's prefix;
- it is removed on every path out (a context manager, `finally`, `addCleanup` / `addClassCleanup`, with `atexit` and SIGTERM as a backstop);
- it honours `TMPDIR`;
- it is kept only on an explicit opt-in that prints the path;
- each repository tests that a run with an empty `TMPDIR` leaves it empty.

**Why**: leftovers from tests filled shared disks twice: video-production-agent's `va_*` directories (14 GB), and later 11 GB in about 78,000 entries in one `/tmp`. Nothing said whose job removing them was.

**Evidence**: [ADR-021](../adr/ADR-021-temporary-directories.md), whose inventory lists what each skill repository left per run and the fix for each: hyperframes-skill (about 114 directories per run), video-editing-skill (138), remotion-ffmpeg-skill (4), transcription-skill (2) and artifacts-skill (1). The other 18 skill repositories leave nothing outside pytest's own retention.

**What follows**: two cases are not fixed yet:

- system-intelligence keeps the clone of a GitHub target by design (`si-github-*`). Removing it unless `--keep-clone` is given is that repository's follow-up.
- Velisa's own `control-room-test-*` and `registry_*` test directories fall under the same rule.

No ecosystem-wide check runs yet; skillpact's conformance job (ADR-014) is the place for one.

## D36 — Reusable checks for every Skill; release methods stay per repository

**Decision** (owner, 2026-11-19, details delegated):
- `contract-diff.yml` is fixed in three places. Overlapping runs no longer leave an old result: callers set a concurrency group, and the workflow re-reads the pull request's head before it writes. The comment says when the check fails the pull request. Only the workflow's own comment is updated.
- Three more reusable workflows are added: `contract-file-check.yml`, `changelog-check.yml` and `release-guard.yml`.
- The release workflows are not unified. Only the shared step is checked: a tag's `contract/contract.json` says the tag's version.

**Why**:
- The three contract-diff problems were found when the workflow was introduced (ADR-020).
- The changelog and tag checks were written per repository, or not at all.
- The Skills release in several different ways (six after the moves of 2026-11-19), each tested where it lives.

**Evidence**: [ADR-022](../adr/ADR-022-reusable-checks-and-release-methods.md) has the table of release methods and the measurements:
- 26 tags carry a contract file, and none disagrees with its tag.
- 14 of 19 CHANGELOGs pass the default settings, and the other five pass with one input each.
- Every Skill already runs `generate --check` in CI from a unit test.

**What follows**:
- contract-diff, with the concurrency group, goes on every Skill with a committed contract. ffmpeg-skill has no contract file. dubbing, sound-design, voice-enhance and slide-sync wait until their contract shape is reworked.
- contract-file-check is called by no Skill for now, because the check would run twice.
- changelog-check and release-guard are on trial in qc-skill, publish-skill and blender-skill. They go wider once the trial runs are clean. `owns` is unchanged.

**Rollout** (2026-11-19): the trial runs were clean, so both checks went on the other 26 Skills with a committed contract (ffmpeg-skill and video-production-agent excluded). Five need one changelog input (`stop-at` in four, `other-headings` in thumbnail-skill); five have no CHANGELOG and call release-guard only. release-guard runs on the completion of the workflow that makes the tag, and also on a pushed `v*` tag where a person can push one. Its first run passed in all 26. [ADR-022](../adr/ADR-022-reusable-checks-and-release-methods.md#rollout-to-every-skill-2026-11-19) has the inputs and triggers.

## D37 — The release job tests its commit before pushing it; chore / ci / docs / test pull requests release nothing

**Decision** (owner, 2026-11-19, details delegated):
- Every release job that pushes a commit to main tests that commit first. The step is called "Test the release commit before pushing it", and it runs the repository's fast tests, which include the CHANGELOG, version and contract tests. A failure pushes nothing.
- Pull requests labelled only chore, ci, docs, test or similar release nothing. A pull request with a release-level label releases, and so does one with no label at all (as a patch). This is imagemagick-skill's rule. In the release-drafter repositories, `release_gate.py` decides it, because release-drafter's `default` cannot say "no release".
- `render_changelog.sh` writes the heading in the form the repository's CHANGELOG already uses.

**Why**: the release commit is pushed with `GITHUB_TOKEN`, so main's CI never runs on it. On 2026-11-19 it broke two mains:
- sound-design-skill: a `## v0.3.4` heading, where the file and its tests use `## 0.3.4`;
- hyperframes-skill: no CHANGELOG section for 0.10.3.

Both releases shipped only a CI change.

**Evidence**: [ADR-023](../adr/ADR-023-release-commit-tested-and-gated.md) has the per-repository table and the measurements.

**What follows**: ffmpeg-skill and video-production-agent are not changed. artifacts-skill and blender-skill release through a pull request, so CI already runs on their release commit. transcription-skill keeps its path-based rule (its ADR-036), which already holds release back for docs / ci / test-only changes. `owns` is unchanged.

**Addendum** (owner, 2026-11-19): a pull request labelled `dependencies` releases, as a patch, in every Skill whose release is decided from labels or changed paths. Before, 18 of the 21 such Skills released nothing for it, or only for some updates; color-grading, media-analysis and qc already released it. `release_gate.py` is one file again in all 17 repositories that have it. Every `version-resolver` maps `dependencies` to a patch and maps no maintenance label. imagemagick and remotion-ffmpeg give it a patch in `resolve_version.py`, and transcription in `release_scope.py` (its ADR-049). [ADR-023](../adr/ADR-023-release-commit-tested-and-gated.md#addendum-2026-11-19-a-dependencies-pull-request-releases-a-patch) has the before / after table.

**Addendum** (2026-11-20): `release_gate.py` no longer counts the `contract:none` / `contract:additive` / `contract:breaking` labels that contract-diff (ADR-020) puts on every pull request. Before, a pull request whose only label was `contract:none` counted as "other labels only" and released nothing, although an unlabelled one ships as a patch. A `contract:*` label that a `version-resolver` maps to a bump would still count; none does today, and no release script reads these labels for the version. The file stays identical in all 17 repositories, each with a regression test.

## D38 — The shared data-format specs get JSON Schemas and conformance fixtures; Skills copy them into their tests

**Decision** (owner, 2026-11-19, details delegated):
- `kit@1`, `title.json`, `stinger.json` and the licence record each get a JSON Schema (draft 2020-12) in `registry/schemas/`. The schema follows the spec document, PROPOSED fields included as optional.
- What a schema cannot state (a time on a frame, `cut_point` inside `cover`, frame numbers agreeing with seconds) is a rule in `registry/spec_conformance.py`.
- Valid and invalid examples sit in `registry/conformance/<spec>/`, listed with their hashes in a generated `manifest.json`. Velisa's CI (`spec-conformance.yml`) fails when one does not behave as its directory says.
- A Skill copies the schemas and fixtures it needs into its tests (`--export`), pinned to a Velisa commit, and tests its writer or reader against them. Trial: hyperframes-skill (writes `title.json` / `stinger.json`) and motion-graphics-skill (reads `title.json`).

**Why**: the specs were tables. Each Skill checked its own reading of them, and nothing checked that a writer and its readers agree.

**Evidence**: [ADR-024](../adr/ADR-024-spec-schemas-and-conformance-fixtures.md) has the table of every place an implementation differs from its spec, and the trial results.

**What follows**: five rows are open for the spec owner and the Skill concerned. ffmpeg-skill refuses the keys kit@1 adds and `colours`, and reads keys the spec's table lacks (K1-K3). Whether a kit's `logo_position` may be `"X,Y"` (K5). Whether sound-design-skill's schema takes the video and image extension (L2). Other Skills take the fixtures one at a time.

## D39 — Sidecar JSON files share a four-field envelope

**Decision** (owner, 2026-11-19, details delegated): every sidecar a Skill writes beside an output carries `schema` (`<namespace>/<name>@<major>`), `producer` (`{skill_id, version}`), `generated_at` (UTC) and `inputs` (the sha256 of each input medium) at its top level. The spec is `docs/specs/sidecar-envelope.md`, the schema `registry/schemas/sidecar-envelope.schema.json`.

**Why**: the sidecars that exist say who wrote them, when, and from what in five different spellings, or not at all.

**Evidence**: [ADR-025](../adr/ADR-025-sidecar-envelope.md); the inventory of today's sidecars is in the spec.

**What follows**: no Skill adopts it in this change. The spec lists one additive follow-up per Skill: hyperframes-skill and subtitle-skill first, then the work-directory manifests of audio-production, color-grading, motion-graphics and video-editing (optional), then a check in skillpact's conformance job.

## D40 — One timebase: exact rates, a half rounds up, drop-frame at 29.97 and 59.94 only

**Decision** (owner request, 2026-11-20, details delegated):
- Frame rates and times are exact fractions. 29.97 is read as 30000/1001, never as 2997/100; no `limit_denominator` on a rounded decimal. Two rates are the same only when their fractions are equal.
- One rounding rule for positions: a half up (`floor(x + 1/2)`). Lengths joined at their own rate round down, keeping a frame within 1 ms. Positions are counted in whole frames, never summed from rounded values.
- SMPTE timecode: NDF at every rate; DF only at 30000/1001 and 60000/1001, written with `;`; a DF label that does not exist is refused; no wrap at 24 hours.
- The spec is `docs/specs/timebase.md`, its vectors `docs/specs/timebase-vectors.json`, and the reference implementation `scripts/timebase.py` here (not in system-intelligence, which is general-purpose).

**Why**: Skills read rates and round in three different ways; the agent's concat landed a frame early per join until its ADR-115; ingest-skill reads DF labels that do not exist; hyperframes-skill cannot render at 29.97.

**Evidence**: [ADR-026](../adr/ADR-026-timebase.md) has the per-repository findings and the issue for each.

**What follows**: no Skill code is changed here; each non-conforming repository has an issue. ffmpeg-skill is listed, not filed. video-editing-skill and video-production-agent must change their rate reading together.

## D41 — Error codes stay per Skill; one taxonomy of 15 classes above them, report only

**Decision** (owner request, 2026-11-20, details delegated):
- Every error code and failure kind a Skill contract declares maps to one of 15 classes in `docs/specs/error-taxonomy.json`. Each class has a meaning, a retry policy and a rule for its message to a person.
- Skills keep their codes and exit codes. A caller retries only when the class allows it and the Skill does not say `retryable: false`. A cancelled run is never retried by a caller.
- `scripts/error_taxonomy.py` lists unknown codes, contracts with no code and retry verdicts that differ. `.github/workflows/error-taxonomy.yml` runs it weekly; it fails nothing.

**Why**: 23 contracts use five shapes and 113 codes, with several names for one meaning and different retry verdicts for the same code; the agent keeps a mapping table per adapter, and those tables disagree.

**Evidence**: [ADR-027](../adr/ADR-027-error-taxonomy.md); every code with its class is in `docs/specs/error-taxonomy-map.md`.

**What follows**: report only. The agent has one issue for its tables; no Skill is filed for its codes now.

## D42 — Maintenance tools are a second plugin, `velisa-maintainer`, with /repin, /release and /roadmap

**Decision** (owner request, 2026-11-20, details delegated):
- `plugins/velisa-maintainer/` is a second local plugin in the marketplace, listed after `velisa` by `scripts/marketplace.py`. `velisa` does not depend on it, so installing the OS does not install it.
- Its skill `velisa-maintainer` is a short `SKILL.md` with six references: re-pin (ADR-117 of the agent), releases (ADR-022, ADR-023 and its addendum, `release_gate.py`, the labels, `dependencies` as a patch), contract diff (ADR-020), the timebase and error taxonomy (ADR-026, ADR-027), the schemas and conformance fixtures (ADR-024, ADR-025), and what a session cannot do on GitHub (tag push, branch deletion, GraphQL, draft to ready, repository settings, `@coderabbitai` comments).
- Commands: `/repin` dispatches the agent's `repin.yml` and reports the pull request; `/release <repo>` explains the repository's release and dispatches only where `workflow_dispatch` exists; `/roadmap <repo>` lists open roadmap steps (`scripts/roadmap.py` in the plugin). REST only; none pushes a tag, merges or marks a draft ready.

**Why**: the facts a maintenance session needs were in five long ADRs and in refusals it met one by one; the OS plugin is for people producing video and should not carry them.

**Evidence**: [ADR-028](../adr/ADR-028-maintainer-plugin-and-field-test-kit.md); `scripts/tests/test_marketplace.py` checks the entry, the skill's length and links, the references' topics, the commands and the roadmap parser.

**What follows**: a reference changes with its ADR. The commands were checked as files, not run from an installed plugin.

## D43 — Steps that need real hardware or media get a field test kit; results are committed here

**Decision** (owner request, 2026-11-20, details delegated):
- `docs/field-test/steps.json` lists the roadmap steps whose "Done when" needs a GPU with weights, a commercial NLE, platform test accounts, a set-top disc player or consented recordings: nine steps in diarization, voice-enhance, nle-bridge, publish, sound-design, transcription (three) and oncemore. No roadmap marks a step 確認待ち / "awaiting confirmation"; they were found by reading each open step and each "still to do" note.
- `docs/field-test/README.md` is the procedure; `scripts/field_test.py record` writes a JSON record (`velisa/field-test-result@1`) and a Markdown page into `docs/field-test/results/`. Media are hashed, never copied, and their paths are not written; media of people need `--consent`; credential-like values are refused; `check` validates committed results in CI.
- The step's own repository is updated from a committed result, and ticked only on `pass`.

**Why**: the owner holds the hardware, accounts and venues; without a fixed list of what to measure and a file to bring back, a field run's numbers do not reach the roadmap.

**Evidence**: [ADR-028](../adr/ADR-028-maintainer-plugin-and-field-test-kit.md); `scripts/tests/test_field_test.py`.

**What follows**: none of the nine steps was run here. A new hardware or media step is added to `steps.json` by hand.

## D44 — The repositories stay separate (no monorepo)

**Decision** (owner request, 2026-11-20, details delegated): no migration to a monorepo, in whole or in part. Cross-repository costs are reduced where they are: reusable workflows here, identical copies checked by tests, the agent's automated re-pin from release tags, shared specs, schemas and vectors here that Skills copy.

**Why**: every Skill installs and releases alone, and the agent pins releases, not a sibling's main; the licences differ (MIT, LGPL-3.0, Apache-2.0, GPL-3.0); ffmpeg-skill, the largest dependency, is maintained apart; the costs measured in November (one pull request per repository per rollout, hand re-pins) are bounded and now automated, while a migration would rewrite every release method, the marketplace sources, the history and every link.

**Evidence**: [ADR-029](../adr/ADR-029-polyrepo-stays.md), with the comparison table.

**What follows**: revisit when ADR-029's conditions hold over a month (for example, a quarter of merged pull requests split across three or more repositories, re-pins regularly needing hand fixes, drifting copies in more than five repositories, or per-subdirectory installs shown to work).

## D45 — A kit is projected onto ffmpeg-skill's brand keys before it is passed (ADR-024 K1, K3)

**Decision** (owner, 2026-11-20, details delegated): a consumer that hands a `kit@1` file to ffmpeg-skill writes a projection and passes that: only the keys of the spec's `brand.json` table, `colours` written as `colors`, `logo` and `font_file` as absolute paths, nothing added. `colours` stays an accepted kit spelling. ffmpeg-skill is not changed.

**Why**: ffmpeg-skill refuses every brand-file key it does not read, so the kit@1 keys and `colours` stop it; that refusal also catches misspelt keys, and Velisa does not change ffmpeg-skill.

**Evidence**: [ADR-030](../adr/ADR-030-kit-projection-for-ffmpeg-skill.md), with the consumers checked; `docs/specs/kit.md` "Rule"; ADR-024's K1 and K3 rows marked decided.

**What follows**: remotion-ffmpeg-skill passes its `--brand` file to ffmpeg-skill's delivery template unchanged ([remotion-ffmpeg-skill#32](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/32)). K2 and K5 stay open.

## D46 — What 1.0 means for a Skill; the Skills go to 1.0 one at a time, most stable first

**Decision** (owner request, 2026-11-20, details delegated):
- From a Skill's 1.0.0, a change that `si contract-diff` calls breaking, to a part of the contract the promise covers, ships only in a major release. Additive changes are minor, and a release with no contract change can be a patch.
- The promise covers the `provides[]` entries marked `STABLE` and the tools they map to. `EXPERIMENTAL` entries may still change in a minor release, with a CHANGELOG line.
- A `STABLE` entry is first marked `DEPRECATED` in a minor release. It keeps working for at least one more minor release and 30 days, and is removed only in the next major release.
- 1.0 is cut through each repository's own flow: the `major` label in the release-drafter Skills.
- The agent's re-pin treats a 0.x → 1.0.0 release with a `none` or `additive` diff as a gate widening.
- Order, from the 2026-11-20 measurements: thumbnail-skill, motion-graphics-skill, publish-skill, imagemagick-skill, subtitle-skill, then the rest of ADR-031's table.
- Enforcement is by review for now: the release flow takes the bump from labels, and contract-diff reports without blocking. A blocking check is a follow-up (ADR-031 section 5).

**Why**: 24 Skills on 0.x, and every lifecycle `EXPERIMENTAL`, meant a version number told a dependent nothing about breakage.

**Evidence**: [ADR-031](../adr/ADR-031-skills-at-1-0.md), with the ranking table and its sources.

**What follows**: each Skill's 1.0 is its own pull request and release. A Skill that hits a problem on the way stops the sequence until it is fixed.

**Addendum** (2026-11-20): the blocking check of ADR-031 section 5 is implemented in the 17 Skills that carry `release_gate.py`. Three files are identical in all 17: `release_gate.py`, `major-label-check.yml` and `tests/test_release_gate_major.py`.
- From a latest tag of 1.0.0, a pull request labelled `contract:breaking` without a major label (what `release-drafter.yml` maps to major) fails the new `major-label-check.yml`, unless the pull request itself bumps the major version in `pyproject.toml`. That check waits for the commit's contract-diff run (and fails if it did not succeed), and runs again on `labeled` / `unlabeled`.
- The release job stops on the same rule, per pull request: `release_gate.py` prints the reason, writes `releasable=false` and exits 1. A major version bumped by hand lets it go.
- From 1.0.0, a pull request that contract-diff left with no `contract:*` label (a fork) fails its check until a maintainer adds one.
- 0.x is unchanged.
- An `EXPERIMENTAL`-only break has no named exception yet: the reviewer removes `contract:breaking` by hand.
- The check goes by version, so the three pre-ADR 1.x Skills (audio-production, color-grading, qc) are covered too.

[ADR-031 section 5, addendum](../adr/ADR-031-skills-at-1-0.md#addendum-2026-11-20-the-check-is-implemented) lists the pull requests.
