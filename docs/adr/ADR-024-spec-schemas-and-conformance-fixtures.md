# ADR-024: JSON Schemas and Conformance Fixtures for the Shared Data-Format Specs

Status: Accepted (decision D38)

## Context

Three specs in `docs/specs/` describe data that one Skill writes and another reads: `kit@1` (a brand kit),
`title.json` / `stinger.json` (metadata beside title and stinger material) and the licence record. They were tables in
Markdown. Each Skill that writes or reads one checked it against its own reading of the table: hyperframes-skill writes
the field lists out in `tests/material.test.mjs`, motion-graphics-skill's `titlejson.py` and `kit.py` check what they
read, sound-design-skill has its own `schemas/licence-record.schema.json`. Nothing checked that the writer and the reader
agree with each other, and a renamed field would only show up when a hand-off failed.

## Decision

1. **One JSON Schema (draft 2020-12) per spec, in `registry/schemas/`**: `kit.schema.json`, `title.schema.json`,
   `stinger.schema.json`, `licence-record.schema.json`, plus `sidecar-envelope.schema.json` (ADR-025). The schema follows
   the spec document, including its PROPOSED fields (optional). Where a spec is silent, the schema chooses and says so in
   its `description`. Where a writer or reader differs from the spec, the schema still follows the spec, and the table
   below records the difference.
2. **What a schema cannot state is a rule in `registry/spec_conformance.py` `rules()`**: a time on a frame (within
   1/1000 of a frame), `cut_point` inside `cover`, and frame numbers agreeing with seconds. A fixture fails either by
   schema or by rule, and the manifest says which.
3. **Fixtures in `registry/conformance/<spec>/valid/` and `invalid/`**: each invalid fixture is wrong in one way, and
   its file name says which. `registry/conformance/manifest.json` lists every schema and fixture with its sha256 and
   how it fails. It is generated and checked.
4. **Velisa's CI fails on any mismatch**: the new `spec-conformance.yml` installs `jsonschema` (4.23.0) and runs
   `python -m registry.spec_conformance --check` and `registry/tests/test_spec_conformance.py`. It is not report-only.
5. **Skills copy, not fetch**: `python3 -m registry.spec_conformance --export <spec>... --to <dir>` copies the schemas,
   fixtures and manifest entries into a Skill's tests, with the Velisa commit. A Skill's test checks the copy's hashes,
   runs its writer's output through the schema, and runs its reader over the fixtures. Tests stay offline and pinned;
   updating is a re-export in a pull request. The procedure is in `registry/README.md`.
6. **Trial in two Skills only**: hyperframes-skill (the writer of `title.json` and `stinger.json`) and
   motion-graphics-skill (the reader of `title.json`). The other Skills are listed under "What follows".

`registry/conformance/` is a fixtures directory without `__init__.py` beside the module `registry/conformance.py`.
Python imports the module first; a test keeps it that way.

## Where the implementations differ from the specs (2026-11-19)

Read from each repository's `origin/main`: ffmpeg-skill `364f2d5`, hyperframes-skill `5de18d8`, motion-graphics-skill
`e5c6cf0`, remotion-ffmpeg-skill `ad17dd1`, thumbnail-skill `b575e74`, sound-design-skill `438a490`, artifacts-skill
`6e684cb`, video-editing-skill `9a41835`, qc-skill `a6492ac`. "Settled" means this ADR decides it. "Open" means the
owner of a spec or a Skill has to decide.

### `kit@1`

