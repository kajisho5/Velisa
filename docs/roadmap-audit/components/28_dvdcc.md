# 28　dvdcc

DVD字幕(CEA-608)。依存・接点は CEA-608・MPEG-2。今回の優先度と概算は **P2/S**。

## 現在地と根拠

対象commit `30dfda8294e61ba8d131562c2ea162b4ac7514aa`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/dvdcc/commit/30dfda8294e61ba8d131562c2ea162b4ac7514aa) · [利用仕様](https://github.com/kajisho5/dvdcc/blob/30dfda8294e61ba8d131562c2ea162b4ac7514aa/README.md) · [Contract定義](https://github.com/kajisho5/dvdcc/blob/30dfda8294e61ba8d131562c2ea162b4ac7514aa/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/28_dvdcc/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

字幕挿入で映像本体や字幕時刻を変えていないことを示したい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 既知の608テキストを挿入する。
2. 抽出して時刻を比較する。
3. 映像フレームの保存を確認する。

## Contract・データの受け渡し

拡張案：字幕検査行に開始フレームと抽出テキスト。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：字幕・MPEG-2→CC入り素材→DVD。NGは該当字幕へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

2件の字幕を読戻し、デコード映像のフレーム数・内容と表示順を確認。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
