# ADR-030: A Kit Is Projected onto ffmpeg-skill's Brand Keys Before It Is Passed

Status: Accepted (decision D45). Decides rows K1 and K3 of [ADR-024](ADR-024-spec-schemas-and-conformance-fixtures.md).

## Context

`kit@1` ([spec](../specs/kit.md)) is a superset of ffmpeg-skill's `brand.json`, and the spec said a kit file could be
passed to ffmpeg-skill as it is, because ffmpeg-skill kept and ignored the keys it did not use. ffmpeg-skill now refuses
every brand-file key it does not read (`check_brand_keys`, ffmpeg-skill #510): the keys kit@1 adds (`schema`, `name`,
`colors.secondary`, `fonts`, `logo_variants`, `contrast`) and the `colours` spelling stop it with an input error.
ADR-024 recorded the difference as K1 and K3.

Two ways out: ffmpeg-skill accepts the kit@1 keys and `colours`, or the spec says how a kit is converted for it.
ffmpeg-skill is maintained apart and Velisa does not change it. Its refusal also catches real misspellings
(`safe_margn`), which accepting extra keys would give up.

## Decision

1. A consumer that hands a kit to ffmpeg-skill (`--brand`, or `"brand"` in a `render` project) writes a projection
   first and passes that, never the kit file:
   - only the keys of the spec's "Keys from `brand.json`" table, at the top level and in `colors`, `caption` and
     `styles.caption`; the keys kit@1 adds are left out;
   - `colours` is written as `colors`;
   - `logo` and `font_file` are resolved against the kit file's directory and written as absolute paths;
   - nothing is added: a key the kit does not state stays absent, so ffmpeg-skill's own defaults apply.
2. `colours` stays an accepted kit spelling (remotion-ffmpeg-skill reads it; never together with `colors`). The schema
   and fixtures are unchanged.
3. ffmpeg-skill is not changed. The keys it reads beyond the spec's table (K2) and `"X,Y"` positions (K5) stay open.

## Consumers checked (each repository's `origin/main`, 2026-11-20)

| Consumer | Hands a kit to ffmpeg-skill | Follow-up |
|---|---|---|
| remotion-ffmpeg-skill `deliver.py` / `pipeline.py --brand` (`f14b27c`) | yes: the `--brand` file is passed unchanged to ffmpeg-skill's delivery template | [remotion-ffmpeg-skill#32](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/32) |
| motion-graphics-skill `options.kit` (ADR-31) | no: maps the kit onto its own theme / `brand_kit` | none |
| thumbnail-skill `--kit` (ADR-18) | no: reads the kit itself | none |
| hyperframes-skill `--kit` (`lib/kit.mjs`) | no: reads the kit itself | none |
| video-production-agent | no: passes no brand file | none |

## Consequences

- A kit file works with every reader, at the price of one conversion step in each consumer that calls ffmpeg-skill.
- ffmpeg-skill keeps refusing unknown brand keys, so a misspelt key is still caught.
