# ADR-032: Editing by Transcript: Word-Index Selections, Cut Edges in the Gaps, Frames by the Timebase

Status: Accepted (decision D47)

## Context

A person reading the transcript of a conference talk, an interview or a seminar picks sentences or words and says
"remove these" or "keep only these". The picture and the sound are then cut there and the gaps are closed (a ripple
delete). The parts exist in three repositories, read on `origin/main` on 2026-11-20:

- **transcription-skill 0.13.1.** Every word has `start`, `end`, `index` (0-based over the whole transcript, ADR-039
  there) and, after a speaker merge, `speaker_id`. A segment has a string `id` and is the unit a person reads as a
  sentence. `transcription/find` maps a phrase to its word indices and times. Nothing turns a selection into times.
- **video-editing-skill 0.8.8.** `CONDENSE` cuts labelled spans frame-accurately and joins the rest; `propose`
  returns cut candidates and applies nothing (ADR-024, ADR-026 there). Nothing retimes a transcript or subtitles
  through a cut. A new operation type would change the pinned `operations` block, a breaking change by its
  `docs/contract.md`.
- **video-production-agent.** `edit.word_cut` (ADR-109 there) lets the AI name word ranges and converts them with
  its own rule `word_ranges@1` (pre-roll 0.10 s, post-roll 0.20 s, clamped at the gap midpoint). Approved cut
  proposals reach `CONDENSE` through `edit.condense` (ADR-099 there). The MCP server runs CLI commands.

## Decision

1. **A selection is word indices, never times.** `{mode: remove | keep, words: [[first, last], ...], segments: [id, ...]}`:
   inclusive index ranges and whole segments (sentences), which may be mixed. Times are derived, so a person or an AI
   never types seconds and the same selection always gives the same cut. A segment with no word timings can be
   named only as a whole segment.
2. **transcription-skill says where the words are** (new tool `transcription/select`, rule `transcript-selection@1`).
   It returns, for each removed run of words, the words' extent and two **windows**: the in edge may go anywhere
   between the end of the kept speech before and the start of the first removed word, the out edge between the end
   of the last removed word and the start of the kept speech after (0 and the duration at the ends). Neighbours are
   found by time, not by index, so overlapping speakers are handled. It also returns the sentences touched, their
   speakers and the seconds of speech removed. It proposes no margin and cuts nothing.
3. **video-editing-skill says exactly where to cut** (new command `video-editing ripple`, rule `ripple@1`, an
   additive top-level `ripple` block like `proposals`; no new operation type, so the contract stays additive):
   - **Margins.** Each edge keeps 0.20 s after kept speech and 0.10 s before it (`ripple.margins`), never past the
     middle of its window, so a pause of at most 0.30 s is left where the gap closes.
   - **Silence.** When the source is given, the engine's measured silences (`ffmpeg-skill silence --list`, -40 dB,
     0.05 s) inside a window move the edge into the silence, the point nearest the margin target. No silence: the
     margin target stands.
   - **Frames.** Each edge is rounded to the nearest frame of the source's rate (velisa/timebase@1 TB-2, TB-4, a half
     up). If that frame leaves the window, the nearest frame inside it is taken; if the window holds no frame, the
     edge goes to the frame on the removed side (a sliver of a removed word may stay; a kept word is never cut). Output
     positions are counted in frames (TB-5).
   - **Result.** The cut list in frames, a JSON edit decision list (sidecar envelope, ADR-025), an `edit_request`
     with one `CONDENSE` for `video-editing run`, and, when given, the transcript and SRT / VTT subtitles retimed
     to the cut: removed words are dropped, a cue that loses part of its time is shortened, one that loses all of it
     is dropped. Nothing is applied by `ripple`; the media is cut by `run`.
4. **Several speakers.** A selection is about words, whoever said them. When a kept word of any speaker overlaps a
   removed span in time, `select` refuses (`INVALID_INPUT`, reason `selection_overlaps_kept_speech`, the words listed),
   because one mixed track cannot be cut for one speaker only; `overlap: include` removes those words too and lists
   them. Speakers are shown to the person beside each sentence.
5. **The agent asks first.** `video-agent transcript-edit` and the MCP tool `transcript_edit` run `select` and
   `ripple` and show which sentences go, by whom and for how many seconds. `--set edit.transcript_edit=<that file>`
   makes a `transcript.ripple` decision with a CONFIRM floor (the profile's semantic-deletion policy may raise it), cut
   by `CONDENSE`; after the render, `ripple` retimes the transcript and subtitles to the cuts the plan made.
6. **Errors** use each Skill's own codes, all already in error-taxonomy@1: `INVALID_INPUT` and `INVALID_REQUEST`
   (their own classes, never retried: the selection or the request must change), `TOOL_ERROR` (`ENGINE_FAILED`,
   retried once).

## Consequences

- Both Skill changes are additive (a new tool; a new top-level block and command). The agent re-pins through its
  repin workflow.
- The agent's `word_ranges@1` stays for AI-named word cuts; `ripple@1` is the rule for a person's selection. Moving
  `edit.word_cut` onto `ripple@1` is a later choice of the agent.
- Retiming is exact only on the source's own timeline. A plan that also changes speed or joins other sources says so
  in a warning beside the retimed files.
