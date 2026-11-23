# 26　vtskit

DVD-Video作成。依存・接点は DVD素材。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `d8babccb954e402acabc510fd491ff2e46d2f81e`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/vtskit/commit/d8babccb954e402acabc510fd491ff2e46d2f81e) · [利用仕様](https://github.com/kajisho5/vtskit/blob/d8babccb954e402acabc510fd491ff2e46d2f81e/README.md) · [Contract定義](https://github.com/kajisho5/vtskit/blob/d8babccb954e402acabc510fd491ff2e46d2f81e/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/26_vtskit/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

DVDメニューで選択したタイトルが意図通り開くかを追う。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. ボタンとPGCの対応を出す。
2. アスペクトを照合する。
3. 戻り先を検証する。

## Contract・データの受け渡し

拡張案：ナビ検査にボタン・PGC・遷移先を保持。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：マスター→VIDEO_TS→oncemore。NGは該当PGCへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

2ボタンのテストディスクで両方の遷移と戻り先を検証し、壊した参照は失敗。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
