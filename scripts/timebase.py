"""Reference implementation of the Velisa timebase spec (docs/specs/timebase.md, ADR-026, decision D40).

Standard library only. Every time is an exact fraction of a second (fractions.Fraction) and every frame
rate is an exact fraction of frames per second. Floats are accepted as input and turned into exact
values through their shortest decimal text (repr), never through binary approximation.

    python3 scripts/timebase.py rate 29.97                 -> 30000/1001
    python3 scripts/timebase.py tc 1800 30000/1001 --df    -> 00:01:00;02
    python3 scripts/timebase.py frames "00:01:00;02" 30000/1001
    python3 scripts/timebase.py vectors                    -> check docs/specs/timebase-vectors.json

The conformance vectors in docs/specs/timebase-vectors.json are the contract; this module is one
implementation that passes them (scripts/tests/test_timebase.py).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

SPEC = "velisa/timebase@1"

# Rule TB-2: decimal names of the NTSC ("N/1001") rates. A decimal within NTSC_TOLERANCE of base*1000/1001
# for one of these bases is that exact rate. 23.98 and 47.95 (two-decimal spellings) are covered.
NTSC_BASES = (24, 30, 48, 60, 120, 240)
NTSC_TOLERANCE = Fraction(5, 1000)
MAX_RATE = Fraction(1000)

# Rule TB-6: drop-frame timecode exists only at these two rates.
DROP_FRAME_RATES = (Fraction(30000, 1001), Fraction(60000, 1001))

# Rule TB-4: the tolerance of the "down" rounding (a length within 1 ms of the next frame keeps that frame).
DOWN_TOLERANCE = Fraction(1, 1000)

_DECIMAL = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
_RATIONAL = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")
_TC = re.compile(r"^(\d{2}):(\d{2}):(\d{2})([:;.,])(\d{2,3})$")

Number = Union[int, float, str, Fraction]


class TimebaseError(ValueError):
    """A value the spec refuses. `code` is one of INVALID_RATE, INVALID_TIME, INVALID_TIMECODE,
    DROP_FRAME_UNSUPPORTED, NONEXISTENT_LABEL, OUT_OF_RANGE."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


# ---------------------------------------------------------------------------------------------- numbers
def _exact(value: Any, what: str) -> Fraction:
    """An exact fraction from an int, a Fraction, a decimal string, an 'N/D' string or a float (via repr)."""
    if isinstance(value, bool):
        raise TimebaseError("INVALID_TIME", f"{what}: a boolean is not a number")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TimebaseError("INVALID_TIME", f"{what}: {value!r} is not finite")
        return Fraction(repr(value))
    if isinstance(value, str):
        text = value.strip()
        m = _RATIONAL.match(text)
        if m:
            num, den = int(m.group(1)), int(m.group(2))
            if den == 0:
                raise TimebaseError("INVALID_TIME", f"{what}: {value!r} has a zero denominator")
            return Fraction(num, den)
        if _DECIMAL.match(text):
            return Fraction(text)
    raise TimebaseError("INVALID_TIME", f"{what}: {value!r} is not a number")


def parse_seconds(value: Number) -> Fraction:
    """A time in seconds as an exact fraction (rule TB-3): '12.5' is 25/2, 0.1 is 1/10, '1001/30000' stays."""
    return _exact(value, "time")


def round_half_up(x: Fraction) -> int:
    """The spec's one rounding to the nearest integer (rule TB-4): a half goes up, toward +infinity.
    floor(x + 1/2) on the exact value; JavaScript's Math.round does the same on numbers."""
    return math.floor(x + Fraction(1, 2))


