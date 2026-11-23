# 23　publish-skill

配信先アップロード / アップロード制限。依存・接点は 任意FF・公開先API。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `ec82a9634e638279d0eba7e4fc370c5650b9b944`。Contract pin は `src/video_agent/tools/publish/contract_1.0.0.json`。[対象commit](https://github.com/kajisho5/publish-skill/commit/ec82a9634e638279d0eba7e4fc370c5650b9b944) · [利用仕様](https://github.com/kajisho5/publish-skill/blob/ec82a9634e638279d0eba7e4fc370c5650b9b944/SKILL.md) · [Contract定義](https://github.com/kajisho5/publish-skill/blob/ec82a9634e638279d0eba7e4fc370c5650b9b944/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/publish/contract_1.0.0.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/publish/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/23_publish-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

再開時に二重投稿や古い承認による公開が起こりうる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 公開予定をモックで提示する。
2. 承認を出力digestに結ぶ。
3. 再試行時に既存投稿を照会する。

## Contract・データの受け渡し

拡張案：納品記録に宛先・承認版・冪等キー候補。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：QC済み→承認→投稿。失敗はリモート状態確認へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

モックで通信中断後の再試行が1投稿に収まり、実投稿は別の実アカウント承認を要求。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
