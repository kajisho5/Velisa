# 02　ingest-skill

素材取り込み(検証付きコピー) / 二重バックアップ / 素材台帳 / URL素材取得。依存・接点は 単体・外部取込は任意。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `9f5247e46c02b3b8707aa6bcff10b63a75899013`。Contract pin は `src/video_agent/tools/ingest/contract_1.1.0.json`。[対象commit](https://github.com/kajisho5/ingest-skill/commit/9f5247e46c02b3b8707aa6bcff10b63a75899013) · [利用仕様](https://github.com/kajisho5/ingest-skill/blob/9f5247e46c02b3b8707aa6bcff10b63a75899013/SKILL.md) · [Contract定義](https://github.com/kajisho5/ingest-skill/blob/9f5247e46c02b3b8707aa6bcff10b63a75899013/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/ingest/contract_1.1.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/ingest/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/02_ingest-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

カードを二重コピーした後の素材IDと短尺候補の出所を追いたい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 元カード・コピーの照合結果を束ねる。
2. 中断した二重コピーを片側だけ再開する。
3. 素材IDをASRと編集の入力へ渡す。

## Contract・データの受け渡し

拡張案：inventoryの任意参照にcopy先別の検証記録。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：カード→取込台帳→ASR。片方の不一致はそのコピーに戻し原本を保持。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

途中停止と同名別素材を含む2カードで両コピーの内容を照合し、未確認コピーを素材選択から外す。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
