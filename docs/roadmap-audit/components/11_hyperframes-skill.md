# 11　hyperframes-skill

HTMLシーンの動画化(HyperFrames) / テロップ・スティンガー・ループ素材 / キネティックタイポ・幾何学モーション。依存・接点は Node・Chromium・任意FF。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `64b787c8786237b6bd579116020a3ff227a8132a`。Contract pin は `src/video_agent/skills/pins/hyperframes-skill_0.11.1.json`。[対象commit](https://github.com/kajisho5/hyperframes-skill/commit/64b787c8786237b6bd579116020a3ff227a8132a) · [利用仕様](https://github.com/kajisho5/hyperframes-skill/blob/64b787c8786237b6bd579116020a3ff227a8132a/SKILL.md) · [Contract定義](https://github.com/kajisho5/hyperframes-skill/blob/64b787c8786237b6bd579116020a3ff227a8132a/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/skills/pins/hyperframes-skill_0.11.1.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/hyperframes/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/11_hyperframes-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

生成と配置をまたぐとstingerの切替点やalpha指定がずれる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. cut pointをフレームで検査する。
2. title・stingerを黒白背景で確認する。
3. レイヤーのみ差し替える。

## Contract・データの受け渡し

拡張案：既存title・stinger・timebase sidecarを再利用。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：HTML→素材→motion-graphics。NGはHTMLシーンのみ戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

30000/1001のstingerで指定フレームに切替があり、差し替え前後の番組尺が一致。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
