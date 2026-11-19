# Timebase: frame rates, times, frames and timecode

**Status: SPEC** (decision [D40](../ecosystem/DECISION_LOG.md), [ADR-026](../adr/ADR-026-timebase.md)). Spec id
`velisa/timebase@1`. It says how every Skill and the agent write a frame rate, turn a time into a frame and back,
round, and read and write SMPTE timecode, for NTSC (23.976, 29.97, 59.94) and PAL (25, 50) material alike.

- Conformance vectors: [`timebase-vectors.json`](timebase-vectors.json). Each vector calls one function below with
  named arguments and gives the result or the error code. A Skill conforms when the functions it has give those
  results. A vector marked `"optional": true` covers a reading a Skill may offer.
- Reference implementation: [`scripts/timebase.py`](../../scripts/timebase.py) (standard library only), tested by
  `scripts/tests/test_timebase.py`. `python3 scripts/timebase.py vectors` runs the vectors.
- Where each repository stands on 2026-11-20 is in ADR-026, with an issue per repository.

## TB-1 Rates and times are exact fractions

- A frame rate is a fraction of frames per second, `N/D`. A time is a fraction of seconds. Arithmetic on either
  is exact (Python `fractions.Fraction`, or integer frame counts). A float is never the value that is computed on.
- The canonical text of a rate is `"25"` when D is 1, else `"N/D"` reduced: `"30000/1001"`, `"24000/1001"`,
  `"60000/1001"`.
