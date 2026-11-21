# ADR-026: One Timebase for the Ecosystem: Exact Rates, One Rounding Rule, SMPTE Drop-Frame

Status: Accepted (decision D40)

## Context

Skills and the agent each turn frame rates and times into frames in their own way. Read from every repository's
`origin/main` on 2026-11-20 (video-editing-skill `9a41835`, video-production-agent `921fac5`, nle-bridge-skill
`ca0f649`, ingest-skill `b6c63fe`, qc-skill `a6492ac`, detection-skill `9a4933d`, hyperframes-skill `5de18d8`,
remotion-ffmpeg-skill `ad17dd1`, media-analysis-skill `f9c5847`, ffmpeg-skill `364f2d5`, and the other Skills, which
do no frame arithmetic):

- **Rates.** ffmpeg-skill's probe writes `fps` rounded to 3 decimals (29.97). Some readers turn it back into the exact
  rate with a table (nle-bridge, ingest, ffmpeg-skill's own `timeline.exact_rate`); others with
  `Fraction(fps).limit_denominator(1001)`, which gives 2997/100 for 29.97 and 2997/50 for 59.94 (video-editing-skill,
  and the agent, which copies it on purpose: video-production-agent ADR-115). The tables differ: nle-bridge reads
  `23.98` as 1199/50, ingest reads `29.970` and `47.952` as 2997/100 and 5994/125. Some Skills compare rates as floats
  within 0.02 fps.
- **Rounding.** Three rules are in use: a half up (`floor(x + 1/2)`: video-editing's joins and transitions, the agent,
  remotion-ffmpeg and hyperframes through JavaScript's `Math.round`, ffmpeg-skill's `decision.py`), a half to even
  (Python `round()`: nle-bridge, ffmpeg-skill's `timeline.py`, video-editing's `proposals.py`), and floor with a 1 ms
  tolerance (video-editing's joined lengths). They differ on exact halves only, and every rule is used for positions.
- **Accumulation.** The agent placed concat clips by their requested lengths while video-editing-skill joined them
  at whole frames, so every join landed a frame early and the error added up (ADR-115 there, fixed). The general
  form of that bug is adding values that were rounded one by one.
- **Timecode.** Only nle-bridge-skill and ingest-skill read or write SMPTE timecode. nle-bridge implements
  drop-frame fully and refuses labels that do not exist. ingest-skill reads `00:01:00;00` at 29.97 and
  `00:00:00:30` without complaint.
- **Rates a Skill can write.** hyperframes-skill accepts integer frame rates only, so a 29.97 or 59.94 programme
  cannot be rendered at its own rate.

## Decision

1. The spec is [docs/specs/timebase.md](../specs/timebase.md) (`velisa/timebase@1`): exact fractions (TB-1); a
   reading of rates with one NTSC table and no `limit_denominator` (TB-2); time on the wire as 6-decimal seconds or
   `N/D`, with milliseconds allowed up to 240 fps when read back by `nearest` (TB-3); one rounding rule, a half up,
   plus `down` for joined lengths (TB-4); positions counted, never summed from rounded values (TB-5); SMPTE
   timecode with drop-frame at 30000/1001 and 60000/1001 only (TB-6).
2. **A half rounds up**, not to even. It is what the frame-grid joins of video-editing-skill and the agent already
   do, what JavaScript's `Math.round` does (hyperframes, remotion-ffmpeg and their compositions), and it needs no
   special code in either language. Python's `round()` differs only on exact halves, so the Skills that use it are
   listed below; nothing is broken by it today except agreement on those halves.
3. The conformance vectors are [docs/specs/timebase-vectors.json](../specs/timebase-vectors.json) (134 vectors:
   NTSC and PAL rates, both rounding modes, joins, NDF and DF at 29.97 and 59.94, the labels that do not exist,
   24-hour refusal). Three vectors are optional (the `p` / `i` suffix).
4. **The reference implementation is `scripts/timebase.py` in this repository**, not in system-intelligence.
   System Intelligence is general-purpose; its ADR-001 keeps video-production assumptions out of its core, and frame
   rates and SMPTE timecode are exactly such assumptions. The spec, the vectors and the code that passes them stay
   in one repository and change in one pull request. `scripts/` is where this repository's runnable checks live;
   the module is standard-library only, so a Skill can copy it or run its vectors without installing anything.
   `scripts/tests/test_timebase.py` runs every vector and checks the stated properties (6-decimal and millisecond
   round trips, seeks never past their frame, 200 random joins without accumulation, every DF label for the first
   20 minutes and 40,000 sampled across a day at 29.97 and 59.94, every skipped label refused).
5. Skills are not changed here. Each repository that does not conform gets an issue; ffmpeg-skill is only listed.

## Where each repository stands (2026-11-20)

| Repository | Not conforming | Rule | Weight | Issue |
|---|---|---|---|---|
| video-editing-skill | The edit's rate is `Fraction(fps).limit_denominator(1001)` of the probe's 3-decimal fps: 2997/100 at 29.97 (`executor.py` 946, 1052, 1240, 1405, 1480; `proposals.py` 245). ffmpeg-skill's join writes 30000/1001, so the plan's timeline and the file part by a frame in about 9 hours (a frame in 4.6 h at 59.94). | TB-2 | medium | [video-editing-skill#59](https://github.com/kajisho5/video-editing-skill/issues/59) |
| | Rates compared as floats within 0.02 fps (`FPS_TOLERANCE`, `executor.py` 33). | TB-2 | low | |
| | `proposals.py` 246 snaps with `round()` (a half to even). | TB-4 | low | |
| video-production-agent | `concat_rate` copies the 2997/100 reading (`agent/editing.py` 688); `programme_rate` and the planner round `params.fps` to 3 decimals (`editing.py` 700, `planner.py` 1047); `FPS_TOLERANCE` 0.02 (`editing.py` 672). It must change together with video-editing-skill, or plan and Skill part again. | TB-2 | medium | [video-production-agent#167](https://github.com/kajisho5/video-production-agent/issues/167) |
| nle-bridge-skill | `parse_rate` matches its NTSC table within 0.0015: `--fps 23.98` gives 1199/50 and `47.95` 959/20, so an EDL or XML is written at a non-NTSC rate. | TB-2 | medium | [nle-bridge-skill#22](https://github.com/kajisho5/nle-bridge-skill/issues/22) |
| | `seconds_to_frames` uses `round()` (a half to even; on purpose, to match ffmpeg-skill's `timeline.py`). | TB-4 | low | |
| | `frames_to_timecode` writes `24:00:00:00` for 24 hours, and `timecode_to_frames` reads it. | TB-6 | low | |
| ingest-skill | `tc_seconds` reads a DF label that does not exist (`00:01:00;00` at 29.97 becomes 59.993 s, the time of `00:00:59;28`), a frame number at or above the nominal rate (`00:00:00:30`), and `;` at 25 fps as NDF, all without an error. It returns a float. | TB-6 | medium | [ingest-skill#26](https://github.com/kajisho5/ingest-skill/issues/26) |
| | `parse_rate` reads `29.970` as 2997/100 and `47.952` as 5994/125 (names outside its table go through `limit_denominator`), and accepts rates above 1000. | TB-2 | low | |
| | `tc_label` rounds through floats and wraps at 24 hours (`% 24`). | TB-6 | low | |
| hyperframes-skill | `fps` must be an integer (`scene-spec.mjs` 113, 652; `tools/render.mjs` 47): no 23.976, 29.97 or 59.94 render. | TB-1 | medium | [hyperframes-skill#33](https://github.com/kajisho5/hyperframes-skill/issues/33) |
| remotion-ffmpeg-skill | The source's rate is the probe's 3-decimal float (`render.py` 104, 151; `sec_to_frames` in `_common.py` 270 on floats); 29.97 is 0.1 frame an hour off 30000/1001. | TB-1, TB-2 | low | [remotion-ffmpeg-skill#28](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/28) |
| detection-skill | Rates and frame counts are floats (`frames.py` 185 `_rate`, 284 `floor(duration * rate + 1e-6)`). Its seek rounds down to the millisecond, as TB-3 asks. | TB-1 | low | [detection-skill#28](https://github.com/kajisho5/detection-skill/issues/28) |
| media-analysis-skill | `_fps_class` (`library.py` 69) names only 23.976 / 29.97 / 59.94 and compares floats; 47.952 and 119.88 are classed "48fps" and "120fps". | TB-2 | low | [media-analysis-skill#40](https://github.com/kajisho5/media-analysis-skill/issues/40) |
| qc-skill | Conforms: rates from `r_frame_rate` as fractions; its `round()` calls compare a decoded frame time with a frame, where no half occurs. | | | none |
| ffmpeg-skill (listed only) | The probe's `fps` is rounded to 3 decimals, which is where 2997/100 comes from downstream (TB-1: give `r_frame_rate` as the rate). `timeline.py` 238 rounds with `round()` while `decision.py` 656 rounds a half up (TB-4, inside one Skill). `exact_rate` matches NTSC within 0.01 and falls back to `limit_denominator(1001)` (TB-2). | | | none (not filed) |

The other Skills (artifacts, audio-production, blender, color-grading, diarization, dubbing, imagemagick,
motion-graphics, publish, slide-sync, sound-design, subtitle, thumbnail, transcription, voice-enhance) keep times in
seconds or milliseconds and do no frame or timecode arithmetic, so the spec asks nothing of them now.

## Consequences

- A Skill that converts a rate, a time or a timecode can check itself against the vectors, in Python or in
  JavaScript, without reading this repository's code.
- Fixing video-editing-skill's rate reading changes its plans at 29.97 and 59.94 by a frame per several hours; the
  agent's `concat_rate` has to move in the same release window, as ADR-115 there requires plan and Skill to agree.
- `timebase.py` is not installed into any Skill. Copying it, or importing the vectors into a Skill's own tests, is
  each repository's choice.