| # | Where | The spec says | The implementation does | Schema | Status |
|---|---|---|---|---|---|
| K1 | ffmpeg-skill `check_brand_keys` (#510) | a kit file can be passed to ffmpeg-skill as it is; keys it does not use are kept and ignored | refuses every key it does not read. So `schema`, `name`, `colors.secondary`, `fonts`, `logo_variants`, `contrast` and `colours` stop ffmpeg-skill with an input error | follows the spec | **Open**: ffmpeg-skill accepts the kit@1 keys, or the spec says a kit is converted for ffmpeg-skill as for motion-graphics. ffmpeg-skill is not changed here |
| K2 | ffmpeg-skill `BRAND_KEYS` | the brand.json keys are the ones in the table | also reads `emoji_assets` (top level and in `caption`), `colors.upcoming`, and `box`, `color`, `colour`, `font` in `caption` (the same keys as `styles.caption`) | allowed: the spec's rule says every brand.json is a kit@1 | **Open**: add them to the spec's table |
| K3 | ffmpeg-skill | "`colours` for remotion" | refuses `colours` as a misspelling | allows `colours` (never with `colors`) | **Open**, with K1 |
| K4 | hyperframes-skill `kit.mjs`, remotion-ffmpeg-skill `_hex_colour` | colours are `RRGGBB` without `#` | accept `#RRGGBB` too (remotion also `0x` and `&H`) | `RRGGBB` only, so a kit with `#` fails | Settled: readers may be lenient; a kit is written without `#` |
| K5 | ffmpeg-skill overlay, thumbnail-skill, motion-graphics-skill | `logo_position`: the four corners "and the other ffmpeg-skill position names" | the nine names of overlay.py (`top-left` ... `bottom-right`); ffmpeg-skill also takes an explicit `"X,Y"` | the nine names | **Open**: whether `"X,Y"` is a kit value |
| K6 | thumbnail-skill `kit.py` (ADR-18), hyperframes-skill `--kit` (step 16), motion-graphics-skill `options.kit` (ADR-31) | mapping table: thumbnail-skill and hyperframes-skill have "no brand input"; motion-graphics takes a theme or `brand_kit` | all three read a kit@1 file themselves now | not affected | Settled: the spec's mapping table is out of date; updating its prose is a follow-up |
| K7 | the spec | `fonts[].embedding` "whether it allows embedding"; required keys in `fonts[]` and `contrast[]` not stated | no writer yet | `embedding` boolean; `fonts[]` needs `family`; `contrast[]` needs `fg`, `bg`, `ratio` (1-21) | Settled here; revisit when a writer appears |
| K8 | the spec | `caption` / `styles.caption` colour notation not stated | ffmpeg-skill passes it to its caption tool | any non-empty text | Settled here |

### `title.json` / `stinger.json`

| # | Where | The spec says | The implementation does | Schema | Status |
|---|---|---|---|---|---|
| T1 | motion-graphics-skill `titlejson.py` (ADR-33) | "No receiver opens the sidecar"; `segments` is read only by hyperframes-skill | `rendered_layer.title_json` opens the file and reads `segments`, `sha256`, `file`, `alpha`, `schema` | not affected | Settled: the spec's "Read by" columns are out of date; updating its prose is a follow-up |
| T2 | motion-graphics-skill | segments are whole frames adding up to the clip's duration | checks the sum against the probed length within one frame + 2 ms, and does not read `frame_rate` or `segment_frames` | whole frames when `frame_rate` is given (rule) | Settled: the reader is lenient; the maker is held to the spec |
| T3 | motion-graphics-skill | `alpha` is `straight` or `premultiplied` | refuses `premultiplied` (ffmpeg-skill overlay composites straight alpha) | both | Settled: a reader's limit, not a spec change |
| T4 | motion-graphics-skill | `sha256` is hex | compares it case-insensitively, so an upper-case hash is read | lower-case hex only (hyperframes and Node write lower case) | Settled |
| T5 | video-production-agent (`editing.py`) | `cut_point` unrounded, at least 6 decimals | stores it rounded to 3 decimals | not affected | Already in the spec as a known gap; the agent's follow-up |
| T6 | video-production-agent | `cover` is `{start, end}` | its request key also takes `"S-E"` | object only: `"S-E"` is a request form, not the file's | Settled |
| T7 | hyperframes-skill `sidecar.mjs` | `cut_point_frame` = `round(cut_point * frame_rate)`; the sidecar's naming is PROPOSED | writes `cut_point * frame_rate` (an integer, since the time is exact); `<stem>.<kind>.json`, and `sha256` absent for a PNG sequence | `cut_point_frame` must equal the rounded value (rule); `sha256` optional | Agrees |
| T8 | the spec | readers' bounds (the agent's 0-60 s `cut_point`, rendered_layer's 60 s `in` / `out`) | each reader refuses beyond its bound | not in the schema: they are a reader's limits, not the file's shape | Settled |
| T9 | the spec | `text[]`: `{role, text, lang, font, font_size}`; `safe_area` in pixels | hyperframes writes all five, and `safe_area` as integers | `text[]` needs `role` and `text`; `safe_area` integers | Settled here |

### Licence record

| # | Where | The spec says | The implementation does | Schema | Status |
|---|---|---|---|---|---|
| L1 | sound-design-skill `schemas/licence-record.schema.json` | an entry requires `licence` | requires `licence`, `kind`, `tags`, `mood`, `loopable`, `sha256`, `measured` and the three `imported_*` | requires `licence` only, so every sound-design entry is valid here and not the other way round | Settled: sound-design's schema is stricter, and its own |
| L2 | sound-design-skill | the extension: `kind` `video` / `image`, `asset_id`, `ai_generated` (PROPOSED) | `kind` is `bgm` / `sfx`; no `asset_id` or `ai_generated` | the extension is optional, in the entry and the record | **Open**: whether sound-design-skill's schema takes the extension or Velisa's stays the only one |
| L3 | the spec | "the same record, with" the extension, without saying the record carries `asset_id` / `ai_generated` | no writer yet | optional in the record | Settled here |
| L4 | artifacts-skill `credits_check.py` | it reads the records "as they are" | names each record by `asset`, `file` or `title`; a record has `title` only | not affected | Settled: `title` is enough; noted for when video and image records arrive without a title |
| L5 | the spec | `status: unknown` gives `licence: "unknown"` and `usable: false`; `declared` gives `usable: true` | sound-design writes it so | enforced (`if` / `then`) | Agrees |

## Trial results (2026-11-19)

- **hyperframes-skill** (writer): `tests/velisa-conformance.test.mjs` checks the copy's hashes, that ajv (8.17.1, a new
  devDependency, strict mode) agrees with Velisa on every fixture, that `SIDECAR`'s read and proposed lists are exactly the
  schema's required and other properties, and that what `buildSidecar` writes validates, with and without a file, alpha
  and text. Everything it writes passed on the first run.
