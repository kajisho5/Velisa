# 担当整理の調査（2026-11-12）

**状態: 調査と選択肢の提示まで。** 担当を決めるのはオーナーです。この調査では `ecosystem.json`、`DECISION_LOG.md`、各スキルのリポジトリを一切変更していません。issue や PR へのコメントも残していません。

## 何を調べたか

- 対象: `ecosystem.json` の 33 コンポーネントすべてと、`docs/ecosystem/ROADMAP.md` の「New skill candidates」「New areas (proposed)」「Decisions only the owner can make」の各項目。
- 方法: 各リポジトリの `origin/main` を読み取り専用で読みました（契約、SKILL.md、主要コード、ECOSYSTEM_ROADMAP.md、ADR）。読んだコミットと版は各ファイルの「読んだもの」の表にあります。
- 事実と推測の区別: 根拠は `repo@sha:path:行` で示しています。推論は **推測**、確かめられなかったものは **未確認** と書いています。
- 着手前の確認: Velisa の開いている PR は依存更新 7 件だけで、同じ調査は進んでいませんでした。関連する issue は #33〜#38 です。

## ファイル

| ファイル | 範囲 |
|---|---|
| [A-visual.md](A-visual.md) | 映像部門 9 スキルと静止画。テロップ、動くオーバーレイ、新スキル候補 3 つ |
| [B-audio-recognition.md](B-audio-recognition.md) | 音と認識の 8 スキル。モデルの重みのライセンス |
| [C-command-ingest-engine-verification.md](C-command-ingest-engine-verification.md) | agent の配線表、ffmpeg-skill の 42 ツール、検証 3 スキル、asset-library、復元 |
| [D-delivery-utility-governance-docs.md](D-delivery-utility-governance-docs.md) | 納品・補助・統制の 10 リポジトリ、Velisa 文書の食い違い 54 件、33 コンポーネントの修正案 |

各ファイルの構成は同じです: 読んだもの / 各スキルが実際にできること / 重複 / 隙間 / `ecosystem.json` との食い違い / Velisa 文書との食い違い / 進行中の作業 / 選択肢 / 追加の問い。

## オーナーが選ぶ項目（優先度順）

推奨は調査の結論で、決定ではありません。各案の影響（agent の配線、ffmpeg-skill への依頼、依存、ライセンス、決定性）は「詳細」の節に表があります。

### 1. 待ちが発生しているもの

| # | 選ぶこと | 推奨 | 詳細 |
|---|---|---|---|
| 1 | 動くオーバーレイの担当（ffmpeg-skill #425 がこれ待ち） | 素材は hyperframes-skill、配置は motion-graphics-skill の `rendered_layer`。両端は出荷済みで、足りないのは agent が hyperframes を実行する経路 1 本。#425 は実装不要になる | A §8 O1、§9(b) |
| 2 | `scaffold` の 4 つ（voice-enhance、dubbing、sound-design、publish）の status | `active` に直す。4 つとも全操作が実装済みで agent に配線済み。ただし git タグと GitHub Release は 4 つとも無い。あわせて `scaffold` の定義を 1 つにする（今は 3 通りある） | B §9(h)、D §5、§9(f) |
| 3 | プラットフォームの尺・サイズ上限が 2 か所にあり値が違う（例: X は ffmpeg-skill 140 秒、publish-skill 1200 秒） | 尺とサイズは publish-skill を正とする（2026-10-30 の決定「アップロード制限は publish」の延長）。ffmpeg-skill 側は目安と明記 | D §3 O1、§8 O1 |

### 2. 新スキル候補と新分野

