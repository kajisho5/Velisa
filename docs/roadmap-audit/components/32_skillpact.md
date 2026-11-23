# 32　skillpact

スキル契約・署名 / スキル適合性検査。依存・接点は 各スキル宣言・試験ハーネス。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `962dae6e9e2cd9a6c705fe18af94cd8689ac1a87`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/skillpact/commit/962dae6e9e2cd9a6c705fe18af94cd8689ac1a87) · [利用仕様](https://github.com/kajisho5/skillpact/blob/962dae6e9e2cd9a6c705fe18af94cd8689ac1a87/SKILL.md)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|自己宣言未確認|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/32_skillpact/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

宣言済みの副作用と実行時観測を混同しやすい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 書込先と通信宣言を照合する。
2. 観測手段の有無を記録する。
3. 差分を週次報告へ渡す。

## Contract・データの受け渡し

拡張案：適合記録に宣言版・観測環境・未検査項目。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：各repo宣言→適合試験→Control Room。不一致は所有repoへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

許可した書込みと宣言外書込みを区別し、観測器なしは未検査として表示。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
