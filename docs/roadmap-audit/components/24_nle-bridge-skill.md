# 24　nle-bridge-skill

NLE連携(タイムライン受け渡し)。依存・接点は 任意FF・NLE交換ファイル。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `d8cdcec660e12dd1783c7aa8d442bbf8aa40f038`。Contract pin は `src/video_agent/tools/nle_bridge/contract_0.1.4.json`。[対象commit](https://github.com/kajisho5/nle-bridge-skill/commit/d8cdcec660e12dd1783c7aa8d442bbf8aa40f038) · [利用仕様](https://github.com/kajisho5/nle-bridge-skill/blob/d8cdcec660e12dd1783c7aa8d442bbf8aa40f038/SKILL.md) · [Contract定義](https://github.com/kajisho5/nle-bridge-skill/blob/d8cdcec660e12dd1783c7aa8d442bbf8aa40f038/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/nle_bridge/contract_0.1.4.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/nle_bridge/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/24_nle-bridge-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

NLEで変えた1カットをどこまで戻せるかの実機証拠が不足。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 素材IDとTCで再リンクする。
2. 変更区間だけdiff表示する。
3. 表現不能な編集を一覧にする。

## Contract・データの受け渡し

拡張案：既存diff・relinkを親recipe revisionに結合。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：project→NLE→diff→承認。未対応編集は手動照合へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

一つのtrim変更だけを既知の返却XMLから読み、他クリップと音声配置を保持。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