| # | 候補 | 推奨 | 理由 | 詳細 |
|---|---|---|---|---|
| 4 | motion-titles-skill | **既存に取り込む**（hyperframes-skill）。`title.json` / `stinger.json` の形だけ Velisa の仕様に置く | 草案の大半は hyperframes 0.8.0 と ffmpeg-skill `export` にある。空いているのはスティンガーを作る側、多言語の組版、ブランド入力 | A §9(c) |
| 5 | design-system-skill | **Velisa の仕様だけ置く**（`kit@1`） | ブランド形式がすでに 3 つ並んでいる。読み口があるのは motion-graphics と remotion だけ | A §9(d) |
| 6 | asset-library-skill | **Velisa の仕様だけ置く**（ライセンス記録の共通の形） | 取得、音の台帳、クレジット照合は既存スキルにある。欠けているのは映像・画像の記録の形と API 検索 | C §9(f)、B §8 D16 |
| 7 | generative-media-skill | **ADR を先に**（新設しない） | 今ある生成は thumbnail-skill の背景画像だけ。重みのライセンスが未確認 | A §9(e) |
| 8 | 復元（超解像・フレーム補間） | 重みを使わない基準（ffmpeg-skill の拡大・補間）を先に配線。新スキルは重みのライセンスを ADR に記録してから | 重みのライセンスが未確認 | C §9(g) |

### 3. 担当の線の引き直し（`owns` の修正）

| # | 選ぶこと | 推奨 | 詳細 |
|---|---|---|---|
| 9 | テロップを 3 か所で作れる | 役割で分ける: 焼き込み = motion-graphics、素材ファイル = hyperframes、remotion のタイトルはコンポジション内だけ | A §8 O2、§9(a) |
| 10 | 静止画オーバーレイと PiP | video-editing = 編集としての静止画合成、motion-graphics = ロゴ・PiP・クロマキー、ffmpeg-skill = B ロールとエンジン | A §8 O3、§9(g) |
| 11 | 動く字幕の持ち主がいない | 字幕キューから出るものは subtitle-skill（ffmpeg-skill `caption` の既存フラグを通す）。語の時刻に合わせた演出は remotion | A §8 O4、§9(h) |
| 12 | ラウドネス正規化が agent の中で 2 経路 | 担当は audio-production、ffmpeg-skill はエンジンと明記。agent の経路を寄せるかは下の「調査間で推奨が割れた点」を参照 | B §8 D1、C §8 S2 |
| 13 | 規格の検査（ffmpeg-skill `check`、qc-skill、agent の QA、publish `plan`） | 分担を記録するだけ: `check` = エンジンの点検、qc = 規格に対する判定。配線は変えない。Velisa #36 を閉じられる | C §8 S1、§9(c) |
| 14 | 計測とカット検出が 3〜5 か所 | 層として記録: 速い一覧 = ffmpeg-skill、観測 = media-analysis、フレーム精度 = detection、判定の中 = qc、スライド = slide-sync | C §8 S2・S3、B §8 D12 |
| 15 | `owns` が実態と合わない 3 件 | 「言い直し・重複の候補提示」の計算は video-editing。「文字起こしの語句検索」は未実装（作るか `owns` から外す）。「納品レポート」は利用者なし | C §5、§8 S4・S6・S7 |
| 16 | 話者 ID の付与が 2 実装 | 規則の持ち主は diarization-skill。transcription 側は同じ規則の写しとし、適合テストを共有 | B §8 D10 |
| 17 | キネティックタイポ・ビジュアライザー・Three.js | 3 スキルで計画が重なるが実装はほぼ無い。着手前に 1 つに決める | A §9(f) |

### 4. 載せ方と文書

| # | 選ぶこと | 推奨 | 詳細 |
|---|---|---|---|
| 18 | ディスク一族 5 つ | `ecosystem.json` は 5 つのまま。agent の SkillSpec は oncemore 1 つに減らす（今は契約に存在しない tool_id を 3 つ名指ししている） | D §8 O4、§9(a) |
| 19 | stepcap と oncemore の位置づけ | 単体アプリとして載せ、種類を示す欄（`kind`）を足す | D §9(d) |
| 20 | 契約検査と監査の重複 | 役割を 1 行ずつ決めて書く: 契約の形 = system-intelligence、副作用・署名 = skillpact、実行時の版ゲート = agent | D §8 O5、§9(e) |
| 21 | 古い文書（HANDOFF、CROSS_REPO_STATUS、CURRENT_STATE） | 「2026-09 の記録」として凍結し、現状は ROADMAP.md に一本化。CAPABILITY_MATRIX と REPOSITORY_MAP は契約から生成 | D §6、§8 O7、A §8 O9 |

