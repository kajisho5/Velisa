# 33　system-intelligence

エコシステム監査。依存・接点は GitHub・台帳・Contract。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `32e087fb3aa499d054e71338e27bcf967eed91cc`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/system-intelligence/commit/32e087fb3aa499d054e71338e27bcf967eed91cc) · [利用仕様](https://github.com/kajisho5/system-intelligence/blob/32e087fb3aa499d054e71338e27bcf967eed91cc/README.md)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|自己宣言未確認|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/33_system-intelligence/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

古い監査資料が現在の接続状態として流通する。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. commit差を検出する。
2. adapterとpinを別列化する。
3. 古い証拠へ期限表示を付ける。

## Contract・データの受け渡し

拡張案：観測記録にrepo・sha・操作・取得日・根拠URL。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：GitHub/台帳→診断→Control Room。誤判定は該当ルールへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

Remotion・HyperFrames・NLE diffで現行ソースを示し、証拠なしを実機合格にしない。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
