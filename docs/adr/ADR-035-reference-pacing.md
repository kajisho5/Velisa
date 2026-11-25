# ADR-035: Reference pacing and protected pauses

Status: Proposed for integration.

## Decision

The wire formats are [pacing-profile@1](../../registry/schemas/pacing-profile.schema.json)
and [protect-ranges@1](../../registry/schemas/protect-ranges.schema.json). The first is an object
identified by its contract field. The second is a bare array in source milliseconds relative to
the first picture. Each interval includes its start and excludes its end. End must exceed start
and fit the source. Overlaps are allowed. Runtime checks also enforce profile cross-field ordering,
finite measurements, and agreement between sample count and sample names.

For a reference-based request the agent must extract a profile from all named references, preview
the cut plan, apply the approved edit and run the independent source-bound verify gate. Handwritten
FFmpeg commands and generic silence removal cannot substitute for any stage. Discover the installed
silence and verify flags; a missing capability blocks the request.

When the profile reports a suspected music bed or low confidence, surface its reasons and warnings.
Request an isolated voice recording, an explicit preset or a manually reviewed profile. No estimated
threshold from that profile may silently drive the edit. The agent owns this decision.

Transcription or the upstream editorial caller converts requested word endings, intentional fillers
and contextual pauses into source intervals and records the reason. Pass the same intervals to
preview, edit and verification. If their timestamps are unknown, request timed input before cutting.
The engine measures the lossless master; a requested MP4 additionally passes the encoded delivery
checks. A human approves semantic deletion. QC consumes the independent gate's measured results.
