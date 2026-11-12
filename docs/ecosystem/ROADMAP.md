# Ecosystem build roadmap

What every repository still needs, how the pieces connect, and the order to build them in. Written from a read-only audit of all 33 components on 2026-10-30 (source, tests, CI, contracts, the agent's adapters), and reviewed again on 2026-11-05 against every repository's `ECOSYSTEM_ROADMAP.md`, with the steps from that day's OSS survey added (see "From the 2026-11 OSS survey"). The same day every skill was also reviewed against field requirements (on-site work, broadcast quality, speed, recovery, natural-language control, the agent contract, live and broadcast delivery formats, motion graphics from a sentence, YouTube editing); the result is the third round below, "Field requirements across every skill", "New skill candidates" and proposals 5-14 to ffmpeg-skill. Each repository carries an `ECOSYSTEM_ROADMAP.md` with PR-sized steps; this page is the map across them. `docs/ROADMAP.md` is the architecture roadmap (phases of the contract layer) and stays as it is. On 2026-11-12 the owner answered the questions of the [ownership audit](ownership-audit/README.md); see "Decided by the owner (2026-11-12)".

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
| Audio | voice-enhance, dubbing, sound-design | 0.1.0, experimental ops, wired (agent #88, #97, #107); `active` in ecosystem.json since 2026-11-12 (no tags or GitHub Releases yet) |
| Recognition | transcription, diarization, detection, slide-sync | implemented and wired; speaker ids end to end (agent #111) |
| Verification | qc, media-analysis, artifacts | implemented and wired (artifacts: agent #110) |
| Delivery | publish | 0.1.0, seven uploaders tested against mocks only; wired as CONFIRM after QC (agent #99); `active` in ecosystem.json since 2026-11-12 (no tags or GitHub Releases yet) |
| Delivery | nle-bridge | 0.1.0 (export / conform / diff / import); agent export / conform wired (agent #101), read-back open; `active` in ecosystem.json (since 2026-10-31, #129) |
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
- **Built as `nle-bridge-skill`:** round-trip diff, FCP7 XML for Premiere, relink manifests and conform packages (0.1.0, nle-bridge #1-#5; the pinned community servers are documented in its `docs/live-control.md`, #2). The agent hands it the executed IR (agent #101); reading the editor's timeline back is agent step 12. `active` in `ecosystem.json` since 2026-10-31 (#129).

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
3. **Recognition.** Done (agent PRs): diarization with speaker ids end to end (#98, #111), detection (#104), slide-sync (#106). Open: transcript phrase search in transcription-skill (`WORK_QUEUE.md` item 25).
4. **Audio.** Done (agent PRs): filler removal (#87), voice-enhance (#88), the translation decision (subtitle-skill ADR-004), dubbing (#97), sound-design BGM (#107).
5. **Delivery.** Done (agent PRs): publish-skill (CONFIRM after QC, #99; real uploads not made yet), ingest adapter and MHL (#83). Partly done: nle-bridge-skill (export / conform #101; reading the editor's timeline back is agent step 12).
6. **Agent brain.** Done: requirements_extraction (agent #79). Open: semantic deletion, now agent step 13 (it had no step in the agent's roadmap), starting with retake and repeated-sentence candidates that the person confirms one by one (`WORK_QUEUE.md` item 26).
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
6. **New area:** restoration. Decided 2026-11-12: no new skill yet; the no-weights baseline is wired first and a skill waits for ADR-017 (see "New areas"). (Live streaming was dropped on 2026-11-05: out of scope.)

### Third round (2026-11-05, field review), in priority order

From a review of every skill against what conference, medical-congress, corporate-event and hybrid-event recording work needs (see "Field requirements across every skill" below). Each line is a step added that day to that repository's `ECOSYSTEM_ROADMAP.md`, named by its title; numbers are in each file.

1. **Delivery for broadcast and NLE** (highest: it decides whether a file can be used at all).
   - The engine side is proposals 5-11 to ffmpeg-skill, all accepted on 2026-11-05. Done (closed completed 2026-11-06): alpha masters #417, key / fill #418, intermediates #419, loudness versions #421, seamless loop #422, safe-area guide #423 (previews only). Open: multitrack audio #420 (with #401). Steps that wait for them say so; until each lands, the agent reports that delivery as a handoff.
   - qc-skill: key and fill pair check, alpha edge check, loop seam check, stinger cut-point check, broadcast and delivery profiles.
   - video-production-agent: delivery presets for broadcast and NLE ("key and fill as two files", "one file per layer"; 「キーフィルで2本」「レイヤー別で」).
   - audio-production-skill: stems and multitrack delivery, loudness versions in one run.
   - Generators: layer export (motion-graphics-skill), alpha deliveries (hyperframes-skill), alpha mode and render passes (blender-skill), style presets and layer output (remotion-ffmpeg-skill), layered output (thumbnail-skill), alpha hygiene for stills (imagemagick-skill).
2. **Motion graphics from a sentence** (文字PV・幾何学模様; see the section below).
   - hyperframes-skill: text animation, international typesetting and text fit, shape and pattern layers, generative layer (Three.js / GLSL), audio and beat lock, IN / LOOP / OUT segments, style presets and recipe gallery.
   - remotion-ffmpeg-skill: source-less runs, KineticType, visualizers, Three.js scenes.
   - blender-skill: procedural motion scenes, 3D text and logo reveal, audio-driven animation.
   - video-production-agent: productions with no source media, motion brief slots, relative revisions and references.
3. **Long recordings and recordings in progress** (終日収録・収録中ファイル).
   - ingest-skill: growing files, sync facts and multicam sets, progress, proxies at ingest.
   - transcription-skill: recordings in progress (growing files), chunked long recordings.
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
   - subtitle-skill: TTML / IMSC 1.1 and EBU-TT-D, regional caption profiles.
   - Disc kits: proceedings discs (bdmvkit), bitrate planner (vtskit), checksum manifest (udfkit), 608 limits (dvdcc), build from the agent and batch discs (oncemore).
8. **Governance.** skillpact: progress events and error classes in the contract, idempotency conformance. system-intelligence: field-readiness audit, roadmap drift check.
9. **New skills:** none created (owner decision 2026-11-12, see "New skill candidates"). Instead: title / stinger material in hyperframes-skill with the [`title.json` / `stinger.json` spec](../specs/title-and-stinger.md), the [`kit@1` spec](../specs/kit.md), the [licence record spec](../specs/licence-record.md), and [ADR-016](../adr/ADR-016-generative-media.md) before any generative media.

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
| 10 | (dropped 2026-11-05: live streaming is out of scope) | — | — |
| 11 | Plans saved and re-run as purpose-built pipeline templates | OpenMontage, ComfyUI (ideas only) | video-production-agent 16 |
| 12 | Translate → dub → subtitles in one run, with the speech rate fitted | pyvideotrans (ideas only) | dubbing-skill 11 |
| 13 | Mastering matched to a reference track | matchering (ideas only) | audio-production-skill 7 |
| 14 | Restoration: super-resolution and frame interpolation behind swappable engines, Real-ESRGAN optional | video2x (ideas only) | new area, below |
| 15 | Keyframe-aware lossless cuts that offer cut-point candidates | LosslessCut (ideas only) | proposal to ffmpeg-skill, below |

## Licence policy for outside projects

- **Ideas and methods from any licence, code from none that forbids it.** AGPL and GPL projects (OpenMontage, ComfyUI, pyvideotrans, matchering, video2x, LosslessCut) are read for how they work; nothing is copied, vendored, linked or imported from them. The step is implemented here from its own design. Every step that takes an idea names it: `参考：<project>（考え方のみ。コードは使わない）`.
- **A dependency** is used only under a licence that allows it (MIT, BSD, Apache-2.0, Unlicense). Its licence is checked in an ADR in the repository that adds it.
- **Terms of use are separate from code licences.** These are written next to the step that meets them:
  - **Model weights** carry their own licence. Example: LTX-2's code is Apache-2.0, but its weights are under the LTX-2 Community License, which limits commercial use by revenue. Real-ESRGAN, TransNetV2 and silero-vad weights are checked in the same ADR as their code.
  - **Remotion** is free for individuals and for companies with up to 3 employees; larger companies need a Remotion company licence (remotion-ffmpeg-skill README). The skill's MIT licence does not change that.

## Internationalisation principles

Velisa is built for use worldwide, not for one country. Each roadmap and pull request from 2026-11-05 on follows these rules. Earlier text that does not is brought in line by the re-profiling steps below.

1. **International defaults.** Defaults are English and international standards: ITU-R BT.709 / BT.2020 / BT.2100, EBU R128, ATSC A/85, SMPTE timecode, W3C TTML / IMSC 1.1 and WebVTT, Unicode (UAX #14 line breaking, UAX #29 grapheme clusters, UAX #9 bidirectional text). National standards and conventions are **regional profiles** the caller picks: ARIB TR-B32 and ARIB caption rules, Japanese vertical writing, ruby and kinsoku are examples. A regional profile is never a default, and no default value comes from one region.
2. **Examples in English first.** Example requests and sample text in documents are written in English. Another language is shown beside it only when the example is about that language.
3. **Many languages in speech and text.** Transcription, dubbing and subtitles assume many languages:
   - The spoken language is detected per file or per segment (with a confidence), unless the caller states it.
   - Every transcript, cue, audio track and subtitle track carries a BCP 47 language tag.
   - Layout covers right-to-left and bidirectional scripts, CJK, complex scripts (Indic, Thai) and combining marks.
   - Line and character limits are per language, not one fixed number.
4. **Loudness targets side by side.** EBU R128 (-23 LUFS, -1 dBTP), ATSC A/85 (-24 LKFS, -2 dBTP) and the streaming platforms' own values (YouTube, Spotify, Apple, Netflix and others, from ffmpeg-skill's platform table) are listed together. A regional broadcast target such as ARIB TR-B32 (-24 LKFS, Japan) is one more profile in the same list.
5. **Engines chosen for many languages.** An engine that is strong in one language is an option for that language. The default is the engine that covers the most languages under a licence that allows commercial use of both code and weights.

### Re-profiling steps (Japan-specific text → regional profiles)

Each line becomes a step in that repository's `ECOSYSTEM_ROADMAP.md` with its next roadmap PR. Until then, this list is the record.

| Repository | What is Japan-specific today | Step |
|---|---|---|
| video-production-agent | requirements_extraction keywords and the examples in steps 18-21 are mostly Japanese | keyword sets per language (English first, Japanese as one set); examples in English with Japanese alongside |
| subtitle-skill | ja / zh / ko locale profiles | step 10 is already "regional caption profiles", with `ja-broadcast` as the first ([subtitle-skill#28](https://github.com/kajisho5/subtitle-skill/pull/28)); still to do: per-language limits for every locale |
| transcription-skill | optional engines tuned for Japanese (`haas_ja`, `speechcpp` models) | language detection by default; an engine table per language; English and multilingual candidates below |
| dubbing-skill | VOICEVOX and Style-Bert-VITS2 (Japanese); pronunciation dictionary examples | the default engine chosen for language coverage; Japanese engines as options for Japanese |
| motion-graphics-skill | — | done: step 9 is "name fit for lower thirds, any language" ([motion-graphics-skill#36](https://github.com/kajisho5/motion-graphics-skill/pull/36)) |
| hyperframes-skill | (written international from the start: typesetting with RTL and CJK; vertical and ruby as profiles) | none |
| qc-skill | (written with `ebu-r128`, `atsc-a85` and `stream` first; `arib-tr-b32` as a regional profile) | none |
| audio-production-skill | — | done: step 9 lists EBU R128, ATSC A/85 and streaming first, ARIB TR-B32 as a regional profile ([audio-production-skill#29](https://github.com/kajisho5/audio-production-skill/pull/29)) |
| detection-skill | OCR languages `jpn` / `jpn_vert` / `eng`; PII patterns | OCR language packs chosen per job (any Tesseract language); PII patterns per locale, none by default |
| diarization-skill, artifacts-skill, publish-skill | examples and checks written for Japanese events (honorifics, variant kanji) | the same checks as per-language rules; Japanese as one rule set |
| thumbnail-skill, remotion-ffmpeg-skill, blender-skill | CJK font handling described for Japanese | font fallback for every script (Noto by default); examples in English |

### Engines for English and other languages (candidates, survey on hold)

Engines to look at when the survey is done. None of them is checked yet: each repository's ADR checks the licences of the code and the weights and the measured quality before one is used.

| Task | Candidates (licence as published; to be checked) |
|---|---|
| Speech recognition | Whisper large-v3 / large-v3-turbo through faster-whisper (MIT); NVIDIA Parakeet TDT (CC-BY-4.0 weights); Distil-Whisper (MIT, English) |
| Word alignment | wav2vec2 alignment models via whisperX (Apache-2.0 models checked in transcription ADR-038); MMS alignment is CC-BY-NC, so not for commercial use |
| Text to speech | Kokoro-82M (Apache-2.0, strong in English); Piper (MIT code, each voice's own licence); Chatterbox Multilingual (MIT, already the default) |
| Machine translation | OPUS-MT on CTranslate2 (already optional; licence per model); Argos Translate (already the default) |
| OCR | Tesseract language packs (Apache-2.0); PaddleOCR (Apache-2.0) |
| Voice isolation | DeepFilterNet3 (already chosen; check on English and other languages too) |

## Field requirements across every skill (2026-11-05 review)

What every skill was checked against, and where each gap landed. "Step" means a step added to that repository's `ECOSYSTEM_ROADMAP.md`.

| Viewpoint | What is there | Gap and where it landed |
|---|---|---|
| On-site work: 撮って出し, short deadlines, 2-8 h recordings, multicam, multi-mic, sync (timecode, waveform), recordings in progress, recording → archive edit | ingest verified offload; ffmpeg-skill `multicam` / `sync` / `proxy`; agent `render --resume` | growing files (ingest, transcription, slide-sync, media-analysis); chunked long jobs and deadline mode (agent); multicam sets at ingest; active speaker (detection); camera matching (color); automixer (audio) |
| Quality: EBU R128, ATSC A/85, BT.709 / BT.2020, SRT / VTT / TTML, regional profiles (e.g. ARIB), QC | qc loudness, flash, cut accuracy, legibility; ffmpeg-skill `broadcast` platform at -23 LUFS | named profiles with ATSC A/85 and streaming targets, ARIB TR-B32 as a regional one (qc); legal range (color); TTML / IMSC and EBU-TT-D (subtitle); ARIB STD-B24 / B36 binary captions declined by ffmpeg-skill (proposal 14, #426: FFmpeg has no ARIB writer), TTML in their place |
| Speed: proxies, GPU (NVENC / VideoToolbox / QSV), parallel, cache, incremental | ffmpeg-skill hardware encoders and `proxy`; media-analysis cache | segment cache and partial re-render (video-editing); incremental QC (qc); chunked parallel transcription; proxies at ingest |
| Recovery: resume, partial re-render, idempotency, logs | agent `--resume`; ingest resumable; hyperframes `bit_exact` | resumable blocks (voice-enhance, transcription, diarization); idempotency conformance (skillpact); series uploads never sent twice (publish) |
| Natural-language control: vague requests, confirmation gates, preview and revise, "さっきの" | requirements_extraction (unambiguous phrases), CONFIRM floors, `revise --feedback` | motion brief slots, relative revisions and references, delivery presets from a sentence (agent) |
| Agent contract: inputs and outputs, error classes, progress | per-skill error codes with `retryable` | one error-class vocabulary and progress events (skillpact; agent over MCP) |
| Future: generated video, many languages, AI voice, vertical shorts, clips from long recordings | dubbing, subtitle translate, remotion `--aspect` | Shorts set and highlight signals (agent, media-analysis); AI clips in an edit (video-editing); AI voice disclosure (dubbing); generative media: [ADR-016](../adr/ADR-016-generative-media.md) first, no skill yet |

### Delivery formats for broadcast and NLE (all skills)

Owner split: the files are written by ffmpeg-skill (proposals 5-9 below, since it is not changed from here); generators keep layers separate and say how their alpha is stored; qc-skill checks the result; the agent turns the request into a preset.

| Need | Engine (ffmpeg-skill) | Generators | Check (qc-skill) | Request (agent) |
|---|---|---|---|---|
| Layers as separate alpha files for After Effects / NLE | alpha masters (proposal 5, done: ffmpeg-skill#417) | layer export (motion-graphics), alpha deliveries (hyperframes), passes (blender), `--layers` (remotion), layered output (thumbnail); placed on upper tracks by nle-bridge | alpha edge check | `nle-layers` preset, "レイヤー別で" |
| Key and fill as two files (same length, same frames), premultiplied or straight | key / fill pair (proposal 6, done: #418) | the alpha mode (straight or premultiplied) recorded by every generator; still key / fill (imagemagick) | key and fill pair check | `key-fill` preset, "key and fill as two files"（「キーフィルで2本」） |
| ProRes 4444 / 4444 XQ, HAP Alpha, QuickTime Animation, PNG / EXR sequence; DNxHR / DNxHD, ProRes 422 HQ | proposals 5 and 7 (done: #417, #419; ProRes 422 HQ exists as `export --preset prores`) | — | profile per codec | `alpha-master`, `intermediate` |
| Stems, multitrack WAV, loudness versions (-14 / -23 / -24) | multitrack audio, loudness versions (proposals 8, 9: #420 with #401 open, #421 done) | stems and loudness set (audio-production) | broadcast and delivery profiles | `loudness-set` |
| Batch in several sizes, fps and aspects; loops; safe-area guides; file naming; checksums | export per preset exists; seamless loop (proposal 10, done: #422); a safe-area guide overlay for previews (proposal 11, done: #423) | one edit in several aspects (video-editing); IN / LOOP / OUT (hyperframes) | loop seam check | `aspect-set`, a naming rule and a checksum manifest per delivery |
| Stingers (transitions inside an edit) and loops | alpha masters (proposal 5) | stinger templates with a cut point (hyperframes; remotion, blender) | stinger cut-point check, loop seam check | the stinger transition in video-editing-skill |

## Motion graphics from a sentence (文字PV・幾何学模様)

The request: "make a cool text-only PV, or a piece finished with geometric patterns, from a sentence" (for example "neon, 120 BPM, 15 s, vertical"; 例：「ネオンで、120BPM、15秒、縦型」).

**What works today** (checked against each skill's README, SKILL.md and contract on 2026-11-05):

- **hyperframes-skill** is the closest fit: a scene from nothing (size, duration, fps, background), text / image / video layers with `fade`, `slide` and `zoom` transitions (CSS, seeked frame by frame, `bit_exact` on one machine), local fonts (Japanese included), templates (`title-card`, `lower-third`, `session-slate`, `break`), a CSV `batch` (one file per speaker), ProRes 4444 with alpha. Missing: per-character / per-word animation, shapes and patterns, audio, beat lock, styles.
- **remotion-ffmpeg-skill**: beat-measured compositions (PeakPulse, BeatMontage), Karaoke and Captioned from word timings, `--aspect 9:16`, `--brand`, transparent `--overlay --keep-graphics`, and any custom React composition Claude writes into the project. Missing: a run with no source footage (`analyze` needs a file), kinetic-type and visualizer compositions, Three.js.
- **motion-graphics-skill**: 13 typed elements burned onto existing video, `fade` only (slide / move / scale are listed as unsupported), `shape` a solid rectangle. Good for burned titles; not for kinetic type.
- **blender-skill**: declarative `scene.json` (assets, lights, camera, background), turntables, transparent sequences. No text objects, no Geometry Nodes presets, no audio drive.
- **video-production-agent**: `plan` needs input media; `html_scene_render` is a handoff, so a text-only PV is not planned yet.

Today's working path, in the chat: Claude writes a hyperframes scene request (or fills a template) and renders it, e.g. "white serif 'Build the future' centred on black, each line sliding up over 0.5 s, vertical 1080x1920, 6 s, 30 fps" → `scene` → `preview` → `render --codec prores` for alpha. For music sync, ffmpeg-skill `background` + `audio --replace` with the track gives a source for remotion `analyze --beats`, then PeakPulse or a custom composition.

**Steps added** (names as in each repository's roadmap): hyperframes-skill — text animation, international typesetting and text fit, shape and pattern layers, generative layer (Three.js / GLSL), audio and beat lock, IN / LOOP / OUT segments, alpha deliveries, style presets and recipe gallery; remotion-ffmpeg-skill — source-less runs, KineticType, visualizers, Three.js scenes, emphasis captions, style presets and layer output; blender-skill — procedural motion scenes, 3D text and logo reveal, alpha and passes, audio-driven animation; motion-graphics-skill — style presets, rendered-layer element, layer export, Japanese name fit, end-screen areas; video-production-agent — productions with no source media, motion brief slots, relative revisions; sound-design-skill — tempo-targeted generation and a tempo map.

**Three.js: where it goes.** Both engines can render Three.js deterministically, so no new skill.
- HyperFrames seeks every frame through frame adapters (GSAP, Lottie, CSS or a custom one; `@hyperframes/core`, Apache-2.0), and hyperframes-skill already forces SwiftShader (no GPU capture), which is what makes WebGL output repeatable. A custom adapter that sets the program's time from the frame number is the whole integration: hyperframes-skill, generative layer.
- Remotion has `@remotion/three` (MIT; Remotion's own licence applies to the render), driven by `useCurrentFrame()`; it suits Three.js that reacts to measured beats: remotion-ffmpeg-skill, Three.js scenes.
- A separate headless-Chromium frame grabber would repeat what both engines already do (seek, capture, encode, verify). Not built.
- GSAP is not used: its licence is GSAP's own standard licence, not an open-source one. CSS / Web Animations and our own adapters only.

**Audio visualizers: no new skill.** ffmpeg-skill `waveform` already draws waveform and spectrum videos, `loop` loops a clip, and remotion-ffmpeg-skill owns measurement-driven motion (beats, peaks, Karaoke lyrics). Visualizers and loops are remotion-ffmpeg-skill's (visualizer compositions), 3D ones blender-skill's (audio-driven animation), looping beds sound-design-skill's.

## Editing a YouTube video: flow × skill

Velisa is an editing, finishing and delivery tool. Planning, idea generation, writing and polishing scripts, shot lists and shooting support, and running a channel after publishing (comments, analytics, improvement ideas) are out of scope: the host AI (Claude) does them in the conversation. A script is used here only as an input to editing.

| Stage | Need | Skill (existing / step added) |
|---|---|---|
| Script as input | script alignment, paper edit in script order, misread lines | transcription-skill script alignment (round 2); agent: paper edit from a script |
| Edit | jump cuts, silence / filler removal, pacing | audio-production SILENCE_REMOVE / FILLER_REMOVE, remotion Jumpcut, agent semantic deletion (round 2) |
| | B-roll inserted automatically | ffmpeg-skill `broll`; picking the clip: the agent, with licence records in the [shared shape](../specs/licence-record.md) (no new skill) |
| | zoom / punch-in on the speaker | video-editing-skill: punch-in on the speaker |
| | sound effects placed (pop, whoosh) | sound-design-skill: sound-effect cue sheet → audio-production MIX |
| | emphasis captions, speech bubbles | remotion-ffmpeg-skill: emphasis captions |
| | chapters | slide-sync chapters; agent: chapters from the transcript |
| | end screen and cards kept clear | motion-graphics-skill: end-screen and card areas |
| Assets | stock footage and images with licence lines | ingest-skill `fetch` plus a licence record in the [shared shape](../specs/licence-record.md); no new skill (2026-11-12) |
| | royalty-free BGM, loops | sound-design-skill library mode; stock music with licence records; loopable beds |
| | AI images and video | thumbnail-skill FLUX backgrounds; video-editing-skill: AI-generated clips in an edit; generative media: [ADR-016](../adr/ADR-016-generative-media.md) first, no skill yet |
| | meme inserts | motion-graphics `meme`; clips: ingest-skill `fetch` with a licence record |
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
| Rights and safety | BGM and asset licences | sound-design licence records; artifacts-skill: credits and licence lines (`credits_attribution`); the [licence record spec](../specs/licence-record.md) |
| | faces and personal data blurred | detection-skill faces / tracks → ffmpeg-skill `redact`; personal and patient data |
| | Content ID risk | sound-design-skill: stock music with licence records (a source's Content ID flag); a real check is not possible offline |

## New skill candidates

**Decided by the owner on 2026-11-12: none of the four is created.** The drafts below are kept as history; the decision for each is in [DECISION_LOG.md](DECISION_LOG.md) (D15-D18) and the evidence in [ownership-audit/](ownership-audit/).

| Candidate | Decision | What exists instead |
|---|---|---|
| motion-titles-skill | Not created. Folded into hyperframes-skill: stinger templates and `stinger.json`, typesetting, brand input. Its `owns` gains テロップ・スティンガー・ループ素材. | [`title.json` / `stinger.json` spec](../specs/title-and-stinger.md): the shape video-editing-skill, motion-graphics-skill, qc-skill and the agent already read |
| design-system-skill | Not created. Revisit as a skill once three or more renderers read `kit@1`. | [`kit@1` spec](../specs/kit.md): a superset of ffmpeg-skill `brand.json`, with a mapping to each renderer's existing input |
| asset-library-skill | Not created. Project credits keep using artifacts-skill `credits_attribution`. | [Licence record spec](../specs/licence-record.md): the record sound-design-skill already writes, extended to video and images |
| generative-media-skill | Not created. An ADR comes first. | [ADR-016](../adr/ADR-016-generative-media.md) (Proposed): engines, code and weight licences, VRAM, commercial terms, reuse of thumbnail-skill's `BackgroundProvider` |

### Drafts (2026-11-05, history)

- **motion-titles-skill** (priority was high): animated title and stinger files for editing (lower thirds, session titles, straps, count-ups, comment cards, stingers, loops) in IN / LOOP / OUT segments, with alpha or key / fill and a metadata file (`title.json`, then named `motion-titles/title@1`: segments, cut point, alpha mode, safe area, text as drawn, font size). Draft contract `motion-titles make <template> --values|--csv --kit --duration --cut-point --format`. The pictures were to be rendered by hyperframes-skill, which is why it was folded there.
- **design-system-skill** (priority was high): one brand kit for every renderer (colours, fonts with licences, logos with clear space, spacing, type rules, generated palettes with contrast checked). Draft contract `design kit validate`, `design kit derive --for <renderer>`, `design palette`, `design event-pack`.
- **asset-library-skill** (priority was medium): search and fetch stock footage and images from sources with a documented licence and an API, record each asset's licence, author, source URL and attribution line, and keep a project ledger. Draft contract `assets search`, `assets fetch` (writing `asset-library/asset@1`), `assets ledger`.
- **generative-media-skill** (priority was low, ADR first): generated stills and clips as edit material behind swappable local engines, each output marked AI_GENERATED with the engine, the weights and their licence.

### Judged not to need a new skill

- **Three.js / GLSL renderer:** hyperframes-skill (generative layer) and remotion-ffmpeg-skill (Three.js scenes), see above. remotion-ffmpeg-skill's Three.js step waits for hyperframes-skill's, so it is not built twice.
- **Audio visualizer:** remotion-ffmpeg-skill owns it (オーディオビジュアライザー, 2026-11-12) and keeps the measured (beat / lyric) versions; ffmpeg-skill `waveform` stays the engine's simple one. blender-skill stays 3D only.
- **TTS narration:** dubbing-skill NARRATE owns AIナレーション.
- **Kinetic typography / geometric PV:** hyperframes-skill owns it (キネティックタイポ・幾何学モーション, 2026-11-12), with the agent planning it.

## New areas (proposed)

**Restoration, decided by the owner on 2026-11-12: no new skill yet.** The no-weights baseline is wired first (ffmpeg-skill scaling, `minterpolate`, `denoise`). A skill comes only after [ADR-017](../adr/ADR-017-restoration.md) records the weights' licences. The steps below are the plan for that skill and stay as written; step 1 is that ADR. Live streaming was proposed here as well; it is out of scope since 2026-11-05 (owner decision: Velisa is an editing tool).

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
5. **Alpha masters.** `export` presets that keep alpha and verify it on an output frame: ProRes 4444 and 4444 XQ (`prores_ks` profiles 4 / 5, `yuva444p10le`), QuickTime Animation (`qtrle`), PNG and EXR sequences, HAP Alpha (FFmpeg's `hap` encoder, needs a build with snappy; reported by `doctor` when missing), WebM VP9 alpha. The alpha mode (straight or premultiplied) is a flag and is written to the result. Asked for by the generators' layer and alpha steps (motion-graphics, hyperframes, blender, remotion, thumbnail) and the agent's delivery presets (2026-11-05 field review). **Decision (ffmpeg-skill, 2026-11-05): accepted** ([ffmpeg-skill#417](https://github.com/kajisho5/ffmpeg-skill/issues/417)). **Done:** ffmpeg-skill#417 closed completed on 2026-11-06.
6. **Key / fill pair.** One call that writes the fill and the key (the alpha as a full-range luma matte, `alphaextract`) from one source with alpha: same frame count, fps, size and start timecode, straight or premultiplied fill as asked, both hashed. qc-skill's key and fill pair check reads the result. **Decision: accepted** ([ffmpeg-skill#418](https://github.com/kajisho5/ffmpeg-skill/issues/418), after [#417](https://github.com/kajisho5/ffmpeg-skill/issues/417)). **Done:** ffmpeg-skill#418 closed completed on 2026-11-06.
7. **Intermediate presets.** DNxHR LB / SQ / HQ / HQX / 444 and DNxHD at the broadcast sizes and rates, beside the existing ProRes 422 HQ (`export --preset prores`). **Decision: accepted** ([ffmpeg-skill#419](https://github.com/kajisho5/ffmpeg-skill/issues/419)). **Done:** ffmpeg-skill#419 closed completed on 2026-11-06.
8. **Multitrack audio.** Several audio inputs into one file as separate tracks with names and language tags: multitrack WAV (or BWF with the start timecode) and MOV / MXF with one track per stem. Asked for by audio-production-skill's stems step and nle-bridge-skill's package. **Decision: accepted** ([ffmpeg-skill#420](https://github.com/kajisho5/ffmpeg-skill/issues/420), done together with [#401](https://github.com/kajisho5/ffmpeg-skill/issues/401); still open on 2026-11-12).
9. **Loudness versions in one pass.** One master, several targets: -14 LUFS (streaming), -23 LUFS / -1 dBTP (EBU R128, the `broadcast` platform has it), -24 LKFS / -2 dBTP (ATSC A/85), and regional profiles such as ARIB TR-B32 (-24 LKFS / -1 dBTP, Japan), each measured after. ATSC A/85 was added to this list after the decision, on the internationalisation principles. **Decision: accepted** ([ffmpeg-skill#421](https://github.com/kajisho5/ffmpeg-skill/issues/421)). **Done:** ffmpeg-skill#421 closed completed on 2026-11-06.
10. **Seamless loop.** `loop --crossfade S` (picture and sound across the seam) and a measurement of the seam; `loop.py` says today that it does not smooth the loop point. **Decision: accepted, top priority** ([ffmpeg-skill#422](https://github.com/kajisho5/ffmpeg-skill/issues/422)). **Done:** ffmpeg-skill#422 closed completed on 2026-11-06.
11. **Safe-area guide.** A guide overlay (title safe / action safe for 16:9 and 4:3 centre cut, and the platform safe zones `_platforms.py` already has) as a preview file, never burned into a delivery. **Decision: accepted, for previews only** ([ffmpeg-skill#423](https://github.com/kajisho5/ffmpeg-skill/issues/423)). **Done:** ffmpeg-skill#423 closed completed on 2026-11-06.
12. **Growing files and LTC.** `probe` and `cut` on a file still being written (fragmented MP4 / MOV, MXF) reporting the duration that is readable so far; and LTC decoded from an audio channel as a sync source for `sync` / `multicam`. Asked for by ingest-skill's growing-files and sync-facts steps. **Decision: on hold** ([ffmpeg-skill#424](https://github.com/kajisho5/ffmpeg-skill/issues/424): the guarantee for a partial read has to be designed first. ingest-skill's growing-files step copies bytes and does not wait for it; transcription / slide-sync / media-analysis follow modes read only the closed part until then).
13. **Typed keyframes on overlay.** Position, scale and opacity keyframes with stated easing on `overlay`, so motion-graphics-skill can offer slide / move / scale (today in its `unsupported_animations`). Until then animated graphics come pre-rendered from hyperframes-skill and are placed by motion-graphics-skill's rendered-layer element. **Decision: on hold** ([ffmpeg-skill#425](https://github.com/kajisho5/ffmpeg-skill/issues/425): who owns animated overlays has to be decided first; the pre-rendered path above stays the way until then). **Not needed (owner decision 2026-11-12):** animated overlays are made by hyperframes-skill and placed by motion-graphics-skill's `rendered_layer`; what is missing is the agent's path that runs hyperframes-skill (DECISION_LOG D12).
14. **ARIB captions.** ARIB STD-B24 caption streams for Japanese broadcast deliveries; a large format decision, so it is a proposal only. subtitle-skill writes TTML with ruby and vertical text meanwhile. **Decision: declined** ([ffmpeg-skill#426](https://github.com/kajisho5/ffmpeg-skill/issues/426): FFmpeg has no ARIB caption writer. subtitle-skill's TTML (IMSC 1.1, with ruby and vertical text) is the replacement).

## Decided by the owner (2026-11-12)

From the [ownership audit](ownership-audit/README.md). Each row is an entry in [DECISION_LOG.md](DECISION_LOG.md) (D12-D32), with its evidence.

| Question | Decision |
|---|---|
| Animated overlays (ffmpeg-skill #425 waited for it) | Material by hyperframes-skill (segments, alpha), placement by motion-graphics-skill's `rendered_layer`. #425 is not needed for this. Missing: the agent's path that runs hyperframes-skill and passes its output to `motion.layer`. |
| Status in `ecosystem.json` | voice-enhance, dubbing, sound-design and publish are `active`. One definition of `status`, in `ecosystem.json`'s `$comment`: `active` = working operations behind the contract, released or not; `scaffold` = the repository exists, no operation works yet; `planned` = no repository yet. Release state is a roadmap step in each of the four. nle-bridge was already `active`. |
| Platform duration and file-size limits | publish-skill's values are authoritative; ffmpeg-skill `check`'s rows are guidance only and `publish plan` does not use them for its verdict. |
| New skill candidates (2026-11-05 field review) | None created; specs and an ADR instead (see "New skill candidates"). |
| New area: restoration | No skill yet; the no-weights baseline first, then ADR-017 on the weights' licences. |
| Overlay / PiP / titles | Titles: motion-graphics burns them into a programme, hyperframes makes the material files, remotion's stay inside its compositions. Overlays: video-editing = still overlay as part of an edit, motion-graphics = logos, PiP, chroma key and placing animated graphics, ffmpeg-skill = B-roll and the engine. |
| Animated subtitles | Generated from subtitle cues: subtitle-skill (passing ffmpeg-skill `caption --animate/--karaoke` through). Word-timed effects: remotion-ffmpeg-skill. |
| Loudness | audio-production-skill owns it, ffmpeg-skill is the engine. The agent's routing is not changed until `loudnorm` and `ebur128` are compared on measurements. |
| Compliance checking | Recorded, no wiring change: ffmpeg-skill `check` = the engine's preflight, qc-skill = judgement against the plan or spec. |
| Measurement and cut detection | Layers, not collisions: fast list = ffmpeg-skill `scenes`, observation = media-analysis (gains 発話区間), frame-accurate shots = detection-skill `shots` (gains ショット検出), judgement = qc-skill, slides = slide-sync. Default providers unchanged. |
| `owns` against reality | video-editing computes retake / duplicate candidates, the agent presents and approves them; transcription-skill implements its phrase search; ffmpeg-skill keeps 納品レポート and gains カットリスト書き出し, nle-bridge keeps the NLE round trip. |
| Speaker ids | diarization-skill owns the assignment rule; transcription-skill's merge is a copy with shared conformance fixtures. |
| Kinetic typography and geometric motion | hyperframes-skill; audio visualizers to remotion-ffmpeg-skill, which keeps the measured versions; blender-skill 3D only. |
| Disc family | Five entries in `ecosystem.json`; the agent keeps one disc SkillSpec (`disc_author` via oncemore). |
| stepcap and oncemore | Listed as stand-alone apps (`"kind": "app"`). |
| Contract checks | OS contract shape = system-intelligence; side effects, signatures and isolation = skillpact; runtime version gates = the agent; Velisa `registry/` = the reference definition of the collision policy. |
| Stale documents | HANDOFF, CROSS_REPO_STATUS and CURRENT_STATE are frozen 2026-09 records; this page is the current state. CAPABILITY_MATRIX and REPOSITORY_MAP are to be generated from the pinned contracts (WORK_QUEUE). |

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
| Engines for voice-enhance, diarization, detection, SFX | Each gets an ADR in its repo. The candidates listed there are unverified until that ADR checks the licences of both code and weights. |
| qc-skill 1.0.0 | Its release workflow made 1.0.0 out of a dependabot bump. Keep 1.0.0 and widen the agent's gate (agent 11), or treat it as a mistake and release the next one as 0.2.x. |

## Tracking in the GitHub Project

The **AI Video Production Ecosystem** project (kajisho5 #1) is filled from this repository alone. `.github/workflows/project-sync.yml` runs hourly and adds every issue and pull request of the repositories in `ecosystem.json`. The other repositories need no setup. It needs the `PROJECT_TOKEN` secret here (see README, "GitHub Project"). Issues cut from the roadmap steps land in the project the same way.

## Per-repository roadmaps

Each repository's `ECOSYSTEM_ROADMAP.md` (added by its "Roadmap" PR): video-production-agent, ingest-skill, video-editing-skill, color-grading-skill, motion-graphics-skill, subtitle-skill, thumbnail-skill, blender-skill, remotion-ffmpeg-skill, hyperframes-skill, audio-production-skill, voice-enhance-skill, dubbing-skill, sound-design-skill, transcription-skill, diarization-skill, detection-skill, slide-sync-skill, qc-skill, media-analysis-skill, artifacts-skill, publish-skill, nle-bridge-skill, imagemagick-skill, stepcap, skillpact, system-intelligence, bdmvkit, vtskit, udfkit, dvdcc, oncemore. ffmpeg-skill has none, because it is complete.
