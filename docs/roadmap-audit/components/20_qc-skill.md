# 20　qc-skill

規格判定(QC)。依存・接点は メディア測定器。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `df73a07105fba979192273cfb863dc72cbd634b6`。Contract pin は `src/video_agent/tools/qc/contract_1.4.5.json`。[対象commit](https://github.com/kajisho5/qc-skill/commit/df73a07105fba979192273cfb863dc72cbd634b6) · [利用仕様](https://github.com/kajisho5/qc-skill/blob/df73a07105fba979192273cfb863dc72cbd634b6/SKILL.md) · [Contract定義](https://github.com/kajisho5/qc-skill/blob/df73a07105fba979192273cfb863dc72cbd634b6/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/qc/contract_1.4.5.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/qc/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/20_qc-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

機械PASSと意味・納品承認を分けて示す必要がある。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 音声目標を明示する。
2. 検査不能をUNKNOWNにする。
3. 失敗行から再編集する区間を特定する。

## Contract・データの受け渡し

拡張案：判定行に基準の出典・対象区間・測定証拠を参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：計画・出力→QC→承認。失敗を担当工程へ返す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

適合・音量のみ超過・TPのみ超過・短尺測定不能の4例で判定を識別。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
