# JSON schemas and conformance fixtures (Velisa ADR-024 / D38, ADR-025 / D39)

## What exists

- `registry/schemas/` (JSON Schema draft 2020-12): `kit.schema.json` (`kit@1`, a brand kit), `title.schema.json` and `stinger.schema.json` (sidecars beside title and stinger material), `licence-record.schema.json`, `sidecar-envelope.schema.json`.
- Each schema follows its spec in `docs/specs/` (PROPOSED fields optional). Where the spec is silent the schema chooses and says so in its `description`. Where a Skill differs from the spec the schema still follows the spec; ADR-024's tables list each difference as Settled or Open (K1-K3, K5 and L2 are open and need the spec owner and ffmpeg-skill or sound-design-skill).
- What a schema cannot state is a rule in `registry/spec_conformance.py` `rules()`: a time on a frame (within 1/1000 of a frame), `cut_point` inside `cover`, frame numbers agreeing with seconds.
- Fixtures: `registry/conformance/<spec>/valid/` and `invalid/`. Each invalid fixture is wrong in one way and its file name says which. `registry/conformance/manifest.json` lists every schema and fixture with its sha256 and whether it fails by schema or by rule; it is generated.

## The sidecar envelope (ADR-025)

Every sidecar a Skill writes beside an output carries four top-level fields: `schema` (`<namespace>/<name>@<major>`), `producer` (`{skill_id, version}`), `generated_at` (UTC, RFC 3339 with `Z`) and `inputs` (`[{sha256, file?, role?}]`, empty when no medium went in). No Skill writes it yet; the spec lists the follow-ups (hyperframes and subtitle first).

## Changing a schema or fixture (in Velisa)

```bash
python3 -m registry.spec_conformance --write-manifest   # after adding or changing a schema or fixture
python3 -m registry.spec_conformance --check            # what spec-conformance.yml runs (it fails the pull request)
python3 -m unittest registry.tests.test_spec_conformance -v
```

A spec change goes with its schema and fixtures in the same pull request. Keep schema changes additive (a new optional field); a field removed or made required is a new major (`@2`) and needs the owner.

## Giving them to a Skill

Skills copy, never fetch at test time:

```bash
python3 -m registry.spec_conformance --export title stinger --to <skill>/tests/fixtures/velisa
```

This copies the schemas, fixtures and manifest entries with `source.commit` (the Velisa commit). The Skill's test checks the copies' sha256 against the manifest (a hand edit fails), runs its writer's output through the schema and its reader over the fixtures. To update, export again and commit the diff in a pull request. A copy goes stale silently until then; `source.commit` says how old it is.

Taken so far: hyperframes-skill (writer of `title.json` / `stinger.json`, ajv) and motion-graphics-skill (reader of `title.json`). Next, one at a time: video-editing and qc (`stinger`), thumbnail, remotion-ffmpeg and motion-graphics (`kit`), sound-design and artifacts (`licence-record`). ffmpeg-skill is not changed from here.
