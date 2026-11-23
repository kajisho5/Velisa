# 12　audio-production-skill

音量・ラウドネス / ミックス / ダイナミクス / 従来型ノイズ低減 / 無音・フィラー除去。依存・接点は FF。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `2efe60b2e2576eec13d53f1d840f85392dff7433`。Contract pin は `src/video_agent/tools/audio_production/contract_1.4.3.json`。[対象commit](https://github.com/kajisho5/audio-production-skill/commit/2efe60b2e2576eec13d53f1d840f85392dff7433) · [利用仕様](https://github.com/kajisho5/audio-production-skill/blob/2efe60b2e2576eec13d53f1d840f85392dff7433/SKILL.md) · [Contract定義](https://github.com/kajisho5/audio-production-skill/blob/2efe60b2e2576eec13d53f1d840f85392dff7433/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/audio_production/contract_1.4.3.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/audio_production/adapter.py) · [既存試験](https://github.com/kajisho5/audio-production-skill/blob/2efe60b2e2576eec13d53f1d840f85392dff7433/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/12_audio-production-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

片ch救済時のレベル変化と放送納品判定が別工程に散る。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 良好chを明示して左右を比較する。
2. 修復前後のピークを併記する。
3. 書出後に日本向け明示目標でcheckする。

## Contract・データの受け渡し

拡張案：修復receiptにch番号・単位・目標値と測定結果を関連付ける。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：音声素材→修復→QC。修復と正規化のどちらで失敗したか戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

4秒PCMのL/R全サンプル一致、約−3.01 dBを確認し、音量のみ・TPのみの違反を判別。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