# ---------------------------------------------------------------------------------------------- rates
def parse_rate(value: Number) -> Fraction:
    """A frame rate as an exact fraction of frames per second (rules TB-1, TB-2).

    - 'N/D' is taken exactly as written ('30000/1001', '25/1', and '2997/100' too).
    - An integer is N/1.
    - A decimal within 0.005 of base*1000/1001 (base 24, 30, 48, 60, 120, 240) that is not itself an integer
      is that NTSC rate: '23.976', '23.98', '29.97', '59.94', '47.952', '119.88'.
    - Any other decimal is its exact value: '12.5' is 25/2. It is never approximated (no limit_denominator).
    - A suffix 'p' names a frame rate ('25p'); a suffix 'i' names a field rate, so the frame rate is half
      ('50i' is 25, '59.94i' is 30000/1001).
    - The rate must be in (0, 1000].
    """
    text: Any = value
    fields = False
    if isinstance(value, str):
        text = value.strip().lower()
        if text.endswith("i"):
            fields, text = True, text[:-1]
        elif text.endswith("p"):
            text = text[:-1]
    try:
        exact = _exact(text, "frame rate")
    except TimebaseError:
        raise TimebaseError("INVALID_RATE", f"frame rate {value!r} is not N/D, an integer or a decimal") from None
    written_as_ratio = isinstance(text, str) and "/" in text
    if isinstance(value, Fraction):
        written_as_ratio = True
    rate = exact
    if not written_as_ratio and exact.denominator != 1:
        for base in NTSC_BASES:
            ntsc = Fraction(base * 1000, 1001)
            if abs(exact - ntsc) <= NTSC_TOLERANCE:
                rate = ntsc
                break
    if fields:
        rate = rate / 2
    if rate <= 0 or rate > MAX_RATE:
        raise TimebaseError("INVALID_RATE", f"frame rate {value!r} is out of range (0, 1000]")
    return rate


def rate_str(rate: Number) -> str:
    """The canonical text of a rate: '25' or '30000/1001'."""
    r = parse_rate(rate)
    return str(r.numerator) if r.denominator == 1 else f"{r.numerator}/{r.denominator}"


def nominal(rate: Number) -> int:
    """Timecode frames per second: the rate rounded half up (24 for 23.976, 30 for 29.97, 25 for 25)."""
    return max(1, round_half_up(parse_rate(rate)))


def is_ntsc(rate: Number) -> bool:
    return parse_rate(rate).denominator == 1001


def same_rate(a: Number, b: Number) -> bool:
    """Two rates are the same only when their exact fractions are equal (rule TB-2): no float tolerance."""
    return parse_rate(a) == parse_rate(b)


# ---------------------------------------------------------------------------------------------- time <-> frames
def frames_at(seconds: Number, rate: Number, mode: str = "nearest", tolerance: Number = DOWN_TOLERANCE) -> int:
    """The frame count of a time (rule TB-4).

    - nearest: the frame nearest to the time, a half up (positions, cut points, markers, captions).
    - down: whole frames of a length, a part frame dropped; a length within `tolerance` (1 ms) of the next
      frame keeps that frame (the length of a clip joined at its own rate).
    """
    t = parse_seconds(seconds)
    r = parse_rate(rate)
    if mode == "nearest":
        return round_half_up(t * r)
    if mode == "down":
        return math.floor((t + _exact(tolerance, "tolerance")) * r)
    raise TimebaseError("INVALID_TIME", f"unknown rounding mode {mode!r} (nearest | down)")


def seconds_of(frames: int, rate: Number) -> Fraction:
    """The exact start time of frame `frames` (0-based): frames / rate."""
    if isinstance(frames, bool) or not isinstance(frames, int):
        raise TimebaseError("INVALID_TIME", f"frame count {frames!r} is not an integer")
    return Fraction(frames) / parse_rate(rate)


def format_seconds(seconds: Number, places: int = 6) -> str:
    """Decimal text of a time, to the nearest `places` digits, a half up (rule TB-3: 6 places by default)."""
    t = parse_seconds(seconds)
    q = Fraction(1, 10 ** places)
    n = round_half_up(t / q)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if places == 0:
        return f"{sign}{n}"
    return f"{sign}{n // 10 ** places}.{n % 10 ** places:0{places}d}"


def seek_seconds(frame: int, rate: Number, places: int = 3) -> str:
    """The time to seek to for frame `frame`: its start rounded DOWN to `places` digits, so a seek that
    returns the first frame at or after the time lands on that frame (rule TB-3)."""
    t = seconds_of(frame, rate)
    q = Fraction(1, 10 ** places)
    return format_seconds(Fraction(math.floor(t / q)) * q, places)


