# D: 納品・補助・統制リポジトリと、Velisa 文書の実態照合

調査日 2026-11-12。読み取りのみ。各リポジトリは `origin/main` を `git show` / `git grep` で読んだ（作業ツリーには触れていない）。
表記: 証拠は `repo@sha:path:行`。推測は「推測」、確認できなかったものは「未確認」と書く。

---

## 1. 読んだもの

### Part 1（担当スライス）

| repo | commit | version（pyproject / 最新タグ） | 読んだファイル | 未確認 |
|---|---|---|---|---|
| publish-skill | 7c6e61c | 0.1.0 / タグなし・GitHub Release なし | README.md, ECOSYSTEM_ROADMAP.md, docs/decisions.md（見出し）, src/publish_skill/{contract,limits,plan,doctor}.py, platforms/*.py（`ffmpeg_skill_platform`） | 実プラットフォームへの送信（リポジトリ自身が「mock のみ」と明記） |
| nle-bridge-skill | 886559a | 0.1.0 / タグなし・Release なし | README.md, ECOSYSTEM_ROADMAP.md, src/nle_bridge/contract.py, pyproject.toml | Premiere / Resolve での実読み込み（同 roadmap step 8 が未完） |
| bdmvkit | 6cc45ac | 0.7.0 / v0.7.0 | README.md, ECOSYSTEM_ROADMAP.md, bdmvkit/contract.py, `__main__.py`, pyproject.toml | — |
| vtskit | da64a03 | 0.4.0 / v0.4.0 | 同上（vtskit/contract.py, `__main__.py`） | PyPI 上の 0.4.0 の有無（タグのみ確認） |
| udfkit | aae9574 | 0.2.0 / v0.2.0 | 同上 | PyPI 上の 0.2.0 の有無 |
| dvdcc | 6999e58 | 0.2.0 / v0.2.0 | 同上 | — |
| oncemore | 36cfb96 | 1.3.0 / v1.3.0 | README.md（抜粋）, SKILL.md, ECOSYSTEM_ROADMAP.md, oncemore/contract.py, `_vendor/*/UPSTREAM`, pyproject.toml, .github/workflows/library-updates.yml | docs/DECISIONS.md 全文、macOS アプリ本体 |
| stepcap | 4f68e4c | 0.1.7 / v0.1.7 | README.md, ECOSYSTEM_ROADMAP.md, src/stepcap/contract.py, pyproject.toml, cli.py（grep） | OCR 実装の詳細 |
| skillpact | 9f0559e | 0.8.1（ref/pyproject.toml）/ v0.8.1 | README.md, ECOSYSTEM_ROADMAP.md, SKILL.md（冒頭）, ref/pyproject.toml | spec 本文、conformance スイートの中身 |
| system-intelligence | a597e40 | 0.4.0 / v0.4.0 | README.md, ECOSYSTEM_ROADMAP.md, src/system_intelligence/analysis/{ownership,contracts,roadmap_drift,field_readiness}.py と discovery/contracts.py の冒頭 | CLI 全コマンドの挙動 |
| ffmpeg-skill（納品側のみ） | 11c153e | 3.6.5（package.json）/ v3.6.5 | scripts/_platforms.py, export.py（PRESETS）, report.py（冒頭）, render.py（`--export-timeline`）, _contract.py（grep） | check.py の行ごとの判定の重さ |
| video-production-agent（到達性の確認） | b2d4e08 | 0.1.0 / タグなし | src/video_agent/skills/{ecosystem,registry}.py, agent/{nle,editor_timeline,publish,timeline}.py 冒頭, project/validator.py:1158-1172, profiles/*.json, tools/ 配下一覧 | アダプター本体の全文 |

### Part 2（Velisa `origin/main` = 45a40f1、VERSION 0.9.0）

ecosystem.json, README.md, docs/ecosystem/{HANDOFF, CROSS_REPO_STATUS, CURRENT_STATE（grep）, ROADMAP, DECISION_LOG（grep）, MATURITY_MODEL, WORK_QUEUE（grep）}.md, registry.json, capability-status.json, docs/CAPABILITY_MATRIX.md, docs/REPOSITORY_MAP.md（冒頭と grep）, docs/DEPENDENCY_GRAPH.md（grep）, docs/ROADMAP.md（冒頭と grep）, docs/ECOSYSTEM_CHANGELOG.md（冒頭と grep）, registry/*.py 冒頭, scripts/*.py 冒頭, .claude-plugin/marketplace.json, plugins/velisa/.claude-plugin/plugin.json。
未確認: WORK_QUEUE.md（81 KB）と DECISION_LOG.md（23 KB）は全文を読んでいない。担当リポジトリ名と件数表現で検索しただけ。

### 33 コンポーネントの現在のバージョン（各 `origin/main`）

| repo | sha | version | 最新タグ | Release |
|---|---|---|---|---|
| video-production-agent | b2d4e08 | 0.1.0 | なし | なし |
| ingest-skill | 38f2c29 | 0.1.0 | なし | なし |
| ffmpeg-skill | 11c153e | 3.6.5 | v3.6.5 | あり |
| video-editing-skill | 078c279 | 0.7.2 | v0.7.2 | あり |
| color-grading-skill | 0ddeaac | 1.1.0 | v1.1.0 | あり |
| motion-graphics-skill | 8e3fcb6 | 0.2.19 | v0.2.19 | あり |
| subtitle-skill | da597e5 | 0.9.1 | v0.9.1 | あり |
| thumbnail-skill | bca8ee2 | 0.1.16 | v0.1.16 | あり |
| blender-skill | 4214430 | 0.31.0 | blender-skill-v0.31.0 | あり |
| remotion-ffmpeg-skill | d135b3b | 0.13.0 | v0.13.0 | あり |
| hyperframes-skill | 3528095 | 0.8.0 | v0.8.0 | あり |
| audio-production-skill | 7ab8022 | 1.2.0 | v1.2.0 | あり |
| voice-enhance-skill | 9e0c150 | 0.1.0 | なし | なし |
| dubbing-skill | f929f4a | 0.2.1 | なし | なし |
| sound-design-skill | d974c26 | 0.3.2 | なし | なし |
| transcription-skill | 99b59b8 | 0.11.4 | v0.11.4 | あり |
| diarization-skill | 3254cc0 | 0.3.0 | なし | なし |
| detection-skill | 9e2f732 | 0.2.2 | なし | なし |
| slide-sync-skill | 7b32715 | 0.1.0 | なし | なし |
| qc-skill | b7475e9 | 1.3.0 | v1.3.0 | あり |
| media-analysis-skill | ab432c0 | 0.1.16 | v0.1.16 | あり |
| artifacts-skill | ae039d3 | 0.4.0 | v0.4.0 | あり |
| publish-skill | 7c6e61c | 0.1.0 | なし | なし |
| nle-bridge-skill | 886559a | 0.1.0 | なし | なし |
| bdmvkit | 6cc45ac | 0.7.0 | v0.7.0 | あり |
| vtskit | da64a03 | 0.4.0 | v0.4.0 | あり |
| udfkit | aae9574 | 0.2.0 | v0.2.0 | あり |
| dvdcc | 6999e58 | 0.2.0 | v0.2.0 | あり |
| oncemore | 36cfb96 | 1.3.0 | v1.3.0 | あり |
| imagemagick-skill | ab89bf9 | 0.10.0 | v0.10.0 | あり |
| stepcap | 4f68e4c | 0.1.7 | v0.1.7 | あり |
| skillpact | 9f0559e | 0.8.1 | v0.8.1 | あり |
| system-intelligence | a597e40 | 0.4.0 | v0.4.0 | あり |

依頼文にあった 16 個のバージョンはすべて一致した（audio-production 1.2.0、transcription 0.11.4、hyperframes 0.8.0、imagemagick 0.10.0、remotion-ffmpeg 0.13.0、qc 1.3.0、video-editing 0.7.2、detection 0.2.2、dubbing 0.2.1、sound-design 0.3.2、artifacts 0.4.0、media-analysis 0.1.16、udfkit 0.2.0、vtskit 0.4.0、dvdcc 0.2.0、skillpact 0.8.1）。

**依頼文の前提の訂正:** 「voice-enhance / dubbing / sound-design / publish は release がある」は確認できなかった。4 つとも git タグも GitHub Release も 0 件（`gh api repos/kajisho5/<repo>/releases` と `/tags` が空）。あるのは pyproject のバージョンと動くコードだけ。nle-bridge、detection、diarization、slide-sync、ingest、agent も同じくタグなし。

---

## 2. 各スキルが実際にできること

### publish-skill 0.1.0（MIT、標準ライブラリのみ、Python 3.9+）

| 項目 | 内容 | 証拠 |
|---|---|---|
| capability | `publish.plan`（オフライン検査）、`publish.upload`（既定は dry run、確認トークン一致時のみ送信） | publish-skill@7c6e61c:src/publish_skill/contract.py:31 `CAPABILITY_IDS` |
| そのほかのコマンド | `contract`, `doctor`, `platforms`, `auth login/status/logout`, `series`（連続投稿と再開、主催者向け受領書） | README.md「Status: 0.1.0, unreleased」、ECOSYSTEM_ROADMAP.md step 9・10 |
| アップローダー | YouTube、Vimeo、TikTok、X、LinkedIn、Facebook、Instagram Reels の 7 つ | src/publish_skill/platforms/{youtube,vimeo,tiktok,x,linkedin,facebook,reels}.py |
| 検証の範囲 | 7 つとも loopback mock のみ。実アップロードは 0 回 | README.md「All seven have been tested only against local mocks」、ECOSYSTEM_ROADMAP.md step 7 が未チェック |
| ffmpeg-skill の読み方 | `check --platform <p>` を子プロセスで実行し、その行をそのまま通す。値は写さない | contract.py:103「ffmpeg-skill owns them; this skill never copies them」、limits.py:108 `"status": "delegated", "value": None` |
| やらないと宣言 | プラットフォーム納品仕様（コーデック・解像度・ビットレート・ラウドネス）、プラットフォーム向けエンコード | contract.py:117-118 `not_provided` |
| 自己申告のステータス | 「status `scaffold`」 | ECOSYSTEM_ROADMAP.md:3 |

### nle-bridge-skill 0.1.0（MIT、標準ライブラリのみ。opentimelineio は任意の検算用）

| 項目 | 内容 | 証拠 |
|---|---|---|
| capability | `nle.timeline_export`（export）、`nle.conform_package`（conform）、`nle.round_trip_diff`（diff）、`nle.timeline_import`（import） | nle-bridge-skill@886559a:src/nle_bridge/contract.py:86-93 |
| 出力形式 | OTIO、FCP7 XML（xmeml 4、Premiere 用）、CMX 3600 EDL、SRT | README.md「Outputs」表 |
| 入力 | 自前の `nle-bridge/timeline@1`、agent の project IR（`delivery.timelines[]`）、ffmpeg-skill の render project、ffmpeg-skill `multicam.py --json`、audio-production の response、グラフィックの layer manifest、auto-editor の FCP7 XML | README.md「Inputs」表 |
| やらないと宣言 | 動いている NLE の操作、FCPXML（ffmpeg-skill の担当）、レンダリング、字幕生成 | contract.py:110-113、ECOSYSTEM_ROADMAP.md「Boundaries」 |
| 未完 | 実 NLE での読み込み確認（step 8） | ECOSYSTEM_ROADMAP.md `- [ ] **8. Real-NLE check**` |
| 自己申告のステータス | 「`planned` in `ecosystem.json` until Velisa updates it」 | ECOSYSTEM_ROADMAP.md:3（古い。ecosystem.json は 2026-10-31 に `active` へ変更済み） |

### ディスク一族

| repo | ライセンス | 実際の tool_id | CLI | やらないと宣言 | 証拠 |
|---|---|---|---|---|---|
| bdmvkit 0.7.0 | LGPL-3.0-or-later | `bdmvkit/encode`, `bdmvkit/build` | あり（`bdmvkit encode/build/contract`） | ディスクイメージ、書き込み、DVD-Video、コピー防止、ネットワーク | bdmvkit@6cc45ac:bdmvkit/contract.py:11-16, 33-39 |
| vtskit 0.4.0 | LGPL-3.0-or-later | `vtskit/titleset`, `vtskit/vmg`, `vtskit/subtitles`, `vtskit/plan`（すべて `kind: python`） | `contract` だけ。「the kit is a Python library」 | MPEG-2 エンコード、ディスクイメージ、書き込み、契約以外の CLI | vtskit@da64a03:vtskit/contract.py:11-17, 37-43 |
| udfkit 0.2.0 | Apache-2.0 | `udfkit/dvd`, `udfkit/bluray`, `udfkit/info`, `udfkit/verify` | あり | VIDEO_TS / BDMV の作成、書き込み、エンコード | udfkit@aae9574:udfkit/contract.py:11-23, 42-47 |
| dvdcc 0.2.0 | Apache-2.0 | `dvdcc/captions`（`mutates_input: True`、`-o` なしなら上書き）、`dvdcc/check` | あり | MPEG-2 エンコード、画像字幕（vtskit.subtitles）、PAL | dvdcc@6999e58:dvdcc/contract.py:11-16, 33-38 |
| oncemore 1.3.0 | GPL-3.0-or-later | `oncemore/{init,testdisc,validate,import-psd,simulate,build,iso,burn,scenes,transcode,preview-menu}`（11 個、lifecycle はすべて `STABLE`） | あり。MCP サーバー `oncemore mcp` と GUI もある | タイトルの編集・グレーディング・ミックス、コピー防止、ネットワーク | oncemore@36cfb96:oncemore/contract.py:12-24, 41-42 |

4 つのキットの lifecycle はすべて `EXPERIMENTAL`、oncemore だけ `STABLE`。5 つとも Python 3.11+、依存なし。エンコードは ffmpeg を直接呼ぶ（ffmpeg-skill 経由ではない: 各 ECOSYSTEM_ROADMAP.md「Wiring」に「encodes with ffmpeg directly」）。

### stepcap 0.1.7（MIT と OFL-1.1、Python 3.11+）

| 項目 | 内容 | 証拠 |
|---|---|---|
| capability | `guide.build`, `skill.draft`, `guide.video`（すべて EXPERIMENTAL） | stepcap@4f68e4c:src/stepcap/contract.py:61-63 |
| ffmpeg-skill の使用 | `stepcap video` だけが ffmpeg-skill を使う（任意） | README.md:258-261、docs/DECISIONS.md:106-109 |
| 独自エンジン | 音声メモ用に faster-whisper を持つ（`voice` extra） | pyproject.toml:51、ECOSYSTEM_ROADMAP.md「Boundaries: faster-whisper voice notes duplicate transcription-skill's engine」 |
| agent との関係 | 「Not a production step; not wired to the agent (by design)」 | ECOSYSTEM_ROADMAP.md「Wiring」 |

### skillpact 0.8.1（コード Apache-2.0、仕様 CC BY 4.0）

`skill.contract.json`（capability、副作用、要件、適合テスト、全ファイルのハッシュと署名）を SKILL.md の横に置き、インストール前に検査する仕組み。CLI は `validate`, `conformance`, `convert --to/--from os-capability` など。GitHub Action（`action.yml`）もある。
「L3 means ... not "safe"」「Runtime enforcement stays with your harness」と、実行時の強制はやらないと明記している（skillpact@9f0559e:README.md「Why」）。
ecosystem 内で `skill.contract.json` を持つのは imagemagick-skill だけ（33 リポジトリの `origin/main` を確認）。

### system-intelligence 0.4.0（MIT、Python 3.11+、pydantic と typer に依存）

汎用の監査ツール。「This is **not** a video-production tool」（system-intelligence@a597e40:README.md）。
実装済みの分析: Capability Contract の検証（analysis/contracts.py）、ownership の重複・未割り当て（analysis/ownership.py、ADR-012）、roadmap と PR のずれ（analysis/roadmap_drift.py、ADR-015）、現場適性の表（analysis/field_readiness.py、ADR-016）。`--read-only` で improve / execute を拒否する。

### ffmpeg-skill 3.6.5 の納品側

| 項目 | 内容 | 証拠 |
|---|---|---|
| プラットフォーム表 | `PLATFORMS`: tiktok, reels, shorts, youtube, youtube-hdr, youtube-av1, x, linkedin, facebook, podcast, broadcast, custom（12 件）。frame / fps / spec / safe / caption / preset / check を 1 か所に持つ | ffmpeg-skill@11c153e:scripts/_platforms.py:65-200 |
| 書き出し preset | youtube, youtube4k, reels, x, prores, prores4444, prores4444xq, qtrle, vp9-alpha, hap-alpha, key-fill, h265, gif, copy, tiktok, shorts, linkedin, facebook, youtube-hdr, youtube-av1（20 件） | scripts/export.py:98-160 |
| 納品レポート | `report.py`: 単一 HTML（before/after、ラウドネス、適合、実行コマンド） | scripts/report.py:2-10 |
| タイムライン書き出し | `render.py --export-timeline`: .fcpxml / .edl / .otio | scripts/render.py:1129, 1204-1205、SKILL.md:176 |
| ディスク関連 | ツールなし。`broadcast` の codecs に `mpeg2video` があるだけ | scripts/_platforms.py:184 |
| Vimeo | 表にない | publish-skill の limits.py:47 も「ffmpeg-skill has no `vimeo` delivery spec」と記録 |

---

## 3. 重複

### O1. プラットフォームの上限値（尺・ファイルサイズ）が 2 か所にあり、値が違う

| platform | ffmpeg-skill `_platforms.py` の `max_duration` / `max_bytes` | publish-skill `limits.py` の値 | 行 |
|---|---|---|---|
| youtube | 12 h / 256 × 1024³ | 12 h / 256 × 1000³ | _platforms.py:105-106、limits.py:114-116 |
| tiktok | 600 s / 4 × 1024³ | 600 s / 4 × 1000³ | _platforms.py:70-71、limits.py:237-239 |
| x | **140 s / 512 MiB** | **1200 s / 8 GB** | _platforms.py:138-139、limits.py:309-313 |
| linkedin | **600 s / 5 GiB** | **1800 s / 500 MB** | _platforms.py:149-150、limits.py:468-473 |
| reels | **90 s / 4 GiB** | **900 s / 300 MB** | _platforms.py:83-84、limits.py:365-368 |
| facebook | 240 min / 4 GiB | 不明（`_unknown`） | _platforms.py:160-161、limits.py:420-424 |

- 2026-10-30 のオーナー決定は「publish-skill は upload 側の上限（file size, duration, rate limits）だけを持つ」（Velisa@45a40f1:docs/ecosystem/ROADMAP.md:421）。同じ行に「nothing in ffmpeg-skill changes」とあるので、ffmpeg-skill の表には尺とサイズが残ったまま。
- 違い: publish 側は出典 URL・引用・閲覧日つき（limits.py:4-8）。ffmpeg-skill 側は出典なしの定数。
- `publish plan` は両方の行を並べて出す（plan.py:6-9）。X 向けの 5 分の動画は publish の行では通り、ffmpeg-skill `check --platform x` の行では 140 秒超過になる。推測: check.py がその行を FAIL にするか WARN にするかは読んでいない。
- agent の経路: `publish_upload` が publish-skill の `plan` と dry run を実行する（video-production-agent@b2d4e08:src/video_agent/agent/publish.py:1-8）。

### O2. プラットフォーム名・preset 名の手書きコピーが agent にある

- video-production-agent@b2d4e08:src/video_agent/project/validator.py:1165-1166
  `known_presets = {"youtube", "youtube4k", "reels", "x", "prores", "h265", "gif"}`
  `known_platforms = {"youtube", "shorts", "reels", "tiktok", "x", "linkedin", "broadcast", "podcast", "custom"}`
- ffmpeg-skill 3.6.5 の実際: preset 20 件、platform 12 件。agent 側に `facebook`, `youtube-hdr`, `youtube-av1` の platform と、`tiktok`, `shorts`, `linkedin`, `facebook`, `prores4444` などの preset がない。
- 結果: profile の delivery target に `preset: "tiktok"` や `platform: "facebook"` を書くと、ffmpeg-skill は知っているのに agent の validator が「unknown」で止める。
- 数値のコピーは profile にもある: profiles/youtube.json の `-14 LUFS / -1 dBTP` は `_platforms.py` の youtube `lufs: -14, tp: -1.0` と同じ値。

### O3. タイムライン書き出し（OTIO / EDL）が 2 つある

| | ffmpeg-skill `render --export-timeline` | nle-bridge-skill `export` |
|---|---|---|
| 形式 | FCPXML、EDL、OTIO | OTIO、FCP7 XML、EDL、SRT |
| 入力 | render project（clips, transitions…） | 自前 plan、agent IR、render project、multicam 結果など |
| 逆方向 | なし | `diff` / `import` で編集者の変更を読み戻す |
| 依存 | ffprobe | 標準ライブラリのみ |
| 決定性 | 推測: 決定的（テキスト生成のみ） | `deterministic: True`（contract.py:34-55） |
| agent の経路 | `delivery.timeline=otio|fcpxml|edl` → SkillSpec `timeline_export` → `ffmpeg-skill/render`（registry.py:448-449） | `delivery.nle=export|conform` → `nle_export` / `nle_conform` → `nle-bridge/export|conform`（registry.py:532-537） |

- 重なるのは OTIO と EDL。FCPXML は ffmpeg-skill だけ、FCP7 XML と SRT と conform と diff は nle-bridge だけ。
- 2 つは直列につながっている: nle-bridge は IR の `delivery.timelines[]` を読むので、`delivery.nle` を使うには `delivery.timeline` が先に計画されている必要がある（agent/nle.py:3「so this needs `delivery.timeline` planned」）。
- nle-bridge 側は形を ffmpeg-skill に合わせ、統合テストで ffmpeg-skill の出力を読み戻している（nle-bridge ECOSYSTEM_ROADMAP.md「Wiring」）。

### O4. ディスク作成: キット 4 つと oncemore の同梱コピー

| キット | 本体の版 | oncemore 同梱の版 | 証拠 |
|---|---|---|---|
| bdmvkit | 0.7.0 | 0.7.0 | oncemore@36cfb96:oncemore/_vendor/bdmvkit/UPSTREAM |
| dvdcc | 0.2.0 | 0.2.0 | `_vendor/dvdcc/UPSTREAM` |
| udfkit | 0.2.0 | **0.1.0**（`manifest.py` と `contract.py` がない） | `_vendor/udfkit/UPSTREAM`、ファイル一覧 |
| vtskit | 0.4.0 | **0.3.1**（`plan.py` がない） | `_vendor/vtskit/UPSTREAM`、ファイル一覧 |

- oncemore は「fixes go to both places」と書く（`_vendor/__init__.py`）。毎日 PyPI を見て draft PR を開く仕組みがある（.github/workflows/library-updates.yml）。udfkit 0.2.0 と vtskit 0.4.0 は本体の main が 2026-11-12 更新なので、まだ PR が開いていないだけの可能性がある（推測）。
- agent 側は同じ仕事に SkillSpec を 5 つ持つ: `bluray_authoring`（bdmvkit/build）、`dvd_authoring`（vtskit/author）、`disc_image`（udfkit/image）、`dvd_line21_captions`（dvdcc/caption）、`disc_author`（oncemore/build）（registry.py:244-256）。5 つとも handoff 専用で、選ばれることはない。

### O5. 契約の検査が 4 か所にある（詳細は 9(e)）

Velisa `registry/`、skillpact、system-intelligence、agent の 4 者が、それぞれ別の方法で「契約を読んで確かめる」。

### O6. stepcap の独自エンジン

- faster-whisper（音声メモ）: transcription-skill のエンジンと同じもの。stepcap は「kept」と決定済み（ECOSYSTEM_ROADMAP.md step 3、docs/DECISIONS.md）。
- OCR: ecosystem.json の detection-skill の engines に「Tesseract 5 … stepcap と共通」とある（Velisa@45a40f1:ecosystem.json:80-83）。stepcap の秘密情報ぼかしは detection-skill の text を使う PR が開いている（stepcap #84）。

### O7. ecosystem.json の写しが 4 つある

| 写し | 場所 | 鮮度 |
|---|---|---|
| ダッシュボード用の名簿 | Velisa docs/ecosystem/registry.json（`updated_at: 2026-10-29`） | 古い（6 節） |
| 事実の鏡 | Velisa docs/ecosystem/capability-status.json（`updated_at: 2026-10-31`） | 古い（6 節） |
| agent の snapshot | video-production-agent src/video_agent/skills/ecosystem.py（「read 2026-10-30」） | 古い。ingest を `scaffold`、nle-bridge を `planned` のまま持つ（:75, :104） |
| marketplace | Velisa .claude-plugin/marketplace.json | scripts/marketplace.py が生成（`--check` あり）。一致 |

---

## 4. 隙間

| # | 仕事 | 現状 | 証拠 |
|---|---|---|---|
| G1 | 実プラットフォームへの最初のアップロード | 7 つとも mock のみ | publish-skill ECOSYSTEM_ROADMAP.md step 7 未完 |
| G2 | 実 NLE での読み込み確認 | Premiere / Resolve とも未確認 | nle-bridge ECOSYSTEM_ROADMAP.md step 8 未完。ROADMAP.md:423「Neither is available here」 |
| G3 | Vimeo の納品仕様 | 持ち主がいない。ffmpeg-skill の表になく、publish は「ffmpeg-skill owns it」として UNCHECKED を返す | publish-skill limits.py:47、plan.py:391-395 |
| G4 | agent の計画からディスクを作る | handoff だけ。実行経路なし | oncemore ECOSYSTEM_ROADMAP.md step 4 未完、agent ADR-094「adapter も実行経路も作らない」 |
| G5 | ownership・roadmap のずれ・現場適性の定期監査 | system-intelligence に実装はあるが、Velisa の workflow が呼ぶのは `si watch`（ecosystem-audit.sh:51）と `si diagnose .`（dashboard.yml:105）だけ。`roadmap-drift` と `diagnose --field --ownership-map` を呼ぶ workflow は見つからない | Velisa .github/workflows と scripts を grep |
| G6 | SkillPact 契約の普及 | `skill.contract.json` は imagemagick-skill のみ。週次ジョブの対象も 1 件 | 33 リポジトリを確認、skillpact ECOSYSTEM_ROADMAP.md step 4 |
| G7 | `status` の定義 | ecosystem.json には `planned` はインストールしないという説明しかない。`scaffold` の定義が文書ごとに違う（6 節 #10） | ecosystem.json:2 `$comment` |
| G8 | Velisa の状態文書の更新 | HANDOFF / CROSS_REPO_STATUS / CURRENT_STATE は 2026-09 の内容のまま。更新を強制するテストがない | 6 節 |
| G9 | agent の handoff が指す tool_id の検証 | キットの handoff が存在しない tool_id を名指ししている（5 節 #6）。pin された契約がないので検出されない | registry.py:244-256 とキットの contract.py |

---

## 5. ecosystem.json との食い違い

| # | repo | ecosystem.json（行） | 実態 | 証拠 |
|---|---|---|---|---|
| 1 | publish-skill | `status: scaffold`（:98）、`plugin` なし | 0.1.0。7 アップローダー、plan / upload / auth / series が動く（mock 検証）。agent にアダプターと実装済み SkillSpec `publish_upload` がある。ルートに SKILL.md がある。タグ・Release はなし | publish-skill README.md、agent registry.py:527-529、tools/publish/ |
| 2 | voice-enhance / dubbing / sound-design | `status: scaffold`（:59, :63, :67）、`plugin` なし | 0.1.0 / 0.2.1 / 0.3.2。agent にアダプターあり（tools/voice_enhance, dubbing, sound_design）。ルートに SKILL.md あり。タグ・Release はなし | バージョン表、agent tools/ 一覧 |
| 3 | `plugin` フラグ | `$comment`: 「set it once the repository has a SKILL.md at its root」（:2） | ルートに SKILL.md があるのに `plugin` がない: voice-enhance, dubbing, sound-design, publish, oncemore, skillpact の 6 つ | 各 `origin/main:SKILL.md` の有無を確認 |
| 4 | oncemore | `role`: 「DVD and Blu-ray authoring app (Mac)」、`owns`: 「ディスク作成アプリ(Mac)」（:117-119） | CLI と MCP は Linux でも動く（README.md:32「so it also works on Linux」、pyproject の classifier に `POSIX :: Linux`）。Mac 専用なのは .app だけ | oncemore@36cfb96 |
| 5 | oncemore | `install: pip` | PyPI にない（SKILL.md「it is not on PyPI」）。git からの pip | oncemore SKILL.md |
| 6 | キット 4 つ | 独立した 4 コンポーネント、`owns` も 4 つ | oncemore の roadmap は「listed separately in ecosystem.json for library use only」。vtskit は CLI なしのライブラリ。agent の handoff が指す `vtskit/author`, `udfkit/image`, `dvdcc/caption` は各契約に存在しない（実在は `vtskit/titleset…`, `udfkit/dvd|bluray`, `dvdcc/captions`） | oncemore ECOSYSTEM_ROADMAP.md「Boundaries」、vtskit contract.py:41、agent registry.py:246-256 |
| 7 | ffmpeg-skill | `owns` に「配信プラットフォーム仕様」、publish に「アップロード制限」 | 決定どおり分かれているが、尺とサイズは両方が持ち、値が違う（O1） | 3 節 O1 |
| 8 | nle-bridge-skill | `owns`: 「NLE連携(タイムライン受け渡し)」1 つだけ | OTIO / EDL の書き出しは ffmpeg-skill `render --export-timeline` にもある。ffmpeg-skill の `owns` にタイムライン書き出しはない | 3 節 O3 |
| 9 | stepcap | `department: utility`, `plugin: true`, `status: active` | 制作工程ではなく、agent に配線しない設計。ecosystem とのつながりは `stepcap video` の ffmpeg-skill 利用だけ | stepcap ECOSYSTEM_ROADMAP.md「Wiring」 |
| 10 | system-intelligence | `role`: 「Read-only auditing … (si diagnose); feeds the Control Room's findings」 | 本体は汎用ツールで、execute / propose も持つ。read-only は `--read-only` / `SI_READ_ONLY=1` のとき | system-intelligence README.md「Status」、Velisa scripts/ecosystem-audit.sh:20-21 |
| 11 | skillpact | `owns`: 「スキル適合性検査」 | 適合性検査は Velisa `registry/conformance.py` にも別物として存在する（9(e)） | Velisa README.md:136 |

---

## 6. Velisa 文書との食い違い

Velisa@45a40f1。行番号は `git show origin/main:<path>` のもの。

### 6.1 件数（スキル数・リポジトリ数・ツール数）

| # | 場所 | 引用 | 実態 |
|---|---|---|---|
| 1 | docs/ecosystem/HANDOFF.md:10-11 | 「an ecosystem of 10 independent video-processing Skill repositories plus one orchestrating Agent」 | ecosystem.json は 33 コンポーネント |
| 2 | HANDOFF.md:39 | 「pipeline integrating all 9 Skills」 | agent のアダプターは 22（tools/ 配下） |
| 3 | HANDOFF.md:58, :61 | 「all 10 Skills' PRs merged」「all 10 registered Skills'」 | 同上 |
| 4 | HANDOFF.md:93 | 「track 12 repos' commit histories」 | 33 + Velisa = 34 |
| 5 | docs/ecosystem/CROSS_REPO_STATUS.md:8 | 「Repository roster (12 known…)」 | 表は 12 行。ecosystem.json は 33 |
| 6 | CROSS_REPO_STATUS.md:12 | 「`ffmpeg-skill` \| Execution foundation, 21 base tools」 | 42 ツール（scripts/ の公開スクリプト 42 本） |
| 7 | CROSS_REPO_STATUS.md:22, :53 | 「all 10 Skills + `ffmpeg-skill`」「across all 9 Skills」 | 同じ文書の中で 10 と 9 が混在 |
| 8 | docs/ecosystem/CURRENT_STATE.md:1, :52, :71 | 「as of 2026-09-06」「21 base-layer tools」「all nine other Skills」 | 2 か月前の状態 |
| 9 | docs/ecosystem/ROADMAP.md:3 | 「all 33 components」 | ecosystem.json と一致 |
| 10 | CHANGELOG.md:196 | 「maturity evidence for all 34 roster repos」 | registry.json は 34 件（33 + Velisa）。数え方が違うだけで矛盾ではない |
| 11 | README.md:130, :133 | 「11-repository audit」「10 Skill repos」 | 同じ README の :150 は「this README does not restate the count」 |
| 12 | docs/REPOSITORY_MAP.md:22, :32 | 「All 11 repositories below」「via 9 skill adapters」 | 表は 12 行（image-skill を含む）。アダプターは 22 |
| 13 | docs/CAPABILITY_MATRIX.md:26 | 「10 of 11 repos ship as a single squashed commit」 | 2026-09 時点の記述 |
| 14 | docs/ecosystem/registry.json:17, :35 | 「Consumes all 10 Skills below」「21 base tools」 | 同上 |
| 15 | docs/ECOSYSTEM_CHANGELOG.md:6 | 「This project spans 11+ separate GitHub repositories」 | 34 |

### 6.2 ステータス

| # | 場所 | 引用 | 実態 |
|---|---|---|---|
| 16 | docs/ecosystem/ROADMAP.md:22 | 「nle-bridge … `planned` in ecosystem.json」 | ecosystem.json:101 は `active`、`plugin: true`（2026-10-31、コミット db887a0 / #129）。ROADMAP は 2026-11-06 に編集されたのに直っていない |
| 17 | ROADMAP.md:434 | 「nle-bridge says `planned` … Not changed here while Velisa #132 edits that file」 | 同上。#132 は 2026-11-05 にマージ済み |
| 18 | ROADMAP.md:18, :21 | 「`scaffold` in ecosystem.json」（voice-enhance, dubbing, sound-design, publish） | ecosystem.json と一致。ただし同じ行が「0.1.0, experimental ops, wired」と書く |
| 19 | README.md:185-189 | 「Future Skills (`voice-production-skill`, `dubbing-skill`, and others) … it is marked `scaffold` (an empty repository)」 | dubbing-skill は 0.2.1 で agent に配線済み。scaffold の 4 つはどれも空ではない |
| 20 | docs/ecosystem/MATURITY_MODEL.md:36 | 「1 \| **Scaffolded** \| Repository exists, has a README, has at least one real source file (not just scaffolding)」 | README.md:188 の「scaffold (an empty repository)」と定義が逆 |
| 21 | agent src/video_agent/skills/ecosystem.py:38-39 | 「a scaffold repository has no package」 | 3 つ目の定義。同じファイルの note が「ecosystem.json still says scaffold, but … ship」と自分で打ち消している（:79-102） |
| 22 | registry.json:105, :112, :119, :126, :203, :210, :217, :252 | 「Repository created 2026-10-29; no package yet.」（dubbing, publish, detection, slide-sync, voice-enhance, sound-design, diarization, ingest） | 8 つとも pyproject とコードがある |

### 6.3 所有・配線

| # | 場所 | 引用 | 実態 |
|---|---|---|---|
| 23 | registry.json:112 | publish-skill「owner of platform delivery specs」 | 2026-10-30 の決定（ROADMAP.md:421）と ecosystem.json:99「reads the platform specs from ffmpeg-skill」の逆 |
| 24 | registry.json:130-133 | imagemagick-skill「Not consumed by video-production-agent」 | agent にアダプターあり（capability-status.json:217-218 自身が「integrated」と書く） |
| 25 | capability-status.json:181-182 | publish-skill「`os_integration`: not_integrated … no adapter module」 | ROADMAP.md:21「wired as CONFIRM after QC (agent #99)」。agent main に tools/publish/ がある |
| 26 | capability-status.json:169-170 | dubbing-skill「not_integrated」 | ROADMAP.md:18「wired (agent #88, #97, #107)」。tools/dubbing/ がある |
| 27 | capability-status.json:234-235 | nle-bridge-skill「not named anywhere in default_registry() … no adapter module」 | ROADMAP.md:22「agent export / conform wired (agent #101)」。registry.py:532-537 |
| 28 | capability-status.json:358-359 | oncemore「not named anywhere in default_registry() or ECOSYSTEM_JOB_SKILLS」 | ROADMAP.md:23「oncemore named by a handoff (agent #109)」。registry.py:252-253 |
| 29 | ROADMAP.md:13 と capability-status.json:12 | 「agent uses 17 directly (list and evidence: capability-status.json)」対「default_registry() lists 20 tool ids」 | 2 つの文書で数が違う |
| 30 | README.md:132 | 「no LLM wired in yet (`NullProvider` only)」 | ROADMAP.md:11「brain = rules + Claude (API or the chat app via MCP)」。agent に providers/claude.py がある |
| 31 | README.md:169 | remotion-ffmpeg-skill「Not yet wired into the agent」 | ROADMAP.md:15「wired (agent #108, CONFIRM)」。tools/remotion/ がある |
| 32 | HANDOFF.md:15-22 | system-intelligence「no real integration exists yet, and nothing in this repository currently depends on or references it」「pre-alpha, Phase 1 in progress as of 2026-09-06」 | ecosystem.json:131 に載り、ecosystem-audit.yml:25 が pip で入れ、dashboard.yml:105 が `si diagnose` を実行する |
| 33 | CROSS_REPO_STATUS.md:45-47 | 「PR #1 … Open, draft, no CI configured on this repo (0 checks)」 | workflow が 10 本ある（.github/workflows/） |
| 34 | ROADMAP.md:445 | 「ffmpeg-skill has none, because it is complete」 | 一致（ffmpeg-skill に ECOSYSTEM_ROADMAP.md はない） |
| 35 | README.md:310 | 「none are currently published to PyPI」 | bdmvkit, vtskit, udfkit, dvdcc, stepcap, skillpact は PyPI にある（capability-status.json:284, 300, 316, 332, 348, 437） |

### 6.4 担当リポジトリが文書に出てこない

次の文書は publish-skill、nle-bridge-skill、bdmvkit、vtskit、udfkit、dvdcc、oncemore、stepcap、skillpact、system-intelligence のどれにも触れていない（grep で 0 件）:
docs/DEPENDENCY_GRAPH.md、docs/ROADMAP.md、docs/REPOSITORY_MAP.md、docs/ecosystem/CURRENT_STATE.md、docs/ecosystem/DECISION_LOG.md、docs/ecosystem/WORK_QUEUE.md。
docs/CAPABILITY_MATRIX.md も、取り込み・納品・ディスク・統制・補助の行がない。

### 6.5 CAPABILITY_MATRIX.md

| # | 行 | 引用 | 実態 |
|---|---|---|---|
| 36 | :288 | 「**15 audio** capabilities」 | 2 節の表は 17 行（:65-81。`audio.loudness_set` と `audio.stems` が増えた） |
| 37 | :291 | 「**3 motion-graphics** capabilities」 | 5 節の表は 4 行（:128-131） |
| 38 | :305 | 「**Total distinct rows: 75**」 | 1〜9 節の実数は 8+17+4+2+4+2+1+19+21 = 78。11 節の image 10 行を足すと 88 |
| 39 | :303, :232 | 「**21 base-layer** capabilities」「`ffmpeg-skill`'s 21 raw tools」 | :263-264 が「Superseded … 42 tools」と自分で打ち消すが、集計は直っていない |
| 40 | :25 | 「Every providing Skill repo is version `0.x` (pre-1.0)」 | audio-production 1.2.0、color-grading 1.1.0、qc 1.3.0、ffmpeg-skill 3.6.5 |
| 41 | :305 | 「all `EXPERIMENTAL`, zero `STABLE`」 | oncemore の契約は 11 個すべて `STABLE`（表に行がないので数に入っていない） |
| 42 | :146 | 「(ADR-012: AI-generated thumbnail backgrounds are now allowed…) **Explicitly unsupported …:** no AI-generated thumbnails」 | 同じ行の中で矛盾 |
| 43 | :113 | 字幕「Explicitly unsupported / not implemented: `convert`, standalone `validate`…」 | ecosystem.json:37-39 は subtitle-skill の role を「Subtitle validation…」、owns に「字幕翻訳」「ロケール別字幕整形」。推測: 表が古い（subtitle-skill は担当外で未確認） |
| 44 | :207 | 「transcription-skill 0.11.2」 | 0.11.4 |
| 45 | :411-427, :464 | 「`image-skill` (unregistered)」「`version: "0.2.0"`」「No `video-production-agent` adapter exists today」 | imagemagick-skill 0.10.0、ecosystem.json に登録済み、agent にアダプターあり |
| 46 | Velisa issue #35（開いたまま、2026-09-07） | 「doesn't reflect ffmpeg-skill 0.11.0/0.12.0」 | 今は 3.6.5。issue の指摘より差が広がった |

### 6.6 バージョンの引用

| # | 場所 | 引用 | 今日 |
|---|---|---|---|
| 47 | docs/REPOSITORY_MAP.md:32-43 | video-editing / audio-production / color-grading / subtitle / motion-graphics / thumbnail / qc / media-analysis がすべて「0.1.0」、transcription「0.2.0」、image-skill「0.2.0」、ffmpeg-skill「0.9.1 (3.x as of 2026-11)」 | 0.7.2 / 1.2.0 / 1.1.0 / 0.9.1 / 0.2.19 / 0.1.16 / 1.3.0 / 0.1.16、0.11.4、imagemagick-skill 0.10.0、3.6.5 |
| 48 | capability-status.json:18 | ffmpeg-skill npm「2.24.0」 | 3.6.5 |
| 49 | capability-status.json:224 | imagemagick-skill npm「0.8.1」 | 0.10.0 |
| 50 | capability-status.json:316, :332, :348 | vtskit「0.3.1」、udfkit「0.1.0」、dvdcc「0.1.1」 | 0.4.0、0.2.0、0.2.0 |
| 51 | capability-status.json:437 | skillpact「0.8.0」 | 0.8.1 |
| 52 | docs/DEPENDENCY_GRAPH.md:191 | 「`ffmpeg-skill`, version range `>=0.9.1,<1.0.0`」 | 3.6.5 |
| 53 | system-intelligence ECOSYSTEM_ROADMAP.md「Where it stands」 | 「v0.2.2」 | 0.4.0 |
| 54 | 各サテライトの ECOSYSTEM_ROADMAP.md 末尾 | 「ffmpeg-skill (42 tools, treated as complete)」 | ツール数は一致 |

agent の契約 pin と今日の版の差: sound_design `contract_0.3.0.json`（スキルは 0.3.2）、transcription `contract_0.11.3.json`（0.11.4）、video_editing `contract_0.7.0.json`（0.7.2）。ほかの pin は一致。

### 6.7 改名（AI-video-production-OS → Velisa、2026-10-31）の残り

| 場所 | 件数 | 例 |
|---|---|---|
| Velisa 本体 | 意図的な「formerly」表記と互換コードだけ | README.md:15, :258、install.sh:45-46、CROSS_REPO_STATUS.md:45（古いブランチ名） |
| video-production-agent | 44 件 / 12 ファイル | src/video_agent/skills/ecosystem.py:16 `MARKETPLACE = "ai-video-production-os"`。handoff が出す `/plugin install <repo>@ai-video-production-os` は今の marketplace 名 `velisa` と合わない |
| system-intelligence | 31 件 / 19 ファイル | ECOSYSTEM_ROADMAP.md:3 |
| skillpact | 27 件 / 16 ファイル | ECOSYSTEM_ROADMAP.md:3 |
| publish-skill | 11 件 / 7 ファイル | README.md「for the [AI Video Production OS](https://github.com/kajisho5/AI-video-production-OS)」 |
| oncemore 7、bdmvkit 4、vtskit 4、udfkit 4、dvdcc 4、stepcap 3、nle-bridge-skill 2、ffmpeg-skill 5 | — | 各 ECOSYSTEM_ROADMAP.md:3 のリンク |

GitHub のリダイレクトが効くのでリンクは切れていない。実害があるのは agent の `/plugin install …@ai-video-production-os` だけ。

---

## 7. 進行中の作業

| repo | 番号 | 題 | 関係 |
|---|---|---|---|
| Velisa | issue #33 | ffmpeg-skill.multicam / sync に担当スキルがない | 開いたまま（2026-09-07） |
| Velisa | issue #34 | ffmpeg-skill.export / render / batch の所有が未記載 | 開いたまま。O3 と関係 |
| Velisa | issue #35 | CAPABILITY_MATRIX.md が古い | 開いたまま。6.5 |
| Velisa | issue #36 | ffmpeg-skill.check 対 qc-skill、scenes 対 media-analysis の衝突 | 開いたまま |
| Velisa | issue #37 | allowed_input_roots が opt-in | 開いたまま |
| Velisa | issue #38 | サテライトの配布（PyPI・タグ・Release） | 開いたまま。タグなしの 10 リポジトリに当てはまる |
| Velisa | issue #152 | Ecosystem health（毎日更新） | 赤: motion-graphics, subtitle, agent, voice-enhance |
| Velisa | issue #97 | Skill updates | 状態保持用 |
| Velisa | PR #142-#149 | dependabot のみ | 所有に関係なし |
| video-production-agent | PR #105 | Print /plugin install <skill>@velisa in handoffs (merge right after Velisa #132) | 2026-10-31 から開いたまま。6.7 の実害を直す PR。Velisa #132 は 2026-11-05 にマージ済み |
| oncemore | PR #152 | one disc per session, in batch (roadmap step 5) | G4 の隣 |
| oncemore | issue #75 | Multi-angle titles, writing DVD titlesets without dvdauthor | vtskit の計画の親 |
| stepcap | PR #84 | blur secrets seen on screen before export (detection-skill text) | O6 |
| stepcap | PR #75 | release 0.1.8 | 47 日開いたまま |
| skillpact | PR #46 | docs(roadmap): tick step 5, the OS weekly run reports declares | — |
| skillpact | PR #16、issue #11, #12, #1 | Seatbelt、公開レビュー（2026-11-21 まで） | — |
| ffmpeg-skill | issue #464 | Audit 2026-11: export.py, check.py, loudness.py, verify.py and platform presets | O1・O2 と重なる可能性。本文は未確認 |
| ffmpeg-skill | issue #420, #424, #425 | Multitrack audio / Growing files and LTC / Typed keyframes | 開いたまま（提案 8、12、13） |
| publish-skill、nle-bridge-skill、bdmvkit、vtskit、udfkit、dvdcc、system-intelligence | — | 開いている PR・issue なし | — |

---

## 8. 選択肢

各項目の先頭が推奨。

### O1. 尺・サイズの上限が 2 か所で違う

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: 尺とサイズは publish-skill の値を正とし、ffmpeg-skill `check` の該当 2 行は「目安」と明記する。`publish plan` は ffmpeg-skill の尺・サイズ行を判定に使わない** | 変更なし（`publish_upload` はそのまま） | 新規の小さな依頼: `check` 出力で `max_duration` / `max_bytes` の行に出典の有無を示す。issue #464 に載せられる | なし | なし | 変わらない |
| B: ffmpeg-skill の表を publish の出典つきの値に合わせる | 変更なし | 新規。2026-10-30 決定の「nothing in ffmpeg-skill changes」を変える | なし | なし | check の合否が変わる（X の 140 秒など） |
| C: 現状のまま、`publish plan` が両方を出す | 変更なし | なし | なし | なし | 同じファイルに 2 つの答えが出続ける |

### O2. agent の preset / platform 名の手書きコピー

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: validator が ffmpeg-skill の契約（または `export --list`）から名前を読む** | validator.py:1165-1166 を契約読みに変える。ffmpeg-skill の契約 pin が要る（今は pin なしで contract_check.py が動的に読む） | なし（契約に preset 名が載っているかは未確認。なければ新規の依頼） | なし | なし | pin すれば決定的 |
| B: 手書きの集合を 3.6.5 に合わせて更新する | 2 行の修正 | なし | なし | なし | 次の preset 追加でまたずれる |

### O3. タイムライン書き出しが 2 つ

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: 現状の直列を正式な分担として書く。ffmpeg-skill = 「カットリストの書き出し（FCPXML / EDL / OTIO）」、nle-bridge = 「NLE との往復（FCP7 XML、conform、diff、import）」。ecosystem.json の ffmpeg-skill `owns` に 1 語足す** | 変更なし | なし（Velisa issue #34 をこれで閉じられる） | なし | なし | 変わらない |
| B: agent の `delivery.timeline` も nle-bridge に寄せ、ffmpeg-skill の書き出しは agent から使わない | `timeline_export` の tool を `nle-bridge/export` に変える。IR の `delivery.timelines[]` の作り方を変える必要がある。FCPXML が出せなくなる | なし | nle-bridge が必須になる | MIT 同士 | nle-bridge は EXPERIMENTAL で実 NLE 未確認 |
| C: nle-bridge の OTIO / EDL 書き出しをやめ、ffmpeg-skill の出力を変換するだけにする | 変更なし | なし | なし | なし | nle-bridge の入力（multicam、layers、stems）が ffmpeg-skill の形に入らない |

### O4. ディスク一族の粒度（9(a) も参照）

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: ecosystem.json は 5 つのまま。agent の SkillSpec は `disc_author`（oncemore）1 つに減らし、キット 4 つの SkillSpec を外す** | registry.py:244-256 の 4 件と ecosystem.py の Component 4 件を外す。存在しない tool_id の名指しがなくなる | なし | なし | agent は oncemore を別プロセスで呼ぶだけなら GPL の影響を受けない（推測: 法的判断は未確認） | 変わらない |
| B: ecosystem.json でキット 4 つを oncemore の `libraries` に畳む | 同上。加えて install.sh、registry.json、capability-status.json、テスト（`test_dashboard_roster_names_the_same_repositories`）の更新 | なし | なし | LGPL / Apache のライブラリ単体利用者には影響なし | 変わらない |
| C: 現状のまま、handoff の tool_id だけ実在のものに直す | registry.py の 3 行修正。キットの契約を pin する | なし | なし | なし | 変わらない |

### O5. 契約検査の重複（9(e) 参照）

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: 役割を 1 行ずつ決めて文書に書く。OS 契約（`contract --json`）の形の検査 = system-intelligence、副作用・署名・隔離テスト = skillpact、実行時の版ゲート = agent、Velisa `registry/` = 参照実装（衝突ポリシーの定義）で CI からは system-intelligence を呼ぶ** | 変更なし | なし | Velisa の CI が system-intelligence に依存（すでに依存） | MIT / Apache | 変わらない |
| B: Velisa `registry/conformance.py` を skillpact conformance に置き換える | 変更なし | なし | 各スキルに `skill.contract.json` が要る（今は 1/33） | Apache-2.0 | 隔離実行になり再現性は上がる |
| C: 現状のまま | — | — | — | — | 同じ検査が 3 か所で別々に進む |

### O6. stepcap の独自エンジン

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: 現状維持（stepcap は単体アプリとして自前で持つ。決定済み）。OCR だけ detection-skill に寄せる PR #84 を進める** | なし | なし | detection-skill（任意） | MIT / Apache-2.0（Tesseract） | 変わらない |
| B: 音声メモも transcription-skill に寄せる | なし | なし | stepcap の単体インストールが重くなる | MIT | 変わらない |

### O7 / G7 / G8. 写しと状態文書

| 案 | agent の配線 | ffmpeg-skill への依頼 | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| **A（推奨）: `status` の定義を ecosystem.json の `$comment` に 1 つだけ書き、registry.json の `role` と agent の ecosystem.py を ecosystem.json から生成する（marketplace.py と同じ方式、`--check` つき）。HANDOFF / CROSS_REPO_STATUS / CURRENT_STATE は冒頭に「2026-09 の記録」と書いて凍結し、現状は ROADMAP.md に一本化する** | ecosystem.py が生成物になる。agent PR #105 を先にマージ | なし | なし | なし | 写しのずれがテストで落ちる |
| B: 全文書を手で直す | ecosystem.py を手で更新 | なし | なし | なし | 次の変更でまたずれる |

### G1〜G6, G9

| 隙間 | 推奨 | 代案 | agent | ffmpeg-skill | 依存・ライセンス・決定性 |
|---|---|---|---|---|---|
| G1 実アップロード | オーナーがテストアカウントで 1 回ずつ送る（publish step 7）。それまで `status` は `active` にしても lifecycle は EXPERIMENTAL のまま | YouTube だけ先に送る | 変更なし | なし | 資格情報が要る。送信は非決定的（HIGH / CONFIRM のまま） |
| G2 実 NLE 確認 | NLE が手に入るまで「未確認」を README に残す（今そうなっている） | DaVinci Resolve 無料版で OTIO / EDL だけ先に確認 | 変更なし | なし | Resolve のインストール |
| G3 Vimeo 仕様 | ffmpeg-skill に `vimeo` の行を足す依頼を出す（新規。決定どおり表は ffmpeg-skill のもの） | Vimeo は「仕様なし・手で確認」と決めて UNCHECKED のままにする | 変更なし | 新規の提案 | なし |
| G4 計画からディスク | oncemore step 4 を待つ。agent は handoff のまま | agent にアダプターを作る | アダプターと pin が要る。CONFIRM | なし | ffmpeg + libx264、GPL の CLI を別プロセスで呼ぶ |
| G5 定期監査 | ecosystem-audit.yml に `si roadmap-drift ecosystem.json` と `si diagnose --field --ownership-map ecosystem.json` を足す | 手動で月 1 回 | 変更なし | なし | system-intelligence（MIT）。読み取りのみ |
| G6 SkillPact 普及 | 公開レビュー終了（2026-11-21）まで広げない。その後 ffmpeg-skill（サンプルが L3）から | qc-skill と ingest-skill から | 変更なし | `skill.contract.json` の追加は ffmpeg-skill 側の判断 | bubblewrap（Linux） |
| G9 handoff の tool_id | O4-A で 4 件を外す | O4-C で直して pin する | registry.py | なし | なし |

---

## 9. 追加の質問

### (a) ディスク一族

**誰が何を持つか**

| repo | 持つもの | 形 |
|---|---|---|
| bdmvkit | BDMV のナビゲーション層（.mpls、.clpi、index.bdmv、MovieObject.bdmv、IGS メニュー、PGS 字幕）と Blu-ray 向けエンコード | ライブラリ + CLI |
| vtskit | VIDEO_TS（IFO、VOB のナビパック、メニュー、字幕、アングル、ビットレート計画） | ライブラリのみ |
| udfkit | UDF 1.02 + ISO 9660（DVD）と UDF 2.50（BD）のイメージ、チェックサム manifest と verify | ライブラリ + CLI |
| dvdcc | CEA-608 の line-21 字幕を MPEG-2 の GOP user data に入れる（再エンコードなし） | ライブラリ + CLI |
| oncemore | 上の 4 つを同梱した作成アプリ。プロジェクト JSON、メニュー、検証、シミュレーター、build / iso / burn、MCP、GUI、Mac アプリ | アプリ |

**同梱の版:** bdmvkit 0.7.0（最新と同じ）、dvdcc 0.2.0（同じ）、udfkit 0.1.0（最新 0.2.0）、vtskit 0.3.1（最新 0.4.0）。

**5 つという粒度は適切か:** インストールとライセンスの単位としては正しい（LGPL が 2、Apache が 2、GPL が 1。キットは PyPI で単体配布されている）。仕事の単位としては細かすぎる。oncemore 自身が「The four kits are listed separately in ecosystem.json for library use only」と書き、agent から意味があるのは `disc_author` だけ。推奨は 8 節 O4-A（ecosystem.json は 5 つのまま、agent の SkillSpec を 1 つに）。

**agent から届くか:** 届かない。5 つとも handoff 専用の phase 2 SkillSpec で、アダプターも実行経路もない（registry.py:216-217 `phase=2`、ADR-094「adapter も実行経路も作らない」）。そのうえ `vtskit/author`、`udfkit/image`、`dvdcc/caption` は実在しない tool_id。キットの ECOSYSTEM_ROADMAP.md も「Not reachable from the agent」と書く。

### (b) プラットフォーム仕様とアップロード

2026-10-30 の決定がコードに反映されているか:

| 決定の内容 | コード | 判定 |
|---|---|---|
| ffmpeg-skill が表を持つ | `_platforms.py` の `PLATFORMS`。check.py、export.py、render.py、caption.py、graphics.py、look.py が読む | 反映済み |
| publish-skill は表を読むだけ | `check --platform` を子プロセスで実行。limits.py は `status: "delegated", value: None`。各 platforms/*.py に `ffmpeg_skill_platform` | 反映済み |
| publish-skill は upload 側の上限だけ持つ | limits.py に出典つきで保持 | 反映済み |
| 尺・サイズの線引き | 両方が持ち、X・LinkedIn・Reels で値が違う | **未解決**（O1） |
| registry.json | 「owner of platform delivery specs」のまま | **未反映**（6 節 #23） |
| agent の delivery preset | profile は preset 名と platform 名だけ持つ（profiles/youtube.json）。validator に名前の手書きコピー、profile にラウドネス値の重複 | 一部ずれ（O2） |
| Vimeo | ffmpeg-skill の表になく、publish は UNCHECKED | 持ち主なし（G3） |

### (c) NLE への受け渡し

| 段 | 誰が | 何を |
|---|---|---|
| 1 | agent（agent/timeline.py、ADR-052） | `delivery.timeline=otio|fcpxml|edl` を決定にし、IR に `delivery.timelines[]` を記録 |
| 2 | ffmpeg-skill `render --export-timeline` | その記録から .otio / .fcpxml / .edl を書く（SkillSpec `timeline_export`） |
| 3 | nle-bridge `export` / `conform` | 同じ IR から OTIO / FCP7 XML / EDL / SRT と relink manifest、zip を書く（`delivery.nle`、ADR-089） |
| 4 | nle-bridge `diff --timeline-out` | 編集者が返したタイムラインを読み、agent が `revise --editor-timeline` で次の計画版にする（ADR-098） |

agent 自身は OTIO を書かない。書くのは ffmpeg-skill と nle-bridge。重なるのは OTIO と EDL の書き出しだけで、nle-bridge は ffmpeg-skill の形に合わせている。nle-bridge の ECOSYSTEM_ROADMAP.md「Wiring」は「reading `diff` back is still open」と書くが、同じファイルの step 7 は agent #117 で完了と書いており、ファイル内で食い違っている。

### (d) stepcap と oncemore は ecosystem の一員か

| | stepcap | oncemore |
|---|---|---|
| OS 契約（`contract --json`） | あり（3 capability） | あり（11 capability） |
| agent からの到達 | なし（設計上） | handoff の名指しのみ |
| ほかのスキルへの依存 | `stepcap video` が ffmpeg-skill（任意） | なし（ffmpeg を直接） |
| ほかのスキルからの依存 | なし | なし |
| 入力が動画編集の成果物か | いいえ（画面操作の記録） | はい（完成した動画） |
| marketplace | 載っている | 載っていない（SKILL.md はある） |

結論: どちらも実態は単体アプリ。oncemore は納品の最終段として意味がつながるが、stepcap は制作工程に入らない。

載せ方の案:

| 案 | 内容 |
|---|---|
| **A（推奨）** | ecosystem.json に `kind` を足す（`skill` / `app` / `library` / `tool`）。stepcap と oncemore は `app`、キット 4 つは `library`、skillpact と system-intelligence は `tool`。部署はそのまま。組織図と install.sh は `kind` で扱いを分けられる |
| B | stepcap を ecosystem.json から外し、README の「関連プロジェクト」に移す。oncemore は残す |
| C | 現状のまま。`role` に「standalone」と書き足すだけ |

### (e) 誰が契約を検査し、誰が監査するか

| 検査 | Velisa `registry/` と scripts | skillpact | system-intelligence | agent |
|---|---|---|---|---|
| OS 契約の JSON Schema 検証 | registry/capability_contract.schema.json、tests/test_schema.py | `convert --to/--from os-capability`（変換と比較） | analysis/contracts.py（渡された schema で検証、ADR-011） | tools/*/contract_X.json の pin と版ゲート、ffmpeg_skill/contract_check.py |
| 適合性テスト | registry/conformance.py（SKILL_SPEC §8 の 8 項目、qc-skill で実走） | `conformance`（宣言したテストを隔離実行、L1〜L3） | field_readiness.py（契約と CI から表を作る） | — |
| capability の衝突 | registry/registry.py（3 段のポリシー） | — | ownership.py（`ownership_provider_overlap`） | SkillRegistry.select_tool |
| `owns` の重複 | scripts/tests/test_ecosystem_manifest.py `test_nothing_is_owned_twice` | — | ownership.py（`ownership_overlap`、未割り当ても見る） | tests/test_unit.py が snapshot と隣の ecosystem.json を比べる |
| 副作用・署名・改ざん検出 | — | あり（本業） | — | — |
| CI の赤・古い PR | scripts/ecosystem-health.py（毎日） | — | ci_quality.py | — |
| 変更の検出 | scripts/skill-updates.py（タグと HEAD） | — | `si watch`（snapshot の差分）、update_intelligence.py | — |
| roadmap と PR のずれ | — | — | roadmap_drift.py（Velisa の workflow からは未使用） | — |

同じ検査が 2 回あるところ:
1. OS 契約の schema 検証: Velisa `registry/` と system-intelligence。
2. `owns` の重複: Velisa のテストと system-intelligence の ownership.py。
3. 適合性: Velisa `registry/conformance.py` と skillpact `conformance`。名前は同じで中身は別（前者は OS の 8 項目、後者はスキルが宣言したテスト）。
4. 変更の検出: skill-updates.py と `si watch`。
5. CI の健全性: ecosystem-health.py と system-intelligence の ci_quality.py。

推奨の分担は 8 節 O5-A。

### (f) 33 コンポーネントの修正案（提案のみ。ecosystem.json は編集していない）

「証拠」は 1 節のバージョン表と agent の tools/ 一覧、各リポジトリの SKILL.md の有無による。担当スライス外のリポジトリは `owns` と `role` の中身を検証していない（「未確認」と書く）。

| # | repo | 今の status | 提案 status | owns / role の提案 | 根拠 |
|---|---|---|---|---|---|
| 1 | video-production-agent | active | active | 未確認 | タグなし 0.1.0 |
| 2 | ingest-skill | active | active | 未確認 | agent アダプターあり |
| 3 | ffmpeg-skill | active | active | `owns` に「カットリスト書き出し(FCPXML/EDL/OTIO)」を足す。「配信プラットフォーム仕様」は尺・サイズを含むかを明記 | O1、O3 |
| 4 | video-editing-skill | active | active | 未確認 | 0.7.2 |
| 5 | color-grading-skill | active | active | 未確認 | 1.1.0 |
| 6 | motion-graphics-skill | active | active | 未確認 | 0.2.19 |
| 7 | subtitle-skill | active | active | 未確認 | 0.9.1 |
| 8 | thumbnail-skill | active | active | 未確認 | 0.1.16 |
| 9 | blender-skill | active | active | 未確認 | agent は handoff のみ（pin あり） |
| 10 | remotion-ffmpeg-skill | active | active | 未確認 | agent アダプターあり |
| 11 | hyperframes-skill | active | active | 未確認 | agent は handoff のみ（pin あり） |
| 12 | audio-production-skill | active | active | 未確認 | 1.2.0 |
| 13 | voice-enhance-skill | scaffold | **active**（lifecycle は EXPERIMENTAL） | `plugin: true` を検討（SKILL.md あり） | 0.1.0、agent アダプターあり、タグなし。CI が赤（Velisa #152） |
| 14 | dubbing-skill | scaffold | **active**（EXPERIMENTAL） | `plugin: true` を検討 | 0.2.1、agent アダプターあり、タグなし |
| 15 | sound-design-skill | scaffold | **active**（EXPERIMENTAL） | `plugin: true` を検討。「効果音」は agent 未配線（registry.py:226） | 0.3.2、agent アダプターあり、タグなし |
| 16 | transcription-skill | active | active | 未確認 | 0.11.4 |
| 17 | diarization-skill | active | active | 未確認 | タグなし |
| 18 | detection-skill | active | active | 未確認 | タグなし |
| 19 | slide-sync-skill | active | active | 未確認 | タグなし |
| 20 | qc-skill | active | active | 未確認 | 1.3.0 |
| 21 | media-analysis-skill | active | active | 未確認 | 0.1.16 |
| 22 | artifacts-skill | active | active | 未確認 | 0.4.0 |
| 23 | publish-skill | scaffold | **active**（EXPERIMENTAL、実アップロード未実施と `role` に書く） | `owns` はそのまま。「アップロード制限」に尺・サイズを含むと明記。`plugin: true` を検討 | 2 節、O1 |
| 24 | nle-bridge-skill | active | active | `role` はそのまま。実 NLE 未確認を書く | 2 節。ROADMAP.md:22, :434 の「planned」を直す |
| 25 | bdmvkit | active | active | `kind: library` を足す案（9(d)） | 0.7.0 |
| 26 | vtskit | active | active | `kind: library`。`role` に「library, no CLI」 | contract.py:41 |
| 27 | udfkit | active | active | `kind: library`。`owns` に「チェックサム検証」を足すかは任意 | 0.2.0 の manifest / verify |
| 28 | dvdcc | active | active | `kind: library` | 0.2.0 |
| 29 | oncemore | active | active | `role` を「DVD and Blu-ray authoring app (CLI / MCP on macOS and Linux; Mac app)」、`owns` を「ディスク作成アプリ」に。`install` は git からの pip と明記。`plugin: true` を検討 | 5 節 #4, #5 |
| 30 | imagemagick-skill | active | active | 未確認 | 0.10.0。唯一 `skill.contract.json` を持つ |
| 31 | stepcap | active | active | `kind: app`。`role` に「standalone; not a production step」 | 9(d) |
| 32 | skillpact | active | active | `kind: tool`。`owns`「スキル適合性検査」は Velisa `registry/conformance.py` との違いを `role` に書く | 9(e) |
| 33 | system-intelligence | active | active | `kind: tool`。`role` を「General-purpose system auditor; Velisa runs it read-only (si watch, si diagnose)」に | 5 節 #10 |

`status` の値そのものについて: 今の 3 値（active / scaffold / planned）では「動くが未リリース・未実証」を表せない。案は 2 つ。
- **推奨:** `status` は「インストールするか」だけに使い（active / planned）、成熟度は契約の lifecycle（EXPERIMENTAL / STABLE）と MATURITY_MODEL の段階に任せる。`scaffold` は廃止する。
- 代案: `experimental` を足して 4 値にする（voice-enhance、dubbing、sound-design、publish、nle-bridge が該当）。

---

## 未確認のまとめ

- WORK_QUEUE.md と DECISION_LOG.md の全文。
- ffmpeg-skill `check.py` が `max_duration` / `max_bytes` 超過を FAIL にするか WARN にするか。
- ffmpeg-skill issue #464 の本文。
- PyPI 上の vtskit 0.4.0 と udfkit 0.2.0 の有無（git タグは確認）。
- 担当スライス外 23 リポジトリの `owns` / `role` の中身。
- oncemore（GPL-3.0-or-later）を agent が別プロセスで呼ぶ場合のライセンス上の扱い。
- subtitle-skill の validate / 翻訳の実装状況（CAPABILITY_MATRIX.md:113 との照合）。
