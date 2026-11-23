# 19　slide-sync-skill

スライド取込 / スライド切替検出。依存・接点は FF・スライド資料。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `073d887728d6885a668c679fee89e19e16c1522f`。Contract pin は `src/video_agent/tools/slide_sync/contract_0.1.3.json`。[対象commit](https://github.com/kajisho5/slide-sync-skill/commit/073d887728d6885a668c679fee89e19e16c1522f) · [利用仕様](https://github.com/kajisho5/slide-sync-skill/blob/073d887728d6885a668c679fee89e19e16c1522f/SKILL.md) · [Contract定義](https://github.com/kajisho5/slide-sync-skill/blob/073d887728d6885a668c679fee89e19e16c1522f/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/slide_sync/contract_0.1.3.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/slide_sync/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/19_slide-sync-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

引用した発言と表示スライドが差し替え後にずれる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. スライド切替時刻と版を保存する。
2. PDFページと映像を照合する。
3. 差し替え区間を再マップする。

## Contract・データの受け渡し

拡張案：ページID・元区間・出力区間の対応表。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：資料・映像→対応表→編集。誤対応は該当ページへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

同じページに戻る講演で2回の表示を区別し、短尺編集後も正しいページを表示。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
