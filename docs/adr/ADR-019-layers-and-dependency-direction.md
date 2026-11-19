# ADR-019: Layers and the Direction of Dependencies

Status: Accepted (the check is report-only; see "When the check starts to fail")

## Context

The ecosystem already behaves as if it had layers:

- ffmpeg-skill is the engine underneath (D21, D23, D24).
- Measurement, observation and judgement are layers, not collisions (D25).
- Each contract check has one owner (D31).

No file says which layer each component is in, though, and nothing checks the direction of the calls between components. A same-layer call such as one skill running another is invisible until someone reads the code. The owner approved making the layering explicit and machine-checked (decision D33 in [DECISION_LOG](../ecosystem/DECISION_LOG.md)).

### Inventory (2026-11-19)

The inventory below was read from the default branch of every repository. The SHAs in the evidence column are the HEADs that were read. Each edge is one of three kinds:

- **call**: a subprocess or an import.
- **data**: a data contract, meaning one component reads a file, sidecar or spec that another one writes or defines. A handoff the agent describes but does not run is also data.
- **ci**: a clone made only in CI to run a test.

**1. Calls declared in contracts.** These are the `dependencies[]` entries of the contracts that video-production-agent pins, at `video-production-agent@7162c69:src/video_agent/tools/<name>/contract_<version>.json`.

| From | To | Kind | Evidence (line, JSON Pointer) |
|---|---|---|---|
| audio-production-skill | ffmpeg-skill | call | `audio_production/contract_1.3.0.json:188` `/dependencies/0` |
| color-grading-skill | ffmpeg-skill | call | `color_grading/contract_1.1.0.json:123` `/dependencies/0` |
| detection-skill | ffmpeg-skill | call | `detection/contract_0.2.2.json:1` `/dependencies/0` |
| dubbing-skill | ffmpeg-skill | call | `dubbing/contract_0.2.1.json:1` `/dependencies/0` |
| motion-graphics-skill | ffmpeg-skill | call | `motion_graphics/contract_0.4.0.json:171` `/dependencies/0` |
| nle-bridge-skill | ffmpeg-skill | call | `nle_bridge/contract_0.1.0.json:1` `/dependencies/0` |
| publish-skill | ffmpeg-skill | call | `publish/contract_0.2.0.json:1` `/dependencies/0` |
| remotion-ffmpeg-skill | ffmpeg-skill | call | `remotion/contract_0.14.0.json:1` `/dependencies/0` |
| slide-sync-skill | ffmpeg-skill | call | `slide_sync/contract_0.1.0.json:1` `/dependencies/0` |
| sound-design-skill | ffmpeg-skill | call | `sound_design/contract_0.3.0.json:1` `/dependencies/0` |
| subtitle-skill | ffmpeg-skill | call | `subtitle/contract_0.10.0.json:1` `/dependencies/0` |
| thumbnail-skill | ffmpeg-skill | call | `thumbnail/contract_0.1.18.json:364` `/dependencies/0` |
| thumbnail-skill | qc-skill | call | `thumbnail/contract_0.1.18.json:381` `/dependencies/1` |
| video-editing-skill | ffmpeg-skill | call | `video_editing/contract_0.8.0.json:1413` `/dependencies/0` |
| voice-enhance-skill | ffmpeg-skill | call | `voice_enhance/contract_0.1.0.json:1` `/dependencies/0` |
| diarization-skill | transcription-skill | data | `diarization/contract_0.3.0.json:1` `/dependencies/3` (`kind: schema`) |
| diarization-skill | detection-skill | data | `diarization/contract_0.3.0.json:1` `/dependencies/4` (`kind: schema`) |

Four pinned contracts declare no dependency on another component: artifacts, imagemagick, media-analysis and qc (their `dependencies` are absent). ingest and transcription declare `[]`. The other entries name packages, binaries, model weights or engines, so they are not components.

**2. Calls in code that no pinned contract shows.** These components have no JSON contract pinned in the agent, or their call is not in that contract.

| From | To | Kind | Evidence |
|---|---|---|---|
| thumbnail-skill | qc-skill | call (subprocess) | `thumbnail-skill@d063550:src/thumbnail_skill/qcskill.py:67` |
| stepcap | detection-skill | call (subprocess) | `stepcap@3613a7a:src/stepcap/build/screen_blur.py:103` |
| stepcap | ffmpeg-skill | call (subprocess) | `stepcap@3613a7a:src/stepcap/cli.py:571` |
| oncemore | bdmvkit, vtskit, udfkit, dvdcc | call (import of vendored copies) | `oncemore@bcbf2af:oncemore/bluray.py:18`, `oncemore/contract.py:39` |
| hyperframes-skill | ffmpeg-skill | call (optional probe cross-check) | `hyperframes-skill@193f84d:lib/contract.mjs:87` |
| ingest-skill | ffmpeg-skill | call (proxies) | `ingest-skill@38f2c29:src/ingest_skill/contract.py:71` |

