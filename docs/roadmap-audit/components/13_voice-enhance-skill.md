# 13　voice-enhance-skill

声の分離(AI) / 残響除去 / マイク被り低減。依存・接点は FF・声分離モデル。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `81846e288be7366e1b301d9426da51378fc85a74`。Contract pin は `src/video_agent/tools/voice_enhance/contract_1.1.0.json`。[対象commit](https://github.com/kajisho5/voice-enhance-skill/commit/81846e288be7366e1b301d9426da51378fc85a74) · [利用仕様](https://github.com/kajisho5/voice-enhance-skill/blob/81846e288be7366e1b301d9426da51378fc85a74/SKILL.md) · [Contract定義](https://github.com/kajisho5/voice-enhance-skill/blob/81846e288be7366e1b301d9426da51378fc85a74/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/voice_enhance/contract_1.1.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/voice_enhance/adapter.py) · [既存試験](https://github.com/kajisho5/voice-enhance-skill/blob/81846e288be7366e1b301d9426da51378fc85a74/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/13_voice-enhance-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

声分離の聴感劣化や子音欠落を数値だけで判断できない。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 同区間の原音と処理音を試聴できるようにする。
2. 区間再処理を選択する。
3. エンジンと設定を固定する。

## Contract・データの受け渡し

拡張案：強調記録にモデル版・原音TC・処理区間。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：対談音声→声強調→音響。聞き取り悪化は原音へ切戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

マイクかぶり例で同期・尺を保持し、聴取NG区間だけ原音に戻せる。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