def transition_frames(seconds: Number, rate: Number) -> int:
    """A transition's length in whole frames: the nearest, a half up, at least one frame (rule TB-4)."""
    return max(1, frames_at(seconds, rate, "nearest"))


def join_positions(lengths: Sequence[Number], rate: Number, transition: Optional[Number] = None) -> Dict[str, Any]:
    """Where clips joined end to end (or overlapped by a transition) start, in frames (rule TB-5).

    Each clip takes its whole-frame length (down), the transition its whole-frame length, and every start is a
    sum of integers, so rounding never adds up however many clips there are."""
    lens = [frames_at(x, rate, "down") for x in lengths]
    overlap = transition_frames(transition, rate) if transition is not None else 0
    starts: List[int] = []
    t = 0
    for i, n in enumerate(lens):
        if i > 0:
            t = max(0, t - overlap)
        starts.append(t)
        t += n
    return {"lengths": lens, "transition": overlap, "starts": starts, "total": t}


# ---------------------------------------------------------------------------------------------- timecode
def _drop_per_minute(rate: Fraction) -> int:
    if rate not in DROP_FRAME_RATES:
        raise TimebaseError("DROP_FRAME_UNSUPPORTED",
                            f"drop-frame timecode exists only at 30000/1001 and 60000/1001, not {rate_str(rate)}")
    return 2 * nominal(rate) // 30


