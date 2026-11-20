"""The timebase spec's reference implementation (scripts/timebase.py) against its conformance vectors
(docs/specs/timebase-vectors.json) and the properties the spec states (ADR-026, decision D40). Offline,
standard library only.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import timebase as tb  # noqa: E402

VECTORS = ROOT / "docs" / "specs" / "timebase-vectors.json"
NTSC = Fraction(30000, 1001)
NTSC60 = Fraction(60000, 1001)
RATES = ["24000/1001", "24", "25", "30000/1001", "30", "48000/1001", "50", "60000/1001", "60", "120000/1001", "120"]


class Vectors(unittest.TestCase):
    def test_file_shape(self):
        doc = json.loads(VECTORS.read_text(encoding="utf-8"))
        self.assertEqual(doc["spec"], tb.SPEC)
        ids = [v["id"] for v in doc["vectors"]]
        self.assertEqual(len(ids), len(set(ids)), "vector ids are unique")
        for v in doc["vectors"]:
            self.assertIn(v["fn"], tb.FUNCTIONS, v["id"])
            self.assertEqual(("expect" in v) + ("error" in v), 1, f"{v['id']}: exactly one of expect | error")

    def test_every_vector_passes(self):
        self.assertEqual(tb.check_vectors(VECTORS), [])

    def test_vectors_cover_pal_ntsc_and_drop_frame(self):
        text = VECTORS.read_text(encoding="utf-8")
        for needle in ('"25"', '"50"', '"24000/1001"', '"30000/1001"', '"60000/1001"', "NONEXISTENT_LABEL",
                       "DROP_FRAME_UNSUPPORTED", "join_positions"):
            self.assertIn(needle, text)

    def test_cli_runs_the_vectors(self):
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "timebase.py"), "vectors"],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("ok: 0 of the vectors failed", out.stdout)

    def test_a_wrong_expectation_is_reported(self):
        ok, got = tb.run_vector({"id": "x", "fn": "parse_rate", "args": {"value": "29.97"}, "expect": "2997/100"})
        self.assertFalse(ok)
        self.assertEqual(got, "30000/1001")
        ok, got = tb.run_vector({"id": "y", "fn": "parse_rate", "args": {"value": "0"}, "expect": "0"})
        self.assertEqual((ok, got), (False, {"error": "INVALID_RATE"}))


class Rates(unittest.TestCase):
    def test_probe_style_decimals_are_ntsc(self):
        # ffmpeg-skill's probe writes fps rounded to 3 decimals; each reads back as the exact NTSC rate
        for base in tb.NTSC_BASES:
            exact = Fraction(base * 1000, 1001)
            for places in (2, 3, 6):
                self.assertEqual(tb.parse_rate(f"{float(exact):.{places}f}"), exact, (base, places))
                self.assertEqual(tb.parse_rate(round(float(exact), places)), exact, (base, places))

    def test_never_the_limit_denominator_value(self):
        # the ADR-115 note: Fraction(29.97).limit_denominator(1001) is 2997/100, which this spec never produces from 29.97
        self.assertEqual(Fraction(29.97).limit_denominator(1001), Fraction(2997, 100))
        self.assertNotEqual(tb.parse_rate(29.97), Fraction(2997, 100))

    def test_integers_and_pal_stay_integers(self):
        for r in (24, 25, 30, 50, 60, 100, 120):
            self.assertEqual(tb.parse_rate(r), r)
            self.assertEqual(tb.parse_rate(f"{r}.000"), r)
            self.assertEqual(tb.rate_str(r), str(r))


class Conversions(unittest.TestCase):
    def test_six_decimal_text_round_trips_every_frame(self):
        for rate in RATES:
            for n in list(range(0, 3000)) + [107892, 215784, 2589407]:
                text = tb.format_seconds(tb.seconds_of(n, rate), 6)
                self.assertEqual(tb.frames_at(text, rate, "nearest"), n, (rate, n))

    def test_millisecond_text_round_trips_up_to_240_fps(self):
        for rate in RATES + ["240"]:
            for n in range(0, 5000):
                text = tb.format_seconds(tb.seconds_of(n, rate), 3)
                self.assertEqual(tb.frames_at(text, rate, "nearest"), n, (rate, n))

    def test_millisecond_text_read_down_can_lose_a_frame(self):
        # the bug class of ADR-115: a millisecond-rounded start read back with a plain floor lands a frame early
        lost = [n for n in range(1, 300)
                if int(Fraction(tb.format_seconds(tb.seconds_of(n, NTSC), 3)) * NTSC) != n]
        self.assertTrue(lost, "a plain floor of a ms-rounded time is not safe")
        self.assertTrue(all(tb.frames_at(tb.format_seconds(tb.seconds_of(n, NTSC), 3), NTSC) == n for n in lost))

    def test_seek_never_lands_after_its_frame(self):
        for rate in RATES:
            for n in range(0, 2000):
                t = Fraction(tb.seek_seconds(n, rate))
                self.assertLessEqual(t, tb.seconds_of(n, rate))
                self.assertGreater(t, tb.seconds_of(n - 1, rate) if n else Fraction(-1))

    def test_joins_never_accumulate(self):
        rng = random.Random(115)
        for rate in ("30000/1001", "25", "24000/1001"):
            lengths = [f"{rng.uniform(0.2, 8):.3f}" for _ in range(200)]
            pos = tb.join_positions(lengths, rate, "0.5")
            expect, t = [], 0
            for i, n in enumerate(pos["lengths"]):
                if i:
                    t -= pos["transition"]
                expect.append(t)
                t += n
            self.assertEqual(pos["starts"], expect)
            self.assertEqual(pos["total"], t)
            for start in pos["starts"]:
                self.assertEqual(tb.frames_at(tb.format_seconds(tb.seconds_of(start, rate), 3), rate), start)


class Timecode(unittest.TestCase):
    def test_drop_frame_round_trip_first_twenty_minutes(self):
        for rate in (NTSC, NTSC60):
            for n in range(0, 20 * 60 * tb.nominal(rate) + 1):
                label = tb.timecode_from_frames(n, rate, True)
                self.assertEqual(tb.frames_from_timecode(label, rate, True), n, (rate, n, label))

    def test_drop_frame_round_trip_sampled_day(self):
        rng = random.Random(6)
        for rate, day in ((NTSC, 2589408), (NTSC60, 5178816)):
            for n in [day - 1] + [rng.randrange(day) for _ in range(20000)]:
                self.assertEqual(tb.frames_from_timecode(tb.timecode_from_frames(n, rate, True), rate, True), n)
            with self.assertRaises(tb.TimebaseError):
                tb.timecode_from_frames(day, rate, True)

    def test_drop_frame_hour_is_clock_hour(self):
        for rate in (NTSC, NTSC60):
            frames = tb.frames_from_timecode("01:00:00;00", rate, True)
            self.assertLess(abs(tb.seconds_of(frames, rate) - 3600), Fraction(1, 200))

    def test_every_skipped_label_is_refused(self):
        for rate in (NTSC, NTSC60):
            drop = 2 * tb.nominal(rate) // 30
            for minute in range(60):
                for f in range(drop):
                    label = f"00:{minute:02d}:00;{f:02d}"
                    if minute % 10:
                        with self.assertRaises(tb.TimebaseError) as cm:
                            tb.frames_from_timecode(label, rate, True)
                        self.assertEqual(cm.exception.code, "NONEXISTENT_LABEL")
                    else:
                        tb.frames_from_timecode(label, rate, True)

    def test_non_drop_round_trip(self):
        for rate in RATES:
            for n in range(0, 100000, 7):
                self.assertEqual(tb.frames_from_timecode(tb.timecode_from_frames(n, rate), rate, False), n)


if __name__ == "__main__":
    unittest.main()
