# 14　dubbing-skill

AIナレーション(TTS) / 吹替・声の置換 / 音声解説。依存・接点は FF・TTS。今回の優先度と概算は **P2/M**。

## 現在地と根拠

対象commit `2d5804c2018e4ecc6dc4226d97e0fd1802743eb8`。Contract pin は `src/video_agent/tools/dubbing/contract_1.1.3.json`。[対象commit](https://github.com/kajisho5/dubbing-skill/commit/2d5804c2018e4ecc6dc4226d97e0fd1802743eb8) · [利用仕様](https://github.com/kajisho5/dubbing-skill/blob/2d5804c2018e4ecc6dc4226d97e0fd1802743eb8/SKILL.md) · [Contract定義](https://github.com/kajisho5/dubbing-skill/blob/2d5804c2018e4ecc6dc4226d97e0fd1802743eb8/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/dubbing/contract_1.1.3.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/dubbing/adapter.py) · [既存試験](https://github.com/kajisho5/dubbing-skill/blob/2d5804c2018e4ecc6dc4226d97e0fd1802743eb8/tests/test_integration.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/14_dubbing-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

翻訳台詞の読み方と映像内の尺に両立条件がある。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. VOICEVOX読みに固有名詞辞書を渡す。
2. 台詞別に予定尺と実尺を比較する。
3. 超過した行だけ再合成する。

## Contract・データの受け渡し

拡張案：台詞IDに発音・音声版・許容尺を関連付ける。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：翻訳cue→合成→ミックス。発音NGは台詞単位で差し戻す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

一行訂正後に他行の位置・音声が維持され、未承認の有料エンジンを呼ばない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
