# Sidecar envelope: the common outer fields of a sidecar JSON file

**Status: SPEC** (owner decision 2026-11-19, details delegated; [DECISION_LOG](../ecosystem/DECISION_LOG.md) D39,
[ADR-025](../adr/ADR-025-sidecar-envelope.md)). No Skill writes the envelope yet. Adopting it is one follow-up per Skill,
listed at the end; until a Skill adopts it, nothing changes for it.

Machine-readable schema: [`registry/schemas/sidecar-envelope.schema.json`](../../registry/schemas/sidecar-envelope.schema.json)
(JSON Schema 2020-12), with valid and invalid examples in `registry/conformance/sidecar-envelope/`.

A **sidecar** is a JSON file a Skill writes beside an output it made, about that output: `lower-third.title.json` beside
`lower-third.mov`, `final.srt.subtitle-skill.json` beside `final.srt`. Each Skill's sidecar has its own body. The envelope
is the four fields every one of them carries, so any reader can tell what wrote the file, when, from which inputs, and
in which shape, without knowing the body.

## The four fields

They sit at the top level of the sidecar, beside the body's own fields.

| Field | Type | Meaning |
|---|---|---|
| `schema` | `"<namespace>/<name>@<major>"` | the spec of the whole file, its name and major version: `velisa/title@1`, `subtitle-skill/output@1`. The same convention `kit@1`, `title@1`, `stinger@1` and motion-graphics-skill `theme@1` already use. A reader refuses a major it does not know |
| `producer` | `{skill_id, version}` | the Skill that wrote the file: its id as its contract states it, which is not always the repository's name (`hyperframes-skill`, but `motion-graphics` for motion-graphics-skill), and its SemVer version (`0.10.4`) |
| `generated_at` | text | when the file was written: UTC, RFC 3339 with `Z` (`2026-11-19T10:00:00Z`, fractions of a second allowed) |
| `inputs` | `[{sha256, file?, role?}]` | every input medium the output was made from, by the sha256 of its content; `file` is its name (never a path), `role` what it was to the producer (`source`, `music`, `logo`). An empty list when the output was made from no medium (a render from a template alone) |

Rules:

- **Nothing is inferred.** An input is listed only when the producer read its bytes and hashed them. A file passed by
  path and never opened is not an input here.
- **The output itself is not an input.** A body that describes one file names it in its own fields (`title.json` `file`
  and `sha256`); the envelope does not repeat it.
- **No paths, no host names, no user names.** `file` is a base name. A sidecar can travel with the output.
- **The body is the body spec's.** The envelope schema allows any other top-level key. A body spec that adopts the
  envelope lists the four fields among its own (its schema is the envelope's schema `allOf` its body), and a closed body
  schema (`additionalProperties: false`, as `title@1` and `stinger@1` are) adds them explicitly.
- **Adding the envelope to an existing sidecar is additive** for its readers when they ignore keys they do not know.
  motion-graphics-skill's `title_json` reader does; a body schema that is closed has to list the four fields first,
  which is a minor version of that spec, not a major one.

## Which sidecars exist (2026-11-19, each repository's `origin/main`)

What each Skill writes beside an output today, and what of the envelope it already has.

| Skill | File | Shape id | Producer | Time | Input hashes |
|---|---|---|---|---|---|
| hyperframes-skill | `<stem>.title.json`, `<stem>.stinger.json` (`lib/sidecar.mjs`) | `schema: velisa/title@1` / `velisa/stinger@1` | none | none | none (`sha256` is the output's) |
| subtitle-skill | `<output>.subtitle-skill.json` (`operations.py` `_write_sidecar`) | none | `skill`, `skill_version` | none | none (`sha256` is the output's; `identity` hashes the request) |
| audio-production-skill | `<intermediate>.json` per node (`executor.py`) | `schema: audio-production/manifest@1` | `skill`, `skill_version`, `tool_versions` | none | `input_hashes` (a list of sha256) |
| color-grading-skill | `<intermediate>.<ext>.json` per node (`executor.py`) | `schema: color-grading/manifest@1` | `skill`, `skill_version`, `tool_versions` | none | `input_hash` (one sha256) |
| motion-graphics-skill | `<intermediate>.json` per stage and per generated clip (`executor.py`); the layer-export manifest | `schema: motion-graphics/manifest@1` | `skill`, `skill_version`, `tool_versions` | none | `input_hashes` (the previous stage's identity, not a content hash) |
| video-editing-skill | `seg_<key>.json` per cut segment, `<operation>.json` per operation, in its work directory (`executor.py`) | none | none (hashed into the key) | none | the input's identity is hashed into the key |
| sound-design-skill | `sound-library.json` at a library's root: one entry per file (licence record) | none | `imported_by: "<skill> <version>"` per entry | `imported_at` per entry | `sha256` per entry (the file's own) |
| nle-bridge-skill | an SRT beside an exported timeline | not JSON | | | |

Only the first two are meant for another program to read. The work-directory manifests (audio-production, color-grading,
motion-graphics, video-editing) are reuse caches that only their own Skill reads; the envelope is optional for them.
`sound-library.json` is a library index, not a sidecar of one output; it keeps its per-entry fields (licence-record spec).

## Follow-up tasks (not done here)

One per Skill, each additive, each in its own repository:

1. **hyperframes-skill**: add `producer`, `generated_at` and `inputs` to `title.json` and `stinger.json` (`inputs`: the
   scene's media files by sha256; empty for a template with no media). Needs `title@1` and `stinger@1` to list the
   four fields first (a Velisa spec change, minor).
2. **subtitle-skill**: add `schema` (`subtitle-skill/output@1`), `producer` (from `skill` / `skill_version`, which stay),
   `generated_at` and `inputs` (the transcript or source file's sha256, when it read one).
3. **audio-production-skill** and **color-grading-skill** (optional, work-directory manifests): add `producer`,
   `generated_at`, and `inputs` beside `input_hashes` / `input_hash`, which stay.
4. **motion-graphics-skill** and **video-editing-skill** (optional, work-directory manifests): the same, when a reader
   outside the Skill appears.
5. **Velisa**: once two Skills write it, a check in skillpact's conformance job (ADR-014) that a declared sidecar
   validates against the envelope schema.
