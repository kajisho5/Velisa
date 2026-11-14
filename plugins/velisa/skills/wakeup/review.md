# Production steps and human-review checkpoints

How to run a job so the user sees the plan before anything is written, sees the result checked
against what they asked for, and knows exactly where a person still has to look or listen.
Who does each step comes from the "Who owns what" table in [SKILL.md](SKILL.md); this page names
the step, not the tool, except where the field names come from `ffmpeg-skill`, the engine most
steps run on. Numbers (tolerances, time limits, thresholds) live in ffmpeg-skill's own docs:
link them, do not restate them.

ffmpeg-skill references used below:
[workflow](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/workflow.md),
[gotchas](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md),
[contract: verification policy](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/contract.md#verification-policy),
[contract: dry run](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/contract.md#dry-run),
[design decisions](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/design-decisions.md).

## 1. Probe every input first

Probe before planning (`media-analysis-skill`, or ffmpeg-skill `probe.py`). Plan from the numbers,
and tell the user about any of these before going on:

- **Variable frame rate** (`variable_frame_rate_suspected`): say so. Re-encodes conform it to a
  constant rate, a lossless cut may be re-encoded instead, and subtitle timing on VFR footage needs
  the spot checks in step 6
  ([gotchas: variable frame rate](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#variable-frame-rate)).
- **Non-square pixels (SAR) or rotation metadata**: the displayed frame is not the coded one. Plan
  any crop or aspect change from the displayed size, and say which one the plan used
  ([gotchas: dimensions and rotation](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#dimensions-and-rotation)).
- **Long sources** (anything a person cannot watch in full for this job): plan a proxy or excerpt
  review up front: which minutes the user will check, and how (a contact sheet, short clips).
  Automatic output checks decode only the ends of a file; full-length passes (loudness re-measure,
  content checks) take minutes per hour of media
  ([design decisions: time limits](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/design-decisions.md#time-limits)).

## 2. Show the plan before writing

Before any write, show the user:

- the steps in order and which skill does each one (the default order of the editorial stages,
  and what to say when a plan departs from it: [stages.md](stages.md));
- the planned commands and encoder from `--dry-run --json` (`commands`, `encoder`), or the owning
  skill's own plan output;
- the requested output: duration, resolution, fps, codec, audio layout, loudness, destination.

Say in the same message what a dry run does **not** check: ffmpeg does not parse the filter graph,
an intermediate a previous step has not written yet is only a placeholder (its probe is a stub),
and nothing about the real output (length, sync, look) is known until it exists
([contract: dry run](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/contract.md#dry-run)).
Wait for the user's go-ahead when the job is long, overwrites anything, or the request left a
choice open.

## 3. Trial first, then the long run

- **Heavy or long jobs: trial on a short excerpt first.** Cut the first 10 s (ffmpeg-skill
  `cut.py --start 0 --end 10`, or the cut owner), run the whole pipeline on that, check it as in
  step 4, and show it to the user. Only then run the full source.
- **Long encodes run in the background**, not in a foreground shell call: the agent's own command
  or MCP request timeout can end the job even when the tool's limit would not. Pass an explicit
  `--timeout` sized to the job (`0` = no limit) and `--progress`, and poll the progress output
  ([design decisions: time limits](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/design-decisions.md#time-limits)).

## 4. After every write: read the result, then compare it yourself

1. Read the result JSON: `verified`, `verification` (the steps that ran), `unverified`, `notes`.
   `verified: true` means the listed checks passed; it does not mean the output matches the
   request. Most writing tools check that the output exists, is readable and keeps the input's
   streams; only a few compare against the requested values
   ([contract: verification policy](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/contract.md#verification-policy)).
2. Probe the output and compare it with the request and the input yourself:
   - duration (requested, or input minus what was removed);
   - fps, video codec, resolution / aspect;
   - stream layout: the same video and audio streams as the input (no lost audio, no lost picture,
     channel layout as asked).
3. Report each item as **matches**, **differs** (with both numbers) or **unknown** (nothing measured
   it). Every entry in `unverified` is reported as unknown, never as passed.
4. Do not say "done" when anything differs, or when a value the user asked for is unknown. Say what
   differs and offer the fix.

## 5. Cuts: say how close the cut is

- Report the cut's `mode`, `precision` and `duration_error_ms` (and `keyframe_snapped`). A lossless
  cut snaps to keyframes and can still be `verified: true` while it is off by a visible amount;
  offer the frame-accurate re-encode when the error matters
  ([gotchas: keyframe cuts](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#keyframe-cuts)).
- **Cut by words or by a transcript time** (`transcription-skill`): show a table of requested vs
  actual in/out per cut, and offer review clips from 1 s before to 1 s after each in and out point
  so the user can hear that the first and last words are whole.

## 6. The review list

End every job with a review list in two parts. Nothing moves from the second part to the first
because it "should be fine".

**Machine-checked** (a tool measured it; quote the field): output exists and decodes at its ends,
stream inventory vs input, durations and lengths that a tool compared, loudness when measured,
platform format rows from `check` / `qc-skill`, the step-4 comparison items that match.

**A person must look or listen here** (list each with a time code or a clip):

- **A/V sync**: spot checks at the start, the middle and the end. No tool verifies lip sync in
  general ([gotchas: sync, multicam and drift](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#sync-multicam-and-drift)).
- **Subtitle vs speech timing** (`subtitle-skill`): nothing checks that a cue starts with its line.
  After silence removal the timing shifts: subtitles made from the source must go through the
  silence step's timemap (source time to output time) before they are burned or delivered; check a
  few cues after long removed spans.
- **Consonant clipping at silence cuts** (`audio-production-skill`): list every cut from
  `cut_points`, put the ones in `cut_warnings` first, and offer a short clip around each
  ([design decisions: silence.py says where it cut](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/design-decisions.md)).
  What was removed is not verified.
- **Framing after a 9:16 crop**: the default crop is the centre and nothing tracks a subject. Pick
  the offset from a contact sheet (ffmpeg-skill `look.py`) or from `detection-skill`, and have the
  user check the sheet of the result
  ([gotchas: reframing](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#reframing-fps-and-duration)).
- **Burned-in subtitles in the source**: they cannot be removed (blur or delogo is not inpainting).
  Offer the options: crop the band, cover it with a box, or get a clean master
  ([ffmpeg-skill FAQ](https://github.com/kajisho5/ffmpeg-skill#can-it-remove-burned-in-subtitles-or-logos)).
- **Caption and transcript text**: no tool checks that the words are right. Speech-to-text is
  evidence with errors (names, numbers, terms, homophones), so a person reads the caption text
  before it is burned or delivered. The before-export list: [stages.md](stages.md).
- Anything in `notes`, every `unverified` item, and every step that ran outside the OS (level 2 or 3
  in [SKILL.md](SKILL.md)).
