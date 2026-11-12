# `kit@1`: one brand kit, mapped to each renderer's existing input

**Status: SPEC** (owner decision 2026-11-12, [DECISION_LOG](../ecosystem/DECISION_LOG.md) D16).
There is no design-system skill; this page is the shape and the mapping. Revisit as a skill once
three or more renderers read `kit@1` directly. Fields marked **(PROPOSED)** are read by no renderer
today.

Read from (each repository's `origin/main`, 2026-11-12): ffmpeg-skill `11c153e`
(`scripts/_common/decision.py` `BRAND_DEFAULTS` / `load_brand`, `references/scripts.md` "brand.json",
`examples/brand.json`), motion-graphics-skill `8e3fcb6` (`docs/decisions.md` ADR-24 and ADR-29,
`motion-graphics/theme@1`), remotion-ffmpeg-skill `d135b3b` (`scripts/_common.py` `brand_look`),
thumbnail-skill `bca8ee2` (README, `src/thumbnail_skill/contract.py`), imagemagick-skill `ab89bf9`
(`brandkit.py` in SKILL.md), hyperframes-skill `3528095` (`ECOSYSTEM_ROADMAP.md` step 14).

## Rule: a superset of ffmpeg-skill `brand.json`

Every `brand.json` is a valid `kit@1`, and every key `brand.json` defines keeps its meaning and its
spelling. `kit@1` only adds keys. So a kit file can be passed as it is to the two readers that take
`brand.json` today: ffmpeg-skill (`load_brand` merges the file over its defaults; keys it does not
use are kept and ignored) and remotion-ffmpeg-skill (`brand_look` reads only the keys below).

### Keys from `brand.json` (existing)

| Key | Type | ffmpeg-skill default |
|---|---|---|
| `font` | family name | `DejaVu Sans` |
| `font_file` | path, relative to the kit file | none |
| `colors` (also `colours` for remotion) | `{primary, text, outline, background, accent}`, each `RRGGBB` without `#` | `FFD200`, `FFFFFF`, `000000`, `101418`, `1E6F8E` |
| `logo` | path, relative to the kit file | none |
| `logo_position` | `top-left` \| `top-right` \| `bottom-left` \| `bottom-right` and the other ffmpeg-skill position names | `top-right` |
| `logo_scale` | logo width in px (`overlay --scale`) | 160 |
| `logo_opacity` | 0-1 | 0.9 |
| `safe_margin` | px | 48 |
| `lang` | language / script hint (`--lang`) | none |
| `styles.caption` | `{font, size, colour \| color, box, position}`: the one caption look | none |
| `caption` | `{size, position, animate, karaoke, bold, outline}`: burn-in defaults; `styles.caption` wins where both set a key | `26`, `bottom`, `pop`, `false`, `true`, `2` |
| `loudness` | `{lufs, tp}` | `-14`, `-1` |

### Keys added by `kit@1` (PROPOSED)

| Key | Type | Why |
|---|---|---|
| `schema` | `"velisa/kit@1"` | the shape's id; absent in a plain `brand.json` |
| `name` | text | the kit's name, as motion-graphics `theme@1` has one |
| `colors.secondary` | `RRGGBB` | motion-graphics-skill's fourth colour role; `brand.json` has none |
| `fonts` | `[{family, file, licence, embedding}]` | the font licence (OFL, Apache, commercial) and whether it allows embedding in video, recorded, not inferred |
| `logo_variants` | `{color, mono, white, black, clear_space}` paths | what imagemagick-skill `brandkit.py` writes from one logo |
| `contrast` | `[{fg, bg, ratio}]` | the pairs checked and their ratio, when a tool has checked them |

## Mapping to each renderer's existing input

| Renderer | What it reads today | From `kit@1` |
|---|---|---|
| ffmpeg-skill | `--brand brand.json` on `caption`, `overlay --logo`, `graphics`; `"brand"` in a `render` project; explicit flags win | the file itself |
| remotion-ffmpeg-skill | `--brand brand.json` on `render` / `still` / `pipeline`: `colors.primary` → `accent`, `colors.text` → `textColor` (the caption colour wins), `styles.caption.font` or `font` → `fontFamily`, `font_file`; `logo`, safe margins and loudness only on delivery (`deliver.py` / `pipeline.py --brand`); caption `size` / `position` / `animate` / `box` / `outline` are reported unused | the file itself |
| motion-graphics-skill, one theme | `options.themes` + `options.theme`, each a `motion-graphics/theme@1` file: `colors` with all four roles (opaque `RRGGBB` or a colour name), `font` (`font_id` or `font_file`), `logo` (`path`, `position`, `margin`, `scale_width`, `opacity`), `spacing.margin`, `base_style`, `name`. Unknown fields are refused (`bad_theme`), so a kit is converted, not passed | `colors.primary` / `secondary` / `background` / `text` → the four roles; `font_file` → `font.font_file`; `logo` → `logo.path`, `logo_position` → `logo.position` (one of its nine position names), `logo_scale` → `logo.scale_width`, `logo_opacity` → `logo.opacity`, `safe_margin` → `spacing.margin` and `logo.margin`; `name` → `name` |
| motion-graphics-skill, colours only | `options.brand_kit`: `{primary?, secondary?, background?, text?}` (opaque, no `@alpha`); refused together with a theme | the same four colour roles |
| thumbnail-skill | no brand input. Colours are `#RRGGBB` / `#RRGGBBAA` per element (`canvas.background`, text `color`, `stroke.color`, `background.color`); fonts only by registered `font_id`; `variants.palettes`: `[{name, color, background?, stroke?}]` | the caller writes `#` + the kit's colours into the request (for example `colors.text` → text `color`, `colors.background` → `canvas.background`, `colors.outline` → `stroke.color`); `font` has no counterpart until a `font_id` is registered for it |
| hyperframes-skill | no brand input; template values per request. Roadmap step 14 plans "a brand kit as input" | the caller fills template values from the kit; step 14 is the place to read `kit@1` |
| imagemagick-skill | `brandkit.py` makes logo variants and a palette from one logo; it reads no kit | its outputs fill `logo_variants` and a palette |

Rules for a converter (the agent, or a person):

- Only what the kit states is passed on. ffmpeg-skill's defaults are not the user's choice
  (remotion-ffmpeg-skill already follows this rule).
- Without `colors.secondary`, a motion-graphics theme cannot be made from the kit (all four roles are
  required); use `options.brand_kit` with the roles the kit has instead. Using `accent` as
  `secondary` is a choice to state, not a default **(PROPOSED)**.
- `#` is added for thumbnail-skill and removed nowhere else.

## Not in this spec

Checking a kit (contrast of every pair, font licences, logo sizes), generating palettes, and an
event pack from a CSV were parts of the design-system-skill draft. motion-graphics-skill checks
contrast for its own templates (`theme-check`); the rest has no owner until the skill is revisited.
