# Reference Capability registry

**Status: CURRENT / IMPLEMENTED.** This is `docs/ROADMAP.md` Phase 1's schema/registry
library: a small, dependency-free, tested Python package that loads real
`CapabilityContract` documents, answers "who provides Capability X", detects real
Capability collisions, and applies `docs/CAPABILITY_MODEL.md`'s 3-tier collision policy.

```
python3 -m unittest discover -s registry/tests -t .
```

## What this is

- `contract.py` — `skill_identity(doc)` (resolves the ecosystem's three real
  skill-identity shapes: flat `skill_id`, flat `id` only, or nested `skill.id`),
  `validate_provides_entry(entry)`, `extract_provides(doc)`.
- `capability_contract.schema.json` / `schema.py` — the full aspirational
  `CapabilityContract` shape `docs/SPEC.md` section 1 sketches, formalized as an actual
  JSON Schema (draft 2020-12) document (`docs/ROADMAP.md` Phase 1, item 1). `required` is
  deliberately narrow — only a skill identity plus `provides[].{id, lifecycle, tool_id}`,
  the subset every real Skill's `contract` output already carries — so it documents the
  richer per-Capability shape (`input_schema`, `security.forbidden_keys`, ...) in full
  while still validating today's real, minimal contracts. `load_schema()` is stdlib-only;
  see "What this deliberately is not" below for why nothing here validates a document
  against it at runtime.
- `registry.py` — `CapabilityRegistry`: `register_contract(doc)`, `providers_of(id)`,
  `is_collision(id)`, `collisions()`, `resolve(id, explicit_skill_id=, default_skill_id=)`
  (raises `CollisionError` — registry refusal — only when neither an explicit nor a
  default choice was given for an id with 2+ independent Providers).
- `conformance.py` — **all eight** checks from `docs/SKILL_SPEC.md` section 8 are now
  real. Three (`publishes_contract`, `lifecycle_declared`, `dependency_version_ranges`)
  are answerable from a contract document alone. Four more (`forbidden_keys_rejected`,
  `doctor_status`, `workspace_confinement`, `no_clobber_input`) are real when given
  callables that talk to a live Skill process — `make_stdin_json_runner()` builds one
  for the ecosystem's common "one JSON request on stdin, one JSON response on stdout"
  CLI convention, verified end-to-end against a real `qc-skill` process
  (`tests/test_conformance_live.py`, skipped when `qc` isn't on `PATH`).
  `workspace_confinement` and `no_clobber_input` turned out not to fit the "submit a bad
  output path, check it's rejected" shape the other two use: live testing found
  `qc-skill`'s `run` request schema has no output-path field at all (its operations are
  read-only measurement; its report cache writes to a fixed, non-request-controlled
  path). They're instead observational — snapshot directories outside the workspace
  before/after a real run (`workspace_confinement`), or hash the input fixture
  before/after (`no_clobber_input`) — properties that hold for any Skill regardless of
  whether it exposes an output-path field. The eighth (`no_unsafe_shell_out`) is real
  when given a Skill's own Python package root: it statically AST-walks the source tree
  (SKILL_SPEC.md section 4.3's pattern) for `eval`/`exec`, `os.system`/`os.popen`, a
  string/f-string first argument to `subprocess.{run,Popen,call,check_call,
  check_output}`, or a `shell=` keyword that isn't the literal, safe `False` — deliberately
  AST-based rather than text/regex, since an earlier draft's regex scan produced two real
  false positives against the ecosystem's actual source (a comment merely *mentioning*
  "eval()/exec()" in `qc-skill`, and the safe, explicit `shell=False` several Skills
  actually use). Manually verified PASS against all 9 real Python Skills' source trees;
  also run against `ffmpeg-skill`: its implementation is Python too (`scripts/`, `mcp/`;
  npm is only the installer), and `scripts/`+`mcp/` at 2.22.1 PASS (59 source files).
- `tests/` — 62 tests: 21 against real captured `provides` data (`tests/fixtures/`,
  trimmed excerpts of `qc-skill`, `media-analysis-skill`, `video-editing-skill`,
  `transcription-skill` and `ffmpeg-skill`'s actual `contract`/`skill --json` output
  after their `provides` field was added — see `docs/ECOSYSTEM_CHANGELOG.md`), including
  the ecosystem's one real documented collision
  (`measure.audio.loudness`/`measure.audio.silence`/`measure.audio.integrity` between
  `qc-skill` and `media-analysis-skill`); 11 more (`tests/test_conformance_live.py`) run
  all four live conformance checks against a real `qc-skill` process, each paired with a
  synthetic sanity check proving it can actually FAIL (not just always PASS); 18 more
  (`tests/test_no_unsafe_shell_out.py`) exercise the AST-walk check's logic against
  synthetic fixtures — every real unsafe pattern, plus regression tests for the two
  false positives found against real ecosystem source; 12 more (`tests/test_schema.py`)
  cover `capability_contract.schema.json` — always: the file is valid JSON and
  `load_schema()` reads it; skipped when the optional `jsonschema` package is absent:
  the schema is itself a valid draft 2020-12 document, every real fixture in
  `tests/fixtures/` validates against it (all three skill-identity shapes included), and
  it actually rejects broken documents (a missing identity, a missing/invalid
  `lifecycle`, a missing `tool_id`) rather than accepting anything handed to it.

## Shared data-format specs: schemas and conformance fixtures

