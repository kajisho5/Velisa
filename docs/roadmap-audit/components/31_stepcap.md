# 31　stepcap

画面収録→手順書。依存・接点は 任意FF・detection。今回の優先度と概算は **P2/S**。

## 現在地と根拠

対象commit `fb05c8988d7e11242b4b42fb7f2f0a259983333a`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/stepcap/commit/fb05c8988d7e11242b4b42fb7f2f0a259983333a) · [利用仕様](https://github.com/kajisho5/stepcap/blob/fb05c8988d7e11242b4b42fb7f2f0a259983333a/README.md) · [Contract定義](https://github.com/kajisho5/stepcap/blob/fb05c8988d7e11242b4b42fb7f2f0a259983333a/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/31_stepcap/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

画面手順書に資格情報や個人情報が残りうる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. OCR候補をレビューに出す。
2. 承認したマスクを画像に適用する。
3. 公開物の全コマを再確認する。

## Contract・データの受け渡し

拡張案：手順ID→マスク版・公開用画像を参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：画面収録→手順書→人間。見落としは該当コマへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

ダミー秘密文字を含む操作で公開版の画像と本文から消え、元の手順順序を保持。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
