# ADR-033: Batch Selects: Facts from the Measuring Skills, the Choice in the Agent, a Yes Before the Render

Status: Accepted (decision D48)

## Context

A person drops 1 to 50 clips from a shoot and asks for the usable shots. For each clip and each shot the system
should flag the picture (blurred or soft focus, under- or over-exposed, black or frozen frames), the camera (shaky or
steady), the sound (silence, no speech) and where the shots change. It then builds a "selects" sequence of the usable
shots, in source order unless asked otherwise, and says for each shot why it was kept or left out. Nothing is rendered
before the person says yes.

What already exists, read on `origin/main` on 2026-11-20:

- **media-analysis-skill 0.1.23** measures, never judges (its ADR-001). `scene_detection` (ffmpeg `scdet`) gives the
  cuts and the scenes between them. `silence` (`silencedetect`) gives the silent spans. `speech_regions` (a voice-activity
  model, optional extra `vad`, `UNKNOWN` without it) gives the speech. Nothing measures sharpness, exposure or camera
  motion.
- **qc-skill 1.4.5** `inspect` on a video measures `video.black_segments` (`blackdetect`) and `video.freeze_segments`
  (`freezedetect`) whatever the rules, with its own sensitivity parameters. It checks deliverables against a caller's
  rules (ADR-007) and has no per-window picture measurements.
- **detection-skill** has a model-based shot table (`shots@1`). Face sharpness is measured only inside face boxes.
- **video-editing-skill 0.9.0** cuts and joins (`TRIM`, `CONDENSE`, `CONCAT`). It has no measurement of picture quality.
- **video-production-agent** scores takes of the same line from measured facts and assembles the picks
  (`agent/takes.py`, its ADR-053). It records sharpness, exposure and faces as `unmeasured` because no Skill measures
  them. Its plan joins each source once: a source is trimmed to its kept ranges, and the trimmed sources are joined in
  input order by `video.concat`.

## Decision

1. **Each measurement has one owner. Nothing is measured twice.**

   | Flag | Owner | Kind / measurement |
   |---|---|---|
   | Shot boundaries | media-analysis-skill | `scene_detection` (existing) |
   | Black frames, frozen frames | qc-skill | `inspect` → `video.black_segments`, `video.freeze_segments` (existing) |
   | Silence | media-analysis-skill | `silence` (existing) |
   | No speech | media-analysis-skill | `speech_regions` (existing; `UNKNOWN` without the `vad` extra) |
   | Blur / soft focus, exposure, shake | media-analysis-skill | **new** `picture_quality` |

   detection-skill's model-based shot table stays an option for later. `scdet` needs no model and is already pinned
   by the agent.

2. **media-analysis-skill adds one measurement**, kind `picture_quality` (tool `media-analysis/picture`, capability
   `measure.video.picture_quality`). It reports facts per window of `window` seconds (default 1.0) and states no
   threshold:
   - **sharpness**: the median of ffmpeg `blurdetect` on frames scaled to `width` pixels (default 640). Higher is
     blurrier. A frame with no edges, such as a black frame, gives no value (`null`), never 0.
   - **exposure**: the mean luma and its 10th and 90th percentiles from ffmpeg `signalstats` (`YAVG`, `YLOW`, `YHIGH`, 8-bit).
   - **camera motion**: the global shift between successive frames sampled at `motion_rate` (default 10 per second),
     scaled to `motion_width` (default 160). Each frame is split into 4 × 3 blocks. The horizontal and vertical
     projection profiles of each block are matched within ±12 % of the width, refined to a sub-pixel shift, and the
     median over the blocks with texture is taken, so a subject moving through part of the frame does not count as
     camera motion. The camera path is the running sum of the shifts. **Jitter** is the RMS distance between that path
     and its centred moving average over `smooth` seconds (default 0.5), in percent of the frame width: shake rather
     than a pan. **Speed** is the mean shift in percent of the width per second.

   Standard library and ffmpeg only. The contract change is additive: one tool, one kind, one `provides` entry and its
   parameters. It ships as a minor release.

3. **The choice is the agent's, by a rule it names** (`selects@1`), the way it chooses takes. Per shot, a shot being a
   scene of `scene_detection`, it reads the facts above in the shot's span and records each flag with the values and
   the observation ids behind it.
   - **Reject**, each with its own reason:
     - black or frozen frames over at least half of the shot;
     - soft (the shot's median blur at least 1.3 × the batch's reference, the 25th percentile of the shots' medians,
       or over an absolute `max_blur` when one is given);
     - under-exposed (mean luma below 40) or over-exposed (mean luma above 210);
     - shaky (median jitter above 1.0 % of the width);
     - shorter than `min_shot` (1.0 s).
   - **Flag only**:
     - **dead air**: silent over at least 90 % of the shot, or no speech when speech was measured. Silent B-roll is
       usable, so dead air rejects only when `reject_dead_air` is set;
     - black, frozen or shaky parts below the reject share.
   - **Score**: 100 minus a penalty per flag, so usable shots can be ranked.
   - **Selection**: the usable shots in source order (input order, then time). `min_score` rejects shots below a score.
     `max_duration` keeps the best-scored usable shots that fit the cap, then puts them back in source order. A shot
     left out by the cap is reported as such.

   The relative blur reference is chosen because `blurdetect` depends on the content (a sharp fractal reads higher than
   a blurred test card). The numbers are defaults chosen here, not taken from a standard. Every one of them is an option
   and is written into the selects file.

4. **The agent asks first.** `video-agent selects <folder | clips>` and the MCP tool `selects` measure, apply
   `selects@1` and write `video-agent/selects@1`. That file holds each clip's sha256, the options, every shot with its
   flags, score, kept or rejected, and the reasons. They print the list and the total duration. Nothing is rendered.
   `--set edit.selects=<file>` on `plan` (a path key, never from a brief) makes one `selects.keep` decision per clip
   with kept shots, with a CONFIRM floor, and a `video.concat` of those clips in source order that cites them. The
   render reuses the existing assembly path: each clip is trimmed frame-accurately to its kept shots, and the clips
   are joined by `video.concat`. Clips with no kept shot are not used. A clip that changed since the preview refuses
   the file.

5. **Order by score is not rendered here.** The plan joins each source once, so shots of different clips cannot be
   interleaved without a new assembly path. The preview can list the shots by score. The rendered sequence stays in
   source order, and the file says so.

## Consequences

- media-analysis-skill: one additive kind and a minor release. The agent's pin moves only through its repin workflow,
  which widens the version gate for a new minor with an additive diff.
- qc-skill, video-editing-skill and detection-skill do not change.
- The agent's take selection can later score sharpness, exposure and shake from the same `picture_quality`
  observation. Until it does, they stay `unmeasured` there.
- A batch shot entirely on soft focus has no sharp reference, so the relative blur rule flags nothing. `max_blur`
  is the way to say what soft means for that batch.
