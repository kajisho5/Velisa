# 07　subtitle-skill

字幕生成・検証 / 字幕焼き込み / 字幕翻訳 / ロケール別字幕整形 / 動く字幕(字幕キュー由来)。依存・接点は 描画・mux時にFF。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `61f575dd04ddce182a27661b93660ddd83751b7d`。Contract pin は `src/video_agent/tools/subtitle/contract_1.1.0.json`。[対象commit](https://github.com/kajisho5/subtitle-skill/commit/61f575dd04ddce182a27661b93660ddd83751b7d) · [利用仕様](https://github.com/kajisho5/subtitle-skill/blob/61f575dd04ddce182a27661b93660ddd83751b7d/SKILL.md) · [Contract定義](https://github.com/kajisho5/subtitle-skill/blob/61f575dd04ddce182a27661b93660ddd83751b7d/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/subtitle/contract_1.1.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/subtitle/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/07_subtitle-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

採用区間の差し替えで日本語字幕の語尾や固有名詞がずれる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 元cue IDを維持する。
2. cut時刻写像で表示区間を引き直す。
3. 固有名詞の人手訂正を次回描画に引き継ぐ。

## Contract・データの受け渡し

拡張案：cueにsource_spanとreviewed_textの任意参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：Transcript・時刻写像→字幕→QC。誤字はcue単位で返す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

修正した一語だけが新字幕に入り、消した区間のcueが残らず、境界誤差1フレーム以内。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
