# 06　motion-graphics-skill

タイトル・テロップ / ロゴ・PiP・クロマキー合成 / 動くグラフィックの配置。依存・接点は FF・生成済みレイヤー。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `d181c06c59147a3cb2ba5e9835759f34ab5b7f8c`。Contract pin は `src/video_agent/tools/motion_graphics/contract_1.0.0.json`。[対象commit](https://github.com/kajisho5/motion-graphics-skill/commit/d181c06c59147a3cb2ba5e9835759f34ab5b7f8c) · [利用仕様](https://github.com/kajisho5/motion-graphics-skill/blob/d181c06c59147a3cb2ba5e9835759f34ab5b7f8c/SKILL.md) · [Contract定義](https://github.com/kajisho5/motion-graphics-skill/blob/d181c06c59147a3cb2ba5e9835759f34ab5b7f8c/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/motion_graphics/contract_1.0.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/motion_graphics/adapter.py) · [既存試験](https://github.com/kajisho5/motion-graphics-skill/blob/d181c06c59147a3cb2ba5e9835759f34ab5b7f8c/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/06_motion-graphics-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

レンダー済みロゴが字幕や安全領域と衝突しうる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. ロゴ位置を画面座標でプレビューする。
2. 字幕との重なり候補を提示する。
3. 合成直前のブランド版を記録する。

## Contract・データの受け渡し

拡張案：配置記録に素材ID・時刻区間・正規化座標を任意追加。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：タイトル生成→配置→QC。重なりはレイヤー位置のみ再編集。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

縦横2出力の先頭・中間・末尾でロゴが指定範囲内、位置変更で字幕本文は不変。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
