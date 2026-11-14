# Reframing to another aspect: keep the subject in the frame

For a change of aspect (16:9 to 9:16, 1:1, 4:5). Nothing in the OS follows a subject yet: a crop
is one fixed window, and no tool checks that the person or product is inside it. So the choice of
window is an editorial decision made from frames, shown to the user, and checked on the result.
Steps 1 to 6 of [review.md](review.md) still apply; this page is what a reframe adds to them.

ffmpeg-skill references:
[gotchas: reframing](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/gotchas.md#reframing-fps-and-duration),
[`fit.py`, `crop.py`, `look.py`, `cropdetect.py`, `scenes.py`](https://github.com/kajisho5/ffmpeg-skill/blob/main/references/scripts.md).

## 1. Say what the tools do not do, before planning

Tell the user in the plan message:

- there is **no face or subject tracking** and no moving crop: each shot gets one window;
- a 16:9 to 9:16 crop keeps under a third of the width (about 32%), so a subject that walks across
  the frame leaves it;
- padding or a blurred fill (`fit.py --fit pad`, `--fit blur`) keeps the whole picture and is the
  safe choice when nobody has looked yet.

## 2. Look at the source first

- One contact sheet across the whole clip (ffmpeg-skill `look.py SRC --tiles 4x3`; more tiles for
  a long clip), and the shot list when there is more than one shot (`scenes.py`, `--shots` labels
  each shot static / pan / motion).
- For each shot, write down where the subject is at the first, a middle and the last tile, as a
  fraction of the width (0 = left edge, 0.5 = centre, 1 = right edge).
- `cropdetect.py --motion-centre` reports the motion centroid per second. It is a measured hint
  for where things move, not a subject detector: use it to choose which frames to look at, never
  as the answer. `detection-skill` gives boxes when it is installed.

## 3. Choose per shot

| What the frames show | Use |
|---|---|
| The subject stays inside one window for the whole shot | `fit.py --aspect 9:16 --fit crop --crop-x F` with `F` from step 2 (`--crop-y` for a vertical move) |
| The subject moves further than the window is wide | Do not crop that shot: `--fit blur` (or `--fit pad --pad-fill blur`), or split the shot where the subject crosses and give each part its own window |
| Two subjects that do not fit one window | `--fit blur` / pad, or ask which one the cut follows |
| Nobody has looked, or the sheet is unclear | `--fit pad`; say that it is the placeholder |

A rectangle that came from somewhere else (a detection box, a saved crop) goes to `crop.py`.

## 4. Show the choice

Add a table to the plan: shot, time range, method (crop / blur / pad), `--crop-x`, and the reason
in a few words ("speaker stands right of centre"). Wait for the go-ahead when any row was a guess.

## 5. Look at the result, over its whole length

- A contact sheet of the output that covers every shot: at least the first and the last frame of
  each shot and one tile between them (`look.py OUT --tiles ...`, `--at T` for single frames).
- `look.py OUT --safe <platform>` when captions or the platform's own buttons sit over the picture.
- In every tile, check that the head, the hands and whatever the shot is about are inside the
  frame. List each tile where something is cut, with its time code.

## 6. Report it as unknown, not as passed

A reframe result lists `subject_framing` in `unverified`. Keep it in the second part of the review
list ([review.md](review.md), step 6) with the sheet's path, the windows used and the time codes
that need a look. A sheet samples frames: between two tiles nobody has checked.

## Not provided

| Asked for | Status |
|---|---|
| The crop follows a face or a moving subject | Not provided. A subject path belongs to `detection-skill` and a moving crop to the engine; neither exists yet. Until then: one window per shot, as above |
| A check that the subject is inside the crop | Not provided by any tool. The sheet in step 5 and the user's look are the check |
