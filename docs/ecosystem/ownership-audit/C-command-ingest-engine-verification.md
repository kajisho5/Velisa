# C: 司令塔・取込・エンジン・検証 の担当整理(読み取り専用の調査)

調査日 2026-11-12。すべて `origin/main` を `git show` / `git grep` で読んだ。作業ツリーには触れていない。
表記: 「事実」は `repo@sha:path:行` か識別子つき。推測は **推測**、確認できなかったものは **未確認** と書く。

## 読んだもの

| repo | commit | version | 読んだファイル | 未確認 |
|---|---|---|---|---|
| Velisa (AI-video-production-OS) | 45a40f1 | tag v0.9.0 | `ecosystem.json`, `docs/ecosystem/ROADMAP.md`(7-56, 300-445行), `docs/CAPABILITY_MATRIX.md`(1-14, 163-310行), `docs/ecosystem/{CROSS_REPO_STATUS,CURRENT_STATE,HANDOFF,DECISION_LOG}.md` と `docs/REPOSITORY_MAP.md`(担当リポ名で grep した行のみ), `docs/ecosystem/capability-status.json`(キーのみ), issue #33 #34 #36 | 5 文書の全文は読んでいない(grep で当たった行だけ) |
| video-production-agent | b2d4e08 | pyproject 0.1.0(タグなし) | `docs/skills.md`, `ECOSYSTEM_ROADMAP.md`(見出しと手順の行), `src/video_agent/skills/registry.py`(全 SkillSpec), `skills/handoff_contracts.py`, `skills/pins/*`, `tools/*/adapter.py` の版ゲート行, `tools/ffmpeg_skill/catalog.py`, pin した契約 JSON(tools / provides / not_provided), `agent/{ingest,audio,qc,takes,word_cut,transcript_verify,documents,crop,faces,slides,bgm}.py` の冒頭, `service.py`(propose 部) | `docs/decisions.md`(ADR 本文)は読んでいない。ADR 番号はコード内コメントからの引用 |
| ingest-skill | 38f2c29 | pyproject 0.1.0(タグなし) | `README.md`, `ECOSYSTEM_ROADMAP.md`, `src/ingest_skill/contract.py`(tools / provides / not_provided), ファイル一覧, ADR 一覧(題名のみ) | ADR 本文、`fetch.py` の中身 |
| ffmpeg-skill | 11c153e | package.json 3.6.5(`git describe` は v3.6.3) | `package.json`, `docs/contract.md`(1-150行), `docs/roadmap.md`(1-80行), `SKILL.md`(54-66行), `README.md`(60-80行), `scripts/_contract.py`(78-232行の役割表), `scripts/check.py`(1-75行と関数一覧), `scripts/scenes.py`・`denoise.py`・`fit.py` 冒頭, 各ツールの引数名, `_common/probe.py`(検出関数の一覧), issue #417-#426 #401 #477 #53 と本文コメント | `docs/design-decisions.md` 本文、42 ツール全部の実装本体 |
| qc-skill | b7475e9 | 1.3.0 (v1.3.0) | `README.md`, `ECOSYSTEM_ROADMAP.md`, `src/qc_skill/contract.py`(40-110行), `docs/decisions.md`(見出しと ADR-007 / ADR-015 の該当段), `measurements/*.py` で使う ffmpeg フィルタ名, `temporal.py`・`text_legibility.py` 冒頭 | `docs/checks.md`, `rules.py` 本文 |
| media-analysis-skill | ab432c0 | 0.1.16 (v0.1.16) | `README.md`(36-42, 86-112, 150-182, 263-280行), `ECOSYSTEM_ROADMAP.md`(手順と Boundaries), `docs/decisions.md`(見出し), `highlights.py`・`library.py`・`analyzers/scenes.py`・`loudness.py` 冒頭, `STATE.md` 冒頭 | `CLAUDE.md`, `SKILL.md`, ADR 本文 |
| artifacts-skill | ae039d3 | 0.4.0 (v0.4.0) | `README.md`(127-157行), `ECOSYSTEM_ROADMAP.md`, `pyproject.toml`, `credits_check.py`・`text_checks.py`・`source_grounding.py`・`leftover_text.py`・`policies.py` 冒頭, agent が pin した `contract_0.4.0.json` | `docs/architecture.md` の "Captions" 節、MCP サーバー |
| (比較用) transcription-skill 99b59b8 / detection-skill 9e2f732 / sound-design-skill d974c26 (0.3.2) / stepcap 4f68e4c / publish-skill 7c6e61c | — | — | CLI のサブコマンド名、README の該当行、`detection_skill/shots.py` 冒頭だけ | これらは担当外。該当行以外は読んでいない |

## 各スキルが実際にできること

### video-production-agent (b2d4e08)
- アダプターは 22 個: `src/video_agent/tools/` 配下の `artifacts, audio_production, color_grading, detection, diarization, dubbing, ffmpeg_skill, imagemagick, ingest, media_analysis, motion_graphics, nle_bridge, publish, qc, remotion, slide_sync, sound_design, subtitle, thumbnail, transcription, video_editing, voice_enhance`。
- SkillSpec は `skills/registry.py` の `default_registry()` に全部ある。実装済み(phase 1)と、アダプターのない仕事の宣言(phase 2 の `ECOSYSTEM_JOB_SKILLS`, 229行〜)に分かれる。
- 自分では ffmpeg / ffprobe を呼ばない。`subprocess` は `capabilities/resolver.py:119`(検出)、`mcp_server.py:222`、`tools/ffmpeg_skill/*` だけ。
- 自分でやっている判断と計算(実行はしない): 無音の余白計算、テイク選び(`agent/takes.py`, ADR-053)、単語番号でのカット(`agent/word_cut.py`, ADR-109)、書き出し後の聞き直し照合(`agent/transcript_verify.py`, ADR-110)、QA の合否(`qa/checks.py`)。詳細は 9(e)。
- やらないと明記: plugin manager / installer / 動的 import / marketplace / remote registry(`docs/skills.md`「作らないもの」)。

### ingest-skill (38f2c29, 0.1.0)
- ツール 4 つ(`contract.py:13-23`): `ingest/offload`(実行、検証つきコピー), `ingest/verify`(計測), `ingest/inventory`(計測), `ingest/fetch`(実行、`network: True`, `deterministic: False`)。
- `offload` のオプション: `--proxy`(ffmpeg-skill `proxy` を下請けに出す、ADR-010)、`--follow`(収録中のファイル、ADR-007)、`--progress`(ADR-009)。
- `inventory`: カード構造ごとに 1 収録 1 クリップ、`sync`(開始 TC、LTC の有無、機材 ID)と `sync_groups`(マルチカムの候補。実測は ffmpeg-skill `multicam`)。README 36-37行。
- `fetch`: yt-dlp をライブラリとして使い、ステージングへ落としてからカードと同じ手順で取り込む。manifest の `"fetch"` に URL(認証情報は除去)、extractor、yt-dlp 版、題名を残す。**ライセンスや作者は記録しない**(README 39行に項目がない)。
- やらない(`contract.py:80` 〜 `not_provided`): 編集・変換、プロキシのエンコード自体、クラウドへのアップロード、ログインや DRM、プレイリスト、LTC のデコード、同期オフセットの実測。

### ffmpeg-skill (11c153e, 3.6.5, contract_version 2.0)
- ツールは 42 個(`scripts/` の `_` で始まらないもの)。全一覧は 9(b)。
- 役割の内訳(`_contract.py:78-232`): analysis = `probe, cropdetect, scenes`、analysis_and_execution = `sync, loudness, silence`、verification = `check, look, verify, report`、残りは execution。
- 決めないことを明記(`SKILL.md:54-66`): どのカットが正しいか、納品してよいか、何が見どころか、字幕の言葉、与えられていない被写体や領域の選択。「同じ入力と同じ引数なら同じ出力」が範囲。
- 依存は一方向(`README.md:76`): 他のスキルは呼ばない。

