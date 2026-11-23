# 18　detection-skill

顔検出 / 文字検出(OCR) / 物体検出 / ショット検出。依存・接点は 動画入力時FF。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `313b5f25ed537c126f06a100337eb3cfe4f90fcc`。Contract pin は `src/video_agent/tools/detection/contract_0.2.7.json`。[対象commit](https://github.com/kajisho5/detection-skill/commit/313b5f25ed537c126f06a100337eb3cfe4f90fcc) · [利用仕様](https://github.com/kajisho5/detection-skill/blob/313b5f25ed537c126f06a100337eb3cfe4f90fcc/SKILL.md) · [Contract定義](https://github.com/kajisho5/detection-skill/blob/313b5f25ed537c126f06a100337eb3cfe4f90fcc/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/detection/contract_0.2.7.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/detection/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/18_detection-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

固定クロップと登壇者の動きを混同すると顔が切れる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 各ショットの始中終で顔箱を測る。
2. 検出不能時刻を残す。
3. crop候補と箱の重なりを表示する。

## Contract・データの受け渡し

拡張案：検出時刻・座標系・信頼度を明示した観測参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：素材→検出→Plan・Vision。箱外ならpad案へ戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

移動と無人の2区間で、追跡不能を成功にせず、再構図を人が承認できる。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
