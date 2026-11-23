# 03　ffmpeg-skill

FFmpeg実行 / 書き出し前の規格点検 / マルチカム同期 / Bロール合成 / 手ぶれ・傾き補正 / プレビュー・縮小一覧 / 納品レポート / 配信プラットフォーム仕様 / カットリスト書き出し。依存・接点は ローカルFFmpeg/ffprobe。今回の優先度と概算は **P0/M**。

## 現在地と根拠

対象commit `c559cb5fcbfbb37b8a48165b0c49e6bdfa674883`。Contract pin は `実行環境から検出`。[対象commit](https://github.com/kajisho5/ffmpeg-skill/commit/c559cb5fcbfbb37b8a48165b0c49e6bdfa674883) · [利用仕様](https://github.com/kajisho5/ffmpeg-skill/blob/c559cb5fcbfbb37b8a48165b0c49e6bdfa674883/SKILL.md) · [Contract定義](https://github.com/kajisho5/ffmpeg-skill/blob/c559cb5fcbfbb37b8a48165b0c49e6bdfa674883/scripts/_contract.py) · [adapter](https://github.com/kajisho5/video-production-agent/blob/5706360af1c4eb08b4aa7c12536c2b6cccc0f16c/src/video_agent/tools/ffmpeg_skill/adapter.py)

|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|
|---|---|---|---|---|---|
|active|実装定義|動的・実行未確認|あり|未確認|未確認|

`UNVERIFIED: acceptance/03_ffmpeg-skill/macos-real/receipt.json`（想定する証拠保管先）。合成試験の実装やpinのバイト一致だけでは、現行macOSでの実行合格までは示せない。

## 課題と開発項目

半透明マスターの色補正で上位が処理を拒否する。以下は次期の追加・検証案で、既存の経路を優先して利用する。

1. 既存#453の両codecを比較する。
2. #721のPCMレベルを記録する。
3. #722の独立checkをレシピから実行する。

## Contract・データの受け渡し

拡張案：既存結果とPR #715の宣言のみを消費。新規の公開面は追加しない。既存の必須フィールド・終了コードを維持し、形式追加が必要な場合は旧入力fixtureと新出力の読戻しを照合する。

上流・下流と差し戻し：確定パラメータ→FF→QC。数値不一致はconsumerへ測定値を返す。QCの失敗箇所・人が却下した理由は入力版とともに保存し、再提出時に修正箇所を示す。

## 受け入れ

#453の下位ゲートと#721・#722を別判定し、不適合を上位が成功として扱わない。試験担当は入力・環境・期待値・実測値をひと組で残す。実案件の承認履歴を合成試験の記録と区別する。

[縦断試験](../01_cross_cutting_usecases.md) · [成熟度表](../README.md)