ADR-024 (decision D38) and ADR-025 (D39). The specs in `docs/specs/` that one Skill writes
and another reads, as JSON Schemas (draft 2020-12) and examples:

| Spec | Schema | Fixtures |
|---|---|---|
| `kit@1` ([kit.md](../docs/specs/kit.md)) | `schemas/kit.schema.json` | `conformance/kit/` |
| `title.json` ([title-and-stinger.md](../docs/specs/title-and-stinger.md)) | `schemas/title.schema.json` | `conformance/title/` |
| `stinger.json` (same page) | `schemas/stinger.schema.json` | `conformance/stinger/` |
| licence record ([licence-record.md](../docs/specs/licence-record.md)) | `schemas/licence-record.schema.json` | `conformance/licence-record/` |
| sidecar envelope ([sidecar-envelope.md](../docs/specs/sidecar-envelope.md)) | `schemas/sidecar-envelope.schema.json` | `conformance/sidecar-envelope/` |
| `pacing-profile@1` ([ADR-035](../docs/adr/ADR-035-reference-pacing.md)) | `schemas/pacing-profile.schema.json` | `conformance/pacing-profile/` |
| `protect-ranges@1` (same ADR) | `schemas/protect-ranges.schema.json` | `conformance/protect-ranges/` |

- `conformance/<spec>/valid/*.json` must pass; `invalid/*.json` must fail, each for the one
  reason its file name gives.
- A fixture fails by `schema`, or by `rules`: what JSON Schema cannot state (a time on a
  frame, `cut_point` inside `cover`, frame numbers agreeing with seconds), checked by
  `spec_conformance.py` `rules()`.
- `conformance/manifest.json` lists every schema and fixture with its sha256 and how it
  fails. It is generated; do not edit it.

```
python3 -m pip install 'jsonschema>=4.18'          # only for this check; registry/ stays dependency-free
python3 -m registry.spec_conformance --check        # what CI (spec-conformance.yml) runs
python3 -m registry.spec_conformance --write-manifest   # after adding or changing a schema or fixture
```

**Changing a spec**: change the page in `docs/specs/`, its schema and its fixtures in the
same pull request (one valid fixture for what is new, one invalid fixture per new way to be
wrong), then `--write-manifest`.

### Using them from a Skill's tests

The owner of a spec is the Skill that writes it; its readers test against the same files.
A Skill copies what it needs into its own tests, so they run offline and are pinned:

1. In a Velisa checkout at the commit to pin (normally `main`):

   ```
   python3 -m registry.spec_conformance --export title stinger --to <skill>/tests/fixtures/velisa
   ```

   This writes `schemas/<spec>.schema.json`, `conformance/<spec>/{valid,invalid}/` and a
   `manifest.json` with `source.commit`. A spec exported earlier and not named again is kept.
2. In the Skill, one test file that:
   - checks every copied file's sha256 against `manifest.json` (a hand edit fails);
   - **a writer**: validates what its code writes against the schema (Python: `jsonschema`
     `Draft202012Validator`; Node: `ajv/dist/2020.js`), and, for a closed schema, checks that
     its own field list equals the schema's `properties`;
   - **a reader**: reads every `valid` fixture and checks what it maps it to; for every
     `invalid` fixture, either refuses it or names it in a list with the reason it does not
     (a field it does not read, a check made later against the media). A new invalid fixture
     then fails the test until someone decides.
3. To update, export again and commit the diff in a pull request.

Trial (2026-11-19): hyperframes-skill `tests/velisa-conformance.test.mjs` (writer of
`title.json` / `stinger.json`) and motion-graphics-skill
`tests/test_velisa_title_conformance.py` (reader of `title.json`).

## What this deliberately is not

- **Not a live registry.** No process execution, no network, no persistence. A caller
  (an Agent, a future CLI) is responsible for fetching each Skill's `contract --json`
  output and calling `register_contract()` with it.
- **Not runtime validation against the full aspirational shape.** `docs/SPEC.md` section 1
  sketches a much richer per-capability shape (`input_schema`, `output_schema`,
  `input_artifact_types`, `security.forbidden_keys`, ...), now formally documented in
  `capability_contract.schema.json`. No Skill in the ecosystem publishes that richer shape
  today — only `{id, lifecycle, tool_id}` plus a few Skill-specific extra fields
  (`operation`, `element_type`, `kind`, `checks`). `contract.py`'s own Python-level
  validation still checks only what is actually real (**EXPERIMENTAL**, matching every
  Capability's own published lifecycle) — the richer fields stay **VISION** until a Skill
  actually publishes them, at which point the schema already describes the shape they'd
  need to match.
- **Not Phase 3.** This library can *apply* an explicit or default-provider choice once
  one is given; deciding what a deployment's default-provider policy should be, and
  where it is configured, is `docs/ROADMAP.md` Phase 3's job, not this library's.
- **Not a CI-integrated harness yet.** All eight `SKILL_SPEC.md` §8 checks are real
  functions a caller can invoke, but nothing here runs them automatically against every
  Skill on a schedule or in a shared CI job — a caller (a future CLI, or each Skill's own
  CI) still wires them in per-Skill. `ffmpeg-skill` is not an exception: it is a Python
  Skill distributed through npm, so `no_unsafe_shell_out` applies to its `scripts/` and
  `mcp/` trees like any other Skill.

## Why it lives here, not a new repository

This is reference/library code for the OS's own kernel concept, not a Skill and not a
distributable package yet — it belongs beside the architecture docs it implements until
there is a real consumer (an Agent, or a published package) that needs it standalone.