**3. The agent's adapters.** Each of these is a call from video-production-agent to the component. Every adapter runs its skill as a separate process through `skill_process`, at `video-production-agent@7162c69:src/video_agent/tools/<name>/adapter.py`. There are 23 adapters: artifacts, audio-production, color-grading, detection, diarization, dubbing, ffmpeg-skill (`ffmpeg_skill/adapter.py:11`, subprocess), hyperframes, imagemagick, ingest, media-analysis, motion-graphics, nle-bridge, publish, qc, remotion-ffmpeg, slide-sync, sound-design, subtitle, thumbnail, transcription, video-editing and voice-enhance.

Two jobs are handoffs only. The agent describes them but has no adapter for them, so they are data, not calls:

- blender-skill `render_3d`, at `src/video_agent/skills/registry.py:242`.
- oncemore `disc_author`, at `src/video_agent/skills/registry.py:248`.

**4. Data contracts in code.** These are not calls.

| From (reads) | To (writes or defines) | What | Evidence |
|---|---|---|---|
| motion-graphics-skill | hyperframes-skill | `title.json` (`velisa/title@1`) | `motion-graphics-skill@f9aecfe:src/motion_graphics/titlejson.py:2` |
| subtitle-skill | detection-skill | `detections@1` (face boxes for placement) | `subtitle-skill@c1d699d:src/subtitle_skill/placement.py:31` |
| thumbnail-skill | detection-skill | `detections@1` (choose-frame) | `thumbnail-skill@d063550:src/thumbnail_skill/contract.py:87` |
| diarization-skill | detection-skill | `detections@1` / `tracks@1` (lower-third names) | `diarization-skill@6fcb3bb:src/diarization_skill/naming.py:35` |
| detection-skill | diarization-skill | `turns@1` (active speaker) | `detection-skill@43cc556:src/detection_skill/speakers.py:16` |
| transcription-skill | diarization-skill | `turns@1`; conformance fixtures vendored by SHA-256 (D27) | `transcription-skill@d8ad0bf:src/transcription_skill/cli.py:605`, `.gitattributes:1` |
| transcription-skill | media-analysis-skill | `speech_regions` (`media-analysis/response@1`) | `transcription-skill@d8ad0bf:src/transcription_skill/chunking.py:56` |
| transcription-skill | slide-sync-skill | `slide-sync/deck@1` (vocabulary) | `transcription-skill@d8ad0bf:src/transcription_skill/vocab.py:23` |
| remotion-ffmpeg-skill | transcription-skill | transcript `0.1` | `remotion-ffmpeg-skill@e34a10d:scripts/_captions.py:144` |
| audio-production-skill | transcription-skill | transcript `0.1` (filler removal) | `audio-production-skill@d179cac:src/audio_production/model.py:54` |
| dubbing-skill | transcription-skill | transcript (term check) | `dubbing-skill@d886971:src/dubbing_skill/pronunciation.py:336` |
| dubbing-skill | subtitle-skill | SRT / WebVTT cues | `dubbing-skill@d886971:src/dubbing_skill/cues.py:5` |
| dubbing-skill | publish-skill | disclosure line handed to publish metadata | `dubbing-skill@d886971:src/dubbing_skill/disclosure.py:68` |
| qc-skill | transcription-skill | transcript format | `qc-skill@9c61ed7:src/qc_skill/measurements/transcript.py:4` |
| media-analysis-skill | transcription-skill | transcript words (highlights) | `media-analysis-skill@bec48a9:src/media_analysis/highlights.py:9` |
| artifacts-skill | sound-design-skill | library licence records | `artifacts-skill@ae039d3:src/artifact_skill/credits_check.py:23` |
| sound-design-skill | audio-production-skill | SFX cue sheet handed to MIX | `sound-design-skill@5b3175e:src/sound_design_skill/cues.py:416` |
| nle-bridge-skill | audio-production-skill | `audio-production/response@1` | `nle-bridge-skill@2f4e7fb:src/nle_bridge/audio_delivery.py:29` |
| nle-bridge-skill | motion-graphics-skill | `nle-bridge/layers@1` | `nle-bridge-skill@2f4e7fb:src/nle_bridge/layers.py:8` |
| nle-bridge-skill | video-production-agent | the agent's project IR (`project.json`) | `nle-bridge-skill@2f4e7fb:src/nle_bridge/plan.py:7` |

**5. Clones made only in CI.** These are not calls.

| From | To | Evidence |
|---|---|---|
| thumbnail-skill | qc-skill | `thumbnail-skill@d063550:.github/workflows/tests.yml:73` |
| sound-design-skill | qc-skill | `sound-design-skill@5b3175e:.github/workflows/tests.yml:62` |
| dubbing-skill | subtitle-skill, publish-skill, transcription-skill | `dubbing-skill@d886971:.github/workflows/tests.yml:70`, `:74`, `:256` |
| diarization-skill | transcription-skill | `diarization-skill@6fcb3bb:.github/workflows/tests.yml:35` |
| transcription-skill | diarization-skill | `transcription-skill@d8ad0bf:.github/workflows/tests.yml:46` |
| stepcap | detection-skill | `stepcap@3613a7a:.github/workflows/tests.yml:119` |
| imagemagick-skill | skillpact (its Action) | `imagemagick-skill@ab89bf9:.github/workflows/skillpact.yml:31` |
| video-production-agent | every skill it adapts | `video-production-agent@7162c69:.github/workflows/tests.yml:72-170` |

