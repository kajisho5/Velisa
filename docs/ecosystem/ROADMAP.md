# Ecosystem build roadmap

What every repository still needs, how the pieces connect, and the order to build them in. Written from a read-only audit of all 33 components on 2026-10-30 (source, tests, CI, contracts, the agent's adapters), and reviewed again on 2026-11-05 against every repository's `ECOSYSTEM_ROADMAP.md`, with the steps from that day's OSS survey added (see "From the 2026-11 OSS survey"). Each repository carries an `ECOSYSTEM_ROADMAP.md` with PR-sized steps; this page is the map across them. `docs/ROADMAP.md` is the architecture roadmap (phases of the contract layer) and stays as it is.

**ffmpeg-skill is treated as complete.** Since 3.0.0 its 42 tools (`contract_version` 2.0; FFmpeg 6.1+ and Python 3.10+; 3.0 changed `cut.py`'s defaults and added `probe`'s start `timecode`) are the engine the others delegate to; every satellite now accepts `>=2.0.0 <4.0.0`. No step below changes it: what a step needs from the engine is written under "Proposals to ffmpeg-skill" and decided in that repository. Several gaps are closed by *using* tools it already has, e.g. `render --export-timeline` (.otio / .fcpxml / .edl), `freeze`, `reverse`, `insert`, `audio --duck --voice`, `metadata` chapters.

## Where things stand

| Department | Repositories | Today (2026-11-05) |
|---|---|---|
| Command | video-production-agent | plans, approves, renders, records; brain = rules + Claude (API or the chat app via MCP); 22 adapters, every ecosystem job has a SkillSpec (handoff when absent) |
| Ingest | ingest-skill | active: verified single-read offload to several destinations, ASC MHL + xxHash64, card-aware inventory, `ingest fetch` (URL via yt-dlp); wired (agent #83 offload, ADR-059 fetch) |
| Engine | ffmpeg-skill | 3.x, 42 tools, complete; agent uses 17 directly |
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
6. **New areas** (owner decision first, below): live streaming, restoration.

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

## Tracking in the GitHub Project

The **AI Video Production Ecosystem** project (kajisho5 #1) is filled from this repository alone. `.github/workflows/project-sync.yml` runs hourly and adds every issue and pull request of the repositories in `ecosystem.json`. The other repositories need no setup. It needs the `PROJECT_TOKEN` secret here (see README, "GitHub Project"). Issues cut from the roadmap steps land in the project the same way.

## Per-repository roadmaps

Each repository's `ECOSYSTEM_ROADMAP.md` (added by its "Roadmap" PR): video-production-agent, ingest-skill, video-editing-skill, color-grading-skill, motion-graphics-skill, subtitle-skill, thumbnail-skill, blender-skill, remotion-ffmpeg-skill, hyperframes-skill, audio-production-skill, voice-enhance-skill, dubbing-skill, sound-design-skill, transcription-skill, diarization-skill, detection-skill, slide-sync-skill, qc-skill, media-analysis-skill, artifacts-skill, publish-skill, nle-bridge-skill, imagemagick-skill, stepcap, skillpact, system-intelligence, bdmvkit, vtskit, udfkit, dvdcc, oncemore. ffmpeg-skill has none, because it is complete.