### qc-skill (b7475e9, 1.3.0)
- 操作 3 つ(`contract.py:47`): `inspect`(計測のみ)、`check`、`validate`。種類 5 つ(48行): `video, audio, subtitle, delivery, delivery_package`。ツール id は `qc/check`, `qc/inspect`, `qc/run`(別名)。
- 判定は呼び出し側が渡す型つきルールだけ。「YouTube は -14 LUFS」のような方針は埋め込まない(README「Measurement vs. Rule vs. Finding」)。結果は PASS / WARN / FAIL / UNKNOWN。
- 自前の計測(ffmpeg を直接呼ぶ): `ebur128`・`astats`・`silencedetect`(`measurements/audio.py`)、`blackdetect`・`freezedetect`・`signalstats`(`video.py`)、`scdet` と点滅(`temporal.py`, ADR-016/017)、`libvmaf`・`ssim`・`psnr`(`reference.py`, ADR-021)、文字の読みやすさ(コントラストとインク高、OCR なし、ADR-018)、スティンガーのアルファ(ADR-024)、ループの継ぎ目(ADR-025)、字幕の時刻と字幕対音声(ADR-023)。
- やらない(pin `contract_1.3.0.json` の `not_provided`): 制作判断、自動修復、AI による判定、文字起こし、意味理解、字幕の生成・翻訳、任意のフィルタグラフ。

### media-analysis-skill (ab432c0, 0.1.16)
- 計測の種類 13(README 150-166行): `media_probe, stream_layout, video_format, audio_format, duration, silence, loudness, integrity, scene_detection, timing, noise_floor, edit_style, speech_regions`。
- CLI だけの作業 2 つ(README 168-178行): `library index / search`(手持ち B ロールの索引、ADR-031)、`highlights`(長尺から見どころ候補、ADR-032)。
- `integrity` だけ PASS / WARN / FAIL を返す。ほかは値のみ。`speech_regions` は silero-vad(MIT、重み同梱、`vad` extra)。
- やらない(README 39-41行): AI、判断、方針、編集、書き出し。ffmpeg-skill には依存しない(README 106-109行)。

### artifacts-skill (ae039d3, 0.4.0)
- 形式 11: PDF, PPTX, DOCX, XLSX, 画像, HTML, SVG, CSV, Markdown, EPUB, Media(README 129-141行)。
- ツール(pin `contract_0.4.0.json` の `provides`): `inspect, plan, execute, render, verify, look, receipt`。
- **検証だけではなく書き換えもする**: PDF `merge / extract_pages / rotate_pages …`、PPTX `strip_placeholders`、画像 `resize / convert_format`(README 131-135行)。
- 文章の照合(全形式共通、`text_checks.py`): `source_grounding`(数値・日付・薬剤名・人名が出典にあるか)、`credits_attribution`(ライセンス記録とクレジット行の照合、`credits_check.py`)、置き忘れ文言(`leftover_text.py`)。
- やらない(`not_provided`): 字幕ファイル(SRT / WebVTT / ASS)の検証は subtitle-skill、映像に対する字幕の時刻は qc-skill、文書の生成、OCR、主観的なデザイン評価。

## 重複

| # | 仕事 | 誰が | やり方の違い | agent の今の振り分け |
|---|---|---|---|---|
| D1 | ラウドネス計測 | ffmpeg-skill `loudness --measure-only`(`loudnorm` の JSON、`loudness.py:68`)と `check.py:60-64`(同じく `loudnorm`)/ media-analysis `loudness`(`ebur128`)/ qc `audio.integrated_loudness_lufs`(`ebur128`) | 3 実装。フィルタが 2 種(loudnorm と ebur128)。qc はルールつき、media-analysis はキャッシュと Observation 契約つき、ffmpeg-skill は素の値 | `loudness_analysis` の候補は `ffmpeg-skill/loudness`, `media-analysis/loudness`。既定は ffmpeg-skill(`registry.py` `DEFAULT_PROVIDERS`)。qc は候補に入らない |
| D2 | 無音の検出 | ffmpeg-skill `silence --list` と `check --content`(`_common/probe.py:975, 1029` の `silencedetect`)/ media-analysis `silence` / qc `audio.silence_segments` | 3 か所(audio-production@origin/main の `src` に `silencedetect` はない。`loudnorm` の記述だけ)。media-analysis は先頭・中間・末尾を分類 | `silence_analysis` 既定は ffmpeg-skill。余白の引き算は agent 自身(`agent/audio.py:49`) |
| D3 | デコードの健全性 | media-analysis `integrity`(PASS/WARN/FAIL)/ qc `video.decodes_without_errors`, `audio.decodes_without_errors` | CAPABILITY_MATRIX §8a が既に衝突として記録 | `integrity_analysis` は media-analysis のみ。qc は最終ゲート |
| D4 | シーン(カット)検出 | ffmpeg-skill `scenes`(`scdet` + 音量の山 + `--shots` `--beats` `--highlights`)/ media-analysis `scene_detection`(`scdet`, `analyzers/scenes.py:71`)/ qc `video.scene_cuts`(`scdet`, ADR-017、予定カットとの照合用)/ detection-skill `shots`(PySceneDetect / TransNetV2、フレーム精度、`shots.py` 冒頭)/ slide-sync `detect`(`scdet`) | `scdet` を直接呼ぶ実装が 4 つ + 別エンジン 1 つ。出力の形と目的が違う(早い一覧 / Observation / 照合 / フレーム精度 / スライド) | `scene_analysis` → media-analysis、`beat_analysis` → ffmpeg-skill/scenes、`detection/shots` は未配線 |
| D5 | 黒・静止・点滅・レベル | ffmpeg-skill `check --content`(黒 / 静止 / 無音 / ドロップアウト / 点滅 / 先頭フレーム)と `check --levels bt709|ebu-r103`(`check.py` 冒頭 22-36行)/ qc `video.black_frames_within_tolerance`, `freeze_frames…`, `luminance_within_legal_range`, `photosensitive_flash_within_limit` | 両方とも合否を返す。ffmpeg-skill はしきい値が固定(例: 黒 WARN >10%)、qc はルールを渡す。点滅は qc が ITU-R BT.1702 準拠、ffmpeg-skill は「前後と違う 1 フレーム」 | qc のルールで判定(`agent/qc.py`)。`check --content` は catalog にない(`catalog.py:22` の flags) |
| D6 | 参照との画質比較 | ffmpeg-skill `check --compare`(SSIM / PSNR、`check.py:676-679`)/ qc `reference_metrics`(VMAF / SSIM / PSNR、ADR-021) | qc は VMAF あり、ずれた組を拒否。ffmpeg-skill は `--expect-changed` で「変えてよい範囲」も見る | どちらも agent は未使用(**推測**: registry に該当 SkillSpec なし) |
| D7 | 納品規格の合否 | ffmpeg-skill `check --platform`(`_platforms.py` の表)/ qc `validate`(kind `delivery`)/ agent 自身の QA(`qa/checks.py:61` `REQUIRED_SKILLS`)/ publish-skill `plan`(行ごとに PASS/WARN/FAIL、README 27-28行) | 4 者が合否を出す。対象が違う: ffmpeg-skill = 書き出し規格、qc = 計画が約束した値、agent = 期待との差、publish = アップロード側の制限 | `delivery_check` → `ffmpeg-skill/check`(AUTO、必須)。`qc_check` → `qc/check`(明示時のみ、最終ゲート、ADR-032) |
| D8 | プローブ | ffmpeg-skill `probe` / media-analysis `media_probe`, `stream_layout`, `video_format`, `audio_format`, `duration` / qc `probe.py` / artifacts-skill media アダプター(`rendering/ffmpeg_probe.py`)/ ingest `inventory`(ffprobe) | 5 か所が ffprobe を直接呼ぶ。artifacts 自身が「Media facts duplicate qc / media-analysis」と書いている(`ECOSYSTEM_ROADMAP.md` Boundaries) | `media_probe` 既定は ffmpeg-skill |
| D9 | 見どころ候補 | ffmpeg-skill `scenes --highlights`(音量か長さで順位)/ media-analysis `highlights`(文字起こしの文境界 + 音量 + 拍手などの外部信号) | 入力が違う(映像だけ / 文字起こし必須) | どちらも未配線(`highlights` は catalog の flag にあるが SkillSpec なし) |
| D10 | 言い直し・重複の候補 | ecosystem.json は agent の担当。実装は video-editing-skill `propose`(`service.py:254-258`, ADR-099)。agent には別に `takes.py`(テイクのグループ分け)がある | `propose` は単語列から繰り返し・言い直し・フィラーを出す。`takes.py` は類似度で同じ行のテイクをまとめる | `video-agent propose` → video-editing-skill |
| D11 | 無音カット | agent が余白を計算して `ffmpeg-skill/cut` か `video-editing/cut`(`silence_cleanup`)、音声は `audio-production` CUT / audio-production `SILENCE_REMOVE`(担当「無音・フィラー除去」)/ ffmpeg-skill `silence`(除去まで 1 回) | 同じ結果に 3 経路 | `SILENCE_REMOVE` は「adapter では実行できるが計画しない」(`agent/audio.py:49-50`) |
| D12 | 静止画の加工 | artifacts-skill 画像 `resize`, `convert_format` / imagemagick-skill `resize` ほか | artifacts は検証つきの書き換え、imagemagick は編集の本体 | agent は imagemagick の `strip / resize / pad` だけ使う |
| D13 | 素材の索引 | media-analysis `library index/search`(映像)/ sound-design `library-import/index/pick`(音、ライセンス宣言つき)/ ingest `inventory`(カード) | ライセンスを持つのは sound-design だけ | `bgm_library` → `sound-design/library-pick`。media-analysis の library は未配線 |
| D14 | クロップ・回転など | ffmpeg-skill `crop`, `fit`, `freeze`, `reverse`, `insert`, `overlay` / video-editing の同名 operation(下請けに ffmpeg-skill を使う) | 重複ではなく委譲。agent は video-editing 経由(ADR-079 で `crop` を移した) | `ffmpeg-skill/crop` と `fit` は catalog に残るが SkillSpec からは外れている |