Several skills also check out Velisa in CI, for the registry conformance checks: detection, diarization, dubbing, ingest, nle-bridge, publish, sound-design and voice-enhance. Most skills also clone ffmpeg-skill in CI. Velisa is not a component.

Other mentions of other components are boundary notes ("X owns this") or thresholds copied with a reference. For example, hyperframes-skill's alpha threshold is copied from qc-skill (`lib/alpha.mjs:82`), and imagemagick-skill's timeout exit code matches hyperframes-skill's. These are neither calls nor data.

## Decision

1. **Five layers, lowest first.** Each component of `ecosystem.json` gets a `layer`. The order is in `registry/layering.json`. The definitions are in the `$comment` of `ecosystem.json`.

   | Layer | Meaning | Components |
   |---|---|---|
   | `engine` | runs media operations for the components above it | ffmpeg-skill |
   | `skill` | one production job behind its own contract, including the disc kits | 27 components: video-editing, audio-production, subtitle, motion-graphics, color-grading, transcription, diarization, detection, media-analysis, qc, thumbnail, hyperframes, remotion-ffmpeg, blender, voice-enhance, dubbing, sound-design, publish, slide-sync, nle-bridge, imagemagick, ingest, artifacts, bdmvkit, vtskit, udfkit, dvdcc |
   | `app` | a stand-alone application a person runs, which may call skills and the engine (D30) | stepcap, oncemore |
   | `orchestrator` | plans a production and calls the skills and the engine | video-production-agent |
   | `governance` | checks the others' contracts and repositories, and is called by none of them | skillpact, system-intelligence |

   `app` sits below `orchestrator` because the agent may hand work to an app (oncemore's `disc_author`, D29), and an app never calls the agent. Velisa itself is the governance home. It is not a component.
2. **The rule.** A component calls only components in lower layers. A call within one layer, or upward, is allowed only when `registry/layering.json` lists it as an exception with its reason. Data contracts are not calls and are allowed in any direction. A data contract is a shared spec or a sidecar that one component writes and another reads. A clone made only in CI is not a call either.
3. **One exception today:** thumbnail-skill → qc-skill. `render_variants` measures each variant's text legibility with qc-skill's rule (thumbnail-skill ADR-16), instead of copying a judgement that qc-skill owns. The call is optional (`required: false`): without qc-skill, the contrast is reported as not measured.
4. **The check.** System Intelligence's `si layer-check` (its ADR-018, v0.6.0) reads the inputs below and fails on a same-layer or upward call that is not listed. Following D31, the check belongs to system-intelligence and Velisa CI calls it.
   - each component's `layer` from `ecosystem.json`;
   - the order and the exceptions from `registry/layering.json`;
   - the `dependencies[]` of the contracts the agent pins, attributed as `si contract-check` attributes them.

   Entries of kind `schema` are data contracts, and packages, binaries and weights are not components, so neither counts as a call. An exception that excuses nothing is reported as stale. `.github/workflows/layering.yml` runs it on changes to `ecosystem.json`, the layering file or the workflow, weekly, and on demand. System Intelligence is pinned to a full commit SHA, like `contract-shape.yml`.
5. **Report-only for now.** The workflow passes `--report-only`, so a violation shows in the job summary and the artifact but does not fail the run.

### When the check starts to fail

Remove `--report-only` from `layering.yml` in one pull request that cites this ADR, once all of the following hold:

- the owner has reviewed the exception list in `registry/layering.json` and the layer of every component, and accepted them;
- two consecutive weekly runs report no violation, no unclassified call and no stale exception;
- the contract-shape baseline no longer lists `/dependencies` for any component. Today detection, diarization, dubbing, slide-sync, sound-design and voice-enhance name their skill dependencies under `id`. The check already reads `id`, but until the contracts are settled, a renamed field could hide a call.

## Consequences

- The direction of every declared call is visible in a weekly report. Today: 15 calls, 14 down to the engine, 1 excepted, 0 violations.
- The check sees only what contracts declare. Calls that are in code but not in a pinned contract are invisible to it until the component's contract is pinned. Today these are stepcap → detection-skill, stepcap → ffmpeg-skill, oncemore → the kits, hyperframes-skill → ffmpeg-skill (optional) and ingest-skill → ffmpeg-skill. All of them are downward, so the inventory above records them and nothing has to change.
- A new same-layer call needs either a reason in `registry/layering.json` or a change of design, for example the caller passing the other skill's output in as data, as most skills already do.
- `owns` is unchanged. `layer` is independent of `department`, which stays the org-chart grouping.
