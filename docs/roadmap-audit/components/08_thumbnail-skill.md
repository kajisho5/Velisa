# 08　thumbnail-skill

サムネイル。依存・接点は 任意FF・QC。今回の優先度と概算は **P2/S**。

## 現在地と根拠

対象commit `3d3ba3b7d5154a1aca934fd973f331bec2b6fa0e`。Contract pin は `src/video_agent/tools/thumbnail/contract_1.0.0.json`。[対象commit](https://github.com/kajisho5/thumbnail-skill/commit/3d3ba3b7d5154a1aca934fd973f331bec2b6fa0e) · [利用仕様](https://github.com/kajisho5/thumbnail-skill/blob/3d3ba3b7d5154a1aca934fd973f331bec2b6fa0e/SKILL.md) · [Contract定義](https://github.com/kajisho5/thumbnail-skill/blob/3d3ba3b7d5154a1aca934fd973f331bec2b6fa0e/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/thumbnail/contract_1.0.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/thumbnail/adapter.py) · [既存試験](https://github.com/kajisho5/thumbnail-skill/blob/3d3ba3b7d5154a1aca934fd973f331bec2b6fa0e/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/08_thumbnail-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

表紙選定の根拠と実際の可読性を追いにくい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 候補静止画を元TCに結ぶ。
2. ブランド書体で複数候補を生成する。
3. QCが読めなかった候補を明示する。

## Contract・データの受け渡し

拡張案：候補IDからframe・kit・QC結果を参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：採用シーン→候補画像→人間選択。NGは文字配置へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

同一フレームの2案で背景は共通、選んだ案だけを納品し、QC未導入時には未測定を表示。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