## 隙間

| # | 仕事 | 根拠 | 今の状態 |
|---|---|---|---|
| G1 | 文字起こしの語句検索 | `ecosystem.json:72` で transcription-skill の担当 | transcription-skill の CLI に `search` がない(`cli.py:461-582` のサブコマンド: transcribe, segments, export, speakers, check, doctor, engines, batch, cache, models, run, contract, skill)。agent にもない(grep 0 件) |
| G2 | ストック素材の取得とライセンス台帳 | ROADMAP 365-370行(asset-library-skill、候補) | 実装なし。ingest `fetch` はライセンスを記録しない。artifacts `credits_attribution` は記録を**読む**だけ |
| G3 | 復元(超解像・フレーム補間) | ROADMAP 388-395行 | 実装なし。ffmpeg-skill にあるのは `fit` の `minterpolate`(スロー時のみ、`fit.py:169-170`)、`denoise`(hqdn3d)、`stabilize`、拡大縮小。詳細は 9(g) |
| G4 | 章分け(文字起こしから) | agent ROADMAP 手順 26(未着手)、ROADMAP 312行 | 未実装。`agent/slides.py:13`「chapters / inserts are … not wired yet」。ffmpeg-skill `metadata --auto-chapters` は存在するが誰も呼ばない |
| G5 | 長尺 → Shorts 一式 | agent 手順 25(未着手) | 未実装。部品(media-analysis `highlights`, detection `reframe`)は未配線 |
| G6 | 意味による削除 | agent 手順 13(未着手)、`semantic_deletion` phase 4 | 宣言のみ |
| G7 | マルチカム・同期の「担当スキル」 | Velisa #33 | ffmpeg-skill が実行、agent が直接呼ぶ(`camera_switch`, `sync_analysis`)。上位スキルなし。ecosystem.json では ffmpeg-skill の担当(「マルチカム同期」)なので、**担当は決まっているが CAPABILITY_MATRIX §9 が古い** |
| G8 | 納品レポート | `ecosystem.json:26` で ffmpeg-skill の担当(`report`) | agent の catalog にあるが(`catalog.py:40`)SkillSpec も呼び出しもない(`ffmpeg-skill/report` の grep 0 件) |
| G9 | 傾き補正 | 同上「手ぶれ・傾き補正」 | `stabilize` は配線済み、`straighten` は誰も使っていない |
| G10 | 拍手・笑いの検出 | media-analysis 手順 5(未着手) | `highlights` は呼び出し側から渡された区間だけ使う |
| G11 | 連番画像(PNG / EXR)と DNxHD の書き出し | ffmpeg-skill #417 / #419 のコメント「Not included」 | 別 issue にすると書かれたまま、該当 issue は**未確認**(open 一覧に見当たらない) |
| G12 | 提案 1-4(カット点候補、動くクロップ、音声だけのテンポとパッド、`audio --sample-rate / --channel`) | ROADMAP 401-404行 | ffmpeg-skill に対応 issue がない(題名検索で 0 件)。機能も main にない(`crop.py` は `--x --y --width --height` のみ、`audio.py` に該当引数なし) |

## ecosystem.json との食い違い

| 対象 | ecosystem.json | 実際 | 根拠 |
|---|---|---|---|
| video-production-agent `owns`「言い直し・重複の候補提示」 | agent の担当 | 候補を出すのは video-editing-skill `propose`。agent は呼ぶだけ | `service.py:254-258`, `cli.py:988-989` |
| transcription-skill `owns`「文字起こしの語句検索」 | 担当あり | 実装なし(G1) | transcription-skill@99b59b8 `cli.py` |
| ffmpeg-skill `owns`「納品レポート」 | 担当あり、実装あり(`report`) | エコシステム内に利用者がいない(G8) | agent@b2d4e08 grep |
| ffmpeg-skill `owns` に計測・シーン・ハイライト・無音がない | — | `probe`, `scenes`, `silence --list`, `loudness --measure-only` を持ち、agent の既定の計測元になっている | `registry.py` `DEFAULT_PROVIDERS` |
| media-analysis-skill `owns`「メディア計測」のみ | 計測だけ | B ロール索引(`library`)と見どころ候補(`highlights`)も持つ | README 168-178行 |
| artifacts-skill `role`「Verifies AI-generated documents」 | 検証 | 文書の書き換え(merge, resize など)と、クレジット行の照合、出典との照合も持つ | README 131-135行, `text_checks.py` |
| qc-skill `owns`「規格判定(QC)」のみ | 判定 | 自前の計測を 60 項目以上持つ(`contract.py:50-90`)。`inspect` は計測だけを返す | 同左 |
| ingest-skill `status: active` | active | 自身の `ECOSYSTEM_ROADMAP.md:3` は「status `scaffold`」。タグもリリースもない(0.1.0) | ingest-skill@38f2c29 |
| ingest-skill `owns`「URL素材取得」 | 担当 | 実装済みで agent も移行済み。ただし agent はアダプター外(`agent/ingest.py`)から呼び、`ingest/fetch` の SkillSpec がない | `agent/ingest.py:7-17`, `tools/ingest/adapter.py:157` |

## Velisa 文書との食い違い