## 調査間で推奨が割れた点

- **無音・ラウドネス計測の既定の提供者。** B は「計測の第 1 候補を media-analysis にする」、C は「既定は ffmpeg-skill のまま記録する（agent の `DEFAULT_PROVIDERS` がすでにその形）」を推奨しています。配線を変えない C の案が安全です。変えるなら、`loudnorm` と `ebur128` の値の差を先に測ってからにします。
- **ライセンス台帳の置き場所。** B は「プロジェクトの台帳は asset-library が作る」、C は「asset-library は今は作らない」を推奨しています。両立する形は、記録の共通の形だけ先に Velisa の仕様に置き、台帳づくりは既存スキル（音は sound-design、照合は artifacts-skill）で足りなくなってから決める、です。

## Velisa の文書で事実と違っている主な箇所

全 54 件は D §6 にファイル名・行・引用つきであります。

- `docs/ecosystem/ROADMAP.md` の提案 5〜7、9〜11 は「accepted」ですが、ffmpeg-skill #417・#418・#419・#421・#422・#423 は 2026-11-06 に完了で閉じています。#420・#424・#425 は開いたまま、#426 は not planned です。
- `HANDOFF.md`、`CROSS_REPO_STATUS.md`、`CURRENT_STATE.md` は「9 Skills」「10 Skills」「12 repos」「21 base tools」のままです（実際は 33 コンポーネント、ffmpeg-skill は 42 ツール、agent のアダプターは 22）。
- `docs/CAPABILITY_MATRIX.md` に hyperframes、remotion、blender、imagemagick、voice、speech、vision、slides の行がありません。集計は 75 行と書いて実数は 78 行です。
- `docs/ecosystem/registry.json:112` は publish-skill を「owner of platform delivery specs」と書いており、2026-10-30 の決定と逆です。
- nle-bridge は `ecosystem.json` では `active` ですが、`docs/ecosystem/ROADMAP.md:22, :434` と agent の `skills/ecosystem.py:109` は `planned` のままです。
- agent の handoff が出すインストール先 `@ai-video-production-os` は、今の marketplace 名 `velisa` と合いません（agent PR #105 が開いたまま）。

## 未確認のまとめ

- **重みのライセンス。** FLUX.2 klein 4B と LTX-2（モデルカード未読）、Whisper の既定の重みと faster-whisper（リポジトリ内に記載なし）、超解像・補間の候補、各 ADR 自身が未確認としているもの（VOICEVOX の一部キャラクター、Style-Bert-VITS2 の CC BY-SA の及ぶ範囲、ACE-Step の学習データ、TransNetV2 の学習データ）。
- **決定性。** remotion-ffmpeg-skill の保証は契約にも文書にも記述が見つかりませんでした。
- **外部の規約。** ストック素材 API の利用規約、oncemore（GPL-3.0-or-later）を agent が別プロセスで呼ぶ場合の扱い。
- **読んでいない範囲。** 各リポジトリの README / CLAUDE.md の一部、agent と ffmpeg-skill の ADR 本文、Velisa の `WORK_QUEUE.md` と `DECISION_LOG.md` の全文（該当語の検索のみ）。各ファイル末尾に一覧があります。
- **実機。** 実プラットフォームへのアップロード、実 NLE での読み込み、実収録での音声系エンジンの計測は、各リポジトリ自身が未実施と書いています。

## この後

オーナーが選んだ後の反映（`ecosystem.json`、`DECISION_LOG.md`、各スキルの `ECOSYSTEM_ROADMAP.md` への作業追加、ffmpeg-skill #425 への連絡）は、別途の指示で行います。