- **motion-graphics-skill** (reader): `tests/test_velisa_title_conformance.py` reads every valid `title.json` fixture with
  `resolve_title_json` and checks the mapping table (`in_duration`, `out_duration`, `loop`). Six of nine invalid fixtures
  are refused by `map_title`. The other three are listed in the test with the reason (T2, T4, and `segment_frames`, which
  it does not read). A new invalid fixture that is neither refused nor listed fails the test.

## Consequences

- A spec change goes with its schema and fixtures in the same pull request; the CI fails otherwise
  (`test_every_spec_document_links_its_schema`, the manifest check).
- A Skill's copy goes stale silently until it re-exports. That is the price of offline, pinned tests. The manifest's
  `source.commit` says how old a copy is.
- The open rows (K1, K2, K3, K5, L2) are decisions for the spec owner and ffmpeg-skill or sound-design-skill. Until
  then a kit with the kit@1 keys cannot be handed to ffmpeg-skill as it is (K1).

## What follows

- The spec prose for K6 and T1 (who reads what) is updated in a later docs pull request.
- Further Skills take the fixtures one at a time: video-editing-skill and qc-skill (`stinger`), thumbnail-skill,
  remotion-ffmpeg-skill and motion-graphics-skill (`kit`), sound-design-skill and artifacts-skill (`licence-record`).
- ffmpeg-skill is not changed (K1-K3, K5).
