# 21　media-analysis-skill

メディア計測 / 発話区間。依存・接点は ローカル解析器。今回の優先度と概算は **P1/S**。

## 現在地と根拠

対象commit `a11b408f9a9232aa891fe3cd3095955c2c2af2b8`。Contract pin は `src/video_agent/tools/media_analysis/contract_0.2.0.json`。[対象commit](https://github.com/kajisho5/media-analysis-skill/commit/a11b408f9a9232aa891fe3cd3095955c2c2af2b8) · [利用仕様](https://github.com/kajisho5/media-analysis-skill/blob/a11b408f9a9232aa891fe3cd3095955c2c2af2b8/SKILL.md) · [Contract定義](https://github.com/kajisho5/media-analysis-skill/blob/a11b408f9a9232aa891fe3cd3095955c2c2af2b8/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/media_analysis/contract_0.2.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/media_analysis/adapter.py) · [既存試験](https://github.com/kajisho5/media-analysis-skill/blob/a11b408f9a9232aa891fe3cd3095955c2c2af2b8/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/21_media-analysis-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

素材の観測値とQC判断の混同がある。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 解析した音声streamを記録する。
2. 発話区間を元TCへ結ぶ。
3. 再解析を入力指紋で判定する。

## Contract・データの受け渡し

拡張案：観測の単位・範囲・測定器版を明記する。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：メディア→観測→Agent/QC。測定失敗は再取得へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

同じ素材の別streamで値を区別し、未測定を無音扱いしない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
