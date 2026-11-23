# 04　video-editing-skill

カット・連結 / 尺・画角合わせ / トランジション / 静止画オーバーレイ / 言い直し・重複の候補計算。依存・接点は FF。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `2acdd7a190cc5414b5d68fdaa4828d6033524c13`。Contract pin は `src/video_agent/tools/video_editing/contract_0.9.0.json`。[対象commit](https://github.com/kajisho5/video-editing-skill/commit/2acdd7a190cc5414b5d68fdaa4828d6033524c13) · [利用仕様](https://github.com/kajisho5/video-editing-skill/blob/2acdd7a190cc5414b5d68fdaa4828d6033524c13/SKILL.md) · [Contract定義](https://github.com/kajisho5/video-editing-skill/blob/2acdd7a190cc5414b5d68fdaa4828d6033524c13/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/video_editing/contract_0.9.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/video_editing/adapter.py) · [既存試験](https://github.com/kajisho5/video-editing-skill/blob/2acdd7a190cc5414b5d68fdaa4828d6033524c13/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/04_video-editing-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

resize後のfitで明示幅と素材相対幅を混同しうる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. Agent #60を現行pinで再現する。
2. 納品画素数がある依頼に明示幅を渡す。
3. カット変更後に時刻写像を再計算する。

## Contract・データの受け渡し

拡張案：編集recipeに要求寸法と実測寸法を別項目で参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：Plan・素材→編集→字幕・QC。寸法NGはfit指定へ戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

640幅の後に正方形化する2ケースで要求と実測を照合し、発話始端の対応が1フレーム以内。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
