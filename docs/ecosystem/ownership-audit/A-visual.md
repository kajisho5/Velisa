# 所有範囲監査 A: 映像部門と静止画ユーティリティ

調査日 2026-11-12。読み取り専用。すべて `origin/main` を `git show` / `git grep` で読んだ(作業ツリーには触れていない)。
表記: 根拠は `repo@sha:path:行` または「ファイル + 引用した識別子」。**推測** = 推論。**未確認** = 読めなかった・確かめられなかった。

## 1. 読んだもの

| repo | commit | version | 読んだファイル | 未確認 |
|---|---|---|---|---|
| motion-graphics-skill | 8e3fcb6 | 0.2.19 (pyproject, tag v0.2.19) | SKILL.md, ECOSYSTEM_ROADMAP.md, `src/motion_graphics/contract.py` 全体, `model.py`(要素表・未対応表), `themes.py` 冒頭, `styles.py`(grep), docs/decisions.md 見出し, CHANGELOG 見出し | README, CLAUDE.md, `executor.py`, `textfit.py` 本体は未読(契約と ROADMAP の記述に依拠) |
| hyperframes-skill | 3528095 | 0.8.0 (package.json, tag v0.8.0) | ECOSYSTEM_ROADMAP.md, `lib/contract.mjs`, `lib/scene-spec.mjs`(grep), `lib/tools/render.mjs`(grep), `templates/lower-third.json`, docs/design-decisions.md D12・D13, CHANGELOG 冒頭 | README, SKILL.md, `lib/tools/batch.mjs` `template.mjs` 本体は未読 |
| remotion-ffmpeg-skill | d135b3b | 0.13.0 (package.json, tag v0.13.0) | SKILL.md 前半, ECOSYSTEM_ROADMAP.md, `scripts/_contract.py`(grep), `scripts/render.py` 引数, `scripts/_common.py`(brand), `compositions/Pip.tsx` 冒頭, テンプレート package.json | ROADMAP.md(自前), `Emphasis.tsx` 本体, 決定性の記述(後述) |
| blender-skill | 4214430 | 0.31.0 (package.json)。ローカルにタグなし | ECOSYSTEM_ROADMAP.md, `scripts/_contract.py`, `scripts/scene.py` 引数, `scripts/render.py`(grep) | 最新タグ(未確認: ローカルにタグが無い。release PR #167 が 0.32.0 を準備中), README, SKILL.md |
| thumbnail-skill | bca8ee2 | 0.1.16 (pyproject, tag v0.1.16) | ECOSYSTEM_ROADMAP.md, pyproject, `background.py`(grep), `contract.py` の tool_id | SKILL.md, README, `renderer.py`。CJK/RTL の扱い(grep で該当なし) |
| subtitle-skill | da597e5 | 0.9.1 (pyproject, tag v0.9.1) | ECOSYSTEM_ROADMAP.md, `contract.py` 20-60行, `engine.py`(grep), README 724-745行 | CLAUDE.md, ADR 本文(見出しと ROADMAP の要約のみ) |
| video-editing-skill | 078c279 | 0.7.2 (pyproject, tag v0.7.2) | ECOSYSTEM_ROADMAP.md, `operations.py`(OPERATIONS 表・stinger), docs/decisions.md 見出し | CLAUDE.md, SKILL.md, `compiler.py` |
| color-grading-skill | 0ddeaac | 1.1.0 (pyproject, tag v1.1.0) | ECOSYSTEM_ROADMAP.md, pyproject | 契約ソース・コード本体は未読(このスライスの重複に関係が薄いため ROADMAP のみ) |
| imagemagick-skill | ab89bf9 | 0.10.0 (package.json, tag v0.10.0) | ECOSYSTEM_ROADMAP.md, `scripts/brandkit.py` 冒頭と引数, ファイル一覧 | `skill.contract.json`, `preset.py`, `overlay.py` 本体 |
| ffmpeg-skill (読み取りのみ) | 11c153e | 3.6.5 (package.json / plugin.json。到達可能な最新タグは v3.6.3) | `scripts/{overlay,graphics,caption,waveform,loop,export,background,insert}.py` の引数, `broll.py` 冒頭, `_common/decision.py` 1000-1016 (BRAND_DEFAULTS), issue #417-#426 | 各スクリプトの本体ロジック |
| Velisa (AI-video-production-OS) | 45a40f1 | tag v0.9.0 | `ecosystem.json` 全体, docs/ecosystem/ROADMAP.md 276-298・332-437, CAPABILITY_MATRIX.md・REPOSITORY_MAP.md・CROSS_REPO_STATUS.md・HANDOFF.md・CURRENT_STATE.md・DECISION_LOG.md(このスライスの語で grep) | 上記 6 文書の全文通読はしていない |
| video-production-agent (配線の確認) | b2d4e08 | 0.1.0 (pyproject) | `src/video_agent/skills/registry.py`(該当 SkillSpec), `agent/finishing.py` 118-145, `agent/editing.py`(stinger), pins 一覧 | 他は未読 |
| qc-skill (stinger / loop の確認) | b7475e9 | 1.3.0 (tag) | `src/qc_skill/contract.py`(grep), ECOSYSTEM_ROADMAP.md 40-43 | 他は未読 |

## 2. 各スキルが実際にできること

### motion-graphics-skill 0.2.19
- 入口は 1 つ: `motion-graphics/run`(型付き Graphics Document → 既存の動画に焼き込み)。`validate` / `plan` / `doctor` / `lower-thirds <csv>` / `theme-check` あり(SKILL.md、ROADMAP step 9・11)。
- 要素 15 種(`model.py:73-344`): `title` `lower_third` `bug` `chapter` `progress` `countdown` `sticker` `hook` `meme`(ffmpeg-skill `graphics` のテンプレート)、`text_overlay` `image_overlay` `video_overlay` `logo` `rendered_layer`(ffmpeg-skill `overlay`)、`shape`(`background` + `overlay`)。
- アニメーション: テンプレート内蔵(`builtin_fade` / `builtin_slide_fade` / `builtin_pulse` / `builtin_pop`)と、`text_overlay` / `image_overlay` だけの直線 `fade`。`slide` `move` `scale` `opacity_keyframes` は `UNSUPPORTED_ANIMATIONS`(`model.py:370-375`)。
- `rendered_layer`: 事前レンダー済みアルファ動画を `overlay --video --place` で置く。`in_duration` / `out_duration` / `loop`。VP9 アルファ WebM は拒否(`model.py:322-344`)。
- 文字組み: `elements[].fit`(`lower_third` / `title` のみ。縮小 → UAX #14 改行、`ja-kinsoku`、RTL を報告)。BudouX は未実装(ROADMAP step 9)。
- ブランド: `options.style`(6 プリセット)、`options.brand_kit`(4 色)、`options.themes` / `theme`(`motion-graphics/theme@1`: colors 4 役・font・logo・spacing・base_style、コントラスト警告。`themes.py:1-22`)。
- `options.layer_export`: 要素ごとの透明レイヤー(.mov)と manifest(契約 `layer_export`)。
- 範囲外と宣言(`contract.py` `not_provided`): AI 推論、デザイン判断、テンプレート選択、任意の ffmpeg フィルター、矩形以外の図形、位置・拡大のアニメーション、動画編集、色、字幕生成。
- 決定性: `deterministic: true`, `idempotency_hint: content_equivalent`(`contract.py` tools)。依存は ffmpeg-skill のみ(`dependencies = []`、pyproject:14)。

### hyperframes-skill 0.8.0
- ツール 7: `batch` `doctor` `preview` `probe` `render` `scene` `template`(package.json description、`lib/tools/`)。`provides` は `html_scene.<tool>`(`lib/contract.mjs` `provides()`)。
- シーン: `text` / `image` / `video` レイヤー(`scene-spec.mjs:28-31`)、遷移 `fade` `slide` `zoom`(:35)、ループ動作 `pulse` `bob` `spin`(:47)、`segments {in, loop, out}`(:54)、同梱フォント(@font-face、:23-27)、`lang`(BCP 47、:116-117)。
- 出力: h264 / vp9(アルファ) / prores(4444 アルファ) / png(RGBA 連番)(`render.mjs:34`)。`--segments` で `<stem>.in|loop|out` と `loop_seam` 計測(:39, :101-103)。アルファは全形式 straight、premultiplied は無い(D13)。
- テンプレート 4: `break` `lower-third` `session-slate` `title-card`(`templates/`)。CSV の `batch`(`demos/speakers-batch`)。
- 範囲外と宣言(`contract.mjs` `not_provided`): AI 推論、構成判断、シーンの内容、ネットワーク、クラウド、音のミックス、「free-form animation (only fade / slide / zoom layer transitions and pulse / bob / spin loop animations)」。
- 決定性: `idempotency_hint: "bit_exact"`(`render.mjs:27`)。ただし拡大を伴うレイヤーのアルファ面は 2 回のレンダーで一致しないことがあると計測済み(D12 "Known gap, measured")。
- 依存: Node >=22、headless Chromium、ffmpeg >=5(`lib/deps.mjs:15-18`)。ffmpeg / ffprobe を直接実行し、ffmpeg-skill は読み戻しだけ(D3、`required: false`)。
- 未実装(ROADMAP で `[ ]`): 7 キネティックタイポ、8 多言語組版と fit、9 図形・パターン、10 Three.js / GLSL、11 音とビート、14 スタイルプリセット、15 スティンガーテンプレート(`stinger.json`)。`lib/` と `templates/` に `stinger` の語は無い(grep 0 件)。ブランドキット入力も無い(`lib/template.mjs` `lib/scene-spec.mjs` に `kit` / `brand` 0 件)。

### remotion-ffmpeg-skill 0.13.0
- ツール: `analyze` `init` `still` `render` `deliver` `pipeline` `doctor`。`provides` は `remotion.<tool>`(`_contract.py:251-252`)。
- コンポジション 9: `BeatMontage` `Captioned` `Emphasis` `Highlights` `Jumpcut` `Karaoke` `PeakPulse` `Pip` `Titled`(`templates/remotion-project/src/compositions/`)。
- 入力は必ず実素材(`analyze.py SOURCE`)。素材なしの実行は未実装(ROADMAP step 6 `[ ]`)。
- 透明レイヤー: `--overlay --keep-graphics`(Captioned / PeakPulse のみ、ProRes 4444)、`--sparse`(Captioned / Karaoke / Titled)(`render.py:42-48`、SKILL.md)。コーデックは `h264` / `prores` のみ(`render.py:33`)。
- ブランド: `--brand` が ffmpeg-skill の `brand.json` をそのまま読む(`_common.py:509, 542-580`)。
- 未実装(`[ ]`): 6 素材なし、7 KineticType、8 ビジュアライザー、9 Three.js、11 スタイルプリセットとレイヤー出力。10 Emphasis は実装済み(#18)。
- 境界の自己申告: 「Pip, Titled, Captioned overlap ffmpeg-skill B-roll, motion-graphics titles, subtitle burn-in; this skill owns only the measurement-driven Remotion compositions.」(ECOSYSTEM_ROADMAP "Boundaries")。
- ライセンス: スキルは MIT。Remotion は従業員 3 人までの企業と個人は無料、それ以上は company licence(README:130)。依存: Node、Remotion 4.0.540、React 19、headless ブラウザー。
- 決定性: 契約・SKILL.md・design-decisions に deterministic / idempotent の記述なし(grep 0 件)。**未確認**。

### blender-skill 0.31.0
- ツール: info, convert, optimize, lod, split, anim, bake, scene, render(thumbnail / turntable / sheet), look, check, fit, verify, batch(ECOSYSTEM_ROADMAP)。`provides` は `3d.<tool>`(`_contract.py:38-39`)。
- 透明出力 `render --transparent`(`render.py:50`、step 3 済み)。ターンテーブル MP4 は Blender 内蔵 FFmpeg(`_contract.py` `dependencies: []` のコメント)。
- 範囲外(`not_provided`): interactive modeling、ffmpeg-skill 経由の編集・エンコード、ネットワーク、クラウド。
- 3D テキストは無い: `scripts/bpy/scene.py` `scripts/scene.py` に `text_add` / `FONT` / `"text"` 0 件。ROADMAP step 7(3D text and logo reveal)は `[ ]`、issue #60 [RM-070] も open。step 6・8・9 も `[ ]`。

### thumbnail-skill 0.1.16
- ツール 9(`contract.py:21-102`): `validate` `render` `extract_frame` `render_batch` `render_layers` `render_variants` `choose_frame` `place_text` `generate_background`。
- 合成は Pillow(決定的)。`text_fit` は 1 行を 1 pt ずつ縮めるだけで、切らない・折り返さない(ROADMAP step 5)。
- `generate_background`: プロバイダーは `flux2-klein-4b` の 1 つ(`background.py:74-80, 138`)。`local_files_only=True`、重みは落とさない(:22, :126)。`seed` 必須(:169-170)。ライセンス `Apache-2.0` を provenance に記録(:77)。VRAM 約 13 GB(:101)。任意 extra `flux2 = torch, diffusers>=0.37.0, transformers>=4.51.0`(pyproject:25)。

### subtitle-skill 0.9.1
- 操作 4: `generate`(SRT / WebVTT / TTML IMSC 1.1 / EBU-TT-D)、`render`(burn / mux)、`translate`、`mux`(`contract.py` `PROVIDES`)。
- 焼き込みは ffmpeg-skill `caption` 経由(`engine.py:115` `FFMPEG_SKILL_TOOLS = ("caption", "probe")`)。`placement`(顔よけ)、`regional_profile: ja-broadcast`、`ruby`、`caption_profile: shorts`(1〜2 語)は自前の ASS を書いて `caption --ass`(ROADMAP step 8-11)。
- アニメーションは無い: `engine.py` は `--animate` / `--karaoke` を渡さない(grep: `--mode` `--fonts-dir` `--font` `--srt` のみ)。縦書きの焼き込みは未対応(`UNSUPPORTED_FORMAT`、step 10)。
- 範囲外(README:724-733): 文字起こし、話者識別、要約、AI による字幕文の生成・書き換え、字幕の「デザイン」判断、任意の FFmpeg フィルター。

### video-editing-skill 0.7.2
- 操作(`operations.py:139-168`): TRIM, CUT, CONCAT, SPEED, FIT, FILL, RESIZE, OVERLAY, ROTATE, FREEZE, REVERSE, IMAGE_INSERT, CROP, CONDENSE, PUNCH_IN。ほかに `propose`(ROADMAP step 14-15)。
- `OVERLAY` は静止画だけ: 「composite a still image (logo, lower-third PNG) at a named position for a time range」(:153-154)、入力「one video plus one image source (png / jpg; alpha respected)」(:205)。
- `IMAGE_INSERT`: 静止画 → 無音クリップ(:161-162)。
- `CONCAT transition: {type: stinger, stinger, cut_point, cover}`(:366-371)。カット点の全面被覆をスティンガー自身のフレームで計測(ADR-032)。`stinger.json` を出す側は未実装(hyperframes step 15)。

### color-grading-skill 1.1.0
- HDR_TO_SDR, LUT_APPLY, RETAG, STRIP_DOVI, PRIMARY_CORRECTION, OCIO_TRANSFORM, MATCH_CAMERA, LEGALIZE(ECOSYSTEM_ROADMAP)。アルファ付き素材の LUT / 補正は straight のみ(step 8 `[ ]`、ADR-25/30/33)。このスライスの他スキルとの重複は無い。

### imagemagick-skill 0.10.0
- 21 ツール: probe, convert, resize, thumb, strip, trim, check, look, compare, optimize, crop, pad, rotate, adjust, overlay, montage, icons, alpha, brandkit, preset, batch(`scripts/`、ECOSYSTEM_ROADMAP)。
- `brandkit.py`: 透過ロゴ 1 枚 → color / mono / white / black / clearspace の各サイズと、ロゴの主要色パレット(割合つき)。「It reports the logo's colours; it never picks colours for the caller.」(`brandkit.py:1-19`)。配色の生成・コントラスト検査・フォントは扱わない。

### ffmpeg-skill 3.6.5(重なる部分のみ)
| ツール | できること | 根拠 |
|---|---|---|
| `graphics` | テンプレート 9 種(lower-third, title, chapter, progress, countdown, bug, sticker, hook, meme)。`--brand` `--lang` `--wrap` `--text-render auto|ass|drawtext` `--keep-alpha` | `graphics.py:56, 85-123, 174` |
| `overlay` | `--image` `--text` `--logo` `--video`(PiP) `--place` `--chromakey` `--fade` `--opacity` `--scale` `--brand`。キーフレームは無い | `overlay.py:238-263` |
| `caption` | SRT / ASS 焼き込み・mux、`--animate none|fade|pop|slide`、`--karaoke`、`--fit-size`、`--wrap`、`--transcribe` | `caption.py:1009-1113` |
| `waveform` | `--style waveform|spectrum`、背景画像、`--title`(sticker 経由)、`--srt` | `waveform.py:52-83` |
| `loop` | `--times` `--duration` `--boomerang` `--crossfade S` と継ぎ目の計測 | `loop.py:1-20, 235-239` |
| `export` | アルファ: `prores4444` `prores4444xq` `qtrle` `vp9-alpha` `hap-alpha` `key-fill`、`--alpha-mode straight|premultiplied` | `export.py:117-137, 480` |
| `background` | 単色・グラデーション、`--transparent` の透明キャンバス | `background.py:7-14` |
| `broll` / `insert` | カットアウェイ(A の時間軸のまま B を見せる) / 静止画 → クリップ(Ken Burns) | `broll.py:1-12`、`insert.py:43-51` |
| `brand.json` | font, font_file, colors{primary,text,outline,background,accent}, logo(+position/scale/opacity), safe_margin, caption, styles, lang, loudness | `_common/decision.py:1000-1016` |

## 3. 重複

| # | 仕事 | できるスキルと方法 | 実際の違い | agent の今の経路 |
|---|---|---|---|---|
| D1 | タイトル・ローワーサード(焼き込み) | motion-graphics `title` / `lower_third`(ffmpeg-skill `graphics`)／ffmpeg-skill `graphics` 直接／remotion `Titled`(`lowerThirds` / `sceneTitles`) | motion-graphics は型付き・ffmpeg だけ・content_equivalent。remotion は Node + ブラウザー、実素材必須、Remotion ライセンス | `motion_graphics` SkillSpec → `motion-graphics/run`(`registry.py:485-486`)。`ffmpeg-skill/graphics` を直接呼ぶ SkillSpec は無い。remotion は利用者が `remotion.comp` を指定したときだけ(`measured_motion`、:409-412) |
| D2 | タイトル・ローワーサードの**素材ファイル**(アルファ) | hyperframes テンプレート `lower-third` / `title-card`(ProRes 4444 / VP9 / PNG、IN/LOOP/OUT)／motion-graphics `layer_export`(要素ごとの .mov)／remotion `--overlay --keep-graphics`(Captioned / PeakPulse のみ)／ffmpeg-skill `background --transparent` + `graphics --keep-alpha` | hyperframes だけがセグメントとループ継ぎ目を持つ。motion-graphics の layer_export は焼いた番組の副産物 | hyperframes は handoff のみ(`html_scene_render`、`registry.py:242-243`)。agent は実行しない |
| D3 | 静止画オーバーレイ・ロゴ | video-editing `OVERLAY`／motion-graphics `image_overlay`(fade あり) `logo`(テーマのロゴ) `bug`／ffmpeg-skill `overlay --image` `--logo` | video-editing は位置名と時間範囲のみ。motion-graphics は fade・テーマ・プラットフォームのセーフゾーン | `video_overlay` → `video-editing/overlay`(:286-287)、`motion.image` / `motion.logo` → `motion-graphics/run`(`finishing.py:131-137`)。**両方が配線済み**で、どちらを使うかは利用者のキー次第 |
| D4 | PiP・クロマキー | motion-graphics `video_overlay`(ADR-15)／ffmpeg-skill `overlay --video --chromakey`／remotion `Pip`(音で同期を計測) | remotion は同期オフセットを計測する。motion-graphics は時刻と位置を受け取るだけ | `motion.video` → `motion-graphics/run`。`ecosystem.json` は「Bロール・画面合成」を ffmpeg-skill に置いているが、agent が直接呼ぶのは `ffmpeg-skill/broll`(顔ぼかしの合成、:433-434)だけ |
| D5 | 静止画 → クリップ | video-editing `IMAGE_INSERT`／ffmpeg-skill `insert`(Ken Burns つき) | video-editing は Ken Burns を出していない(**推測**: `operations.py` の要約に zoom の記述なし) | `video_image_insert` → `video-editing/image_insert`(:307-309) |
| D6 | 字幕の焼き込み | subtitle-skill `render`(静的、配置・地域プロファイル・shorts)／ffmpeg-skill `caption`(`--animate` `--karaoke`)／remotion `Captioned` `Karaoke` `Emphasis` | subtitle-skill はアニメーションを出さない。動く字幕は ffmpeg-skill `caption` か remotion にしか無い | `subtitle_burn_in` → `subtitle/render`(:441-442)。「ffmpeg-skill/caption directly」は使わない方針(:438) |
| D7 | ショート向けの大きな字幕・強調 | subtitle-skill `caption_profile: shorts`／remotion `Emphasis`／motion-graphics `sticker` `hook` `meme`／ffmpeg-skill `caption --animate pop` | 入力が違う: 字幕キュー(subtitle)、語の時刻(remotion)、時刻つきの文字列(motion-graphics) | subtitle は 0.9.1 を pin 済み。`caption_profile` を agent が渡すかは **未確認** |
| D8 | サムネイル | thumbnail-skill `render`／imagemagick `preset`(youtube-thumbnail)／remotion `still`／blender `render`(thumbnail) | thumbnail-skill だけが文字・顔よけ・A/B・プラットフォーム検査を持つ | `thumbnail/render` `thumbnail/extract_frame`(:450-463) |
| D9 | ブランド(色・フォント・ロゴ) | ffmpeg-skill `brand.json`／motion-graphics `theme@1` と `brand_kit`／remotion `--brand`(brand.json を読む)／imagemagick `brandkit`(ロゴ派生とパレット抽出) | 形式が 3 つ: brand.json(5 色 + caption + loudness)、theme@1(4 色 + spacing + base_style)、brand_kit(4 色のみ)。hyperframes・thumbnail・subtitle・blender には入力が無い | agent は `motion.themes` / `motion.theme` を渡す(`decision_finishing.py:164-167`)。共通キットは無い |
| D10 | スタイルプリセット(swiss / neon / wafu …) | motion-graphics(実装済み、ADR-24)／hyperframes step 14(`[ ]`)／remotion step 11(`[ ]`) | 実装は motion-graphics だけ。残り 2 つは同じ名前のプリセットを各自で作る計画 | — |
| D11 | ループ素材 | hyperframes `segments.loop`(構成時に継ぎ目なし)／ffmpeg-skill `loop --crossfade`(後からならす)／remotion step 8 `--loop`(`[ ]`) | hyperframes は拒否で保証、ffmpeg-skill は任意の素材を加工 | どちらも agent からは未配線(**推測**: registry に `ffmpeg-skill/loop` の SkillSpec なし) |
| D12 | 波形・スペクトラム映像 | ffmpeg-skill `waveform`(実装済み)／remotion step 8(`[ ]`)／blender step 9(`[ ]`) | 実物は ffmpeg-skill だけ | agent に `ffmpeg-skill/waveform` の SkillSpec なし |
| D13 | キネティックタイポ・Three.js | hyperframes step 7・10／remotion step 7・9／blender step 6・7 — **すべて `[ ]`** | 紙の上の重複のみ。実装は 0 | — |
| D14 | レイヤー書き出し(NLE 用) | motion-graphics `layer_export`／thumbnail `render_layers`／remotion `--keep-graphics`、step 11 `--layers`(`[ ]`) | 媒体が違う(動画 / 静止画)。重複ではなく同じ型の機能 | — |

## 4. 隙間

| # | 持ち主のいない仕事 | 根拠 |
|---|---|---|
| G1 | 動くオーバーレイ(位置・拡大・不透明度のキーフレーム)の持ち主 | ffmpeg-skill#425 open、「Decision: open, scope question first」。Velisa ROADMAP:411、:437「Still open for the owner」 |
| G2 | hyperframes の出力を agent が実行して `rendered_layer` に渡す経路 | `html_scene_render` は handoff(`registry.py:242`)。`rendered_layer` は配線済み(`finishing.py:137`)だが、入力のファイルは利用者が用意する |
| G3 | スティンガー素材とその `stinger.json` を作る側 | 受け側は実装済み(video-editing ADR-023/032、qc-skill `video.stinger`、agent `edit.concat.stinger`)。作る側 hyperframes step 15 は `[ ]` |
| G4 | 動画のループ継ぎ目・key/fill の一致・アルファ縁の QC | qc-skill の `loop_seam` は音だけ(`contract.py:73, 388`)。key/fill・alpha edge の検査は grep 0 件。motion-titles 案は qc-skill がこれらを検査すると書いている(Velisa ROADMAP:351) |
| G5 | 多言語の組版(RTL、CJK 改行、縦書き、ルビ)を**素材ファイル**側で | hyperframes step 8 `[ ]`。motion-graphics の `fit` は `lower_third` / `title` の焼き込みだけ |
| G6 | 素材なしの制作(文字だけの PV) | remotion step 6 `[ ]`、agent の `plan` は入力メディア必須(Velisa ROADMAP:286) |
| G7 | 3D テキスト・ロゴリビール | blender step 7 `[ ]`、issue #60 |
| G8 | 全レンダラー共通のブランドキットと検査(フォントの埋め込み可否など) | Velisa ROADMAP:357-363。検査の一部(コントラスト)は motion-graphics `theme-check` にだけある |
| G9 | 動画の AI 生成 | 実装なし。画像は thumbnail-skill の背景だけ |
| G10 | premultiplied アルファの素材出力 | hyperframes は straight のみ(D13)。ffmpeg-skill `export --alpha-mode` で変換は可能(**推測**: 経路として誰も配線していない) |
| G11 | 動く字幕(pop / カラオケ)の所有 | subtitle-skill は出さない。ffmpeg-skill `caption --animate/--karaoke` は agent から直接呼ばない方針。remotion は CONFIRM で利用者のプロジェクトが要る |

## 5. ecosystem.json との食い違い

| 行 | ecosystem.json | 実際 |
|---|---|---|
| :36-38 motion-graphics | owns `タイトル・テロップ`、role "Title cards, lower thirds, overlays" | 実際は PiP・クロマキー(`video_overlay`)、ロゴ、図形、進行バー、カウントダウン、ブランドテーマ、レイヤー書き出し、事前レンダー素材の配置まで持つ。owns に出ていない |
| :26-28 ffmpeg-skill | owns `Bロール・画面合成` | PiP を型付きで agent に出しているのは motion-graphics。agent が ffmpeg-skill で直接使う合成は `broll` だけ |
| :30-32 video-editing | owns `静止画オーバーレイ`、role "Cut, trim, concat, fit, overlay" | 同じ仕事を motion-graphics `image_overlay` / `logo` も行い、どちらも agent に配線済み(D3)。video-editing 側は PUNCH_IN・CONDENSE・propose・stinger・サイズ上限書き出しも持つが owns に無い |
| :39-41 subtitle | role "Subtitle validation, SRT/WebVTT generation, burn-in" | TTML(IMSC 1.1)/ EBU-TT-D、翻訳、多言語 mux、顔よけ配置、地域プロファイル、shorts がある。role 文が古い |
| :42-45 thumbnail | owns `サムネイル` | 一致。エンジン注記(FLUX.2 klein 4B、Apache-2.0、VRAM 約 13 GB)もコードと一致 |
| :49-51 remotion | owns `計測連動モーショングラフィックス(Remotion)` | 一致。ただし Captioned / Titled / Pip は計測に依らない重複(スキル自身が Boundaries で認めている) |
| :52-54 hyperframes | owns `HTMLシーンの動画化(HyperFrames)` | テンプレート(ローワーサード、タイトルカード、セッションスレート、休憩)、CSV バッチ、IN/LOOP/OUT、アルファ納品を持つ。「テロップ素材」は owns のどこにも無い |
| :46-48 blender | owns `3D素材・3Dレンダリング` | 一致 |
| :121-123 imagemagick | owns `静止画編集` | `brandkit`(ロゴ派生・パレット)が入っているが owns に無い |
| status | 9 つとも `active` | 一致(全スキルにリリースと実装あり) |

## 6. Velisa 文書との食い違い

| 文書:行 | 書いてあること | 実際 |
|---|---|---|
| CAPABILITY_MATRIX.md:53 | `edit.overlay` は「video/PiP-shaped」 | 静止画(png / jpg)のみ(`operations.py:153-154, 205`) |
| CAPABILITY_MATRIX.md:56-57 | `CROP, FREEZE, REVERSE, IMAGE_INSERT, POSITION` は拒否 | CROP / FREEZE / REVERSE / IMAGE_INSERT は実装済み(`operations.py:157-164`) |
| CAPABILITY_MATRIX.md:111 | `subtitle.render` は「SRT only; ASS/SSA burn-in not implemented」 | placement / regional / shorts は自前 ASS を `caption --ass` で焼く。`translate` `mux` の行が無い |
| CAPABILITY_MATRIX.md:128-131 | motion-graphics は 4 能力 | 15 要素、`provides` 15 件(`contract.py` `CAPABILITY_IDS`) |
| CAPABILITY_MATRIX.md:146-147 | 「ADR-012: AI 背景は可」と「no AI-generated thumbnails, no best-frame selection, no face detection」が同じ段落に並ぶ | `generate_background` `choose_frame` `place_text` が実装済み |
| CAPABILITY_MATRIX.md 全体 | — | hyperframes / remotion / blender / imagemagick の節が無い(grep 0 件) |
| REPOSITORY_MAP.md:34-39 | video-editing / color-grading / subtitle / motion-graphics / thumbnail が 0.1.0 | 0.7.2 / 1.1.0 / 0.9.1 / 0.2.19 / 0.1.16 |
| REPOSITORY_MAP.md:43 | `image-skill` 0.2.0 | リポジトリ名は imagemagick-skill、0.10.0 |
| REPOSITORY_MAP.md:321-331 | motion-graphics は「linear fade only」、thumbnail は「No AI-generated thumbnails, no best-frame selection, no face detection」 | 上と同じく古い |
| docs/ecosystem/ROADMAP.md:285 | motion-graphics は「13 typed elements」 | 15 |
| docs/ecosystem/ROADMAP.md:283 | hyperframes に無いもの:「per-character animation, shapes, audio, beat lock, styles」 | 今も無い(一致)。IN/LOOP/OUT とアルファ納品は入った |
| docs/ecosystem/ROADMAP.md:351 | qc-skill が「alpha edges, loop seam, key / fill match」を検査 | qc-skill 1.3.0 にあるのは stinger と音の loop_seam だけ |
| docs/ecosystem/ROADMAP.md:18 | blender / hyperframes は handoff のみ | 一致(agent `registry.py:240-243`) |

各スキル自身の ECOSYSTEM_ROADMAP.md の "Where it stands" も古い: motion-graphics「0.2.16」「Pinned 0.2.8」(実 0.2.19、agent の pin も 0.2.19)、hyperframes「v0.6.4」(実 0.8.0)、remotion「v0.12.1」(実 0.13.0)、video-editing「v0.4.4」「Pinned at 0.4.2」(実 0.7.2、pin 0.7.0)、thumbnail「0.1.9」(実 0.1.16)、color-grading「v0.4.0」(実 1.1.0)、imagemagick「v0.9.0」(実 0.10.0)、subtitle「Pinned at 0.4.1」(pin 0.9.1)。
hyperframes の CHANGELOG.md には `## 0.8.0` の節が無く、segments とアルファ納品が両方 `## 0.7.0` に入っている(package.json は 0.8.0)。

## 7. 進行中の作業

| repo | 番号 | 内容 | 関係 |
|---|---|---|---|
| ffmpeg-skill | #425 open | Typed keyframes on overlay。「open, scope question first」 | G1。持ち主の決定待ち |
| ffmpeg-skill | #417 #418 #419 #421 #422 #423 closed(completed, 2026-11-06) | アルファマスター、key/fill、中間コーデック、ラウドネス版、シームレスループ、セーフエリア | `export` プリセットと `loop --crossfade` に入っている |
| ffmpeg-skill | #420 #424 open、#426 closed(not planned) | マルチトラック音声、growing files / LTC、ARIB 字幕 | このスライス外 |
| motion-graphics-skill | issue #10 open | shape の再調査、PiP / クロマキーの所有、`--audio-stream`、`dropped_non_av_streams` | 4 点とも実装済み(ADR-15, 16, 17, 22)。**閉じ忘れの可能性(推測)** |
| video-editing-skill | issue #11 open | rotate / flip、動画レイヤー PiP + クロマキーを OVERLAY に、stabilize / sequence / background の所有 | ROTATE は実装済み。PiP は motion-graphics が実装したので D4 の所有を決めれば閉じられる |
| hyperframes-skill | PR #6 draft(2026-09-22 更新) | audio レイヤーと動画の volume | ROADMAP step 11 の前半に当たる。本文に「Windows is still not supported」とあり古い(**推測**: 0.8.0 に対して要リベース) |
| blender-skill | PR #167 | release 0.32.0 | — |
| blender-skill | issue #60 [RM-070]、#68 [RM-078] | 3D テキスト、ffmpeg-skill 連携の最終書き出し | G7 |
| subtitle-skill | issue #37 | ffmpeg-skill 互換チェックの定期実行が失敗 | 所有とは無関係 |
| Velisa | issue #35 | CAPABILITY_MATRIX.md が古い | 6 章の内容と重なる |
| Velisa | issue #33 #34 #36 | multicam / sync、export / render / batch、check と qc の衝突 | 同じ型の所有の穴(このスライス外) |
| video-production-agent | PR #105 #62 draft | handoff の文言、GitHub 自動化 | 所有とは無関係 |
| remotion / thumbnail / color-grading / imagemagick | open PR・issue なし | — | — |

## 8. 選択肢

共通の前提: ffmpeg-skill は Velisa から変更しない(ROADMAP:399)。

### O1 動くオーバーレイの持ち主(G1、#425)
| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| A. motion-graphics が ffmpeg のキーフレームで持つ | 契約の再 pin のみ(語彙は契約から読む) | #425 を実装してもらう(新規の大きな機能) | ffmpeg のみ | MIT のみ | content_equivalent を保てる(**推測**: 式ベースなら再現可) |
| **B. 推奨: 素材は hyperframes、配置は motion-graphics `rendered_layer`** | hyperframes のアダプターを handoff から実行に上げ、出力(ProRes 4444)を `motion.layer` に渡す 1 本の経路を足す。pin は両方とも済み | なし。#425 は not planned で閉じる | Node 22 + headless Chromium | MIT(スキル)、hyperframes 0.8.61、Chromium | hyperframes は 1 台の中で bit_exact(拡大レイヤーのアルファ面は例外、D12)。配置側は content_equivalent |
| C. remotion が持つ | 既存 `measured_motion`(CONFIRM、利用者の Remotion プロジェクト必須) | なし | Node + Remotion + ブラウザー | Remotion company licence(4 人以上の企業) | 記述なし(未確認) |
| D. 新スキル | SkillSpec・アダプター・pin を新設 | なし | 実体は B か C のレンダラー | 新規 | レンダラー次第 |

推奨 B。理由: 両端が出荷済み(hyperframes 0.8.0 の segments / アルファ、motion-graphics ADR-25、agent ADR-102)。足りないのは agent が hyperframes を実行する 1 本だけ。A は ffmpeg-skill の `overlay` の責任を広げる(#425 のコメントそのもの)。C はライセンス条件がつく。

### O2 タイトル・ローワーサードの重複(D1・D2)
| 案 | 内容 | 影響 |
|---|---|---|
| **A. 推奨: 役割で分ける** | 焼き込み = motion-graphics(owns `タイトル・テロップ` のまま)。素材ファイル = hyperframes(owns に `テロップ・スティンガー素材` を足す)。remotion `Titled` は「コンポジション内だけ」と明記 | agent: 既定は motion-graphics、動きが要るときだけ O1-B。ffmpeg-skill: なし。決定性は現状維持 |
| B. hyperframes のテンプレートを motion-graphics に移す | motion-graphics が Node / Chromium を抱える | 依存が増え、`dependencies = []` を失う。非推奨 |

### O3 静止画オーバーレイ・PiP(D3・D4)
| 案 | 内容 | 影響 |
|---|---|---|
| **A. 推奨: 名前で線を引き直す** | video-editing `OVERLAY` = 編集の一部としての素の静止画合成(owns `静止画オーバーレイ` のまま)。motion-graphics = グラフィックとしての画像・ロゴ・PiP・クロマキー(owns に `ロゴ・PiP・クロマキー合成` を足す)。ffmpeg-skill の `Bロール・画面合成` は「カットアウェイ(broll)とエンジン」と読み替える | agent: 配線は今のまま。`edit.overlay` と `motion.image` の使い分けを SkillSpec の説明に書く。video-editing#11 の 2 と motion-graphics#10 の 2 を閉じられる。ffmpeg-skill: なし |
| B. video-editing `OVERLAY` を廃止して motion-graphics に寄せる | agent の `video_overlay` SkillSpec と imagemagick の前処理(ADR-077)を付け替える | 契約の破壊的変更。得るものが少ない |

### O4 字幕とテロップ(D6・D7・G11)
| 案 | 内容 | 影響 |
|---|---|---|
| **A. 推奨: 入力で分ける** | 字幕キュー(SRT / 文字起こし)から出るものはすべて subtitle-skill。語の時刻に合わせた演出は remotion(`Karaoke` `Emphasis`)。時刻つきの単発の文字は motion-graphics。subtitle-skill に `animate`(fade / pop / slide)と `karaoke` を足す(ffmpeg-skill `caption` の既存フラグを通すだけ) | agent: subtitle の再 pin。ffmpeg-skill: なし(既存フラグ)。依存: なし。決定性: 変わらず |
| B. 動く字幕は remotion だけ | 現状のまま | Node + Remotion ライセンスが要る。ffmpeg だけで足りる要求に重い |

### O5 ブランド(D9・D10・G8) → 9(d)
### O6 スティンガー・ループ素材(G3・G4・D11) → 9(c)
### O7 キネティックタイポ・ビジュアライザー・Three.js(D12・D13) → 9(f)
### O8 AI 生成(G9) → 9(e)

### O9 古い文書(5・6 章)
| 案 | 内容 |
|---|---|
| **A. 推奨** | CAPABILITY_MATRIX.md と REPOSITORY_MAP.md を各スキルの pin 済み契約から生成する(Velisa #35 を拡張)。各スキルの ECOSYSTEM_ROADMAP "Where it stands" はリリース時に版数を書き換える |
| B | 手で直す(また古くなる) |

## 9. 追加の問い

### (a) タイトル・テロップ・ローワーサードを今作れるのは誰か

| 作り手 | 入力 | 静止 / 動き | アルファ出力 | 文字組み | 決定性 | 依存 |
|---|---|---|---|---|---|---|
| motion-graphics `title` `lower_third` `text_overlay` ほか | 型付き JSON + 既存の動画。CSV(`lower-thirds`) | 内蔵 fade / slide+fade / pulse / pop、設定可能なのは fade のみ | `layer_export`(要素ごとの .mov、prores4444 など、straight) | `fit`: 縮小 → UAX #14 改行、`ja-kinsoku`、RTL は報告。`lower_third` / `title` のみ | content_equivalent | ffmpeg-skill |
| hyperframes テンプレート `lower-third` `title-card` `session-slate` `break` | テンプレート値 JSON、CSV(`batch`)。素材不要 | fade / slide / zoom + pulse / bob / spin、IN/LOOP/OUT | ProRes 4444 / VP9 / PNG 連番、straight のみ | `lang` はタグだけ。fit・RTL・縦書きは未実装(step 8)。テンプレートは `max_length` で制限 | bit_exact(1 台。拡大レイヤーのアルファは例外) | Node 22、Chromium、ffmpeg |
| remotion `Titled`(`lowerThirds` / `sceneTitles` / chapters) | 実素材 + timeline.json + options | React の動き | `--sparse` は合成済みを返す。透明レイヤーは Captioned / PeakPulse のみ | CJK フォントを自動で用意(SKILL.md)。fit は **未確認** | 記述なし(未確認) | Node、Remotion(ライセンス条件)、ブラウザー |
| ffmpeg-skill `graphics` / `overlay --text` | CLI フラグ + 動画 | テンプレート内蔵のみ | `--keep-alpha`(透明キャンバス上) | `--wrap phrase` ほか、`--lang`、`--text-render ass|drawtext`、絵文字 | (エンジン) | ffmpeg |
| subtitle-skill `render`(burn) | SubtitleDocument(キュー) | 静止 | なし(焼き込み / mux のみ) | ロケール別の行長・禁則、ルビ、話者色。縦書きの焼き込みは不可 | **未確認**(契約の該当箇所は未読) | ffmpeg-skill |
| thumbnail-skill のテキスト | ThumbnailDocument | 静止画 | `render_layers`(PNG) | 1 行を縮めるのみ、折り返さない。CJK / RTL の扱いは未確認 | 決定的(Pillow) | Pillow |
| blender 3D テキスト | — | — | — | — | — | **未実装**(step 7、issue #60) |

### (b) 動くオーバーレイの持ち主(#425)
- 状態: #425 は open、ラベル feature、コメント 1 件「Decision: open, scope question first … pre-rendered layers placed by `overlay` remain the supported path.」(2026-11-05)。#417-#419・#421-#423 は 2026-11-06 に completed、#420・#424 は open、#426 は not planned。
- 選択肢と推奨は O1。**推奨 B(hyperframes が素材、motion-graphics `rendered_layer` が配置)**。決めたら #425 を not planned で閉じ、motion-graphics の `unsupported_animations` の文言はそのまま残す。
- B で残る作業: (1) agent が `hyperframes-skill/render` を実行する経路、(2) `rendered_layer` は VP9 アルファを拒否するので ProRes 4444 に固定、(3) hyperframes step 8(組版)と 7(文字の動き)。

### (c) `motion-titles-skill`

| 草案の項目(Velisa ROADMAP:336-355) | すでにあるもの | 無いもの |
|---|---|---|
| `template --list`、`make <template> --values|--csv` | hyperframes `template`、`batch`(CSV)、テンプレート 4 種 | strap / count-up / comment card / end roll / speaker introduction、スティンガー 5 種 |
| `--kit kit.json` | — | hyperframes にブランド入力なし |
| `in.mov` / `loop.mov` / `out.mov` | hyperframes `render --segments` → `<stem>.in|loop|out<ext>` + `loop_seam` | — |
| `--format prores4444|webm-alpha|png` | hyperframes `--codec prores|vp9|png` | — |
| `key-fill` | ffmpeg-skill `export --preset key-fill` | hyperframes からの経路 |
| `--alpha straight|premultiplied` | straight のみ(D13)。ffmpeg-skill `export --alpha-mode` | premultiplied の直接出力 |
| `--duration 1.2 --cut-point 0.5`、スティンガー | 受け側: video-editing `transition: stinger`、qc-skill `video.stinger`、agent `edit.concat.stinger` | 作る側(hyperframes step 15)、`stinger.json` |
| `title.json`(`motion-titles/title@1`) | hyperframes の結果 JSON に `segments[]`(フレーム数)・`alpha`・`loop_seam` | セーフエリア、描いた文字、使ったフォントサイズ、独立したメタデータファイル |
| 組版(RTL / CJK / 縮小 / 縦書き / ルビ) | — | hyperframes step 8 |
| 配置 | motion-graphics `rendered_layer` | — |
| QC(全面被覆、アルファ縁、ループ継ぎ目、key/fill) | 全面被覆のみ | 動画のループ継ぎ目・アルファ縁・key/fill(qc-skill) |

| 案 | agent | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| 新リポジトリ | SkillSpec・アダプター・pin を新設。中身は hyperframes を呼ぶだけの薄い層になる | なし | Node + Chromium(間接) | MIT | hyperframes と同じ |
| **推奨: hyperframes-skill に畳む + メタデータだけ Velisa の仕様** | hyperframes を実行に上げる 1 本(O1-B と同じ作業) | なし(key/fill と premultiplied は既存の `export` を通す) | 変わらず | MIT | 変わらず |
| Velisa の仕様のみ | なし | なし | — | — | 何も作られない |

推奨の中身: hyperframes の step 15(スティンガー + `stinger.json`)・8・14 を進め、`title.json` / `stinger.json` のスキーマは Velisa に置く(video-editing・motion-graphics・qc-skill・agent の 4 者が読むため)。ecosystem.json は hyperframes の owns に `テロップ・スティンガー・ループ素材` を足す。草案が挙げる「新スキルの理由」(IN/LOOP/OUT、カット点、アルファ明示)は 0.8.0 でほぼ hyperframes に入っており、草案自身も絵は hyperframes が描くと書いている(ROADMAP:347)。

### (d) `design-system-skill`

| 草案の項目(ROADMAP:357-363) | すでにあるもの |
|---|---|
| キットの形式 | ffmpeg-skill `brand.json`(`decision.py:1000-1016`)、motion-graphics `theme@1` と `brand_kit`。3 形式が並立 |
| `kit derive --for …` | remotion は brand.json を直接読む。motion-graphics は theme@1。hyperframes / thumbnail / subtitle / blender は読み口が無い |
| コントラスト検査 | motion-graphics `theme-check` / `response.theme.contrast`(自分のテンプレートの組み合わせだけ) |
| ロゴ派生・クリアスペース・パレット抽出 | imagemagick `brandkit`(抽出のみ、生成はしない) |
| 1 色からのパレット生成、フォントの埋め込み可否 | 無い |
| `event-pack sessions.csv` | 無い(制作計画に当たるので agent の仕事に近い、**推測**) |

| 案 | agent | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| 新リポジトリ | SkillSpec + アダプター + pin。全レンダラーの前段に 1 手順 | なし(`ffmpeg-brand` を出力するだけ) | Python のみ。Material Color Utilities(Apache-2.0)は任意 | MIT | 純粋な JSON 変換なので決定的 |
| imagemagick-skill に畳む | 既存 pin の更新 | なし | 変わらず | MIT | — ただし「静止画編集」の範囲を超える |
| **推奨: まず Velisa の仕様のみ(`kit@1` スキーマと対応表)** | agent がキットを読み、各スキルの既存の入力(`motion.themes`、remotion `--brand`、thumbnail の色)に展開する | なし | なし | — | 変わらず |

推奨の理由: 実装済みの読み口は motion-graphics と remotion の 2 つだけで、今「導出」しても渡す先が少ない。先に `kit@1` を brand.json の上位互換として決め、hyperframes step 14・thumbnail に読み口が入ってから、検査(フォントライセンス、パレット生成)が残るなら新リポジトリに切り出す。`event-pack` は agent に置く。

### (e) `generative-media-skill`
- 今あるもの: thumbnail-skill `generate_background` だけ。FLUX.2 [klein] 4B、重みは `black-forest-labs/FLUX.2-klein-4B`、Apache-2.0 とコードに記録(`background.py:76-79`)、ローカルの重みのみ、seed 指定、VRAM 約 13 GB。9B 版は非商用として除外(:20-21、Velisa ADR-012:37)。モデルカード上のライセンスそのものは **未確認**(ネットワークで確かめていない)。
- video-editing ADR-022: 生成クリップは呼び出し側が `sources[].ai_generated {generator, licence}` を宣言し、`AI_GENERATED` の印がつく。生成はしない。
- 動画生成の実装はどこにも無い。ROADMAP:375 の「LTX-2: Apache-2.0 code, weights under a community licence」は **未確認**。
- 決定性: seed を固定しても GPU・ドライバーが違えば画素は一致しない(**推測**)。thumbnail-skill は生成物を「普通の画像素材」として渡し、合成側の決定性を保っている(`background.py:4-5`)。

| 案 | 判断 |
|---|---|
| 新リポジトリ | 時期尚早。重みのライセンスが未確認 |
| thumbnail-skill に畳む | 動画は「サムネイル」の範囲外 |
| 仕様のみ | 生成物の印(`AI_GENERATED`)は video-editing にすでにある |
| **推奨: ADR を先に(Velisa)** | 候補エンジンごとにコードと重みのライセンス・VRAM・商用条件を表にする。画像は thumbnail-skill の provider インターフェース(`BackgroundProvider`)を再利用できるかも ADR で判断する。agent・ffmpeg-skill への影響は ADR が通るまで 0 |

### (f) キネティックタイポ・オーディオビジュアライザー・Three.js / GLSL

| 仕事 | hyperframes | remotion | blender | ffmpeg-skill |
|---|---|---|---|---|
| キネティックタイポ(文字・語ごと) | step 7 `[ ]`。今は レイヤー単位の fade / slide / zoom | step 7 `[ ]`。今は `Karaoke` `Emphasis`(語の時刻) | step 7 `[ ]` | `caption --karaoke` `--animate pop` |
| ビジュアライザー | step 11(音・ビート)`[ ]`、PR #6 draft(音レイヤーのみ) | step 8 `[ ]`。今は `PeakPulse` `BeatMontage`(計測したピーク・ビート) | step 9 `[ ]` | `waveform`(waveform / spectrum、背景画像、タイトル)**実装済み** |
| Three.js / GLSL | step 10 `[ ]` | step 9 `[ ]` | — | — |
| 幾何学パターン | step 9 `[ ]` | — | step 6 `[ ]` | `background --gradient` のみ |

- 実物があるのは ffmpeg-skill `waveform` と remotion の計測連動コンポジションだけ。ほかは全部計画。
- 計画どうしが重なっている: キネティックタイポ(hyperframes 7 / remotion 7)、Three.js(hyperframes 10 / remotion 9)、スタイルプリセット(hyperframes 14 / remotion 11 / motion-graphics 6 済み)。
- 選択肢: (A) **推奨** — Velisa ROADMAP:436 の案どおり、素材なしで作るものは hyperframes(owns に `キネティックタイポ・幾何学モーション`)、音や語の時刻に連動するものは remotion(owns に `オーディオビジュアライザー`)、3D の奥行きが要るものだけ blender。remotion step 9(Three.js)は hyperframes step 10 が出るまで保留にして二重実装を避ける。(B) すべて hyperframes に寄せる — remotion の計測連動(既存の強み)を捨てることになる。
- 影響(A): agent は hyperframes の実行経路(O1-B と共通)。ffmpeg-skill への依頼なし。依存は Node + Chromium(+ three は同梱、MIT)。GSAP は使わない(ROADMAP:296)。決定性は SwiftShader 前提で 1 台の中のみ。

### (g) 静止画オーバーレイ・画像の挿入・PiP

| 仕事 | video-editing | motion-graphics | ffmpeg-skill | remotion |
|---|---|---|---|---|
| 静止画を重ねる | `OVERLAY`(png / jpg、位置名、時間範囲) | `image_overlay`(fade、scale、opacity)、`logo`、`bug` | `overlay --image` `--logo` | — |
| 静止画をクリップにして挟む | `IMAGE_INSERT` → CONCAT | — | `insert`(Ken Burns) | — |
| PiP・クロマキー | なし(issue #11 で要望) | `video_overlay` | `overlay --video --chromakey` | `Pip`(同期計測つき) |
| カットアウェイ(B ロール) | なし | なし | `broll` | — |
| 事前レンダー素材の配置 | CONCAT `stinger`(継ぎ目の上) | `rendered_layer`(クリップの上) | `overlay --video --place` | — |

agent の経路: `edit.overlay` → `video-editing/overlay`(前処理に imagemagick strip / resize / pad、ADR-077)。`motion.image` / `motion.video` / `motion.layer` → `motion-graphics/run`。`ffmpeg-skill/broll` は顔ぼかしの合成だけ。推奨は O3-A。

### (h) 字幕とテロップの重なり

| | 入力 | 動き | 出どころ |
|---|---|---|---|
| subtitle-skill `render` burn | キュー(SubtitleDocument) | なし。配置移動・話者色・ルビ・shorts(1〜2 語) | `caption` / `caption --ass` |
| ffmpeg-skill `caption` | SRT / ASS / テキスト | `--animate fade|pop|slide`、`--karaoke sweep|word` | 直接(agent は呼ばない) |
| remotion `Captioned` / `Karaoke` / `Emphasis` | SRT + 語の時刻(transcription-skill の transcript) | React。Emphasis は語を pop / 色 / 箱、吹き出し、コメントカード | `render.py --comp` |
| motion-graphics `text_overlay` / `sticker` / `hook` / `meme` | 時刻つきの文字列(1 要素ずつ) | fade / pop(内蔵) | `overlay --text` / `graphics` |

- 重なる場所: (1) ショート向けの大きな字幕 = subtitle `shorts` と remotion `Emphasis` と ffmpeg-skill `caption --animate pop`。(2) 強調の一語 = remotion `Emphasis` と motion-graphics `sticker`。(3) ローワーサードをよける字幕 = subtitle `placement.avoid` が motion-graphics の領域を入力として受ける(重複ではなく連携点)。
- 線の引き方は O4-A(入力で分ける)を推奨。subtitle-skill に `animate` / `karaoke` を通すと、Node なしで動く字幕が subtitle-skill の所有に収まり、remotion は「語の時刻に合わせた演出」に限定できる。

## 未確認のまとめ
- remotion-ffmpeg-skill の決定性の保証(記述が見つからない)。
- thumbnail-skill の CJK / RTL の扱い、subtitle-skill の決定性の宣言(該当コード未読)。
- blender-skill の最新タグ(ローカルにタグなし。package.json は 0.31.0)。
- FLUX.2 klein 4B と LTX-2 の重みライセンスの一次確認(ネットワークで見ていない。コードと ROADMAP の記述のみ)。
- agent が subtitle の `caption_profile` / `placement` を渡すかどうか。
- Velisa の 6 文書は語で grep しただけで、全文は通読していない。
