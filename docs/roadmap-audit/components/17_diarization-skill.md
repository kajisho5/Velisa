# 17　diarization-skill

話者識別 / 話者IDの付与規則。依存・接点は 話者モデル・Transcript。今回の優先度と概算は **P1/M**。

## 現在地と根拠

対象commit `e49556e997e61c3fb7a882439f5fba796030a880`。Contract pin は `src/video_agent/tools/diarization/contract_1.0.1.json`。[対象commit](https://github.com/kajisho5/diarization-skill/commit/e49556e997e61c3fb7a882439f5fba796030a880) · [利用仕様](https://github.com/kajisho5/diarization-skill/blob/e49556e997e61c3fb7a882439f5fba796030a880/SKILL.md) · [Contract定義](https://github.com/kajisho5/diarization-skill/blob/e49556e997e61c3fb7a882439f5fba796030a880/contract/contract.json) · [Agent pin](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/diarization/contract_1.0.1.json) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/diarization/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|あり|一致・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/17_diarization-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

短尺化後に話者IDの割当てが変わると確認がやり直しになる。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 原音上の話者割当を保持する。
2. 重複発話を要確認にする。
3. 人手の再割当を保存する。

## Contract・データの受け渡し

拡張案：turn ID・元時刻・訂正者を参照する任意記録。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：原音・Transcript→話者付き語→字幕。NGは該当turnへ。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

交差発話を含む録音で未確定箇所を示し、一話者の訂正で他の割当を変えない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
