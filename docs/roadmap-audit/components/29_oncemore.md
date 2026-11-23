# 29　oncemore

ディスク作成アプリ(Mac)。依存・接点は 25〜28の各kit。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `dd19c4c34af7044c7e2fe2af6235b98a2bfbe419`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/oncemore/commit/dd19c4c34af7044c7e2fe2af6235b98a2bfbe419) · [利用仕様](https://github.com/kajisho5/oncemore/blob/dd19c4c34af7044c7e2fe2af6235b98a2bfbe419/SKILL.md) · [Contract定義](https://github.com/kajisho5/oncemore/blob/dd19c4c34af7044c7e2fe2af6235b98a2bfbe419/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|引渡し|未確認|未確認|

`UNVERIFIED: acceptance/29_oncemore/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

ISO作成の承認と物理媒体への書込みの承認を区別したい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. メニュー付きISOをプレビューする。
2. 各kitの検査結果を集約する。
3. 実媒体と対象装置を確認する。

## Contract・データの受け渡し

拡張案：ディスク制作票にイメージdigest・媒体・承認を記録。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：4キット→ISO→人間。NGは構築へ、書込みは明示承認後。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

macOSでISOまで完走し、対象媒体変更後に旧承認で書き込めない。物理再生は別ゲート。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
