# Error taxonomy: one set of classes for every Skill's error codes

**Status: SPEC, report only** (decision [D41](../ecosystem/DECISION_LOG.md), [ADR-027](../adr/ADR-027-error-taxonomy.md)).
Spec id `velisa/error-taxonomy@1`. Skills keep their own error codes. This spec puts each code in one shared
class, says whether a caller may retry it, and how its message to a person is written.

- Machine-readable: [`error-taxonomy.json`](error-taxonomy.json) (`classes`, `retry_policies`, `codes`, `kinds`, `overrides`).
- Every code each Skill declares today, with its class: [`error-taxonomy-map.md`](error-taxonomy-map.md).
- Check: `python3 scripts/error_taxonomy.py --contracts <dir>` (or `--checkouts <dir>`, or contract files) lists
  codes the taxonomy does not know, contracts that declare no code, and codes a Skill calls retryable that its class
  does not retry. It exits 0; `--strict` exits 1 on an unknown code. `.github/workflows/error-taxonomy.yml` runs it
  weekly on the contracts video-production-agent pins, and reports only.

## Classes

| Class | Meaning | Retry | Message to a person |
|---|---|---|---|
| `INVALID_REQUEST` | The request breaks the contract: a missing or wrong argument, a bad time range, a path outside the allowed roots, an output that would overwrite an input or already exists. | never | Name the argument and what is wrong. When the agent built the request, say it is the agent's fault; do not ask the person to fix arguments they never typed. |
| `INPUT_NOT_FOUND` | A file, folder, manifest or cache entry the request names does not exist. | after_change | Name the missing file by its path. |
| `INVALID_INPUT` | The input exists but cannot be used: corrupt, wrong type, unreadable, encrypted, or a document that fails its schema. | never | Name the file and the reason (`details.reason`), and what would make it usable. |
| `UNSUPPORTED` | The Skill does not offer this operation, format, platform or combination, or the target format cannot carry the content. | never | Say what is not supported and the alternative when the error names one. Never present it as a fault of the person's file. |
| `DEPENDENCY_MISSING` | A tool, engine, model, language pack, credential store or sibling Skill is not installed or cannot be reached. | after_change | Name what is missing and how to install or enable it (the Skill's `doctor`). |
| `ACTION_REQUIRED` | A person must act first: consent, confirmation, a licence or terms, signing in. | after_change | Say exactly what the person must provide. The agent never makes, signs or guesses it. |
| `RESOURCE_LIMIT` | GPU memory, disk space, a page or size limit, an analysis budget is too small. | after_change | Name the limit, what is needed and what is available, and what to change. |
| `RATE_LIMITED` | A remote service refused for now (an API quota, an upload limit). Nothing was done. | later | Say nothing was uploaded or changed, which limit was hit and when it resets. |
| `TRANSIENT` | A temporary fault the same request can get past: a fetch, an interrupted upload, a source that changed while it was copied, a copy that did not verify. | once | Say it is being retried; if the retry fails, show the error. |
| `TIMEOUT` | The operation ran out of time and was stopped. | once_longer | Say it took too long and is retried with more time. |
| `CANCELLED` | A person or the system stopped the run. Not a timeout. | never | Say the run was stopped; the person re-runs it. |
| `ENGINE_FAILED` | The engine (FFmpeg, a model, a renderer, a remote service) ran and failed, or refused the content. | once | The engine's message, shortened, and the step. |
| `OUTPUT_FAILED` | The result could not be written or delivered whole. | never | Where the output was to go and what is left there. |
| `VERIFICATION_FAILED` | The Skill's own check of its result failed, or the result breaks its schema or promise. | never | What was checked and what was measured; never call the result delivered. |
| `INTERNAL` | A bug in the Skill. | never | Say it is a fault in the Skill (name, version, code), so it can be reported. |

Retry policies:

- **never**: the same request fails the same way.
- **after_change**: retry only after what the error names has changed (installed, freed, supplied).
- **later**: not in this run; after the wait the error states, or the next day.
- **once**: at most once with the same arguments, and only when the Skill's own `retryable` is true.
- **once_longer**: at most once with a longer time limit.

## Rules

1. **The Skill's verdict wins when it is the stricter one.** A caller retries only when the class allows it *and*
   the Skill does not say `retryable: false`. A Skill that says `retryable: true` for a class that is not retried
   (for example `CANCELLED`) is listed by the check; the class decides.
2. **Every declared code maps to one class.** A new code is added to `codes` in `error-taxonomy.json` in the same
   change that adds it to a contract; until then the check lists it as unknown. A code that means something else in
   one Skill goes under `overrides.<skill_id>`.
3. **The failure document keeps its shape.** `{ok: false, error: {code, message, retryable, details}}` with the
   Skill's own code. Nothing in this spec renames a code or changes an exit code. A Skill may add
   `error.class` with its class name; that is additive.
4. **Messages.** `message` is one or two sentences a person can act on: what failed, on which file or argument, and
   what to do. Paths are shown as the person gave them. No stack traces, no secrets, no raw command lines; those go
   in `details` or a log.
5. **Kinds.** The ffmpeg-skill family reports a lower-case `kind` (`input`, `missing_tool`, `timeout`, ...). Each
   kind has a class in `kinds`. `input` covers both a bad request and a bad input, so it is `INVALID_REQUEST`;
   `error.reason` tells them apart.

## How the agent's recovery classes line up

video-production-agent reads each Skill's code into its own recovery class (`RECOVERY_TABLE` in
`execution/recovery.py`; `RECOVERY_CLASS` in `tools/skill_process.py` and one table per adapter). The classes that
match:

| Class | Agent recovery class (action) |
|---|---|
| `INVALID_REQUEST` | `INVALID_ARGS` (BLOCK) |
| `INPUT_NOT_FOUND` | `INPUT_MISSING` (BLOCK) |
| `INVALID_INPUT` | `UNSUPPORTED_MEDIA` (BLOCK), or `INVALID_ARGS` for a document the agent passed between Skills |
| `UNSUPPORTED` | `UNSUPPORTED_MEDIA` or `INVALID_ARGS` (BLOCK) |
| `DEPENDENCY_MISSING` | `TOOL_MISSING` (BLOCK) |
| `ACTION_REQUIRED` | `CONSENT_REQUIRED` or a class of its own (BLOCK) |
| `RESOURCE_LIMIT` | `INSUFFICIENT_VRAM`, `DISK_FULL` (BLOCK) |
| `RATE_LIMITED`, `OUTPUT_FAILED`, `VERIFICATION_FAILED`, `INTERNAL` | `SKILL_ERROR` (BLOCK) |
| `TRANSIENT` | `UNKNOWN` (RETRY_SAME, once) |
| `TIMEOUT` | `TIMEOUT` (RETRY_LONGER) |
| `CANCELLED` | `INTERRUPTED` (BLOCK) |
| `ENGINE_FAILED` | `UNKNOWN` when the Skill says retryable, else `SKILL_ERROR` |

Where the agent's tables differ today is listed in ADR-027.
