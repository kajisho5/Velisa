# 22　artifacts-skill

生成文書の検証。依存・接点は 原稿・証拠文書。今回の優先度と概算は **P1/S**。

## 現在地と根拠

対象commit `de3302c2c868cee84cd70cddb13eeceb2ce2264e`。Contract pin は `src/video_agent/tools/artifacts/contract_0.4.0.json`。[対象commit](https://github.com/kajisho5/artifacts-skill/commit/de3302c2c868cee84cd70cddb13eeceb2ce2264e) · [利用仕様](https://github.com/kajisho5/artifacts-skill/blob/de3302c2c868cee84cd70cddb13eeceb2ce2264e/SKILL.md) · [Contract定義](https://github.com/kajisho5/artifacts-skill/blob/de3302c2c868cee84cd70cddb13eeceb2ce2264e/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/artifacts/contract_0.4.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/artifacts/adapter.py) · [既存試験](https://github.com/kajisho5/artifacts-skill/blob/de3302c2c868cee84cd70cddb13eeceb2ce2264e/tests/integration/__init__.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/22_artifacts-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

台本・字幕原稿の訂正後に古い証拠が流用される。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 固有名詞の根拠を結ぶ。
2. 原稿revisionを識別する。
3. 修正部分のみ再照合する。

## Contract・データの受け渡し

拡張案：文書Receiptに原稿digestと証拠範囲を関連付ける。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：原稿→照合→人間レビュー。NGは該当文へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

一語変更で古い承認が無効になり、根拠なしの記述を未確認として表示。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
