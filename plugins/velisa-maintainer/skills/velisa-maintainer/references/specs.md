# Timebase and error taxonomy (Velisa ADR-026 / D40, ADR-027 / D41)

Both specs live in kajisho5/Velisa under `docs/specs/`. No Skill was changed when they were accepted; each non-conforming repository has an issue. Check a change against them; do not invent a third rule.

## Timebase (`velisa/timebase@1`, `docs/specs/timebase.md`)

| Rule | What it says |
|---|---|
| TB-1 | Rates and times are exact fractions. Two rates are the same only when their fractions are equal (no float comparison within 0.02 fps). |
| TB-2 | A decimal rate is read through one NTSC table: 23.976 / 23.98 → 24000/1001, 29.97 → 30000/1001, 59.94 → 60000/1001 (and 47.95, 119.88, 239.76). Never `Fraction(x).limit_denominator(...)` on a rounded decimal (that gives 2997/100). |
| TB-3 | On the wire a time is 6-decimal seconds or `N/D`; milliseconds are allowed up to 240 fps when read back with `nearest`. |
| TB-4 | Time to frames: a half rounds up (`floor(x + 1/2)`, JavaScript's `Math.round`), not Python's `round()` (half to even). `down` only for lengths joined at their own rate, keeping a frame within 1 ms. |
| TB-5 | Positions are counted in whole frames, never summed from values rounded one by one (the agent's concat landed a frame early per join until its ADR-115). |
| TB-6 | SMPTE timecode: NDF at every rate; drop-frame only at 30000/1001 and 60000/1001, written with `;`. A DF label that does not exist (`00:01:00;00` at 29.97) is refused. No wrap at 24 hours. |

Tools: `python3 scripts/timebase.py rate 29.97`, `tc 1800 30000/1001 --df`, `frames "00:01:00;02" 30000/1001`, and `vectors` (runs `docs/specs/timebase-vectors.json`, 134 vectors; the conformance contract). The module is standard-library only: a Skill may copy it or run the vectors against its own code. It stays in Velisa, not system-intelligence (which keeps video assumptions out of its core).

Known gaps when the spec was written: video-editing-skill and the agent read rates with `limit_denominator` and must change together; ingest-skill accepts DF labels that do not exist; hyperframes-skill renders integer rates only; nle-bridge, ffmpeg-skill's `timeline.py` and video-editing's `proposals.py` round half to even.

## Error taxonomy (`docs/specs/error-taxonomy.md`, `.json`)

Skills keep their own codes and exit codes. Every code and failure kind a contract declares maps to one of 15 classes; each class has a retry policy and a rule for the message to a person.

| Retry policy | Classes |
|---|---|
| `never` | INVALID_REQUEST, INVALID_INPUT, UNSUPPORTED, CANCELLED, OUTPUT_FAILED, VERIFICATION_FAILED, INTERNAL |
| `after_change` (a person or the environment must change something first) | INPUT_NOT_FOUND, DEPENDENCY_MISSING, ACTION_REQUIRED, RESOURCE_LIMIT |
| `later` (not in this run) | RATE_LIMITED |
| `once` (only if the Skill's own `retryable` is true) | TRANSIENT, ENGINE_FAILED |
| `once_longer` (once, with a doubled time limit) | TIMEOUT |

- A caller retries only when the class allows it and the Skill does not say `retryable: false`. A cancelled run is never retried; a cancel is not a timeout.
- A new code in a contract: add it to the map in `error-taxonomy.json` in the same change (or the weekly report lists it as unknown). Prefer an existing name with the same meaning over a new one.
- `python3 scripts/error_taxonomy.py --checkouts ..` (sibling checkouts) or `--contracts <agent>/src/video_agent/tools` lists unknown codes, contracts with no code and retry verdicts that differ; `--table` prints the per-code map, `--strict` makes unknown codes fail. `.github/workflows/error-taxonomy.yml` runs it weekly and fails nothing.
- The agent's per-adapter tables (`RECOVERY_CLASS`, `ERROR_CLASSES` ...) disagree with the taxonomy in places listed in ADR-027; the agent has one issue for them.
