"""The shared data-format specs' schemas and conformance fixtures (registry/spec_conformance.py, ADR-024).

The file-layout checks are stdlib-only and always run. Validating needs the `jsonschema` package; those tests skip
without it, as test_schema.py's do. The spec-conformance workflow installs it, so in CI they always run.
"""
from __future__ import annotations

import importlib
import json
import unittest

from .. import spec_conformance as sc

try:
    import jsonschema  # noqa: F401

    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


class LayoutTests(unittest.TestCase):
    def test_every_spec_has_a_schema_and_both_kinds_of_fixture(self) -> None:
        for spec, (schema_file, doc) in sc.SPECS.items():
            with self.subTest(spec=spec):
                schema = sc.load_json(sc.SCHEMA_DIR / schema_file)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertTrue(schema["$id"].endswith(f"/registry/schemas/{schema_file}"))
                self.assertTrue((sc.ROOT.parent / doc).is_file(), doc)
                self.assertTrue(list((sc.FIXTURE_DIR / spec / "valid").glob("*.json")))
                self.assertTrue(list((sc.FIXTURE_DIR / spec / "invalid").glob("*.json")))

    def test_every_spec_document_links_its_schema(self) -> None:
        for spec, (schema_file, doc) in sc.SPECS.items():
            with self.subTest(spec=spec):
                self.assertIn(f"registry/schemas/{schema_file}", (sc.ROOT.parent / doc).read_text(encoding="utf-8"))

    def test_no_stray_fixture_directories(self) -> None:
        for d in sc.FIXTURE_DIR.iterdir():
            if d.is_dir():
                self.assertIn(d.name, sc.SPECS)
                self.assertEqual(sorted(p.name for p in d.iterdir()), ["invalid", "valid"])

    def test_the_conformance_directory_does_not_shadow_the_conformance_module(self) -> None:
        # registry/conformance/ (fixtures, no __init__.py) sits beside registry/conformance.py; the module must win
        mod = importlib.import_module("registry.conformance")
        self.assertTrue(mod.__file__.endswith("conformance.py"))

    def test_the_manifest_lists_every_fixture_with_its_hash(self) -> None:
        manifest = json.loads(sc.MANIFEST.read_text(encoding="utf-8"))
        listed = {f["path"]: f for e in manifest["specs"].values() for f in e["fixtures"]}
        on_disk = {p.relative_to(sc.ROOT).as_posix(): p for p in sc.FIXTURE_DIR.glob("*/*/*.json")}
        self.assertEqual(sorted(listed), sorted(on_disk))
        for rel, p in on_disk.items():
            self.assertEqual(listed[rel]["sha256"], sc.sha256_file(p), rel)
        for spec, entry in manifest["specs"].items():
            self.assertEqual(entry["schema_sha256"], sc.sha256_file(sc.ROOT / entry["schema"]), spec)


    def test_rules_catch_what_the_schema_cannot(self) -> None:
        # each would pass the schema; only the rules refuse it
        self.assertTrue(sc.rules("stinger", {"cut_point": 0.7, "cover": {"start": 0.5, "end": 0.7}}))
        self.assertTrue(sc.rules("stinger", {"frame_rate": "24/1", "cut_point": 1.042, "cover": {"start": 1.0, "end": 1.25}}))
        self.assertEqual(sc.rules("stinger", {"frame_rate": "24/1", "cut_point": 25 / 24, "cover": {"start": 1.0, "end": 1.25}}), [])
        self.assertTrue(sc.rules("title", {"frame_rate": "30/1", "segments": {"in": 0.51, "loop": 1, "out": 0.5}}))
        self.assertEqual(sc.rules("title", {"segments": {"in": 0.51, "loop": 1, "out": 0.5}}), [])  # no frame_rate: nothing to check

    def test_export_copies_the_named_specs_with_their_manifest(self) -> None:
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory(prefix="registry_export_") as d:
            out = sc.export(["title"], Path(d), source="0" * 40)
            self.assertEqual(out["source"]["commit"], "0" * 40)
            self.assertEqual(list(out["specs"]), ["title"])
            for f in out["specs"]["title"]["fixtures"]:
                self.assertEqual(sc.sha256_file(Path(d) / f["path"]), f["sha256"])
            self.assertTrue((Path(d) / "schemas" / "title.schema.json").is_file())
            sc.export(["stinger"], Path(d), source="1" * 40)  # a second export keeps the first spec
            self.assertEqual(sorted(json.loads((Path(d) / "manifest.json").read_text(encoding="utf-8"))["specs"]), ["stinger", "title"])


@unittest.skipUnless(HAVE_JSONSCHEMA, "jsonschema package not installed")
class FixtureTests(unittest.TestCase):
    def test_valid_fixtures_pass_and_invalid_ones_fail(self) -> None:
        result = sc.run()
        self.assertEqual(result["failures"], [])

    def test_the_committed_manifest_is_current(self) -> None:
        self.assertEqual(sc.MANIFEST.read_text(encoding="utf-8"), sc.manifest_text(sc.run()["manifest"]))

    def test_the_cli_check_passes(self) -> None:
        self.assertEqual(sc.main(["--check"]), 0)

    def test_a_sound_design_entry_is_a_velisa_entry(self) -> None:
        # the spec's base: sound-design-skill's stored entry, with every field it writes, validates here unchanged
        validator = sc._validator(sc.load_json(sc.SCHEMA_DIR / "licence-record.schema.json"))
        entry = sc.load_json(sc.FIXTURE_DIR / "licence-record" / "valid" / "sound-design-entry.json")
        self.assertEqual(list(validator.iter_errors(entry)), [])
