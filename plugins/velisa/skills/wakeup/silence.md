# Silence removal: list the cuts, get a yes, then cut

Removing pauses changes what is said and when. A threshold on the sound level does not know where
a sentence ends or what a breath is, so the cut list is shown to the user before anything is
written, and the cut runs only after a go-ahead. Steps 1 to 6 of [review.md](review.md) still
apply; this page is what a silence cut adds to them. The owner of the step is in the "Who owns
what" table in [SKILL.md](SKILL.md); the field and flag names below are ffmpeg-skill's
`silence.py`, the engine it runs on.

ffmpeg-skill references:
[`silence.py`](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/scripts.md),
[design decisions: silence.py says where it cut](https://github.com/kajisho5/ffmpeg-skill/blob/main/docs/design-decisions.md),
[FAQ: are silence removal and captions stable?](https://github.com/kajisho5/ffmpeg-skill#are-silence-removal-and-captions-stable).

## 1. List first; write nothing

Run the list, not the cut: `silence.py SRC --list --json` (add `--edl keep.txt` to save the kept
ranges and `--timemap map.json` when subtitles exist). It detects and measures on the real file
and writes no media. Read from the result:

- `silences` and `keep`: what would go and what would stay;
- `removed_seconds`, `kept_duration`, `input_duration`;
- `margins`: the air kept on each side of speech with the settings used;
- `cut_points`: the level just before and just after every cut;
- `cut_warnings`: the cuts that sit close to sound (a breath or a word's weak tail may be cut).

The threshold, the shortest gap removed and the margins are the tool's own defaults unless the
request set them: quote the values the result reports, do not restate them from memory.

## 2. Show the list before cutting

In one message:

- how many cuts, how many seconds go, the new length;
- the settings used (threshold, shortest gap, margins) in one line;
- a table of the removed spans (start, end, length). Put the `cut_warnings` cuts first. For a long
  list show those and the longest spans, and give the path of the saved list for the rest;
- what the list cannot tell: nothing has checked what was said in a removed span
  (`removed_span_content` is unverified), and a level is not a sentence end.

Offer to play the doubtful ones before deciding: a short clip of the source from 1 s before to 1 s
after each flagged cut (the cut owner, frame-accurate).

## 3. Tune before cutting, then list again

| What the user hears or fears | Change |
|---|---|
| Word endings or breaths clipped | more air: `--margin`, or `--margin-tail` for endings and `--margin-lead` for starts |
| Breaths inside a sentence go | `--speech-aware` (keeps short breaths inside a sentence, cuts at the longer pauses) |
| Sentence ends feel rushed | with a transcript (`--words`, or `--transcribe` when an engine is installed): `--sentence-min-silence`, `--sentence-margin-tail` |
| A quiet room: speech is taken for silence | a lower `--threshold` |
| The run is refused for too many cuts (`--max-cuts`) | the settings are catching speech: fix them; do not raise the limit to get past it |
| One span must stay | edit the saved list and cut from it (`cut.py --segments ... --accurate`), or leave that part out of the pass |

Run step 1 again after every change and show the difference in count and seconds.

## 4. Wait for the go-ahead

Cut only after the user says yes to the list, unless they asked up front for no review. Say so in
the report when the cut ran without one.

## 5. After the cut

- Compare as in [review.md](review.md) step 4: the output's length against the input minus
  `removed_seconds`.
- Subtitles made from the source go through the time map before they are burned or delivered.
- In the review list (step 6): every `cut_warnings` cut with its output time and a clip around it,
  the settings used, and `removed_span_content` as unknown.

## Not provided

| Asked for | Status |
|---|---|
| A preview player or a waveform with the cuts marked | Not provided. The list, the saved ranges and short clips around the cuts are the preview |
| Cuts that follow the meaning of what is said | Not provided. With a transcript the cut knows sentence ends from punctuation; it does not judge content. Removing retakes or a topic is an editorial decision: [transcript.md](transcript.md) |
