# `title.json` and `stinger.json`: metadata beside a title or stinger file

**Status: SPEC, shape of what the receivers already read** (owner decision 2026-11-12,
[DECISION_LOG](../ecosystem/DECISION_LOG.md) D15). Fields marked **(PROPOSED)** are not read by
any receiver today; they are a suggestion for the maker (hyperframes-skill roadmap steps 8 and 15)
and change nothing until a receiver reads them.

A title or stinger file is made by `hyperframes-skill` (or `remotion-ffmpeg-skill` /
`blender-skill`) and used by four receivers: `video-editing-skill` (stinger transition),
`motion-graphics-skill` (`rendered_layer`), `qc-skill` (stinger cut-point check) and
`video-production-agent` (plans both). The metadata file sits next to the media file with the
same stem: `bumper.mov` → `bumper.stinger.json`, `lower-third.mov` → `lower-third.title.json`
**(PROPOSED naming)**.

**No receiver opens the sidecar.** Each one takes the values as request fields, and the caller
(the agent, or a person) reads the file and passes them on (video-editing-skill ADR-023,
qc-skill `docs/checks.md` "Opt-in stinger cut point"). This spec is therefore the contract between
the maker and that caller.

Read from (each repository's `origin/main`, 2026-11-12): video-editing-skill `078c279`
(`src/video_editing_skill/contract.py`, `docs/decisions.md` ADR-023 / ADR-032), qc-skill `b7475e9`
(`docs/checks.md`, `src/qc_skill/contract.py`, ADR-024), motion-graphics-skill `8e3fcb6`
(`src/motion_graphics/model.py` `rendered_layer`, ADR-25), video-production-agent `b2d4e08`
(`src/video_agent/agent/editing.py`, `finishing.py`, `qc_checks.py`, ADR-099 / ADR-102 / ADR-112),
hyperframes-skill `3528095` (`SKILL.md`, `docs/contract.md`, `ECOSYSTEM_ROADMAP.md` step 15).

## Times

Seconds on the file's own timeline, from its first frame. A time that names a frame must be on
one: `t * frame_rate` within 1/1000 of a whole frame (qc-skill; video-editing-skill refuses it as
`cut_point_not_on_frame`). The frame at `t` is `round(t * frame_rate)` with the exact rate from
ffprobe's `r_frame_rate`.

**Precision.** The 1/1000-of-a-frame rule needs more than millisecond precision: at 24 fps, frame
25 is 1.041666... s, and 1.042 s is 25.008 frames, which video-editing-skill refuses
(`cut_point_not_on_frame`) and qc-skill reports UNKNOWN. A maker writes `cut_point` and `cover`
with at least 6 decimals (or as `frame / frame_rate` exactly), and a caller passes them on
unrounded. Known gap: video-production-agent stores `edit.concat.stinger.cut_point` rounded to 3
decimals (`editing.py`), so a cut point that is not on a whole millisecond can be refused; that
is a follow-up in the agent. Carrying `cut_point_frame` and `frame_rate` **(PROPOSED, below)**
lets a caller recompute the exact time.

## `stinger.json`

A stinger is a graphic with alpha that covers the whole picture for a moment; the edit cuts
underneath it at the cut point.

| Field | Type | Read by | Meaning |
|---|---|---|---|
| `cut_point` | seconds | video-editing-skill (required), qc-skill (required), agent (required, 0-60, stored rounded to 3 decimals: see Precision) | the frame the clips switch at; the stinger starts `cut_point` before each join |
| `cover` | `{start, end}` seconds | video-editing-skill (required), qc-skill (optional), agent (required; also accepts `"S-E"`) | the window the maker states is fully covered: frames at `start <= t < end`; must contain `cut_point` |

How each receiver takes them:

| Receiver | Request field | Checks |
|---|---|---|
| video-editing-skill | CONCAT `params.transition: {type: stinger, stinger: <source id>, cut_point, cover: {start, end}}` | refused without `cut_point` (`stinger_no_cut_point`) or `cover` (`stinger_no_cover`), `cut_point` outside `cover` (`stinger_not_covering`), not on a frame (`cut_point_not_on_frame`); the frame at `cut_point` is measured opaque in every pixel before anything runs (ffmpeg-skill `look`, ADR-032); the file must have an alpha plane (`stinger_no_alpha`) |
| qc-skill | `rules.video.stinger: {cut_point, cover?, file?, cut_at?, max_cut_frame_difference?}` | `video.stinger_cut_point_in_cover`, `video.stinger_opaque_at_cut_point` (alpha >= 253/255 in every pixel), `video.stinger_cut_frame_matches` |
| video-production-agent | `edit.concat.stinger=<file>`, `edit.concat.stinger.cut_point`, `edit.concat.stinger.cover` | `cut_point` inside `cover`; with `qc.stinger=true` it passes the concat's own `cut_point` / `cover` to qc-skill (`qc_stinger@1`) |

Not from the sidecar: the stinger's length is the file's (probed), and `cut_at` (one per join,
on the delivered video) comes from video-editing-skill's report `stinger.joins[].cut_at`.

**(PROPOSED)**, from hyperframes-skill step 15 ("cut point in frames and seconds, the fully covered
window, alpha mode") and nothing that reads them yet:

| Field | Type | Meaning |
|---|---|---|
| `schema` | `"velisa/stinger@1"` | the shape's id |
| `file` | file name | the media file this describes, relative to the sidecar |
| `sha256` | hex | the media file's content, so a stale sidecar is detected |
| `frame_rate` | `"num/den"` | the rate the frame numbers below use |
| `cut_point_frame` | integer | `round(cut_point * frame_rate)` |
| `cover_frames` | `{start, end}` integers | the cover window in frames |
| `alpha` | `"straight"` \| `"premultiplied"` | the alpha mode; hyperframes-skill writes `straight` for every alpha output today |
| `duration`, `frames` | seconds, integer | as probed |
| `audio` | boolean | whether the stinger carries sound (video-editing-skill mixes it in) |

## `title.json`

A title (lower third, session title, strap) made as one clip with IN / LOOP / OUT segments, so an
edit can hold it for any length.

| Field | Type | Read by | Meaning |
|---|---|---|---|
| `segments` | `{in, loop, out}` seconds, whole frames, adding up to the clip's duration; `in` / `out` may be 0 | hyperframes-skill (`scene` request and `render --segments` result) | where the clip's IN, LOOP and OUT parts are |

motion-graphics-skill's `rendered_layer` and the agent's `motion.layer` take the same facts as
element parameters, so the caller maps them:

| `title.json` | `rendered_layer` parameter (agent key) | Notes |
|---|---|---|
| the full clip (`render -o`) | `video_path` (`motion.layer`) | must decode with alpha (yuva / rgba: ProRes 4444, QuickTime Animation, PNG in MOV); a VP9 alpha WebM is refused |
| `segments.in` | `in_duration` (`motion.layer.in_duration`), 0-60 s | plays at the element's start |
| `segments.out` | `out_duration` (`motion.layer.out_duration`), 0-60 s | ends at the element's end |
| `segments.loop > 0` | `loop: true` (`motion.layer.loop`) | the part between IN and OUT repeats to fill the window; `false` plays it once and cuts |

hyperframes-skill's `render --segments` also writes each segment as its own file
(`<stem>.in<ext>`, `<stem>.loop<ext>`, `<stem>.out<ext>`) and measures the loop seam (`loop_seam`).
`rendered_layer` reads the full clip, not the pieces.

**(PROPOSED)**, from the 2026-11-05 draft (`motion-titles/title@1`), read by no receiver yet:

| Field | Type | Meaning |
|---|---|---|
| `schema` | `"velisa/title@1"` | the shape's id |
| `file`, `sha256`, `frame_rate`, `alpha` | as in `stinger.json` | |
| `segment_frames` | `{in, loop, out}` integers | the segments in frames, as hyperframes-skill's result already reports (`segments[].frames`) |
| `loop_seam` | object | hyperframes-skill's measurement of the loop file, copied |
| `safe_area` | `{x, y, width, height}` pixels | the box the text was kept inside |
| `text` | `[{role, text, lang, font, font_size}]` | the text as drawn and the font size used after fitting |

A video loop-seam check, an alpha-edge check and a key / fill pair check are not in qc-skill yet;
qc-skill's `loop_seam` rule today is for audio (`AudioRule.loop_seam`).