| 場所 | 書いてあること | 実際 |
|---|---|---|
| `docs/ecosystem/ROADMAP.md:22` | nle-bridge は「`planned` in ecosystem.json」 | ecosystem.json は `"status": "active"` |
| `ROADMAP.md:13` | agent は ffmpeg-skill を「17 directly」 | SkillSpec が指す ffmpeg-skill ツールは 18(probe, silence, loudness, cut, export, check, audio, look, sync, scenes, multicam, grid, redact, deinterlace, stabilize, broll, cropdetect, render)。catalog は 21(+ fit, crop, report)。数え方の差は**未確認** |
| `ROADMAP.md:405-411` | 提案 5-11 は「accepted」 | #417 #418 #419 #421 #422 #423 は 2026-11-06 に completed で閉じ、PR #430 で出荷済み(`export --preset prores4444|…|key-fill`, `loudness --versions`, `loop --crossfade` が main にある)。#420 だけ open |
| `ROADMAP.md:409` | ARIB TR-B32 は -24 LKFS / -1 dBTP | #421 のコメントは `broadcast-jp` として同じ値で受理。食い違いなし(確認のみ) |
| `ROADMAP.md:422` | URL 取得は「until then the agent keeps it」 | 既に移行済み(agent ADR-059)。ROADMAP 12行目は正しく、422行だけ古い |
| `ROADMAP.md:429` | 規格検査の分担は「owner が決める」 | qc-skill は自分の文書で既に同じ分担を書いている(`ECOSYSTEM_ROADMAP.md` Boundaries、`docs/decisions.md` ADR-015「not a collision」)。Velisa 側に記録がない |
| `docs/CAPABILITY_MATRIX.md:232-261` | ffmpeg-skill は 21 ツール、`sync` は「available-but-unmapped」、`multicam` は agent で `implemented=False` | 42 ツール。`sync_analysis`(ADR-044)と `camera_switch`(ADR-045)は実装済み(`docs/skills.md`)。263行の「Superseded」注記は表を直していない |
| `CAPABILITY_MATRIX.md:254-255` | `check` と `scenes` は「Not confirmed identical」 | qc ADR-015 が `check` を比較済み。`scenes` は未比較のまま。qc も `scdet` を持つ(8b に行がない) |
| `CAPABILITY_MATRIX.md:187-189` | 黒・静止・クリップは「qc-skill only」 | ffmpeg-skill `check --content` も黒・静止・無音を測って合否を出す |
| `CAPABILITY_MATRIX.md:206` | ffmpeg-skill のノイズ床は「公開されていない」 | 確認していない(**未確認**) |
| `docs/ecosystem/CROSS_REPO_STATUS.md:12, 22` | 「21 base tools」「all 10 Skills」 | 42 ツール、アダプター 22 |
| `docs/ecosystem/CURRENT_STATE.md:52` | 「21 base-layer tools」 | 42 |
| `docs/REPOSITORY_MAP.md:32, 40, 41` | agent「via 9 skill adapters」、qc 0.1.0、media-analysis 0.1.0 | 22 アダプター、qc 1.3.0、media-analysis 0.1.16 |
| REPOSITORY_MAP / CROSS_REPO_STATUS / CURRENT_STATE | ingest-skill と artifacts-skill の行がない | 両方とも active で配線済み |
| artifacts-skill `ECOSYSTEM_ROADMAP.md:8` | 「v0.3.0」 | 0.4.0(agent の pin も 0.4.0) |

## 進行中の作業

| repo | 番号 | 内容 | 関係 |
|---|---|---|---|
| Velisa | #33 (open) | multicam / sync に担当スキルがない | G7 |
| Velisa | #34 (open) | export に利用者なし、render / batch に担当注記なし | 9(b) |
| Velisa | #36 (open) | check 対 qc、scenes 対 scene_detection | D4, D5, D7。qc ADR-015 が前半に回答済み |
| Velisa | #35 (open) | CAPABILITY_MATRIX が古い | 上の食い違い |
| ffmpeg-skill | #420 (open) / #477 (open) | マルチトラック音声。#477 は同じ依頼の重複(audio-production STEMS から) | 提案 8 |
| ffmpeg-skill | #424 (open) | 収録中ファイルと LTC | 提案 12 |
| ffmpeg-skill | #425 (open) | overlay の型つきキーフレーム | 提案 13 |
| ffmpeg-skill | #442 (open) | `check --expect-changed` の第 2-4 段階 | D6(qc の参照比較と近づく) |
| ffmpeg-skill | #464, #459, #458 (open) | 2026-11 監査: export / check / loudness、sync / multicam / scenes、render / batch | 担当整理より先に不具合修正が走っている |
| ffmpeg-skill | #453, #454 (open) | `color --keep-alpha` | 担当外、提案 5 の後続 |
| ffmpeg-skill | #484 (PR) | 全ツールで probe の記述どおりに映像と音声を map | — |
| qc-skill | #28 (PR) | roadmap 手順 8(静止した時間)、9(レンダー講評レポート) | 9 は ffmpeg-skill `report` と近い(**推測**、本文未読) |
| qc-skill | #7 (open) | 測っているのに判定していない値 | ADR-015 で大半は閉じた |
| artifacts-skill | #73 (PR) | release v0.5.0 | agent のゲートは `0.3.` `0.4.` のみ。出ると再 pin が要る |
| video-production-agent | #50 (open) | URL 素材から見どころを切る 3 つの隙間 | G5, D9 |
| video-production-agent | #105 (PR) | handoff に `/plugin install` を表示 | — |
| ingest-skill / media-analysis-skill | — | open の PR / issue なし | — |

## 選択肢

各行で ◎ が推奨。影響は「agent の配線 / ffmpeg-skill への依頼 / 依存 / ライセンス / 決定性」の順。

### S1 規格の検査(D5, D7): ffmpeg-skill `check` と qc
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | 分担を記録する。`check` = エンジンの出荷前点検(固定の表としきい値、修正コマンドつき)。qc = 計画に対する判定(ルールは呼び出し側、UNKNOWN あり)。agent は今のまま両方 | 配線変更なし。ffmpeg-skill への依頼なし。依存・ライセンス変更なし。決定性は両方とも維持。Velisa の CAPABILITY_MATRIX §8b / §9 と ROADMAP 429行を直すだけ |
| B | qc が計測を ffmpeg-skill `check --json` / `probe` に委ねる | qc が ffmpeg-skill に依存する(今は依存なし)。qc の契約と agent の pin を作り直す。`check` のしきい値固定と qc の「方針を埋め込まない」が衝突する |
| C | agent の `delivery_check` を qc に一本化し `check` を外す | `qa/checks.py` の必須スキルを変える。qc がない環境で QA が動かなくなる。プラットフォーム表を qc に渡す変換が要る |

### S2 計測の三重持ち(D1-D4, D8)
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | 現状の 3 実装を「同じ Capability id の提供者が複数」として記録し、既定を明記する(計測 = ffmpeg-skill が既定、media-analysis は Observation が要るとき、qc は判定の中だけ)。値の差を出す比較テストを Velisa 側に置く | 配線変更なし(`DEFAULT_PROVIDERS` が既にこの形)。依頼なし。決定性: loudnorm と ebur128 の差を数値で持てる |
| B | media-analysis を唯一の計測元にし、qc と ffmpeg-skill の利用者はそれを読む | qc と agent の経路を作り直す。ffmpeg-skill は単体利用があるので削れない。得るものが少ない |
| C | 共有ライブラリを作る | 新しいリポか依存が増える。3 スキルとも「標準ライブラリのみ」をやめることになる |

### S3 シーン検出が 5 か所(D4)
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | 用途で名前を分けて記録: 早い一覧 = ffmpeg-skill `scenes`、Observation = media-analysis、フレーム精度 = detection `shots`、照合 = qc、スライド = slide-sync。CAPABILITY_MATRIX §8 に qc の `video.scene_cuts` と detection の `shots` を足す | 配線変更なし。依存なし。決定性: `scdet` 系は同じ、detection は PySceneDetect / TransNetV2(重みのライセンスは detection-skill の ADR 側、**未確認**) |
| B | qc の照合を detection `shots` の出力読みに替える | qc に入力が 1 つ増える。agent が `detection/shots` を配線する必要がある |

