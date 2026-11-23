# 16　transcription-skill

文字起こし / 文字起こしの語句検索。依存・接点は ローカルASR。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `4dbffe6266670bbbb0645bcb9ff48a98ceebcf59`。Contract pin は `src/video_agent/tools/transcription/contract_0.14.0.json`。[対象commit](https://github.com/kajisho5/transcription-skill/commit/4dbffe6266670bbbb0645bcb9ff48a98ceebcf59) · [利用仕様](https://github.com/kajisho5/transcription-skill/blob/4dbffe6266670bbbb0645bcb9ff48a98ceebcf59/SKILL.md) · [Contract定義](https://github.com/kajisho5/transcription-skill/blob/4dbffe6266670bbbb0645bcb9ff48a98ceebcf59/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/transcription/contract_0.14.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/transcription/adapter.py) · [既存試験](https://github.com/kajisho5/transcription-skill/blob/4dbffe6266670bbbb0645bcb9ff48a98ceebcf59/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/16_transcription-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

日本語ASRの誤認を含む発話候補を元音声へ戻したい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 語単位で元TCを保存する。
2. 人名・数値の訂正履歴を保持する。
3. 修正後も候補の語を再同定する。

## Contract・データの受け渡し

拡張案：Transcriptの語IDと訂正revisionを互換追加候補にする。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：素材→Transcript→選択・字幕。誤認は発話単位で再確認。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

日本語2話者の一語を直し、時刻参照を保持したまま該当字幕だけ更新。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
