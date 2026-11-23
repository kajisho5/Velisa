# 09　blender-skill

3D素材・3Dレンダリング。依存・接点は Blender。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `1c1e47cc97b046d06132568394c412ba690ff990`。Contract pin は `src/video_agent/skills/pins/blender-skill_0.31.1.json`。[対象commit](https://github.com/kajisho5/blender-skill/commit/1c1e47cc97b046d06132568394c412ba690ff990) · [利用仕様](https://github.com/kajisho5/blender-skill/blob/1c1e47cc97b046d06132568394c412ba690ff990/SKILL.md) · [Contract定義](https://github.com/kajisho5/blender-skill/blob/1c1e47cc97b046d06132568394c412ba690ff990/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/skills/pins/blender-skill_0.31.1.json)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|引渡し|未確認|未確認|

`UNVERIFIED: acceptance/09_blender-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

3Dレンダーのhandoffで合成条件が失われやすい。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. モデルとカメラ指定を引渡票にする。
2. 透過ターンテーブルを出力する。
3. 受領側で尺・alphaを照合する。

## Contract・データの受け渡し

拡張案：handoffにfps分数・alpha格納方式・素材参照。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：3Dモデル→Blender→合成。受領NGはカメラまたは出力設定に戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

短い回転モデルでフレーム数と背景透過を確認し、白黒背景の参照画像を添える。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
