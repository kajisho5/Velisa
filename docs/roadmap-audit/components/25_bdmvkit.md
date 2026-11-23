# 25　bdmvkit

Blu-ray作成。依存・接点は BD素材。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `119ac5a56f6b750654f3e8449f7bcf9265f5e8ec`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/bdmvkit/commit/119ac5a56f6b750654f3e8449f7bcf9265f5e8ec) · [利用仕様](https://github.com/kajisho5/bdmvkit/blob/119ac5a56f6b750654f3e8449f7bcf9265f5e8ec/README.md) · [Contract定義](https://github.com/kajisho5/bdmvkit/blob/119ac5a56f6b750654f3e8449f7bcf9265f5e8ec/contract/contract.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/25_bdmvkit/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

メニューと本編のチャプター到達を独立検査したい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. チャプター遷移表を出す。
2. 字幕付きタイトルを構造検査する。
3. 破損した参照を特定する。

## Contract・データの受け渡し

拡張案：BDMV検査記録にplaylistとentry番号を関連付ける。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：マスター→BDMV→oncemore。NGはメニュー構造へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

2タイトル・3章で全参照が有効、欠落playlistを検出。再生機試験は別記録。試験担当は入力・環境・期待値・実測値をひと組で残す。独立用途で受け入れ、Agent自動起動は合格条件から外す。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
