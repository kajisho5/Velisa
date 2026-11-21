# ADR-027: One Error Taxonomy Above Every Skill's Own Codes, Checked and Reported Only

Status: Accepted (decision D41)

## Context

Read from each Skill's `contract/contract.json` on `origin/main`, 2026-11-20 (the versions are listed in
[error-taxonomy-map.md](../specs/error-taxonomy-map.md)), and from video-production-agent `921fac5`:

- **Codes.** 23 contracts declare 113 distinct error codes and 9 lower-case failure kinds in five shapes:
  a `codes` list with a `retryable` map (the audio-production family, video-editing), with a `non_retryable` list
  (subtitle), or with a `classes` map of FATAL / RETRYABLE / BLOCKED (media-analysis); a map of code to
  `{exit_code, retryable}` (detection, diarization, dubbing, ingest, nle-bridge, publish, slide-sync, sound-design,
  voice-enhance); `kinds` that name codes (hyperframes); kinds with exit codes (blender, remotion-ffmpeg); and code
  lists per tool (artifacts). imagemagick-skill and transcription-skill declare no code in their contract, and
  ffmpeg-skill has no contract file (its kinds are `input`, `ffmpeg`, `missing_tool`, `output`, `timeout`,
  `interrupted`, `verification`).
- **The same meaning, many names**: the input is missing is `MISSING_INPUT`, `INPUT_NOT_FOUND`, `FILE_NOT_FOUND`,
  `SOURCE_NOT_FOUND`, `ARTIFACT_INPUT_NOT_FOUND`; an engine is not installed is `DEPENDENCY_ERROR`,
  `DEPENDENCY_MISSING`, `ENGINE_UNAVAILABLE`, `ENGINE_NOT_FOUND`, `ENGINE_TOOL_MISSING`, `FFMPEG_SKILL_NOT_FOUND`,
  `FFMPEG_SKILL_UNAVAILABLE`, `FFMPEG_NOT_FOUND`, `ANALYZER_UNAVAILABLE`, `kind: missing_tool`.
- **Retry verdicts that disagree.** `CANCELLED` is retryable in nine contracts (audio-production, color-grading,
  dubbing, motion-graphics, publish, sound-design, thumbnail, video-editing, voice-enhance) and not retryable in
  subtitle-skill. subtitle-skill's `non_retryable` list leaves out `DEPENDENCY_ERROR`, `INTERNAL_ERROR` and
  `OUTPUT_ERROR`, so they read as retryable. Exit codes for the same code differ between families (`CANCELLED` is 13,
  15, 6 or 130).
- **The agent** maps each code to a recovery class in a table per adapter (`RECOVERY_CLASS` in
  `tools/skill_process.py`, `ERROR_CLASSES` / `ERROR_CODES` / `ERROR_KINDS` in 15 adapters) and acts on it in
  `execution/recovery.py`. The tables disagree with each other and with the codes' meaning in these places:

  | Agent table | Code | Agent class | Taxonomy class | What differs |
  |---|---|---|---|---|
  | ingest | `FETCH_FAILED`, `INCOMPLETE`, `SOURCE_CHANGED`, `VERIFY_MISMATCH`, `FILE_MISSING` | `SKILL_ERROR` (BLOCK) | `TRANSIENT` | the action: ingest-skill calls them retryable, the agent never retries |
  | publish | `UPLOAD_INTERRUPTED` | `SKILL_ERROR` (BLOCK) | `TRANSIENT` | the action |
  | ingest | `MANIFEST_NOT_FOUND` | `SKILL_ERROR` | `INPUT_NOT_FOUND` | the hint |
  | skill_process, video_editing, audio_production | `INVALID_INPUT` | `INPUT_MISSING` ("input file disappeared") | `INVALID_INPUT` | the hint |
  | skill_process, video_editing, audio_production | `DEPENDENCY_ERROR` | `INVALID_ARGS` ("agent bug") | `DEPENDENCY_MISSING` | the hint |
  | skill_process, video_editing, audio_production, dubbing, voice_enhance | `CANCELLED` | `TIMEOUT` | `CANCELLED` | the class; `recovery.py` turns it into `INTERRUPTED` unless `details.reason` is `timeout` |
  | publish, sound_design | `CANCELLED` | `INTERRUPTED` | `CANCELLED` | none (listed to show the other tables differ) |
  | hyperframes | kind `interrupted` | `SKILL_ERROR` | `CANCELLED` | the hint |
  | sound_design | `NOT_IMPLEMENTED` | `TOOL_MISSING` | `UNSUPPORTED` | the hint (voice_enhance and dubbing map it to `SKILL_ERROR`) |
  | sound_design, publish | `CONFIRMATION_REQUIRED`, `LICENCE_REQUIRED`, `CONFIRM_MISMATCH` | `INVALID_ARGS` | `ACTION_REQUIRED` | the hint |
  | publish | `CREDENTIALS_MISSING`, `AUTH_FAILED` | `TOOL_MISSING` | `ACTION_REQUIRED` | the hint |
  | sound_design | `TOOL_ERROR` | `SKILL_ERROR` | `ENGINE_FAILED` | the action (every other table: `UNKNOWN`, retried once) |

## Decision

1. The spec is [docs/specs/error-taxonomy.md](../specs/error-taxonomy.md) (`velisa/error-taxonomy@1`), with its data in
   [error-taxonomy.json](../specs/error-taxonomy.json): 15 classes, each with its meaning, a retry policy (never,
   after_change, later, once, once_longer) and how its message to a person is written. Every one of the 113 codes
   and 14 kinds (the 9 declared, plus ffmpeg-skill's `ffmpeg` and `output` and artifacts-skill's exit categories
   `capability`, `execution`, `security`) is in one class.
2. **Skills keep their codes and exit codes.** Nothing is renamed. A Skill may add `error.class` beside its code;
   that is additive. The classes are for callers: what to retry, what to tell a person.
3. **The stricter verdict wins.** A caller retries only when the class allows it and the Skill does not say
   `retryable: false`. `CANCELLED` is never retried by a caller: a person stopped the run.
4. **The check is `scripts/error_taxonomy.py`**, in this repository for the reason ADR-026 gives for
   `timebase.py`: the classes are this ecosystem's, not a general System Intelligence concern, and `si` has no
   knowledge of Skill error codes to build on. It reads all five contract shapes and reports unknown codes,
   contracts with no code, and retryable verdicts the class does not share. It exits 0; `--strict` exits 1 on an
   unknown code. `.github/workflows/error-taxonomy.yml` runs it weekly and when the taxonomy changes, on the
   contracts the agent pins, and writes the job summary. It fails nothing.
5. Report only for now: no Skill is changed and no Skill gets an issue for its codes. The agent gets one issue
   for the table above ([video-production-agent#168](https://github.com/kajisho5/video-production-agent/issues/168)).

## Results (2026-11-20)

- Skills' own contracts (`origin/main`), 23 read: no unknown code. No code: imagemagick-skill, transcription-skill.
  Retryable where the class is not: `CANCELLED` in the nine contracts above; `DEPENDENCY_ERROR`, `INTERNAL_ERROR`,
  `OUTPUT_ERROR` in subtitle-skill.
- The agent's 21 pinned contracts: the same, minus the versions not yet re-pinned.

## Consequences

- A new code shows up in the weekly summary until it is added to `error-taxonomy.json`; adding it is one line.
- When the agent moves to the classes, its per-adapter tables can shrink to the overrides; that is its decision.
- Making the check fail a build is a later decision, once imagemagick-skill and transcription-skill declare codes.
