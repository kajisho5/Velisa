# 10　remotion-ffmpeg-skill

計測連動モーショングラフィックス(Remotion) / 語の時刻に合わせた字幕演出 / オーディオビジュアライザー。依存・接点は FF・Remotion。今回の優先度と概算は **P1/S**。

## 現在地と根拠

対象commit `f14b27c334e86afde606c5c558eb91acdeff801f`。Contract pin は `src/video_agent/tools/remotion/contract_0.14.4.json`。[対象commit](https://github.com/kajisho5/remotion-ffmpeg-skill/commit/f14b27c334e86afde606c5c558eb91acdeff801f) · [利用仕様](https://github.com/kajisho5/remotion-ffmpeg-skill/blob/f14b27c334e86afde606c5c558eb91acdeff801f/SKILL.md) · [Contract定義](https://github.com/kajisho5/remotion-ffmpeg-skill/blob/f14b27c334e86afde606c5c558eb91acdeff801f/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/remotion/contract_0.14.4.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/remotion/adapter.py) · [既存試験](https://github.com/kajisho5/remotion-ffmpeg-skill/blob/f14b27c334e86afde606c5c558eb91acdeff801f/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/10_remotion-ffmpeg-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

kit@1をそのまま納品へ渡すとFFで未知キー拒否になる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. #32のconsumer投影を実装する。
2. coloursを仕様通り正規化する。
3. stillとdeliveryの共通色を比較する。

## Contract・データの受け渡し

拡張案：既存kit@1からFF既知キーへの投影。原本を保持。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：kit→render/still→deliver。未対応ブランド要素は投影記録へ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

同一kitでstillとdeliveryが成功し、原本digest不変、不要キーがFF引数に渡らない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
