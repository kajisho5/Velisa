# 15　sound-design-skill

BGM生成 / 効果音。依存・接点は FF・音源エンジン。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `eaa36ea98d654c81168dcce3b4e40edf7b74525f`。Contract pin は `src/video_agent/tools/sound_design/contract_0.3.6.json`。[対象commit](https://github.com/kajisho5/sound-design-skill/commit/eaa36ea98d654c81168dcce3b4e40edf7b74525f) · [利用仕様](https://github.com/kajisho5/sound-design-skill/blob/eaa36ea98d654c81168dcce3b4e40edf7b74525f/SKILL.md) · [Contract定義](https://github.com/kajisho5/sound-design-skill/blob/eaa36ea98d654c81168dcce3b4e40edf7b74525f/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/sound_design/contract_0.3.6.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/sound_design/adapter.py) · [既存試験](https://github.com/kajisho5/sound-design-skill/blob/eaa36ea98d654c81168dcce3b4e40edf7b74525f/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/15_sound-design-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

効果音の権利・位置・音量が編集修正で乖離する。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. cue sheetを編集区間に結ぶ。
2. 使用許諾をチェックする。
3. BGM版の差し替えを局所化する。

## Contract・データの受け渡し

拡張案：既存licence-recordとcue時刻を素材IDで連結。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：音源→効果音配置→音響。権利不明は公開を保留。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

一つのcueを移すと指定箇所だけ変わり、許諾不明素材に公開承認が付かない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