### S4 言い直し・重複の候補(D10)
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | `ecosystem.json` の `owns` を実態に合わせる: 候補の計算は video-editing-skill、agent は「候補の提示と承認」 | 配線変更なし。`owns` の重複検査(`scripts/tests/test_ecosystem_manifest.py`)に注意 |
| B | `propose` を agent に戻す | agent が単語列の解析を持つことになり「実行も計測もしない」に反する |

### S5 無音カットの 3 経路(D11)
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | 今の形を記録: 検出は計測スキル、余白は agent の判断、カットは video-editing / audio-production の CUT。`SILENCE_REMOVE` と ffmpeg-skill `silence` の一括除去は単体利用向け | 変更なし。決定性は今のまま(余白が Decision に残る) |
| B | 音声経路を `SILENCE_REMOVE` に寄せる | agent の計画と lowering を書き換える。余白の根拠が Skill の中に入り、Decision から見えなくなる |

### S6 文字起こしの語句検索(G1)
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | transcription-skill に `search` を作る(担当どおり) | agent は pin を上げて計測として配線。依存なし |
| B | `owns` から外し、agent の編集ビュー(手順 14)に含める | ecosystem.json を変える。検索が agent の中に入る |

### S7 ffmpeg-skill の利用者なしツール(G7-G9, 9(b))
| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A | 「agent が直接呼ぶエンジンの仕事」として明記し、CAPABILITY_MATRIX §9 を 42 行に作り直す。`report`・`straighten`・`metadata` は agent の配線候補として列挙だけする | 配線変更は任意。ffmpeg-skill への依頼なし |
| B | multicam / sync / export を video-editing-skill の operation に包む(Velisa #33 / #34 の案) | video-editing の契約が増え、agent の `camera_switch` などを付け替える。ecosystem.json の「マルチカム同期」を移す |

### S8 asset-library(G2)、復元(G3)
9(f)、9(g) に書いた。

## 追加の問い

### (a) video-production-agent の配線表

版ゲート = `SUPPORTED_SKILL_VERSIONS`(各 `tools/<x>/adapter.py`)。pin = `contract_<版>.json`。「未配線」は pin の `tools` にあって SkillSpec が指していないもの。

| ecosystem.json の部品 | アダプター | 版ゲート / pin | SkillSpec → tool | pin にあるが配線していないもの |
|---|---|---|---|---|
| video-production-agent | (本体) | 0.1.0 | — | — |
| ingest-skill | `tools/ingest` | `0.1.` / 0.1.0 | `media_offload` → `ingest/offload`。`inventory` と `verify` はアダプター内。`fetch` は `agent/ingest.py` から直接 | `ingest/fetch` の SkillSpec、`--proxy` `--follow` `--progress`(ingest ROADMAP「re-pin on its side」) |
| ffmpeg-skill | `tools/ffmpeg_skill` | 0.8.4 ≤ v < 4.0.0、契約メジャー 1 / 2 | 18 ツール(上の一覧) | catalog のみ: `fit`, `crop`, `report`。catalog 外の 21: `background, batch, caption, color, denoise, freeze, graphics, insert, join, loop, metadata, overlay, pad, proxy, reverse, sequence, speedramp, sphere, straighten, verify, waveform` |
| video-editing-skill | `tools/video_editing` | `0.1.`〜`0.7.` / 0.7.0 | `video_concat, speed, resize, fit, fill, overlay, trim, rotate, punch_in, condense, cut, image_insert, crop` + `silence_cleanup` の候補 | FREEZE, REVERSE(手順 17 未着手)。`propose` は CLI 経由 |
| color-grading-skill | `tools/color_grading` | `0.2.`〜`1.1.` / 1.1.0 | `color_*` 8 種 → `color-grading/run`、`thumbnail_frame_ranking` の候補 | `alpha_mode` / `drop_alpha` |
| motion-graphics-skill | `tools/motion_graphics` | `0.1.` `0.2.` / 0.2.19 | `motion_graphics` → `motion-graphics/run` | 計画しない要素型あり(`agent/finishing.py:139`) |
| subtitle-skill | `tools/subtitle` | `0.1.`〜`0.9.` / 0.9.1 | `subtitle_generation` → `generate`、`subtitle_burn_in` / `subtitle_mux` → `render` | `subtitle/translate`, `subtitle/mux`(tool id としては未使用) |
| thumbnail-skill | `tools/thumbnail` | `0.1.` / 0.1.16 | `thumbnail_frame, render, variants, layers, batch, frame_ranking` | `generate_background`(FLUX)は SkillSpec なし、`place_text`, `validate` |
| blender-skill | **なし**(handoff の pin のみ `skills/pins/blender-skill_0.31.0.json`) | — | `render_3d`(phase 2)→ `blender-skill/render` | 全部(実行しない) |
| remotion-ffmpeg-skill | `tools/remotion` | `0.12.` `0.13.` / 0.13.0 | `measured_motion` → `pipeline` | `analyze --emphasis` ほか |
| hyperframes-skill | **なし**(pin のみ `hyperframes-skill_0.8.0.json`) | — | `html_scene_render`(phase 2) | 全部 |
| audio-production-skill | `tools/audio_production` | `0.1.`〜`1.2.` / 1.2.0 | `audio_*` 14 種 → `audio-production/run` | `SILENCE_REMOVE`(実行可・計画しない)、`LOUDNESS_SET`, `STEMS`(`adapter.py:49`「the agent plans neither」) |
| voice-enhance-skill | `tools/voice_enhance` | `0.1.` / 0.1.0 | `voice_isolate, voice_dereverb, voice_bleed_reduce` | ステムを映像へ戻す処理(`agent/voice.py:12`) |
| dubbing-skill | `tools/dubbing` | `0.1.` `0.2.` / 0.2.1 | `speech_dub` → `dubbing/dub` | NARRATE, AUDIO_DESCRIPTION(phase 2 の `dubbing`) |
| sound-design-skill | `tools/sound_design` | `0.1.`〜`0.3.` / 0.3.0 | `bgm_library` → `library-pick`、`bgm_generate` → `generate-bgm` | `generate-sfx`(「配線しない」)、`loop-bed`, `stinger`, `seam-check`, `sfx-cues`, `library-import`, `library-index` |
| transcription-skill | `tools/transcription` | `0.2.` `0.7.`〜`0.11.` / 0.11.3 | `speech_transcription` → `transcribe` | `segments, export, speakers, check, batch` |
| diarization-skill | `tools/diarization` | `0.1.`〜`0.3.` / 0.3.0 | `speaker_diarization` → `diarize` | 声紋の enroll / name / check(`adapter.py:64`) |
| detection-skill | `tools/detection` | `0.1.` `0.2.` / 0.2.2 | `face_detection`, `face_attributes` → `faces`(+ `tracks`) | `text, objects, shots, reframe, speakers, pii, rank, check`(phase 2 `visual_detection`) |
| slide-sync-skill | `tools/slide_sync` | `0.1.` / 0.1.0 | `slide_sync` → `detect`(+ import, match) | 章分け・差し込みへの利用(`agent/slides.py:13`) |
| qc-skill | `tools/qc` | `0.1.` `0.2.` `1.0.`〜`1.3.` / 1.3.0 | `qc_check` → `qc/check` | `qc/inspect` はアダプター内のみ。参照比較・スティンガー・ループ継ぎ目のルールは**未確認**(ADR-112 で一部配線と ROADMAP 手順 15 にある) |
| media-analysis-skill | `tools/media_analysis` | 契約 `1`、`0.1.` / 0.1.16 | `stream_layout, video_format, audio_format, duration, integrity, scene, timing, edit_style` + `media_probe / silence / loudness` の候補 | `media-analysis/noise`, `media-analysis/vad`(`adapter.py:31`「not planned」)、CLI の `library`, `highlights` |
| artifacts-skill | `tools/artifacts` | `0.3.` `0.4.` / 0.4.0 | `document_verify` → `artifacts-skill/verify` | `inspect, plan, execute, render, look, receipt`、`source_grounding`, `credits_attribution` の方針は**未確認**(agent が渡すのは置き忘れ文言の方針、`agent/documents.py` 冒頭) |
| publish-skill | `tools/publish` | `0.1.` / 0.1.0 | `publish_upload` → `publish/upload`(`plan` はアダプター内) | `publish/series` |
| nle-bridge-skill | `tools/nle_bridge` | `0.1.` / 0.1.0 | `nle_export`, `nle_conform`、`diff` は `revise --editor-timeline` | `nle-bridge/import` |
| imagemagick-skill | `tools/imagemagick` | `0.8.`〜`0.10.` / 0.10.0 | `image_strip, image_prepare, image_pad` | `still_image_edit`(phase 2)、`alpha` ほか約 20 ツール |
| bdmvkit / vtskit / udfkit / dvdcc / oncemore | **なし** | — | phase 2: `bluray_authoring, dvd_authoring, disc_image, dvd_line21_captions, disc_author` | 全部(handoff) |
| stepcap | **なし** | — | SkillSpec もなし(ROADMAP 24行「standalone by design」) | — |
| skillpact / system-intelligence | **なし** | — | なし(統制) | — |

アダプターがないもの: blender-skill, hyperframes-skill, stepcap, bdmvkit, vtskit, udfkit, dvdcc, oncemore, skillpact, system-intelligence(10 個)。

### (b) ffmpeg-skill の 42 ツール

「下請け」= pin した契約に `ffmpeg-skill/<tool>` か `<tool>.py` が出るスキル。「agent 直」= SkillSpec が直接指す。

| ツール | 役割 | 同じ仕事を出す別スキル | 利用者 | 担当注記の有無 |
|---|---|---|---|---|
| probe | 計測 | media-analysis(5 種)、qc、artifacts(media)、ingest inventory | ほぼ全スキル、agent 直 | あり(§8c) |
| cut | 実行 | video-editing CUT / TRIM / CONDENSE、audio-production CUT | video-editing, audio-production, sound-design, agent 直 | あり |
| fit | 実行 | video-editing FIT / FILL / RESIZE / SPEED / ROTATE | video-editing, remotion | あり |
| crop | 実行 | video-editing CROP / PUNCH_IN | video-editing | §9 に行なし |
| cropdetect | 計測 | なし | agent 直 | 行なし |
| deinterlace | 実行 | なし | agent 直 | 行なし |
| denoise | 実行 | なし(音は audio-production / voice-enhance) | **なし** | 行なし |
| redact | 実行 | なし(領域は detection が出す) | agent 直 | 行なし |
| waveform | 実行 | remotion / blender の可視化(ROADMAP 380行) | **なし** | 行なし |
| sphere | 実行 | なし | **なし** | 行なし |
| grid | 実行 | なし | agent 直 | 行なし |
| straighten | 実行 | なし | **なし**(担当「傾き補正」) | 行なし |
| freeze | 実行 | video-editing FREEZE | video-editing | 行なし |
| pad | 実行 | なし | dubbing | 行なし |
| speedramp | 実行 | video-editing SPEED(一定速のみ) | **なし** | 行なし |
| broll | 実行 | なし(担当「Bロール・画面合成」) | video-editing, agent 直(顔ぼかしの合成) | 行なし |
| metadata | 実行 | publish(説明欄の章)、slide-sync(章の元) | remotion | 行なし |
| loop | 実行 | sound-design `loop-bed`(音) | **なし**(pin 上) | 行なし |
| insert | 実行 | video-editing IMAGE_INSERT | video-editing | 行なし |
| background | 実行 | なし | motion-graphics | 行なし |
| reverse | 実行 | video-editing REVERSE | video-editing | 行なし |
| stabilize | 実行 | なし(担当「手ぶれ補正」) | agent 直 | 行なし |
| sequence | 実行 | なし | **なし** | 行なし |
| caption | 実行 | subtitle-skill(生成・焼き込み・mux) | subtitle | あり |
| overlay | 実行 | video-editing OVERLAY、motion-graphics | motion-graphics, video-editing, remotion | あり |
| graphics | 実行 | motion-graphics-skill | motion-graphics | あり |
| sync | 計測+実行 | なし | agent 直、remotion | 「unmapped」(古い)。#33 |
| multicam | 実行 | なし | agent 直。ingest と nle-bridge は呼び方を案内するだけ | 「implemented=False」(古い)。#33 |
| audio | 実行 | audio-production(16 operation) | audio-production, video-editing, dubbing, voice-enhance, agent 直(`audio_mux`) | あり |
| loudness | 計測+実行 | 計測: media-analysis, qc。正規化: audio-production NORMALIZE / LOUDNESS_SET | audio-production, dubbing, sound-design, agent 直 | あり |
| silence | 計測+実行 | 計測: media-analysis, qc。除去: audio-production SILENCE_REMOVE | video-editing, dubbing, remotion, agent 直 | あり |
| join | 実行 | video-editing CONCAT、audio-production CONCAT | 3 スキル + remotion | あり |
| color | 実行 | color-grading-skill | color-grading, motion-graphics, remotion | あり |
| proxy | 実行 | なし | ingest(`offload --proxy`) | 行なし |
| export | 実行 | なし(規格表は ffmpeg-skill の担当) | color-grading, video-editing, agent 直(`delivery_export`) | 「sole consumer なし」。#34 |
| check | 検証 | qc-skill、publish `plan`、agent QA | color-grading, remotion, agent 直(`delivery_check`) | 「Not confirmed identical」。#36 |
| scenes | 計測 | media-analysis, qc, detection shots, slide-sync | video-editing, remotion, agent 直(`beat_analysis`) | 同上。#36 |
| look | 検証 | thumbnail `extract_frame`、artifacts `look` | color-grading, thumbnail, video-editing, remotion, detection, agent 直 | あり |
| render | 実行 | video-editing の operation graph、nle-bridge(タイムライン書き出し) | agent 直(`--export-timeline` だけ)、remotion(`--template`) | 注記なし。#34 |
| batch | 実行 | transcription `batch`, thumbnail `render_batch`(別の物) | **なし** | 注記なし。#34 |
| verify | 検証 | qc(別の物: `verify` は ffmpeg-skill 自身の自己診断) | **なし** | 古い注記のみ |
| report | 検証 | qc PR #28 手順 9(**推測**) | **なし**(担当「納品レポート」) | 注記なし |

エコシステム内に利用者がいないツール: `denoise, waveform, sphere, straighten, speedramp, loop, sequence, batch, verify, report`(10 個)。単体利用(`npx ffmpeg-skill`)向けなので削る理由にはならない。

### (c) 規格の検査: 三者の実際

| | ffmpeg-skill `check` | qc-skill | media-analysis-skill |
|---|---|---|---|
| 返すもの | 行ごとの PASS / WARN / FAIL と修正コマンド(`fix`)、理由(`reason`) | check ごとの PASS / WARN / FAIL / UNKNOWN、計測値、finding | 値(`integrity` だけ合否) |
| 基準の出どころ | `_platforms.py` の表(youtube, shorts, reels, tiktok, x, linkedin, facebook, broadcast, podcast, custom)。`--content` と `--levels` のしきい値は固定 | 呼び出し側の型つきルールだけ。既定の方針なし | なし |
| 測るもの | 尺、サイズ、fps、コーデック、画素形式、色タグ、容量、LUFS / TP(`loudnorm`)。任意: 黒、静止、無音、ドロップアウト、点滅、先頭フレーム、レベル、`--compare`(SSIM / PSNR)、`--expect-changed` | 同じ項目 + VFR、フィールド順、クリップ、チャンネル、VMAF、点滅(BT.1702)、予定カット、文字の読みやすさ、字幕、スティンガー、ループ継ぎ目、複数ファイルの組 | プローブ系、無音、ラウドネス、健全性、カット、時刻、ノイズ床、編集スタイル、発話区間 |
| キャッシュ・来歴 | なし | あり(fingerprint、provenance) | あり(analysis identity) |
| 依存 | 標準ライブラリ + ffmpeg | 同左、ffmpeg-skill には依存しない | 同左 |

計測コードが重なる所: ラウドネス(3)、無音(3)、黒・静止(2)、レベル(2: 両方 `signalstats`)、点滅(2、定義が違う)、SSIM / PSNR(2)、`scdet`(3 + slide-sync)、ffprobe(5)。

記録すべき分担(推奨): **ffmpeg-skill `check` = 書き出し直後のエンジン側点検(固定の規格表、直し方つき)。qc-skill = 計画が約束した値に対する最終判定(ルールは agent が IR から作る)。media-analysis-skill = 判断の前に取る事実(合否を出さない。`integrity` は例外として現状維持)。** qc-skill は既にこの文言を自分の ROADMAP に持つ。agent の実装(ADR-032「qc は追加のゲートで、置き換えではない」`agent/qc.py:8-10`)とも合う。

### (d) 計測の重なり

| 計測 | ffmpeg-skill | media-analysis | qc | ほか |
|---|---|---|---|---|
| コンテナ・ストリーム | probe | media_probe, stream_layout, video_format, audio_format, duration | probe.py | artifacts(media), ingest inventory |
| ラウドネス(I / LRA / TP) | loudness, check(loudnorm) | loudness(ebur128) | audio.py(ebur128) | — |
| 無音 | silence, check --content | silence | audio.py | — |
| カット | scenes | scene_detection, edit_style | temporal.py | detection shots, slide-sync |
| 黒・静止 | check --content | なし(範囲外と明記) | video.py | — |
| レベル(合法範囲) | check --levels | なし | video.py(signalstats) | color-grading LEGALIZE(直す側) |
| デコード健全性 | 各ツールの verify | integrity | _decode_errors.py | — |
| ピーク・RMS・クリップ | check(volumedetect、`check.py:587`) | noise_floor(astats) | audio.py(astats) | — |
| 参照比較 | check --compare | なし | reference.py | — |
| クロップ枠 | cropdetect | なし | なし | — |
| ビート | scenes --beats | なし | なし | — |
| 同期オフセット | sync, multicam | timing(A/V 開始差のみ) | なし | ingest(時計からの候補のみ) |
| 発話区間 | scenes --speech(エネルギー比) | speech_regions(silero-vad) | なし | transcription |

三重: コンテナ・ストリーム、ラウドネス、無音、カット。二重: 黒・静止、レベル、健全性、ピーク、参照比較、発話区間。

### (e) agent が自分でやっていること

| 仕事 | agent の実装 | スキル側 | あるべき場所(推奨) |
|---|---|---|---|
| URL 取得 | `agent/ingest.py:7-17`: `ingest fetch <url> --json` を呼ぶ。yt-dlp は持たない(ADR-059) | ingest-skill `fetch` | **解決済み**。残りは `ingest/fetch` を SkillSpec にして handoff と版ゲートに載せること |
| 無音の余白計算 | `agent/audio.py:49`「the agent already subtracts margins itself」 | audio-production `SILENCE_REMOVE`、ffmpeg-skill `silence --margin` | agent のまま(Decision に根拠を残すため)。S5-A |
| 言い直し候補 | `service.py:254` で video-editing `propose` を呼ぶ | video-editing-skill | video-editing-skill。`owns` を直す(S4-A) |
| テイクのグループ分けと採点 | `agent/takes.py`(類似度、計測値の加点、ADR-053) | なし(transcription の台本整列は別) | agent のまま(判断)。類似度計算だけ transcription-skill へ移す案は**推測** |
| 単語番号カット | `agent/word_cut.py`(ADR-109) | なし | agent(判断の語彙) |
| 文字起こしの検索 | なし | transcription-skill(担当だが未実装) | transcription-skill(S6-A) |
| 書き出し後の聞き直し照合 | `agent/transcript_verify.py`(ADR-110、聞く箇所の一覧) | qc の字幕対音声(ADR-023)が近い | agent のまま(QA の状態を変えない一覧)。qc への移管は owner 判断 |
| Shorts 一式 | 未実装(手順 25)。`shorts` はプラットフォーム名としてだけ出る | media-analysis `highlights`, detection `reframe`, subtitle, publish `series` | agent が計画、部品は各スキル |
| 章分け | 未実装(手順 26) | ffmpeg-skill `metadata --auto-chapters`, slide-sync, publish | agent が提案、書き込みは ffmpeg-skill `metadata` |
| レビュー一覧 | `transcript_verify` の「listen and check here」一覧、`propose` の候補文書 | qc PR #28 手順 9(講評レポート、**未確認**) | agent(ProductionReceipt の一部) |
| QA の合否 | `qa/checks.py`(尺・ストリーム・ラウドネス・TP)。計測は選ばれたツール | qc-skill | 今のまま(qc は追加ゲート)。S1-A |
| 発話のまとめ | `agent/speech_inference.py`(間隔のマージ) | media-analysis `speech_regions` | agent(推論)。計測は media-analysis |

### (f) asset-library-skill の候補

| 比較 | 取得 | 記録するもの | ライセンス | 検索 |
|---|---|---|---|---|
| ingest-skill `fetch` | 1 本の URL(yt-dlp)、検証つきコピー | URL、extractor、版、題名、ハッシュ、ASC MHL | **記録しない**。「権利は利用者が持つこと」とだけ書く(README 40行) | なし |
| ingest-skill `inventory`(素材台帳) | — | カードのクリップ、機材、TC | なし | なし |
| sound-design-skill library | 利用者の手持ちファイルを `library-import`(ネットワークなし) | `sound-library.json`: `licence, kind, tags, mood, loopable, source, author, credit` | 宣言必須(`LICENCE_REQUIRED`)、`verified: false`、不明は使わない | `library-pick` |
| media-analysis-skill `library` | 手持ちの映像フォルダを索引(書くのは索引だけ) | 計測タグと外部タグ | なし | `library search` |
| artifacts-skill `credits_attribution`(0.4.0) | — | — | ライセンス記録を**読んで**クレジット文を照合 | — |
| asset-library-skill(案) | Pexels / Pixabay / Openverse / Wikimedia の API | `asset-library/asset@1`(licence, author, attribution, sha256) | 素材ごとに記録、条件の不明な出どころは拒否 | `assets search` |

| 案 | 内容 | 影響 |
|---|---|---|
| A 新しいリポ | ROADMAP 365-370行のとおり | agent にアダプターと pin が 1 つ増える。依存: 各 API のキー(`request_credential` 相当、環境変数か keychain)とネットワーク。ライセンス: コードは自前(MIT)、素材は出どころごと。決定性: 検索結果は日によって変わるので `deterministic: False`。ffmpeg-skill への依頼なし |
| ◎ B まず Velisa の仕様だけ(ライセンス記録の形を 1 つに決める)、実装は後 | sound-design の `sound-library.json` の項目と artifacts `licence_records` の読み方を突き合わせ、`asset@1` を共通の形として Velisa に置く。取得は当面 ingest `fetch` + 利用者の宣言 | 配線変更なし。新しい依存なし。今ある 3 つ(sound-design, media-analysis library, artifacts)がそのまま使える。API 利用規約の確認(**未確認**: 各サービスの規約は読んでいない)を ADR で済ませてから A に進める |
| C ingest-skill に畳む | `ingest fetch` に検索と出どころ別 API を足す | ingest の「検証つきコピー」という単純さが崩れる。`not_provided` の「network access outside ingest fetch」を書き換える。ingest は 0.1.0 でリリースもまだ |

推奨は B。理由: 取得(ingest)、音の台帳(sound-design)、映像の索引(media-analysis)、照合(artifacts)が既にあり、欠けているのは**映像・画像のライセンス記録の形**と**API での検索**だけ。前者は仕様、後者は規約確認が先。A に進むときは ingest `fetch` を下請けに使い、ダウンロードを二重に実装しない。

### (g) 復元(超解像・フレーム補間)

| ffmpeg-skill に今あるもの | 根拠 | 復元として足りるか |
|---|---|---|
| 拡大縮小 | `fit --width/--height`, `export`(プリセットのスケール) | 補間だけ。細部は増えない |
| fps 変換 | `fit --fps`(一定 fps 化)、各ツールの `fps=` | フレームの複製か間引き |
| 動き補間 | `fit --smooth interpolate` → `minterpolate`(`fit.py:169-170`)。**スローにするときだけ** | fps を上げる単独の操作はない |
| 手ぶれ補正 | `stabilize`(vidstab 2 パス) | あり |
| ノイズ低減 | `denoise`(hqdn3d) | あり(細部は減る、と自分で書いている) |
| インターレース解除 | `deinterlace`(yadif) | あり |
| その他 | `color`(zscale / libplacebo のトーンマップ) | 復元ではない |

| 案 | 内容 | 影響 |
|---|---|---|
| ◎ A 新スキルは作らず、重みなしの基準を先に配線する | agent に「アーカイブ素材の下ごしらえ」として `deinterlace` → `denoise` → `stabilize` → `fit` を並べる。超解像は ADR が重みのライセンスを記録するまで待つ | agent に `denoise` の catalog と SkillSpec を足す。ffmpeg-skill への依頼は 1 つだけ候補: 「fps を上げる補間」を `fit` の独立した引数にする(新規、提案 1-14 にない)。依存なし。ライセンス: FFmpeg のみ。決定性は保てる |
| B 新スキル `restoration-skill` を今作る | ROADMAP 392-395行の UPSCALE / INTERPOLATE | アダプターと pin が 1 つ増える。依存: GPU(実用上)、PyTorch か ncnn。ライセンス: Real-ESRGAN のコードは BSD-3-Clause(ROADMAP の記載)、**重みは未確認**。補間エンジンは候補も未確認。決定性: GPU と版で画素が変わるので、検収は qc の VMAF / SSIM(ADR-021)に頼る。出力は AI_GENERATED の印が要る |
| C ffmpeg-skill に `dnn_processing` 系を頼む | エンジンに入れる | ffmpeg-skill の「ローカルの FFmpeg だけ」「同じ入力なら同じ出力」に合わない(#426 を断った理由と同じ)。断られる見込み(**推測**) |

推奨は A。新スキルが要るのは「重みを使う」と決めたときで、その判断は ADR(コードと重みの両方のライセンス)が先。

### (h) artifacts-skill「生成文書の検証」の重なり

| 相手 | 重なるか | 根拠 |
|---|---|---|
| stepcap(手順書) | 重ならない。stepcap は `guide.md / guide.html / checklist.html` を**作る**側で、検証機能は見当たらない(README 31, 60行)。artifacts は HTML / Markdown を検証できるので、stepcap の出力を artifacts に通す連携が空いている | stepcap@4f68e4c README。stepcap 内部の検査は**未確認** |
| publish のメタデータ | 部分的に隣り合う。題名・説明・タグの**長さ制限**は publish `plan`(PASS / WARN / FAIL)。説明文の**クレジット行や出典**は artifacts(`credits_attribution`, `source_grounding`)。同じ説明文を 2 つが別の観点で見る | publish README 27-28行、artifacts `credits_check.py` 冒頭 |
| 字幕の検証 | 重ならない(明示的に除外)。SRT / WebVTT / ASS は subtitle-skill と qc-skill | artifacts `not_provided` 先頭 3 行、README 151-156行 |
| qc の文字チェック | 対象が違う。qc は**映像の中**の文字(コントラスト、インク高、ADR-018)と字幕の文字数・行頭禁則(ADR-023)。artifacts は**文書**の文字 | qc `text_legibility.py`, artifacts `text_checks.py` |
| qc / media-analysis の計測 | 重なる。artifacts の media アダプターが ffprobe で事実を取る | artifacts `ECOSYSTEM_ROADMAP.md` Boundaries「Media facts duplicate qc / media-analysis」 |
| imagemagick | 重なる。画像の `resize`, `convert_format` | README 135行 |
| ProductionReceipt | 名前は整理済み(「Artifact Verification Receipt」に改名、手順 2) | 同 ROADMAP |

`owns` に足すと実態に合うもの(推奨): 「クレジット・出典の照合」。media アダプターと画像の書き換えは「文書に付く添付の検証用」と範囲を書いておけば、qc や imagemagick と取り合いにならない。

### (i) ffmpeg-skill への提案 1-14 の状態

| # | 提案 | issue | 状態(2026-11-12) | 待っている担当の問い |
|---|---|---|---|---|
| 1 | 無劣化カットのカット点候補 | **なし** | 未起票。`cut.py` は事後の `lossless_alternative` だけ(`cut.py:1864`) | なし(起票するかどうか) |
| 2 | 時間で動くクロップ | **なし** | 未起票。`crop.py` は 1 矩形 | 動く枠を当てるのは video-editing(CROP / PUNCH_IN)か ffmpeg-skill か。detection `reframe` の出力の受け手 |
| 3 | 音声だけのテンポとパッド | **なし** | 未起票。`pad` は映像つき、`audio.py` に該当引数なし | 話速合わせは dubbing-skill の中か、audio-production の operation か |
| 4 | `audio --sample-rate`, `--channel N` | **なし** | 未起票。`loudness` と `join` には `--sample-rate` あり、`audio` にはない。`--audio-stream` はある | なし |
| 5 | アルファつきマスター | #417 | closed / completed(2026-11-06、PR #430)。PNG / EXR 連番は含まず | 連番書き出しの担当(`sequence` の逆)。未起票 |
| 6 | キーとフィルの組 | #418 | closed / completed。`export --preset key-fill` | なし。qc 側の「組の検査」は**未確認** |
| 7 | 中間コーデック | #419 | closed / completed(DNxHR のみ)。DNxHD は含まず | なし |
| 8 | マルチトラック音声 | #420(+ 重複の #477) | open。#401(監査 D)と同時にやる | ステムの束ね方を決めるのは audio-production(STEMS)。ファイルに書くのは ffmpeg-skill。#477 と #420 の統合 |
| 9 | ラウドネス違いを 1 回で | #421 | closed / completed。`loudness --versions` | audio-production `LOUDNESS_SET` と役割が重なる(配る側 / 作る側)。agent は未計画 |
| 10 | 継ぎ目のないループ | #422 | closed / completed。`loop --crossfade` | 音のループは sound-design `loop-bed`、検査は qc(ADR-025)。映像ループの利用者がいない |
| 11 | セーフエリアのガイド | #423 | closed / completed。プレビュー専用 | なし |
| 12 | 収録中ファイルと LTC | #424 | open、予定なし | 「途中までの読み」の保証を誰が定義するか(ingest `--follow` は自前でバイトを写す)。LTC のデコードは ingest が `not_provided` に入れている |
| 13 | overlay の型つきキーフレーム | #425 | open、範囲の問いが先 | **動くオーバーレイの担当**(ROADMAP 437行)。motion-graphics か、事前レンダー(hyperframes / remotion)+ `overlay` のままか |
| 14 | ARIB 字幕 | #426 | closed / not planned | なし。代替は subtitle-skill の TTML |

Velisa の ROADMAP 405-411行は「accepted」のままなので、5-7, 9-11 を「出荷済み」に直す必要がある(提案は Velisa 側の文書更新だけで、ffmpeg-skill には何も頼まない)。
