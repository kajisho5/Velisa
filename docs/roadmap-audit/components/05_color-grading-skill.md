# 05　color-grading-skill

色補正 / LUT / HDR→SDR。依存・接点は FF。今回の優先度と概算は **P0/M**。

## 現在地と根拠

対象commit `f679706b9993fcc849b39f9ccd0cbf2fa776d115`。Contract pin は `src/video_agent/tools/color_grading/contract_1.1.4.json`。[対象commit](https://github.com/kajisho5/color-grading-skill/commit/f679706b9993fcc849b39f9ccd0cbf2fa776d115) · [利用仕様](https://github.com/kajisho5/color-grading-skill/blob/f679706b9993fcc849b39f9ccd0cbf2fa776d115/SKILL.md) · [Contract定義](https://github.com/kajisho5/color-grading-skill/blob/f679706b9993fcc849b39f9ccd0cbf2fa776d115/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/color_grading/contract_1.1.4.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/color_grading/adapter.py) · [既存試験](https://github.com/kajisho5/color-grading-skill/blob/f679706b9993fcc849b39f9ccd0cbf2fa776d115/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/05_color-grading-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

alpha保持のLUT・一次補正が入力の格納方式によって止まる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 下位機能を検出して条件付きで拒否解除する。
2. straight既定の回帰を確認する。
3. 半透明エッジ比較をReceiptへ添付する。

## Contract・データの受け渡し

拡張案：既存project.source.alpha_modeと下位のsource_alpha_modeを対応づける。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：ブランドマスター→grade→合成・QC。許容差超過は該当操作へ戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

03の2段階を通し、旧エンジンで理由付き拒否、新ビルドで同じAgent requestを完走。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
