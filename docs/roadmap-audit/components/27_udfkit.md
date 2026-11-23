# 27　udfkit

ディスクイメージ(UDF)。依存・接点は ディスク構造。今回の優先度と概算は **P2/S**。

## 現在地と根拠

対象commit `577daaf93813543cd0369d09006eb8c07cf120d5`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/udfkit/commit/577daaf93813543cd0369d09006eb8c07cf120d5) · [利用仕様](https://github.com/kajisho5/udfkit/blob/577daaf93813543cd0369d09006eb8c07cf120d5/README.md) · [Contract定義](https://github.com/kajisho5/udfkit/blob/577daaf93813543cd0369d09006eb8c07cf120d5/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/27_udfkit/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

イメージ化で欠落したファイルを作成成功だけでは検出できない。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 元ディレクトリを列挙する。
2. 作成後に読戻す。
3. 欠落パスを報告する。

## Contract・データの受け渡し

拡張案：マニフェストに相対パス・サイズ・検証結果。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：DVD/BD構造→UDF→検査。差異はイメージ再構築へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

日本語名と空ファイルを含むfixtureで一覧・サイズ一致、切断イメージを拒否。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
