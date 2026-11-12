# Licence record: one shape for music, sound effects, footage and images

**Status: SPEC** (owner decision 2026-11-12, [DECISION_LOG](../ecosystem/DECISION_LOG.md) D17). There
is no asset-library skill. The shape is the one `sound-design-skill` already writes for its library
files; this page extends it to video and images. Fields marked **(PROPOSED)** are written by no skill
today. Project credits keep being checked by `artifacts-skill` `credits_attribution`.

Read from (each repository's `origin/main`, 2026-11-12): sound-design-skill `d974c26`
(`src/sound_design_skill/library.py` `licence_info`, `attribution_line`, `licence_warnings`, the
`library-import` entry; `src/sound_design_skill/cli.py` `library-import`;
`src/sound_design_skill/contract.py` `provenance.library_fields`; `SKILL.md`), artifacts-skill `ae039d3`
(`SKILL.md`, `licence_records`).

## Principles (as sound-design-skill applies them)

- A licence is recorded exactly as declared, with `verified: false`. No skill checks or clears a
  licence: say "declared as CC-BY-4.0", never "cleared".
- A missing, empty or placeholder licence (`unknown`, `n/a`, ...) is refused at import
  (`LICENCE_REQUIRED`). A file without a declared licence is reported as `licence: "unknown"` and is
  not used.
- Nothing is inferred or filled in. A part that was not declared is left out.

## The stored entry

One entry per file, keyed by its path inside the library (`/`-separated, Unicode NFC).
sound-design-skill keeps them in `sound-library.json` in the library folder.

| Field | Type | Meaning |
|---|---|---|
| `licence` | text | as declared: an SPDX id (`CC-BY-4.0`, `CC0-1.0`) or the licence's name or text; required |
| `kind` | `bgm` \| `sfx` | what the file is; extended below |
| `source` | text | where it came from: the source URL, or text |
| `provider` | text | the site or service it was downloaded from (e.g. Freesound, YouTube Audio Library) |
| `author` | text | author / composer |
| `title` | text | the work's title |
| `credit` | text | the credit line the licence asks for |
| `attribution` | text | the attribution line exactly as the source asks for it |
| `licence_url` | URL | the licence's address, recorded, never opened |
| `licence_file` | path | the licence text that came with the download, copied into `<library>/licences/` |
| `licence_text_sha256` | hex | that text's hash |
| `content_id` | `registered` \| `not-registered` | only as the source states it; anything else reads as `unknown` |
| `sha256` | hex | the file's content at import; a later mismatch is reported |
| `measured` | object | probed facts (duration, streams; for audio also loudness) |
| `imported_from`, `imported_at`, `imported_by` | file name, UTC time, `<skill> <version>` | how the entry was made |
| `tags`, `mood`, `loopable` | lists, boolean | for selection; not part of the licence |

## The record a reader gets

Readers get the entry resolved into one record (sound-design-skill `licence_info`, in
`library-index` rows and in the `licence` block of provenance):

| Field | Meaning |
|---|---|
| `licence` | the declared text, or `unknown` |
| `status` | `declared` \| `unknown` |
| `declared_as` | the raw declared value |
| `verified` | always `false` |
| `usable` | `true` only for a declared licence |
| `declared_in` | the manifest file name |
| `source`, `provider`, `author`, `title`, `credit`, `licence_url`, `licence_file`, `licence_text_sha256`, `content_id` | as stored |
| `attribution` | the line to show with the video |
| `attribution_source` | `declared` (the `attribution` field), `credit` (the `credit` field), `composed` (for a Creative Commons attribution licence: `"Title" by Author (source), licensed under <licence> (<licence URL>)`, from the declared parts only), or `null` |
| `note` | a plain sentence saying the licence is declared, not verified |

Warnings that go with it (plain facts, never a judgement that the file is cleared): a
non-commercial term; a no-derivatives term on a trimmed or looped file; a CC BY licence with no
credit; a composed attribution line to check against the source's wording; `content_id: registered`
(a video using it may receive a Content ID claim).

## How credits are checked

`artifacts-skill` reads `licence_records` in its policy: one record per asset used, with `asset`,
`licence` and, where the licence asks for one, `attribution` or `credit`, `author`, `title`,
`licence_url`. It reads sound-design-skill's records and `library-index` rows as they are. The
`credits_attribution` check fails for each asset whose required attribution is missing or not worded
as its record asks. A record in this shape for video or images is read the same way.

## Extended to video and images (PROPOSED)

The same entry and record, with:

| Field | Change |
|---|---|
| `kind` | adds `video` and `image` (stock footage, photos, illustrations, meme clips) |
| `source` | for a download through `ingest-skill fetch`, the URL `fetch` recorded |
| `asset_id` | the source's own id for the asset, when it has one |
| `ai_generated` | `{generator, licence}`, the same fields video-editing-skill's `sources[].ai_generated` takes (its ADR-022), when the asset was generated |

Rules that carry over unchanged: declared, never verified; refused without a licence; a file
without a declared licence is not used. Before any stock API is wired, its terms of use are read and
recorded; none has been read for this spec.