def timecode_from_frames(frames: int, rate: Number, drop_frame: bool = False) -> str:
    """A frame count from 00:00:00:00 as a timecode label (rule TB-6). Drop-frame labels use ';' before the
    frames. A count of 24 hours or more is refused, never wrapped."""
    if isinstance(frames, bool) or not isinstance(frames, int) or frames < 0:
        raise TimebaseError("OUT_OF_RANGE", f"frame count {frames!r} must be a non-negative integer")
    r = parse_rate(rate)
    fps = nominal(r)
    n = frames
    if drop_frame:
        drop = _drop_per_minute(r)
        per_10min = fps * 600 - drop * 9
        per_min = fps * 60 - drop
        d, m = divmod(n, per_10min)
        n += drop * 9 * d + (drop * ((m - drop) // per_min) if m >= drop else 0)
    h, rem = divmod(n, fps * 3600)
    if h >= 24:
        raise TimebaseError("OUT_OF_RANGE", f"frame count {frames} is 24 hours or more of timecode")
    mi, rem = divmod(rem, fps * 60)
    s, f = divmod(rem, fps)
    width = 3 if fps > 100 else 2
    return f"{h:02d}:{mi:02d}:{s:02d}{';' if drop_frame else ':'}{f:0{width}d}"


def parse_timecode(label: str) -> Tuple[int, int, int, int, bool]:
    """'hh:mm:ss:ff' -> (h, m, s, f, written as drop-frame). ';', ',' or '.' before the frames marks drop-frame."""
    m = _TC.match(str(label).strip())
    if not m:
        raise TimebaseError("INVALID_TIMECODE", f"{label!r} is not hh:mm:ss:ff")
    h, mi, s, sep, f = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), int(m.group(5))
    if h > 23 or mi > 59 or s > 59:
        raise TimebaseError("INVALID_TIMECODE", f"{label!r}: hours 00-23, minutes and seconds 00-59")
    return h, mi, s, f, sep != ":"


def frames_from_timecode(label: str, rate: Number, drop_frame: Optional[bool] = None) -> int:
    """A timecode label as a frame count from 00:00:00:00 (rule TB-6). `drop_frame` states the mode; when it
    is None the separator decides (';' is drop-frame). A drop-frame label that does not exist (00:01:00;00 at
    29.97) is refused, never moved."""
    h, mi, s, f, written_df = parse_timecode(label)
    r = parse_rate(rate)
    fps = nominal(r)
    df = written_df if drop_frame is None else bool(drop_frame)
    if f >= fps:
        raise TimebaseError("INVALID_TIMECODE", f"{label!r}: frame {f} is out of range at {fps} timecode frames per second")
    total = ((h * 60 + mi) * 60 + s) * fps + f
    if df:
        drop = _drop_per_minute(r)
        if s == 0 and f < drop and mi % 10 != 0:
            raise TimebaseError("NONEXISTENT_LABEL", f"{label!r} does not exist in drop-frame timecode "
                                f"(frames 00-{drop - 1:02d} are skipped at the start of each minute not divisible by 10)")
        minutes = h * 60 + mi
        total -= drop * (minutes - minutes // 10)
    return total


def timecode_to_seconds(label: str, rate: Number, drop_frame: Optional[bool] = None) -> Fraction:
    """Seconds from 00:00:00:00 of a timecode label: its frame count over the exact rate."""
    return seconds_of(frames_from_timecode(label, rate, drop_frame), rate)


def seconds_to_timecode(seconds: Number, rate: Number, drop_frame: bool = False) -> str:
    """The label of the frame nearest to a time."""
    return timecode_from_frames(frames_at(seconds, rate, "nearest"), rate, drop_frame)


# ---------------------------------------------------------------------------------------------- vectors
def _out(value: Any) -> Any:
    """How a result is written in the vectors file: a Fraction as its 'N/D' (or 'N') text."""
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {k: _out(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_out(v) for v in value]
    return value


FUNCTIONS = {
    "parse_rate": parse_rate, "rate_str": rate_str, "nominal": nominal, "same_rate": same_rate,
    "parse_seconds": parse_seconds, "frames_at": frames_at, "seconds_of": seconds_of,
    "format_seconds": format_seconds, "seek_seconds": seek_seconds, "transition_frames": transition_frames,
    "join_positions": join_positions, "timecode_from_frames": timecode_from_frames,
    "frames_from_timecode": frames_from_timecode, "timecode_to_seconds": timecode_to_seconds,
    "seconds_to_timecode": seconds_to_timecode,
}


def run_vector(vec: Dict[str, Any]) -> Tuple[bool, Any]:
    """(passed, what came out) for one vector {id, fn, args, expect | error}."""
    fn = FUNCTIONS[vec["fn"]]
    try:
        got = _out(fn(**vec["args"]))
    except TimebaseError as e:
        return ("error" in vec and e.code == vec["error"]), {"error": e.code}
    return ("expect" in vec and got == vec["expect"]), got


def check_vectors(path: Path) -> List[Dict[str, Any]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    for vec in doc["vectors"]:
        ok, got = run_vector(vec)
        if not ok:
            failures.append({"id": vec["id"], "expected": vec.get("expect", {"error": vec.get("error")}), "got": got})
    return failures


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("rate", help="a frame rate as N/D")
    a.add_argument("value")
    a = sub.add_parser("tc", help="a frame count as a timecode label")
    a.add_argument("frames", type=int)
    a.add_argument("rate")
    a.add_argument("--df", action="store_true", help="drop-frame")
    a = sub.add_parser("frames", help="a timecode label as a frame count")
    a.add_argument("label")
    a.add_argument("rate")
    a.add_argument("--df", action="store_true", default=None, help="drop-frame (default: the separator decides)")
    a = sub.add_parser("vectors", help="run the conformance vectors")
    a.add_argument("path", nargs="?", default=str(Path(__file__).resolve().parents[1] / "docs/specs/timebase-vectors.json"))
    args = p.parse_args(argv)
    try:
        if args.cmd == "rate":
            print(rate_str(args.value))
        elif args.cmd == "tc":
            print(timecode_from_frames(args.frames, args.rate, args.df))
        elif args.cmd == "frames":
            print(frames_from_timecode(args.label, args.rate, args.df))
        else:
            failures = check_vectors(Path(args.path))
            for f in failures:
                print(json.dumps(f, ensure_ascii=False))
            print(f"{'FAIL' if failures else 'ok'}: {len(failures)} of the vectors failed")
            return 1 if failures else 0
    except TimebaseError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
