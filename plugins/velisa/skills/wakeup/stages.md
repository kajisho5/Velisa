# Stage order, the before-export list, and what a check does not accept

A set of tools is not a production. This page gives the default order of the editorial stages,
the list to go through before the final export, and the line between what a tool checked and what
only a person can accept. Who does each stage comes from the "Who owns what" table in
[SKILL.md](SKILL.md). The steps for running any one write (probe, plan, trial, compare, review
list) are in [review.md](review.md).

## 1. The default order

A plan is not a fixed pipeline: skip a stage the job does not need, and change the order when the
job calls for it. But each stage below changes something the later ones are built on, so a plan
that departs from this order says which line it breaks and why that is safe here.

| # | Stage | What it settles | Why it comes before the next |
|---|---|---|---|
| 1 | Ingest and probe | The inputs and their numbers ([review.md](review.md) step 1) | Everything is planned from the numbers |
| 2 | Transcript, when speech matters | Words and their times on the source | Selects and captions are read from it |
| 3 | Rough cut | What stays and in what order: selects, retakes ([transcript.md](transcript.md)), then pause removal | Every later time is counted on the cut, not on the source |
| 4 | Picture | Colour, reframe, stabilising | Captions and graphics are sized and placed for the final frame |
| 5 | Captions | Text and timing, moved through the cut's time map | Graphics must not sit on them |
| 6 | Graphics and motion | Titles, overlays, B-roll | The mix needs the final picture length |
| 7 | Sound | Mix, music, then loudness last | Loudness is measured on the finished mix |
| 8 | Export, then check | The file for its destination | The check reads the file that will be delivered |

Order rules that are broken most often:

- **Captions made before the cut is final are on the wrong clock.** Make them from the source and
  move them through the time map, or make them from the cut. Check a few cues after long removed
  spans.
- **A reframe after text is burned in can crop the text.** Reframe first.
- **Loudness before the music goes in measures another mix.** Normalise last.
- **Never export "final" to find out what is wrong.** A trial export is fine: name it a trial.

## 2. Before a transcript or captions: is a speech engine installed?

Speech-to-text is a separate install; the engine and the editing tools do not bring one. Before
planning a stage that needs it, ask the owner what is there (`transcription-skill`, or
ffmpeg-skill `doctor`, which lists a missing speech engine as optional and missing). When none is
installed, say so, give the install line the tool prints, and offer the other routes: a transcript
or subtitle file the user already has, cues typed by hand, or the job without captions. Never
write dialogue that was not transcribed or given.

## 3. The before-export list

Go through this list after the last edit and before the final export. Answer each line **yes**,
**no** or **unknown**, with the field or the file that shows it. A **no** is fixed first. An
**unknown** is not a yes: it goes to the person's part of the review list.

| Line | Shown by |
|---|---|
| The cut is approved: the user saw the cut list (and the pause list, when pauses were removed) | The approval in the conversation |
| Length matches the request, or the difference is stated | Probe of the cut against the request |
| Frame matches the destination: aspect, resolution, frame rate | Probe; the platform rows of the check |
| After a reframe: a sheet of the result was looked at over its whole length | The sheet's path |
| Caption text was read by a person: names, numbers, terms, homophones | Who read it, or **unknown** |
| Caption timing spot-checked at the start, the middle, the end and after long removed spans | The cues checked |
| Captions and graphics sit clear of each other and of the platform's own buttons | A frame with the safe areas shaded |
| Spelling in titles and graphics was read | Who read it, or **unknown** |
| Loudness is at the destination's target, measured on the finished mix | The measured value |
| Nothing is left from a trial: excerpt lengths, placeholder fills, test text | The plan |
| Every item still open is written down for the review list | The list |

Then export, run the destination's format check on the exported file, and end with the two-part
review list ([review.md](review.md) step 6).

## 4. What a check accepts, and what it does not

"Verified" and "passed" are statements about a file's measured properties. They are not an
acceptance of the finished piece. Say which one is meant every time the word is used.

| Says | Means | Does not mean |
|---|---|---|
| A tool's `verified: true` | The checks listed in `verification` passed on the file it wrote | The output matches the request, or looks and sounds right |
| A tool's `unverified` list | Properties nothing measured (framing, placement, legibility, what a removed span held, mix balance, lip sync) | Passed |
| The format check (`check`, `qc-skill`) | The file meets the destination's technical rows | The content is right |
| ffmpeg-skill `verify.py` | The tools ran on the user's own source files, pass or fail per step | Anything about a finished edit |
| A transcript | What an engine heard | What was said: it is evidence, with errors |

Only a person accepts: the composition and whether the subject is in frame, what the captions
say and whether the transcript is right, whether a cut lands where the speech allows, how the mix
sounds, and whether the piece does its job. Each goes in the second part of the review list with
a time code, a sheet or a clip, never in the first.
