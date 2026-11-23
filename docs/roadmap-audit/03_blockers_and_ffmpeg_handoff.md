# 入力alphaの受け入れ手順と実行基盤への引き渡し

## 対象と事前記録

唯一の下位P0はFF #453。上位の project.source.alpha_mode が premultiplied、alphaを保持し、操作が LUT_APPLY または PRIMARY_CORRECTION の時に UNSUPPORTED_FORMAT / alpha_premultiplied で止まる。stream-copyのRETAG、straight入力を対照にする。[上位Contract](https://github.com/kajisho5/color-grading-skill/blob/main/src/color_grading/contract.py) · [既存fixture](https://github.com/kajisho5/color-grading-skill/blob/main/tests/test_alpha_mode.py) · [#453](https://github.com/kajisho5/ffmpeg-skill/issues/453)

`UNVERIFIED: acceptance/453/real/input-manifest.json`。実素材パスは未指定。権利確認済みの短尺ロゴとタイトル、ProRes 4444（pix_fmt・色域・行列・レンジを明示）と8 bit qtrle、透明・薄い縁・半透明・不透明を含むものを用意する。同じ制作元のstraight版、または量子化前の参照画像とタイムラインを保存。実素材は所有者の保管先で管理し、公開repoには素材ID・利用条件・指紋・匿名化した測定結果を記録する。

## ゲート①　PR #715のエンジン

1. macOS、PR head SHA、比較用main SHA、FFmpeg/ffprobeの版、codec、実際の作業bit深度を記録する。合成素材は一色の帯（不透明、128、64、0）と滑らかな縁を作り、実素材とは別系列で扱う。
2. 入力をpremultipliedと明示し、keep-alphaで①gamma 1.6の一次補正、②黒点を持ち上げる固定LUT（ファイルdigest保存）を両codecに適用。同じgradeをstraight参照へ適用する。straight既定のコマンドと出力も以前の版と比較する。
3. 同一の色変換でRGBAをデコードし、alpha面とRGBを別々に測る。alpha 0は除算せず透明・RGBの期待を確認。qtrleのalphaはbit一致、ProResは8 bit相当1コード以内。不透明帯、半透明帯内部、縁を別々に記録する。
4. **比較前に許容差の表を確定する。** 正規化alphaを a、作業bit数を b とすると、premultiplied RGBの丸め半LSBがstraight色へ伝わる単項は8 bitコード換算で 255 / (2 × (2^b−1) × a)。b=8ならalpha 128で約1、64で約2コード。これは単一丸め項のみ。量子化したalphaの誤差、入力と出力の丸め、LUT局所勾配、YUV↔RGB・codec往復の誤差を別項にする。無補正のencode/decode対照と高精度参照を使い、codec・実効bit深度・alpha帯・操作ごとの上限、単位、導出根拠を測定前に票へ記入する。高bitの容器に8 bit作業段があればその段は8 bitとして扱う。根拠が確定しないセルは保留。
5. PRの報告ではalpha 128のqtrle＋LUTが最大1.71、alpha 64のqtrle＋gammaが2.94、同ProRes＋LUTが1.7コード。PR側のテストしきい値とこの受入票を独立して残す。観測値を見て事後に合格線を動かさない。[PR測定表](https://github.com/kajisho5/ffmpeg-skill/pull/715)
6. 半透明縁を黒背景・白背景にそれぞれ合成し、同一TC・倍率の参照／出力／差分画像を保存。色ずれ、黒縁、白縁、ちらつきを実時間と拡大で確認。共有のpremultiplied書出しを使う別経路も同じ素材で比較する。どれかがNGなら該当帯のデータ、コマンド、probeを添えて下位へ返す。

## ゲート②　上位からの完走

旧ビルドとPRビルドを明示して同じrequestを使う。上位は下位能力を読み、旧ビルドでは従来の理由付き拒否を維持。対応時だけ入力alphaの格納方式を渡し、結果とalpha stepを読み戻す。LUTと一次補正をAgentからそれぞれ実行し、原本・Plan・出力・QCの対応をReceiptに残す。非alpha・straight・RETAGにも回帰がないことを確認。下位ゲートと同じ数値票を上位出力に適用する。**数値合格かつ黒白両背景の実素材をオーナーが目視承認**した時点で完了。保留・NGには理由、codec、TC、修正版を記録する。

## 他の境界

|案件|引き渡しと残条件|
|---|---|
|FF #721|既存の良好ch指定・ステレオ化、48 kHz PCMで左右一致と約−3.01 dBを確認。振幅保持の新モードは別判断。[#721](https://github.com/kajisho5/ffmpeg-skill/issues/721)|
|FF #722|broadcast-jp生成物に check --platform broadcast --lufs -24 --tp -1。音声2行を独立評価し、映像を含む放送全体の合格とは区別する。[#722](https://github.com/kajisho5/ffmpeg-skill/issues/722)|
|ブランド納品|kit@1をそのまま渡す問題はRemotion側で既知キーへ投影。FFのキーを追加しない。[#32](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/32)|
|resize後のfit|Agentの現行pinで再現し、納品寸法が指定されていれば上位compilerで明示するか期待値を訂正する。旧版の結果だけでFFの不具合にしない。[Agent #60](https://github.com/kajisho5/video-production-agent/issues/60)|

追加のFF凍結例外は提案しない。上位で吸収できない候補が将来現れた場合は、consumer、最小入力、期待値、実測、使用版、試した回避策を揃えて初めてP0を判定する。
