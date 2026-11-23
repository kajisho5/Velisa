# 01　video-production-agent

制作計画 / スキルの呼び分け / 制作記録(ProductionReceipt) / 言い直し・重複の候補の提示と承認。依存・接点は 各専門adapter。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `5706360af1c4eb08b4aa7c12536c2b6cccc0f16c`。Contract pin は `独立用途／Agent自身のため対象外`。[対象commit](https://github.com/kajisho5/video-production-agent/commit/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c) · [利用仕様](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/SKILL.md) · [Contract定義](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/skills/contract.py) · [既存試験](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/tests/integration_shards.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|実装定義|対象外|対象外|未確認|未確認|

`UNVERIFIED: acceptance/01_video-production-agent/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

採択区間を一つ直した後の再開点が部門をまたぐ。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 発話候補を元TC付きでプレビューする。
2. 修正箇所から依存ステージだけ無効化する。
3. 承認済みrecipeとReceiptを再開時に照合する。

## Contract・データの受け渡し

拡張案：recipeの任意欄に親revision・変更区間・承認対象のdigest。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：取込台帳→Plan→編集・QC。NG区間だけ新revisionへ戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

60秒の候補の2番目だけ差し替え、未変更の文字起こしを再利用し、旧版の承認で新版を公開できない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
