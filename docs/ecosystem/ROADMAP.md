# Ecosystem build roadmap

What every repository still needs, how the pieces connect, and the order to build them in. Written from a read-only audit of all 33 components on 2026-10-30 (source, tests, CI, contracts, the agent's adapters), and reviewed again on 2026-11-05 against every repository's `ECOSYSTEM_ROADMAP.md`, with the steps from that day's OSS survey added (see "From the 2026-11 OSS survey"). The same day every skill was also reviewed against field requirements (on-site work, broadcast quality, speed, recovery, natural-language control, the agent contract, live and broadcast delivery formats, motion graphics from a sentence, YouTube editing); the result is the third round below, "Field requirements across every skill", "New skill candidates" and proposals 5-14 to ffmpeg-skill. Each repository carries an `ECOSYSTEM_ROADMAP.md` with PR-sized steps; this page is the map across them. `docs/ROADMAP.md` is the architecture roadmap (phases of the contract layer) and stays as it is.

**ffmpeg-skill is treated as complete.** Since 3.0.0 its 42 tools (`contract_version` 2.0, with a stability promise for the whole of 3.x: [docs/contract.md](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/contract.md#stability-guarantee-3x); FFmpeg 6.1+ and Python 3.10+; 3.0 changed `cut.py`'s defaults and added `probe`'s start `timecode`) are the engine the others delegate to; every satellite now accepts `>=2.0.0 <4.0.0`. No step below changes it: what a step needs from the engine is written under "Proposals to ffmpeg-skill" and decided in that repository. Several gaps are closed by *using* tools it already has, e.g. `render --export-timeline` (.otio / .fcpxml / .edl), `freeze`, `reverse`, `insert`, `audio --duck --voice`, `metadata` chapters.

## Where things stand

| Department | Repositories | Today (2026-11-05) |
|---|---|---|
| Command | video-production-agent | plans, approves, renders, records; brain = rules + Claude (API or the chat app via MCP); 22 adapters, every ecosystem job has a SkillSpec (handoff when absent) |
| Ingest | ingest-skill | active: verified single-read offload to several destinations, ASC MHL + xxHash64, card-aware inventory, `ingest fetch` (URL via yt-dlp); wired (agent #83 offload, ADR-059 fetch) |
| Engine | ffmpeg-skill | 3.x, 42 tools, complete (tool list: `npx ffmpeg-skill contract --json`); agent uses 17 directly (list and evidence: [capability-status.json](capability-status.json)) |
| Visual | video-editing, color-grading, motion-graphics, subtitle, thumbnail | implemented and wired, every parameter reachable (agent #80-#82, #91, #94, #100) |
| Visual | remotion-ffmpeg | wired (agent #108, CONFIRM) |
| Visual | blender, hyperframes | implemented; handoff-only SkillSpecs with pinned contracts (agent #95) |
| Audio | audio-production | implemented and wired (MIX / NR / DYNAMICS / FILLER_REMOVE / duck) |
| Audio | voice-enhance, dubbing, sound-design | 0.1.0, experimental ops, wired (agent #88, #97, #107); `scaffold` in ecosystem.json |
| Recognition | transcription, diarization, detection, slide-sync | implemented and wired; speaker ids end to end (agent #111) |
| Verification | qc, media-analysis, artifacts | implemented and wired (artifacts: agent #110) |
| Delivery | publish | 0.1.0, seven uploaders tested against mocks only; wired as CONFIRM after QC (agent #99); `scaffold` in ecosystem.json |
| Delivery | nle-bridge | 0.1.0 (export / conform / diff / import); agent export / conform wired (agent #101), read-back open; `planned` in ecosystem.json |
| Delivery | 5 disc kits (optional) | implemented, standalone; oncemore named by a handoff (agent #109) |
| Utility | imagemagick, stepcap | imagemagick wired for overlay images (agent #92); stepcap standalone by design |
| Governance | skillpact, system-intelligence | skillpact conformance runs weekly (#127); system-intelligence reads contracts and ownership |

## Wiring

```
                      Claude Code / Claude Desktop (the brain in the chat, ADR-050)
                         │ MCP                      │ MCP (community, unofficial)
                         ▼                          ▼
 ingest-skill ──► video-production-agent ──► DaVinci Resolve MCP / Premiere Pro MCP
 (card offload)   plan → approve → render          ▲
                         │ adapters                │ .otio / FCP7 .xml / .edl + .srt
   ┌─────────────┬───────┼───────────┬─────────────┤
 recognize      visual   audio      verify      nle-bridge-skill (0.1.0)
 transcription  editing  production qc          timeline export / round trip
 diarization    color    voice-enh. media-an.
 detection      motion   dubbing    artifacts
 slide-sync     subtitle sound-des.
                thumbnail
                         │ every media operation
                         ▼
                    ffmpeg-skill (3.x, 42 tools) ──►  publish-skill (upload, CONFIRM after QC)
```

- **Data flows.**
  - transcript → diarization (speaker ids) → subtitle (cues, locale shaping, translation) → dubbing (TTS per cue) → audio-production MIX.
  - detection boxes → ffmpeg-skill redact / crop.
  - slide-sync changes → ffmpeg-skill metadata chapters.
  - sound-design BGM → audio-production MIX.
- **Rule for a missing skill.**
  - The agent names the step as a handoff (ADR-051). For that, every job needs a SkillSpec, even when its skill is not built yet (agent step 1).
  - The routing skill in the marketplace (ADR-013) then prefers OS skills, falls back to other tools, and says so.

## Premiere Pro and DaVinci Resolve

Neither vendor ships a desktop MCP server. Community servers exist. Verified on 2026-10-30; the sources are in the research notes of PR #78.

| | DaVinci Resolve | Premiere Pro |
|---|---|---|
| Recommended server | [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) (MIT, most mature, compound mode) | [leancoderkavy/premiere-pro-mcp](https://github.com/leancoderkavy/premiere-pro-mcp) (MIT; eval tools off by default, token-authenticated UXP bridge, path confinement) |
| Requirement | **Resolve Studio**: external scripting is Studio-only, and free 21.1 moved Python scripting to Studio | Premiere 25.6+ for UXP; the CEP bridge works on older versions but CEP is being retired |
| Timeline import | `ImportTimelineFromFile`: AAF / EDL / FCP7 XML / FCPXML / OTIO | OTIO import (since 2024-10), FCP7 XML, EDL, AAF; **no native FCPXML** |

**How it connects.**
1. The agent exports the edit as a timeline.
   - Primary format: **OTIO**, which both NLEs import natively.
   - Fallback: **FCP7 XML** (carries cuts, tracks, markers and basic levels).
   - Subtitles always go as a sidecar **SRT**; no interchange format carries them.
   - Effects, speed ramps and titles do not survive interchange. They stay in the agent's ffmpeg path or are documented as manual steps.
2. Claude imports the files through the NLE's MCP server (Resolve `ImportTimelineFromFile` / Premiere OTIO import), adds markers and queues the render. The agent's MCP server and the NLE's server sit side by side in the same chat app.
3. Later, the human's edit comes back: the NLE exports OTIO, and the agent reads it as a new plan version.

**Build vs reuse.** Neither NLE is available yet (see Decided), so the interchange files come first and live control waits.
- **Later, reuse:** live NLE control. Don't fork the community servers. Pin a version, keep eval and script tools off, and opt out of telemetry where it exists.
- **Build, first in the agent:** `timeline_export` through ffmpeg-skill `render --export-timeline` (agent step 4, done: ADR-052).
- **Built as `nle-bridge-skill`:** round-trip diff, FCP7 XML for Premiere, relink manifests and conform packages (0.1.0, nle-bridge #1-#5; the pinned community servers are documented in its `docs/live-control.md`, #2). The agent hands it the executed IR (agent #101); reading the editor's timeline back is agent step 12. Still `planned` in `ecosystem.json` (see the owner's decisions).

**Risks.**
- **Resolve:** automation needs Studio.
- **Premiere:** CEP-based servers will break once CEP is retired.
- **Security:** arbitrary-script tools (`execute_extendscript`, `execute_lua`) and shared temp-directory IPC.
- **Licences:** one Resolve server has no licence and another is GPL-3.0. Do not copy code from either.

**Claude Desktop config with all three servers.** Paths are placeholders; check each server's README for its current install command.

```json
{"mcpServers": {
  "video-agent": {"command": "/abs/path/video-agent-mcp", "args": ["--workspace", "/abs/path/video-agent-work"]},
  "davinci-resolve": {"command": "<from samuelgursky/davinci-resolve-mcp setup>"},
  "premiere-pro": {"command": "<from leancoderkavy/premiere-pro-mcp setup>"}
}}
```

## Order of work

### First round (2026-10-30), state on 2026-11-05

1. **Hygiene, every repo, small PRs.** Done: version drift fixed with the agent's gates (agent #65, #84, #93); every contract in the OS shape; ffmpeg-skill 3.0.0 accepted everywhere (`>=2.0.0 <4.0.0`).
2. **Agent: make the whole map visible.** Done in the agent: SkillSpecs for every job (#76), the contract-backed ffmpeg-skill catalog check (#75, 3.x in #102), timeline export (ADR-052), the satellites' parameters (#80-#82, #86, #87, #91, #94).
3. **Recognition.** Done (agent PRs): diarization with speaker ids end to end (#98, #111), detection (#104), slide-sync (#106).
4. **Audio.** Done (agent PRs): filler removal (#87), voice-enhance (#88), the translation decision (subtitle-skill ADR-004), dubbing (#97), sound-design BGM (#107).
5. **Delivery.** Done (agent PRs): publish-skill (CONFIRM after QC, #99; real uploads not made yet), ingest adapter and MHL (#83). Partly done: nle-bridge-skill (export / conform #101; reading the editor's timeline back is agent step 12).
6. **Agent brain.** Done: requirements_extraction (agent #79). Open: semantic deletion, now agent step 13 (it had no step in the agent's roadmap).
7. **Governance.** Done: system-intelligence reads ownership and contracts (system-intelligence #121, #122); skillpact conformance runs weekly, non-blocking (Velisa #127).

### Second round (2026-11-05), in dependency order

Each line is a step in that repository's `ECOSYSTEM_ROADMAP.md`. A line that needs an earlier one says so.

1. **Unblock QC.** agent 11: re-pin qc-skill 1.0.0. qc's release workflow cut 1.0.0 from a dependabot bump alone, and the agent's gate accepts only `0.1.` / `0.2.`, so an install of the current qc-skill turns the QC gate off.
2. **Measurements the later steps read.**
   - detection 8: shots (`detection-skill/shots@1`).
   - media-analysis 4: speech regions (silero-vad).
   - transcription 8: script alignment (stable-ts).
   - qc 8: frozen-time spans.
3. **Picture and caption placement.**
   - detection 9: the subject path (needs detection 6 tracks).
   - subtitle 8: face-avoiding placement (needs detection 3 faces; detection 9 when present).
   - color-grading 5: OCIO / ACES.
4. **Agent loop.**
   - agent 14: the edit view (needs detection 8; uses media-analysis 4 when present).
   - qc 9: the critique report.
   - agent 15: self-review at cut boundaries (needs agent 14 and qc 9).
   - agent 16: pipeline templates.
5. **Round trips and chains.**
   - agent 12: read the editor's timeline back (closes nle-bridge 7).
   - nle-bridge 13: auto-editor XML.
   - dubbing 11: translate → dub → subtitles with speech-rate fit (needs subtitle 5, transcription 8 for the source timing).
   - audio-production 7: reference mastering.
6. **New areas** (owner decision first, below): live streaming, restoration.

### Third round (2026-11-05, field review), in priority order

From a review of every skill against what conference, medical-congress, corporate-event and hybrid-stream work needs (see "Field requirements across every skill" below). Each line is a step added that day to that repository's `ECOSYSTEM_ROADMAP.md`, named by its title; numbers are in each file.

1. **Delivery for live, broadcast and NLE** (highest: it decides whether a file can be used on site at all).
   - The engine side is proposals 5-9 to ffmpeg-skill (alpha masters, key / fill, intermediates, multitrack audio, loudness versions).
   - qc-skill: key and fill pair check, alpha edge check, loop seam check, stinger cut-point check, broadcast and delivery profiles.
   - video-production-agent: delivery presets for live, broadcast and NLE ("キーフィルで2本", "レイヤー別で").
   - audio-production-skill: stems and multitrack delivery, loudness versions in one run.
   - Generators: layer export (motion-graphics-skill), alpha deliveries (hyperframes-skill), alpha mode and render passes (blender-skill), style presets and layer output (remotion-ffmpeg-skill), layered output (thumbnail-skill), alpha hygiene for stills (imagemagick-skill).
2. **Motion graphics from a sentence** (文字PV・幾何学模様; see the section below).
   - hyperframes-skill: text animation, Japanese typesetting and text fit, shape and pattern layers, generative layer (Three.js / GLSL), audio and beat lock, IN / LOOP / OUT segments, style presets and recipe gallery.
   - remotion-ffmpeg-skill: source-less runs, KineticType, visualizers, Three.js scenes.
   - blender-skill: procedural motion scenes, 3D text and logo reveal, audio-driven animation.
   - video-production-agent: productions with no source media, motion brief slots, relative revisions and references.
3. **Long recordings and recordings in progress** (終日収録・収録中ファイル).
   - ingest-skill: growing files, sync facts and multicam sets, progress, proxies at ingest.
   - transcription-skill: streaming and growing-file mode, chunked long recordings.
   - video-editing-skill: segment cache and partial re-render, keyframe-aware long-form cuts.
   - qc-skill: incremental and parallel QC. voice-enhance-skill and diarization-skill: long files.
   - video-production-agent: long-form and recording-in-progress jobs, deadline mode (撮って出し), progress and error classes over MCP.
4. **Multicam and multi-mic.**
   - detection-skill: active speaker for multicam switching. color-grading-skill: match cameras to a reference.
   - audio-production-skill: automixer for panel microphones, per-input pan and language tracks.
   - transcription-skill: one transcript per microphone. nle-bridge-skill: multicam sources for the editor.
5. **Medical and conference safety.**
   - detection-skill: personal and patient data in slides and frames.
   - artifacts-skill: event documents against their source, numbers and terms in generated text, credits and licence lines.
   - transcription-skill: domain vocabulary from the programme. dubbing-skill: pronunciation dictionary.
6. **YouTube-style editing and derived clips** (see "Editing a YouTube video" below).
   - video-production-agent: long video → Shorts set, chapters from the transcript, YouTube editing pass, paper edit from a script.
   - video-editing-skill: punch-in on the speaker, one edit in several aspects, AI-generated clips in an edit.
   - subtitle-skill: Shorts captions. sound-design-skill: sound-effect cue sheet, stock music with licence records. thumbnail-skill: batch, frame choice, A/B variants. publish-skill: chapters, scheduled time, captions per language, clips as a series.
7. **Formats and archive delivery.**
   - subtitle-skill: TTML / IMSC 1.1 and EBU-TT-D, Japanese broadcast-style captions, live and rolling captions.
   - Disc kits: proceedings discs (bdmvkit), bitrate planner (vtskit), checksum manifest (udfkit), 608 limits (dvdcc), build from the agent and batch discs (oncemore).
8. **Governance.** skillpact: progress events and error classes in the contract, idempotency conformance. system-intelligence: field-readiness audit, roadmap drift check.
9. **New skills** (owner decision first): broadcast-graphics-skill, design-system-skill, asset-library-skill, generative-media-skill (see "New skill candidates").

## From the 2026-11 OSS survey

What was taken from the survey, and where it landed. A project's licence decides only whether its *code* may be used. Ideas and methods are taken from any licence and implemented here (see "Licence policy").

| # | Idea | Source (licence) | Lands in |
|---|---|---|---|
| 1 | An edit view the agent reads: a ~12 KB transcript digest plus timeline images from ffmpeg-skill `look` / `scenes`; after the render, a self-review at every cut boundary, at most 3 rounds | browser-use/video-use (MIT) | video-production-agent 14, 15 |
| 2 | Shot detection, PySceneDetect by default and TransNetV2 optional, as `shots@1` | PySceneDetect (BSD-3-Clause), TransNetV2 (MIT) | detection-skill 8 |
| 3 | Forced alignment of a known script | stable-ts (MIT) | transcription-skill 8 |
| 4 | Subject path for reframing: faces and tracks smoothed into a list of crop windows | OpenChatCut (ideas only) | detection-skill 9 |
| 5 | Speech regions measured with a VAD | silero-vad (MIT) | media-analysis-skill 4 |
| 6 | Captions placed away from faces | OpenChatCut (ideas only) | subtitle-skill 8 |
| 7 | Frozen-time spans and a render critique loop | echris6/motion-video-kit (MIT) | qc-skill 8, 9 |
| 8 | OCIO / ACES transforms | OpenColorIO (BSD-3-Clause) | color-grading-skill 5 |
| 9 | Read the XML that auto-editor writes | auto-editor (Unlicense) | nle-bridge-skill 13 |
| 10 | Live streaming: drive OBS through obs-websocket | OBS (ideas only) | new area, below |
| 11 | Plans saved and re-run as purpose-built pipeline templates | OpenMontage, ComfyUI (ideas only) | video-production-agent 16 |
| 12 | Translate → dub → subtitles in one run, with the speech rate fitted | pyvideotrans (ideas only) | dubbing-skill 11 |
| 13 | Mastering matched to a reference track | matchering (ideas only) | audio-production-skill 7 |
| 14 | Restoration: super-resolution and frame interpolation behind swappable engines, Real-ESRGAN optional | video2x (ideas only) | new area, below |
| 15 | Keyframe-aware lossless cuts that offer cut-point candidates | LosslessCut (ideas only) | proposal to ffmpeg-skill, below |

## Licence policy for outside projects

- **Ideas and methods from any licence, code from none that forbids it.** AGPL and GPL projects (OpenMontage, ComfyUI, pyvideotrans, matchering, video2x, LosslessCut, OBS) are read for how they work; nothing is copied, vendored, linked or imported from them. The step is implemented here from its own design. Every step that takes an idea names it: `参考：<project>（考え方のみ。コードは使わない）`.
- **A dependency** is used only under a licence that allows it (MIT, BSD, Apache-2.0, Unlicense). Its licence is checked in an ADR in the repository that adds it.
- **Terms of use are separate from code licences.** These are written next to the step that meets them:
  - **Model weights** carry their own licence. Example: LTX-2's code is Apache-2.0, but its weights are under the LTX-2 Community License, which limits commercial use by revenue. Real-ESRGAN, TransNetV2 and silero-vad weights are checked in the same ADR as their code.
  - **Remotion** is free for individuals and for companies with up to 3 employees; larger companies need a Remotion company licence (remotion-ffmpeg-skill README). The skill's MIT licence does not change that.
  - **OBS** is GPL-2.0. The live area talks to it only over the obs-websocket protocol, from its own client; no OBS code or plugin code is used.

## Field requirements across every skill (2026-11-05 review)

What every skill was checked against, and where each gap landed. "Step" means a step added to that repository's `ECOSYSTEM_ROADMAP.md`.

| Viewpoint | What is there | Gap and where it landed |
|---|---|---|
| On-site work: 撮って出し, short deadlines, 2-8 h recordings, multicam, multi-mic, sync (timecode, waveform), recordings in progress, live → archive | ingest verified offload; ffmpeg-skill `multicam` / `sync` / `proxy`; agent `render --resume` | growing files (ingest, transcription, slide-sync, media-analysis); chunked long jobs and deadline mode (agent); multicam sets at ingest; active speaker (detection); camera matching (color); automixer (audio) |
| Quality: EBU R128, ARIB TR-B32, BT.709 / BT.2020, SRT / VTT / TTML / ARIB, QC | qc loudness, flash, cut accuracy, legibility; ffmpeg-skill `broadcast` platform at -23 LUFS | ARIB TR-B32 (-24 LKFS) and named profiles (qc); legal range (color); TTML / IMSC and EBU-TT-D (subtitle); ARIB STD-B24 / B36 binary captions stay a proposal (below) |
| Speed: proxies, GPU (NVENC / VideoToolbox / QSV), parallel, cache, incremental | ffmpeg-skill hardware encoders and `proxy`; media-analysis cache | segment cache and partial re-render (video-editing); incremental QC (qc); chunked parallel transcription; proxies at ingest |
| Recovery: resume, partial re-render, idempotency, logs | agent `--resume`; ingest resumable; hyperframes `bit_exact` | resumable blocks (voice-enhance, transcription, diarization); idempotency conformance (skillpact); series uploads never sent twice (publish) |
| Natural-language control: vague requests, confirmation gates, preview and revise, "さっきの" | requirements_extraction (unambiguous phrases), CONFIRM floors, `revise --feedback` | motion brief slots, relative revisions and references, delivery presets from a sentence (agent) |
| Agent contract: inputs and outputs, error classes, progress | per-skill error codes with `retryable` | one error-class vocabulary and progress events (skillpact; agent over MCP) |
| Future: generated video, many languages, AI voice, vertical shorts, clips from streams | dubbing, subtitle translate, remotion `--aspect` | Shorts set and highlight signals (agent, media-analysis); AI clips in an edit (video-editing); AI voice disclosure (dubbing); generative-media-skill (candidate) |

### Delivery formats for live, broadcast and NLE (all skills)

Owner split: the files are written by ffmpeg-skill (proposals 5-9 below, since it is not changed from here); generators keep layers separate and say how their alpha is stored; qc-skill checks the result; the agent turns the request into a preset.

| Need | Engine (ffmpeg-skill) | Generators | Check (qc-skill) | Request (agent) |
|---|---|---|---|---|
| Layers as separate alpha files for After Effects / NLE | alpha masters (proposal 5) | layer export (motion-graphics), alpha deliveries (hyperframes), passes (blender), `--layers` (remotion), layered output (thumbnail); placed on upper tracks by nle-bridge | alpha edge check | `nle-layers` preset, "レイヤー別で" |
| Key / fill pair for a switcher DSK (ATEM, Roland), premultiplied or straight | key / fill pair (proposal 6) | the alpha mode (straight or premultiplied) recorded by every generator; still key / fill (imagemagick) | key and fill pair check | `live-dsk` preset, "キーフィルで2本" |
| ProRes 4444 / 4444 XQ, HAP Alpha, QuickTime Animation, PNG / EXR sequence; DNxHR / DNxHD, ProRes 422 HQ | proposals 5 and 7 (ProRes 422 HQ exists as `export --preset prores`) | — | profile per codec | `alpha-master`, `live-playback`, `intermediate` |
| Stems, multitrack WAV, loudness versions (-14 / -23 / -24) | multitrack audio, loudness versions (proposals 8, 9) | stems and loudness set (audio-production) | broadcast and delivery profiles | `loudness-set` |
| Batch in several sizes, fps and aspects; loops; safe-area guides; file naming; checksums | export per preset exists; seamless loop (proposal 10); a safe-area guide overlay (proposal 11) | one edit in several aspects (video-editing); IN / LOOP / OUT (hyperframes) | loop seam check | `aspect-set`, a naming rule and a checksum manifest per delivery |
| Live: looping standby screens, playout formats and playlists (vMix, OBS, CasparCG) | HAP Alpha (proposal 5) | visualizers and loops (remotion), loopable beds (sound-design) | loop seam, stinger cut point | playout package: broadcast-graphics-skill (candidate) |

## Motion graphics from a sentence (文字PV・幾何学模様)

The request: "make a cool text-only PV, or a piece finished with geometric patterns, from a sentence" (例：「ネオンで、120BPM、15秒、縦型」).

**What works today** (checked against each skill's README, SKILL.md and contract on 2026-11-05):

- **hyperframes-skill** is the closest fit: a scene from nothing (size, duration, fps, background), text / image / video layers with `fade`, `slide` and `zoom` transitions (CSS, seeked frame by frame, `bit_exact` on one machine), local fonts (Japanese included), templates (`title-card`, `lower-third`, `session-slate`, `break`), a CSV `batch` (one file per speaker), ProRes 4444 with alpha. Missing: per-character / per-word animation, shapes and patterns, audio, beat lock, styles.
- **remotion-ffmpeg-skill**: beat-measured compositions (PeakPulse, BeatMontage), Karaoke and Captioned from word timings, `--aspect 9:16`, `--brand`, transparent `--overlay --keep-graphics`, and any custom React composition Claude writes into the project. Missing: a run with no source footage (`analyze` needs a file), kinetic-type and visualizer compositions, Three.js.
- **motion-graphics-skill**: 13 typed elements burned onto existing video, `fade` only (slide / move / scale are listed as unsupported), `shape` a solid rectangle. Good for burned titles; not for kinetic type.
- **blender-skill**: declarative `scene.json` (assets, lights, camera, background), turntables, transparent sequences. No text objects, no Geometry Nodes presets, no audio drive.
- **video-production-agent**: `plan` needs input media; `html_scene_render` is a handoff, so a text-only PV is not planned yet.

Today's working path, in the chat: Claude writes a hyperframes scene request (or fills a template) and renders it, e.g. 「黒背景に白の明朝体で『未来をつくる』を中央、0.5秒ずつ下からスライドイン、縦型 1080x1920、6秒、30fps」 → `scene` → `preview` → `render --codec prores` for alpha. For music sync, ffmpeg-skill `background` + `audio --replace` with the track gives a source for remotion `analyze --beats`, then PeakPulse or a custom composition.

**Steps added** (names as in each repository's roadmap): hyperframes-skill — text animation, Japanese typesetting and text fit, shape and pattern layers, generative layer (Three.js / GLSL), audio and beat lock, IN / LOOP / OUT segments, alpha deliveries, style presets and recipe gallery; remotion-ffmpeg-skill — source-less runs, KineticType, visualizers, Three.js scenes, emphasis captions, style presets and layer output; blender-skill — procedural motion scenes, 3D text and logo reveal, alpha and passes, audio-driven animation; motion-graphics-skill — style presets, rendered-layer element, layer export, Japanese name fit, end-screen areas; video-production-agent — productions with no source media, motion brief slots, relative revisions; sound-design-skill — tempo-targeted generation and a tempo map.

**Three.js: where it goes.** Both engines can render Three.js deterministically, so no new skill.
- HyperFrames seeks every frame through frame adapters (GSAP, Lottie, CSS or a custom one; `@hyperframes/core`, Apache-2.0), and hyperframes-skill already forces SwiftShader (no GPU capture), which is what makes WebGL output repeatable. A custom adapter that sets the program's time from the frame number is the whole integration: hyperframes-skill, generative layer.
- Remotion has `@remotion/three` (MIT; Remotion's own licence applies to the render), driven by `useCurrentFrame()`; it suits Three.js that reacts to measured beats: remotion-ffmpeg-skill, Three.js scenes.
- A separate headless-Chromium frame grabber would repeat what both engines already do (seek, capture, encode, verify). Not built.
- GSAP is not used: its licence is GSAP's own standard licence, not an open-source one. CSS / Web Animations and our own adapters only.

**Audio visualizers: no new skill.** ffmpeg-skill `waveform` already draws waveform and spectrum videos, `loop` loops a clip, and remotion-ffmpeg-skill owns measurement-driven motion (beats, peaks, Karaoke lyrics). Visualizers and standby loops are remotion-ffmpeg-skill's (visualizer compositions), 3D ones blender-skill's (audio-driven animation), looping beds sound-design-skill's.

## Editing a YouTube video: flow × skill

Velisa is an editing, finishing and delivery tool. Planning, idea generation, writing and polishing scripts, shot lists and shooting support, and running a channel after publishing (comments, analytics, improvement ideas) are out of scope: the host AI (Claude) does them in the conversation. A script is used here only as an input to editing.

| Stage | Need | Skill (existing / step added) |
|---|---|---|
| Script as input | script alignment, paper edit in script order, misread lines | transcription-skill script alignment (round 2); agent: paper edit from a script |
| Edit | jump cuts, silence / filler removal, pacing | audio-production SILENCE_REMOVE / FILLER_REMOVE, remotion Jumpcut, agent semantic deletion (round 2) |
| | B-roll inserted automatically | ffmpeg-skill `broll`; picking the clip: asset-library-skill (candidate) |
| | zoom / punch-in on the speaker | video-editing-skill: punch-in on the speaker |
| | sound effects placed (pop, whoosh) | sound-design-skill: sound-effect cue sheet → audio-production MIX |
| | emphasis captions, speech bubbles | remotion-ffmpeg-skill: emphasis captions |
| | chapters | slide-sync chapters; agent: chapters from the transcript |
| | end screen and cards kept clear | motion-graphics-skill: end-screen and card areas |
| Assets | stock footage and images with licence lines | asset-library-skill (candidate) |
| | royalty-free BGM, loops | sound-design-skill library mode; stock music with licence records; loopable beds |
| | AI images and video | thumbnail-skill FLUX backgrounds; video-editing-skill: AI-generated clips in an edit; generative-media-skill (candidate) |
| | meme inserts | motion-graphics `meme`; clips: asset-library-skill (candidate) |
| Sound | voice cleanup | audio-production VOICE_CLEANUP, voice-enhance ISOLATE / DEREVERB |
| | BGM ducking | audio-production MIX duck |
| | -14 LUFS | ffmpeg-skill `export --normalize`, audio-production NORMALIZE; loudness versions |
| | AI narration, one voice | dubbing-skill NARRATE; one voice per channel; pronunciation dictionary; AI voice disclosure |
| Finish | thumbnail: A/B, faces, text size | thumbnail-skill: batch, frame choice, A/B variants and the small-size check; detection-skill: face attributes |
| | title, description, tags | written by the host AI; checked against platform limits by publish-skill `plan` |
| | chapter timestamps | publish-skill: chapters, scheduled time and captions per language |
| | captions, many languages | subtitle-skill generate / translate / mux; Shorts captions |
| Derived | Shorts / Reels / TikTok: vertical reframe, highlights, burned captions | agent: long video → Shorts set; detection subject path (round 2); media-analysis: highlight signals |
| Publish | upload, metadata, chapters | publish-skill (existing uploaders; first real uploads; clips as a series) |
| Rights and safety | BGM and asset licences | sound-design licence records; artifacts-skill: credits and licence lines; asset-library-skill (candidate) |
| | faces and personal data blurred | detection-skill faces / tracks → ffmpeg-skill `redact`; personal and patient data |
| | Content ID risk | sound-design-skill: stock music with licence records (a source's Content ID flag); a real check is not possible offline |

## New skill candidates

None of these is created here. Each needs the owner's decision: repository name, `owns` entries in `ecosystem.json` (status `planned`), department. Priority is for the field work this ecosystem serves.

### broadcast-graphics-skill (送出用グラフィックス) — priority: high

- **Role.** Graphics made to be played out live, not burned in: lower thirds (name and title), session titles, breaking-news straps, score and number count-ups, social-comment cards, stingers, standby loops, and the playout package for OBS, vMix and CasparCG.
- **Why a new skill.** It is one job family with its own rules: every graphic in IN / LOOP / OUT segments so an operator can take IN and OUT separately; stingers with a cut point (the frame where the picture is fully covered) delivered as metadata; key / fill or alpha in the format the player takes; a player configuration written beside the files (OBS / vMix stinger transition point in ms). motion-graphics-skill burns titles into programme video and hyperframes-skill renders whatever scene it is given and decides nothing; neither owns a playout package.
- **Contract (draft).** `bgfx template --list`; `bgfx make <template> --values v.json|--csv rows.csv --kit kit.json --duration 1.2 --cut-point 0.5 --format prores4444|webm-alpha|png|key-fill [--alpha straight|premultiplied]` → one directory per graphic: `in.mov`, `loop.mov`, `out.mov` (or the single stinger file with its audio), `graphic.json` (`broadcast-graphics/graphic@1`: segments with frame counts, cut point in frames and ms, alpha mode, safe area, the text as drawn and the font size used), and `obs-stinger.json` / `vmix-stinger.txt` with the transition point; `bgfx playlist` → a CasparCG / vMix playlist of the files. Errors in the OS classes; `--dry-run` writes the plan only.
- **Templates.** Lower third, session title, speaker introduction, break screen, end roll, breaking strap, count-up, comment card; stingers: geometric, particles, brush, glitch, logo reveal. Japanese typesetting (vertical, ruby, kinsoku, variable fonts, auto shrink and line break) comes from hyperframes-skill's typesetting step.
- **Boundaries.** Rendering through hyperframes-skill (HTML scenes, segments, alpha), remotion-ffmpeg-skill or blender-skill; files written through ffmpeg-skill; brand values from design-system-skill when present; checks by qc-skill (key / fill, alpha edges, loop seam, stinger cut point); natural-language requests and the delivery preset by the agent. Live control of the switcher or OBS belongs to the live-streaming area (above).
- **Licence.** Own code (MIT like the rest). CasparCG is GPL-3.0: only its documented playlist and AMCP formats are written, no code used. OBS (GPL-2.0) and vMix (commercial): only their documented settings. Stinger designs: 参考：Remotion / HyperFrames 公式テンプレート、video-shotcraft（Apache-2.0）、motion-video-kit（MIT）（考え方のみ。コードは使わない）.
- **Example requests.** 「登壇者テロップを10人分、CSV から、企業カラーで、IN/OUT 別で」「ロゴ入りのスティンガー、1.2秒、カット点 0.5秒、WebM と OBS 設定も」「休憩画面のループ、5分、BGM 付き」.

### design-system-skill (ブランドキット・デザイン規則) — priority: high

- **Role.** One brand kit for every renderer: colours, fonts (with their licences), logos (variants and clear space), spacing and a layout grid, type rules (sizes, weights, line lengths per aspect), and palettes generated from a logo or one colour with contrast checked.
- **Why a new skill.** At least six renderers read colours and fonts (motion-graphics, hyperframes, remotion, thumbnail, subtitle, blender), each in its own way; ffmpeg-skill's `brand.json` is one of these formats and ffmpeg-skill is not changed from here. Checking a kit (WCAG contrast of every text / background pair, font licence allows video embedding, logo sizes) has no owner today.
- **Contract (draft).** `design kit validate kit.json` → `design-system/kit@1` with findings; `design kit derive --for hyperframes|motion-graphics|remotion|thumbnail|subtitle|ffmpeg-brand` → each renderer's own options file; `design palette --from logo.png|#hex [--count N]` → a palette with contrast pairs; `design event-pack sessions.csv --kit kit.json` → the render requests for one event (opening, session title, speaker introduction, break, end roll) for hyperframes-skill `batch` or broadcast-graphics-skill. It never renders.
- **Boundaries.** Rendering stays with each renderer; thumbnails with thumbnail-skill; legibility judged by qc-skill; logo variants made through imagemagick-skill.
- **Licence.** Own code. Palette generation may use Material Color Utilities (Apache-2.0) as a dependency; font licences read from the font files' name tables (OFL, Apache, commercial) and recorded.

### asset-library-skill (ストック素材の取得とライセンス台帳) — priority: medium

- **Role.** Find and fetch stock footage, photos, illustrations and meme clips from sources with a documented licence and an API (for example Pexels, Pixabay, Openverse, Wikimedia Commons), record each asset's licence, author, source URL and attribution line, and keep a project ledger the credits are built from. B-roll picking (a query from the transcript's nouns) is the agent's; this skill searches, fetches and records.
- **Boundaries.** URL download stays with ingest-skill (`ingest fetch`); music and sound effects stay with sound-design-skill (library mode); attribution text is checked by artifacts-skill.
- **Contract (draft).** `assets search "<query>" --kind video|image --orientation portrait --licence cc0|cc-by|platform` → candidates with licence facts; `assets fetch <id> --dest DIR` → the file plus `asset-library/asset@1` (licence, author, attribution, sha256); `assets ledger` → the project's credits. API keys from the environment or keychain, never printed.
- **Licence.** Own code; each source's terms are recorded per asset, and a source without stated terms is refused.

### generative-media-skill (AI 画像・動画の生成) — priority: low, start with an ADR

- **Role.** Generated stills and video clips as edit material (inserts, backgrounds, establishing shots), behind swappable local engines, every output marked AI_GENERATED with the engine, the weights and their licence. thumbnail-skill keeps its own background generator.
- **Why later.** Weight licences decide what is possible (for example LTX-2: Apache-2.0 code, weights under a community licence that limits commercial use by revenue). The ADR checks code and weights first; video-editing-skill's "AI-generated clips in an edit" step already makes inserted clips safe.

### Judged not to need a new skill

- **Three.js / GLSL renderer:** hyperframes-skill (generative layer) and remotion-ffmpeg-skill (Three.js scenes), see above.
- **Audio visualizer:** remotion-ffmpeg-skill, blender-skill and ffmpeg-skill `waveform`, see above.
- **TTS narration:** dubbing-skill NARRATE owns AIナレーション.
- **Kinetic typography / geometric PV:** hyperframes-skill's owned job (HTMLシーンの動画化), with the agent planning it.

## New areas (proposed)

Both need an owner decision first: a repository name, its `owns` entries in `ecosystem.json` (status `planned`), and its department. Until then they are written here, not in `ecosystem.json`.

### Live streaming (配信・ライブ)

Conference, corporate event and hybrid (on site + online) streams. 参考：OBS（考え方のみ。コードは使わない）.

1. **Engine ADR.** OBS Studio 28+ with its built-in obs-websocket v5, as an external app the user runs. Our own client of the documented protocol: no GPL client library, no OBS plugin. Password from the environment or the OS keychain, never printed; loopback by default.
2. **Read-only doctor and inventory.** Connection, OBS version, scenes, sources, outputs, encoder, dropped frames.
3. **Run of show.** A cue list (scene, source, lower third, start / stop streaming and recording) checked offline against the inventory. Every live switch needs CONFIRM; a dry run prints the requests.
4. **Health monitor.** Bitrate, dropped / skipped frames, audio levels per source (LUFS short-term, peak), with thresholds and an event log the agent can read.
5. **Recording handoff.** OBS's local ISO / program recording becomes an ingest-skill offload, then the usual post (live → VOD: trim the start and end, chapters from slide-sync, captions).
6. **Delivery limits.** Stream keys and ingest URLs stay with the user; publish-skill keeps upload-side limits only.

Needed on site and not covered yet. These are steps for the live repository, or for the owner named:
- **Interpretation audio.** Several language tracks in one recording and one stream (audio-production MIX per language, ffmpeg-skill mux).
- **Mix-minus for remote speakers.** Each remote guest hears the room without their own voice.
- **Live captions.** Real-time speech-to-text into the stream (a transcription-skill streaming mode; today it is batch only).
- **Confidence and timer output** for the speaker. This is OBS's job: document how to set it up, no code here.
- **Sign-language picture in picture** with a fixed safe area that captions avoid (subtitle 8).
- **Delivery loudness for streams.** Platform targets are in ffmpeg-skill's platform table already; add the broadcast target (EBU R128, -23 LUFS) where a venue asks for it.

### Restoration (復元)

Super-resolution and frame interpolation for archive footage and low-resolution sources. 参考：video2x（考え方のみ。コードは使わない）.

1. **Engine ADR.** One engine interface (frames in, frames out, scale or rate factor), engines swappable. Baseline with no weights: ffmpeg-skill's own scaling and frame-rate conversion. Optional: Real-ESRGAN (BSD-3-Clause code; check the weights' licence in the same ADR). Frame interpolation candidates to check the same way.
2. **UPSCALE op.** Frames come from ffmpeg-skill, and the result is reassembled through ffmpeg-skill with the source's audio. Provenance names the engine, the weights and their licence.
3. **INTERPOLATE op.** Same shape; the output frame rate is checked by probe.
4. **Acceptance.** Measured against a reference with qc-skill's VMAF / SSIM / PSNR (qc 3), never by eye only. Generated pixels are recorded as AI_GENERATED in the agent.

## Proposals to ffmpeg-skill

ffmpeg-skill is not changed from here. Each item is a hand-over for its maintainers to accept, reshape or decline. A step that needs one says so, and works without it until then.

1. **Cut-point candidates for lossless cuts.** `cut.py` already reports `lossless_alternative` after a forced re-encode. Proposal: a measuring mode, run before the cut, that lists the keyframes around each requested in and out point. Each candidate gets its offset in frames and whether a stream copy would be exact there, so the agent or the editor can choose before anything is written. 参考：LosslessCut（考え方のみ。コードは使わない）.
2. **A time-varying crop.** detection 9 produces a list of crop windows over time, and nothing in the engine applies a moving crop yet (`crop.py` takes one rectangle, `fit.py --fit crop` one position). Proposal: `crop.py --path windows.json` with a stated interpolation. Until then, reframing uses one window per shot through video-editing CROP.
3. **Audio-only tempo and pad.** Asked for by dubbing-skill (ADR-007, ADR-013). dubbing 11's speech-rate fit renders only at tempo 1.0 until it exists.
4. **`audio --sample-rate` and `audio --channel N`.** Asked for by voice-enhance-skill (ADR-003, ADR-005).
5. **Alpha masters.** `export` presets that keep alpha and verify it on an output frame: ProRes 4444 and 4444 XQ (`prores_ks` profiles 4 / 5, `yuva444p10le`), QuickTime Animation (`qtrle`), PNG and EXR sequences, HAP Alpha (FFmpeg's `hap` encoder, needs a build with snappy; reported by `doctor` when missing), WebM VP9 alpha. The alpha mode (straight or premultiplied) is a flag and is written to the result. Asked for by the generators' layer and alpha steps (motion-graphics, hyperframes, blender, remotion, thumbnail) and the agent's delivery presets (2026-11-05 field review).
6. **Key / fill pair.** One call that writes the fill and the key (the alpha as a full-range luma matte, `alphaextract`) from one source with alpha: same frame count, fps, size and start timecode, straight or premultiplied fill as asked, both hashed. For switcher DSKs (ATEM, Roland). qc-skill's key and fill pair check reads the result.
7. **Intermediate presets.** DNxHR LB / SQ / HQ / HQX / 444 and DNxHD at the broadcast sizes and rates, beside the existing ProRes 422 HQ (`export --preset prores`).
8. **Multitrack audio.** Several audio inputs into one file as separate tracks with names and language tags: multitrack WAV (or BWF with the start timecode) and MOV / MXF with one track per stem. Asked for by audio-production-skill's stems step and nle-bridge-skill's package.
9. **Loudness versions in one pass.** One master, several targets: -14 LUFS (streaming), -23 LUFS / -1 dBTP (EBU R128, the `broadcast` platform has it), -24 LKFS / -1 dBTP (ARIB TR-B32, a `broadcast-jp` target), each measured after.
10. **Seamless loop.** `loop --crossfade S` (picture and sound across the seam) and a measurement of the seam; `loop.py` says today that it does not smooth the loop point.
11. **Safe-area guide.** A guide overlay (title safe / action safe for 16:9 and 4:3 centre cut, and the platform safe zones `_platforms.py` already has) as a preview file, never burned into a delivery.
12. **Growing files and LTC.** `probe` and `cut` on a file still being written (fragmented MP4 / MOV, MXF) reporting the duration that is readable so far; and LTC decoded from an audio channel as a sync source for `sync` / `multicam`. Asked for by ingest-skill's growing-files and sync-facts steps.
13. **Typed keyframes on overlay.** Position, scale and opacity keyframes with stated easing on `overlay`, so motion-graphics-skill can offer slide / move / scale (today in its `unsupported_animations`). Until then animated graphics come pre-rendered from hyperframes-skill and are placed by motion-graphics-skill's rendered-layer element.
14. **ARIB captions.** ARIB STD-B24 caption streams for Japanese broadcast deliveries; a large format decision, so it is a proposal only. subtitle-skill writes TTML with ruby and vertical text meanwhile.

## Decided by the owner (2026-10-30)

| Question | Decision |
|---|---|
| Who translates subtitles (字幕翻訳)? | **subtitle-skill**, as `ecosystem.json` already says. Its README's "translation is out of scope" is corrected. The MT engine gets an ADR in subtitle-skill. Dubbing builds on it. |
| Who owns the platform specs (配信プラットフォーム仕様)? | **ffmpeg-skill** keeps the table (`_platforms.py`; nothing in ffmpeg-skill changes). publish-skill reads it and owns only upload-side limits (アップロード制限: file size, duration, rate limits). |
| Who owns URL download (URL素材取得)? | **ingest-skill**. The agent's own yt-dlp call moves there; until then the agent keeps it. |
| Premiere / Resolve | Neither is available here. Build the **interchange files** first (OTIO, FCP7 XML, SRT), which open in either NLE later. Live control through the community MCP servers waits until the software is at hand. |

## Decisions only the owner can make

| Question | Options |
|---|---|
| Compliance checking | Recommendation: qc-skill judges against the spec, and ffmpeg-skill `check` is the engine's preflight. Record that split. |
| Overlay / PiP / titles | The jobs are split by name. video-editing owns still overlay, motion-graphics owns titles, and ffmpeg-skill owns B-roll and screen compositing. Templates in remotion and hyperframes stay inside their own compositions. |
| Engines for voice-enhance, diarization, detection, SFX | Each gets an ADR in its repo. The candidates listed there are unverified until that ADR checks the licences of both code and weights. |
| New areas: live streaming, restoration | Repository names, `owns` and departments in `ecosystem.json` (see "New areas (proposed)"). |
| qc-skill 1.0.0 | Its release workflow made 1.0.0 out of a dependabot bump. Keep 1.0.0 and widen the agent's gate (agent 11), or treat it as a mistake and release the next one as 0.2.x. |
| Status in `ecosystem.json` | voice-enhance, dubbing, sound-design and publish say `scaffold` and nle-bridge says `planned`, though each has a 0.1.0 with working ops. Not changed here while Velisa #132 edits that file. |
| New skill candidates (2026-11-05 field review) | broadcast-graphics-skill and design-system-skill (high), asset-library-skill (medium), generative-media-skill (low, ADR first): repository names, `owns` and departments (see "New skill candidates"). Recommended `owns`: 送出用グラフィックス / スティンガー / 待機画面・ループ素材 / 送出機パッケージ; ブランドキット / 配色・レイアウト規則; ストック素材取得 / 素材ライセンス台帳; AI映像生成 |
| Kinetic typography and geometric motion | Recommendation: hyperframes-skill's `owns` gains キネティックタイポ・幾何学モーション (its HTML scenes are the renderer); remotion-ffmpeg-skill keeps the measured (beat / lyric) versions and gains オーディオビジュアライザー |
| Delivery formats (alpha, key / fill, intermediates, multitrack, loudness versions) | Proposals 5-9 go to ffmpeg-skill's maintainers. If they decline, the owner names another engine owner; nothing here writes those files with raw ffmpeg |

## Tracking in the GitHub Project

The **AI Video Production Ecosystem** project (kajisho5 #1) is filled from this repository alone. `.github/workflows/project-sync.yml` runs hourly and adds every issue and pull request of the repositories in `ecosystem.json`. The other repositories need no setup. It needs the `PROJECT_TOKEN` secret here (see README, "GitHub Project"). Issues cut from the roadmap steps land in the project the same way.

## Per-repository roadmaps

Each repository's `ECOSYSTEM_ROADMAP.md` (added by its "Roadmap" PR): video-production-agent, ingest-skill, video-editing-skill, color-grading-skill, motion-graphics-skill, subtitle-skill, thumbnail-skill, blender-skill, remotion-ffmpeg-skill, hyperframes-skill, audio-production-skill, voice-enhance-skill, dubbing-skill, sound-design-skill, transcription-skill, diarization-skill, detection-skill, slide-sync-skill, qc-skill, media-analysis-skill, artifacts-skill, publish-skill, nle-bridge-skill, imagemagick-skill, stepcap, skillpact, system-intelligence, bdmvkit, vtskit, udfkit, dvdcc, oncemore. ffmpeg-skill has none, because it is complete.
