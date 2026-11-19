# ADR-025: A Common Envelope for Sidecar JSON Files

Status: Accepted (decision D39). Spec and schema only; no Skill writes the envelope yet.

## Context

Several Skills write a JSON file beside an output they made (the inventory is in
[`docs/specs/sidecar-envelope.md`](../specs/sidecar-envelope.md)). Each one says some of the same things in its own way:

- which shape the file is: `schema: velisa/title@1` in hyperframes-skill; `schema: <skill>/manifest@1` in
  audio-production, color-grading and motion-graphics; nothing in subtitle-skill or video-editing-skill;
- who wrote it: `skill` + `skill_version` in four Skills, `imported_by: "<skill> <version>"` in sound-design-skill,
  nothing in hyperframes-skill;
- when: only sound-design-skill (`imported_at`);
- from which inputs: `input_hashes` (a list), `input_hash` (one), an identity hashed into a key, or nothing.

A reader that wants to know whether a sidecar is stale, or which version of a Skill wrote it, has to know each Skill's
spelling. Provenance (ADR-008) needs the same facts.

## Decision

1. **Four top-level fields, the same in every sidecar**: `schema` (`<namespace>/<name>@<major>`), `producer`
   (`{skill_id, version}`), `generated_at` (UTC, RFC 3339 with `Z`) and `inputs` (`[{sha256, file?, role?}]`, empty when
   no medium went in). The spec is `docs/specs/sidecar-envelope.md`; the schema is
   `registry/schemas/sidecar-envelope.schema.json`, with fixtures in `registry/conformance/sidecar-envelope/`.
2. **Top level, not nested.** hyperframes-skill's sidecars already carry `schema` at the top level, and five Skills
   already spell the shape id `x/y@N`. Nesting the four fields under one key would move a field that a reader
   (motion-graphics-skill's `title_json`) already reads.
3. **`schema` carries the spec's name and version in one string**, as `kit@1`, `title@1`, `stinger@1` and `theme@1`
   already do. A separate `{name, version}` object would repeat it.
4. **`producer.skill_id` is the id the Skill's contract states.** It is not always the repository's name
   (`motion-graphics` for motion-graphics-skill). `version` is SemVer.
5. **`inputs` holds content hashes of media the producer read**, never paths. The described output is not an input; a
   body that describes one file keeps naming it itself (`title.json` `file` and `sha256`).
6. **The envelope schema is open**: it allows any other key, since the body is the body spec's. A closed body schema
   (`title@1`, `stinger@1`) lists the four fields before its writer adds them. That is a minor change of that spec.
7. **Nothing is adopted in this change.** Each Skill adopts it in its own pull request, additively; the list is in the
   spec, "Follow-up tasks".

## Alternatives considered

- **A separate `<output>.provenance.json` per output.** One more file to keep in step with the output, and the
  sidecars already exist. Rejected.
- **Reusing each Skill's existing keys (`skill`, `skill_version`, `input_hashes`) as the standard.** They differ
  between Skills (`input_hash` vs `input_hashes`; motion-graphics' `input_hashes` holds a stage identity, not a content
  hash). The new names avoid changing what those keys mean; the old keys stay where they are.

## Consequences

- A sidecar that adopts the envelope can be checked by anyone with one schema, whatever its body.
- `generated_at` makes a sidecar's bytes differ between two runs of the same input. A Skill whose reuse check compares
  the whole sidecar (subtitle-skill compares `identity` and `sha256` only, so it is not affected) must leave
  `generated_at` out of that comparison.
- A sidecar is not a ProductionReceipt (ADR-008): the envelope says who wrote one file from what, not what a whole run did.