- A stream's rate comes from ffprobe's `r_frame_rate`, which is exact. `avg_frame_rate` only tells a variable-rate
  stream from a constant one. A rate given only as a rounded decimal (ffmpeg-skill's probe `fps` has 3 decimals)
  is read by TB-2.
- A variable-rate stream has no frame grid. Frame arithmetic on it is refused, or done after it is conformed to a
  constant rate, and that rate is the one used.
- A Skill that writes video at a rate the caller chooses accepts every rate this spec reads, NTSC included.

## TB-2 Reading a rate

| Written as | Read as |
|---|---|
| `N/D` | exactly that fraction, reduced. `"2997/100"` stays 2997/100: an explicit ratio is never "corrected". |
| an integer (`25`, `"30"`, `"30.0"`) | N/1 |
| a decimal within 0.005 of base x 1000/1001, for base 24, 30, 48, 60, 120 or 240, that is not an integer | that NTSC rate: `23.976` and `23.98` are 24000/1001, `29.97` and `29.970` 30000/1001, `47.952` and `47.95` 48000/1001, `59.94` 60000/1001, `119.88` 120000/1001 |
| any other decimal | its exact decimal value: `12.5` is 25/2, `29.98` is 1499/50 |
| a JSON number | its shortest decimal text (Python `repr`), then as above |
| optional: a suffix `p` or `i` | `p` names frames, `i` names fields: `25p` is 25, `50i` is 25, `59.94i` is 30000/1001 |

- The rate must be in (0, 1000]. Anything else is `INVALID_RATE`.
- **Never** turn a rounded decimal into a fraction with `limit_denominator(...)`: `Fraction(29.97).limit_denominator(1001)`
  is 2997/100, not 30000/1001, and 59.94 becomes 2997/50.
- Two rates are the same rate only when their fractions are equal after this reading. Do not compare floats
  within a tolerance (`|a - b| < 0.02`): 23.976 and 23.98 are the same rate, 29.97 and 30 are not.
- The nominal rate (timecode frames per second) is the rate rounded half up: 24 for 23.976, 30 for 29.97, 60 for 59.94.

## TB-3 Writing a time

- A time on the wire is decimal seconds with 6 places (`"11.466667"`), or the exact `N/D` text. A frame count is an
  integer together with its rate.
- 3 places (milliseconds) is allowed for rates up to 240 fps, and only when every reader turns the time back into a
  frame with `nearest` (TB-4). A millisecond is less than half a frame up to 500 fps, so `nearest` gives back the
  same frame; a plain floor does not (frame 1 at 29.97 starts at 0.0333667 s, written `0.033`, floored to frame 0).
- Decimal text is rounded to the nearest place, a half up.
- A seek time (where a decoder starts and returns the first frame at or after it) is the frame's start rounded
  **down** to the places written, so it never lands on the next frame: frame 2 at 29.97 is sought at `0.066`.

## TB-4 Time to frames: one rounding rule, two uses

- **nearest**: `floor(t x rate + 1/2)` on the exact values. A half goes up (toward +infinity), as JavaScript's
  `Math.round` does. Used for positions: cut points, markers, captions, a time read back from text.
  0.25 s at 30 fps is 7.5 frames and gives 8; 0.35 s gives 11.
- **down**: `floor((t + 1 ms) x rate)`. Used for the length of a clip joined at its own rate: the part frame at
  the end is dropped, and a length within 1 ms of the next whole frame keeps that frame (a measured length is
  written to the millisecond).
- A transition takes `nearest` frames, at least one.
- Frames to time is exact: frame n starts at n / rate.
- Python's `round()` and `int(round(x))` round a half to the even neighbour (10.5 to 10). Do not use them for frames;
  they differ from `nearest` on exact halves only.

## TB-5 Positions are counted, never summed from rounded values

- A position on a timeline is a sum of integer frame counts (or of exact fractions), rounded once. A length or a
  position rounded to the millisecond, or to a frame, is never added to the next one. Adding rounded values is how
  a join landed a frame early per clip, adding up over the programme (video-production-agent ADR-115).
- A clip joined at another rate, or conformed from a variable rate, takes `nearest` frames of the output rate.
- `join_positions` in the vectors gives the starts of clips joined end to end or across a transition.

## TB-6 Timecode

- A label is `hh:mm:ss:ff` (`hh` 00-23, `mm` and `ss` 00-59, `ff` 00 to nominal - 1, three digits above 100).
  It counts frames at the nominal rate. A count of 24 hours or more is refused (`OUT_OF_RANGE`), never wrapped.
- **Non-drop-frame (NDF)** works at every rate. At an NTSC rate it runs slower than the clock: one hour of NDF at
  29.97 (`01:00:00:00`, 108000 frames) is 3603.6 s.
- **Drop-frame (DF)** exists only at 30000/1001 and 60000/1001 (`DROP_FRAME_UNSUPPORTED` at any other rate,
  23.976 and 25 included). It skips frame numbers 00-01 (00-03 at 59.94) at the start of every minute except
  minutes 00, 10, 20, 30, 40 and 50, so one hour of DF (`01:00:00;00`, 107892 frames at 29.97) is 3599.9964 s.
- DF is written with `;` before the frames (`00:01:00;02`). On reading, `;`, `,` or `.` before the frames marks DF.
  A mode stated by the caller (an EDL's `FCM`, an XML `displayformat`, a flag) wins over the separator.
- A DF label that does not exist (`00:01:00;00`, `00:01:00;01` at 29.97) is refused (`NONEXISTENT_LABEL`), never
  moved to a neighbour. A frame number at or above the nominal rate is `INVALID_TIMECODE`.
- A record or source timecode is the start timecode's frame count plus the frame position, then written as a label.

## Functions (the vectors' `fn`)

| fn | arguments | result |
|---|---|---|
| `parse_rate` | value | the rate as `"N/D"` text (TB-2) |
| `rate_str` | rate | canonical text |
| `nominal` | rate | timecode frames per second |
| `same_rate` | a, b | true when the fractions are equal |
| `parse_seconds` | value | the exact time as `"N/D"` text |
| `frames_at` | seconds, rate, mode (`nearest` / `down`) | integer frames (TB-4) |
| `seconds_of` | frames, rate | the exact start time, `"N/D"` |
| `format_seconds` | seconds, places | decimal text (TB-3) |
| `seek_seconds` | frame, rate, places | decimal text, rounded down (TB-3) |
| `transition_frames` | seconds, rate | integer frames, at least 1 |
| `join_positions` | lengths, rate, transition? | `{lengths, transition, starts, total}` in frames (TB-5) |
| `timecode_from_frames` | frames, rate, drop_frame | label (TB-6) |
| `frames_from_timecode` | label, rate, drop_frame? | integer frames (TB-6) |
| `timecode_to_seconds` | label, rate, drop_frame? | exact seconds, `"N/D"` |
| `seconds_to_timecode` | seconds, rate, drop_frame | label of the nearest frame |

Error codes in the vectors: `INVALID_RATE`, `INVALID_TIME`, `INVALID_TIMECODE`, `DROP_FRAME_UNSUPPORTED`,
`NONEXISTENT_LABEL`, `OUT_OF_RANGE`. A Skill reports them with its own error code; the error taxonomy
([error-taxonomy.md](error-taxonomy.md)) puts them all in `INVALID_REQUEST` or `INVALID_INPUT`.

## Not in this spec

- Clock-style input such as `"1:30"` or `"00:01:30.250"` for seconds. A Skill may accept it.
- Audio sample positions, and SMPTE ST 12-1 field and binary-group bits.
- Interlaced field order and pull-down (3:2 cadence).
