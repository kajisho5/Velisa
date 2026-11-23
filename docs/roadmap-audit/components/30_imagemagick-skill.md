# 30　imagemagick-skill

静止画編集。依存・接点は ImageMagick。今回の優先度と概算は **P2/S**。

## 現在地と根拠

対象commit `ab7e59bb3ac49f8b0b31a2dbd60d9e18128021c8`。Contract pin は `src/video_agent/tools/imagemagick/contract_1.0.0.json`。[対象commit](https://github.com/kajisho5/imagemagick-skill/commit/ab7e59bb3ac49f8b0b31a2dbd60d9e18128021c8) · [利用仕様](https://github.com/kajisho5/imagemagick-skill/blob/ab7e59bb3ac49f8b0b31a2dbd60d9e18128021c8/SKILL.md) · [Contract定義](https://github.com/kajisho5/imagemagick-skill/blob/ab7e59bb3ac49f8b0b31a2dbd60d9e18128021c8/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/imagemagick/contract_1.0.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/imagemagick/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/30_imagemagick-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

ブランド色・透明縁が静止画から合成へ渡る際にずれる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. ICCの扱いを記録する。
2. 透過ロゴを黒白背景で比較する。
3. kitの指定色を照合する。

## Contract・データの受け渡し

拡張案：素材sidecarに色空間・alpha・kit版を参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：ブランド原本→画像→配置。色差NGは変換設定へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

半透明ロゴのサイズ・色・alphaが参照範囲内、静止画再生成で他素材は変わらない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
