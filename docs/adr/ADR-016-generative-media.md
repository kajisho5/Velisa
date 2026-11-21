# ADR-016: Generative Media (Images and Video as Edit Material)

Status: Proposed

## Context

The 2026-11-05 field review proposed a `generative-media-skill`: generated stills and video clips as
edit material (inserts, backgrounds, establishing shots) behind swappable local engines. On
2026-11-12 the owner decided not to create it until this ADR is settled
([DECISION_LOG](../ecosystem/DECISION_LOG.md) D18; evidence in
`docs/ecosystem/ownership-audit/A-visual.md` §9(e)).

What exists today (read from each repository's `origin/main` on 2026-11-12):

- **thumbnail-skill** `generate_background` is the only generator. It asks one provider class
  (`BackgroundProvider` in `src/thumbnail_skill/background.py`: `provider_id`, `engine`, `model`,
  `licence`, `licence_url`, `model_card`, `configure_env`, `status()`, `generate(prompt, width,
  height, seed, steps, guidance_scale)`) for an image from a caller-written prompt and an explicit
  seed. The one provider runs FLUX.2 [klein] 4B from local weights only, never downloads a model,
  and the code records its licence as Apache-2.0. The generated image becomes an ordinary image asset,
  so composition stays deterministic. ADR-012 of this repository allows exactly this engine and not
  the non-commercial 9B variant.
- **video-editing-skill** ADR-022: an inserted clip that was generated is declared by the caller
  (`sources[].ai_generated {generator, licence}`) and marked `AI_GENERATED`. It generates nothing.
- **Video generation** exists nowhere in the ecosystem.

## Decision (proposed)

No skill and no engine is added until the table below is filled from primary sources (the
licence files and model cards themselves) and reviewed by the owner. When it is:

1. Each candidate engine gets one row: code licence, weight licence, commercial terms (including any
   revenue or user-count limits), VRAM and hardware, whether it runs from local weights only, and
   what it records about its output.
2. A candidate whose weights are non-commercial or unclear is not used.
3. Whether stills reuse thumbnail-skill's `BackgroundProvider` interface (and so live in, or are
   shared with, thumbnail-skill) or need their own owner is decided here, before any new repository.
4. Every output is marked `AI_GENERATED` with the engine, the weights and their licence, as
   video-editing-skill ADR-022 already expects for inserted clips.

| Candidate | Code licence | Weight licence | Commercial terms | VRAM | Status |
|---|---|---|---|---|---|
| FLUX.2 [klein] 4B (stills; in use in thumbnail-skill) | to verify | recorded as Apache-2.0 in thumbnail-skill's code; the model card was not read for this ADR | to verify | about 13 GB (as `ecosystem.json` states) | in use for thumbnail backgrounds |
| LTX-2 (video) | to verify | to verify | to verify | to verify | named in the 2026-11-05 draft; nothing checked |
| others | — | — | — | — | none listed yet |

## To verify before this ADR can be accepted

- The weight licence of each candidate, from its own licence file and model card (the audit did not
  read them over the network; for FLUX.2 [klein] 4B only thumbnail-skill's record was read).
- The code licence of each candidate's runtime (pipeline library, custom nodes).
- Commercial-use terms, including thresholds by revenue or users, and any acceptable-use policy.
- Training-data statements, where the model card makes them.
- Whether outputs carry a watermark or an embedded label, and whether one is required.
- VRAM and run time on the hardware this ecosystem targets, measured.
- Determinism: a fixed seed may not give the same pixels across GPUs and drivers (not measured); the
  acceptance rule for generated material has to say what is compared.

## Consequences

- Until this ADR is accepted, no agent wiring and no request to ffmpeg-skill follow from it.
- thumbnail-skill keeps its own background generator unchanged.
- The ROADMAP's "New skill candidates" table points here.
