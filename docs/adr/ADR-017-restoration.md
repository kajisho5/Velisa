# ADR-017: Restoration (Super-Resolution and Frame Interpolation)

Status: Proposed

## Context

Super-resolution and frame interpolation for archive footage and low-resolution sources were
proposed as a new area (`docs/ecosystem/ROADMAP.md`, "New areas"). On 2026-11-12 the owner decided:
no new skill now; wire the baseline that uses no weights first; a skill only after an ADR records
the weights' licences ([DECISION_LOG](../ecosystem/DECISION_LOG.md) D19; evidence in
`docs/ecosystem/ownership-audit/C-command-ingest-engine-verification.md` §9(g)).

What ffmpeg-skill has today (as the audit read it at `11c153e`):

| Job | Tool | What it does |
|---|---|---|
| Scaling | `fit --width/--height`, `export` preset scaling | interpolation only; adds no detail |
| Frame-rate change | `fit --fps` | duplicates or drops frames |
| Motion interpolation | `fit --smooth interpolate` (`minterpolate`) | only when slowing down; there is no stand-alone "raise the frame rate" operation |
| Noise reduction | `denoise` (hqdn3d) | reduces detail as well, as its own docs say |
| Deinterlacing | `deinterlace` (yadif) | |
| Stabilisation | `stabilize` (vidstab, two passes) | |

## Decision (proposed)

1. **Baseline first, no weights.** The agent gets an "archive preparation" path built from the
   tools above (for example `deinterlace` → `denoise` → `stabilize` → `fit`). FFmpeg only, no new
   dependency, deterministic. This needs a `denoise` SkillSpec in video-production-agent. A
   stand-alone frame-rate-raising interpolation in `fit` would be a new proposal to ffmpeg-skill,
   decided there.
2. **One engine interface for anything with weights:** frames in, frames out, a scale or rate
   factor, engines swappable; frames are extracted and reassembled through ffmpeg-skill with the
   source's audio; provenance names the engine, the weights and their licence; output is marked
   `AI_GENERATED` in the agent.
3. **Acceptance by measurement:** against a reference with qc-skill's VMAF / SSIM / PSNR, never by
   eye only.
4. **A restoration skill is created only when the table below is complete and the owner accepts
   this ADR.**

| Candidate | Job | Code licence | Weight licence | Status |
|---|---|---|---|---|
| ffmpeg-skill baseline (scaling, `minterpolate`, `denoise`) | both | FFmpeg's | no weights | available |
| Real-ESRGAN | super-resolution | BSD-3-Clause per the ROADMAP draft; to verify | to verify | not checked |
| frame interpolation engines | interpolation | to verify | to verify | none named yet |

## To verify before this ADR can be accepted

- The weight licence of every candidate model, from its own licence file or model card, separately
  from the code licence.
- The code licence of each runtime (PyTorch, ncnn or another backend) and of the candidate's own
  repository.
- Training-data terms, where stated.
- GPU and VRAM needs, measured on the target hardware; whether a CPU path is usable at all.
- How far results differ across GPUs and versions, since acceptance relies on qc-skill's metrics.
- Whether ffmpeg-skill would take a frame-rate-raising `fit` option (its decision, not this one).

## Consequences

- No new repository and no `ecosystem.json` entry until this ADR is accepted.
- The baseline path is the agent's work and can start now.
- An engine with weights never enters through ffmpeg-skill's `dnn_processing`: that would conflict
  with ffmpeg-skill's local-FFmpeg-only, same-input-same-output scope (inference, as the audit
  noted, not a recorded ffmpeg-skill decision).
