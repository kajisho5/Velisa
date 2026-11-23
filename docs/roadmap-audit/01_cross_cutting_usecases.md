# 縦断ユースケースと受け入れ順序

一次環境はmacOS、ローカルFFmpeg／ffprobe、利用可能なVideoToolbox、ローカルASRとVOICEVOX。OS・チップ・エンジン版・モデル・素材指紋・Plan revisionを記録する。モデルがない場合は未実施とする。ローカルプレビューは自動で作成できる。意味を変える削除、有料生成、公開投稿、実ディスク書込みには、その操作・素材版・対象を示した明示承認が必要。承認後に内容を変えたら該当範囲を再提示する。

## 1　日本語講演・対談から、承認付きの短尺納品へ（P1・L）

**試験入力**　利用許可のある日本語の対談、話者2名、言い直し・間・人名と数字、片chが正常な箇所、講演スライド、元TCが照合できる参照。依頼例は「この発言を残して60秒へ」。期待する固有名詞・採択必須区間を先に編集者が記録する。

|工程・所有者|受け渡す証拠|受け入れ条件|
|---|---|---|
|ingest→認識|素材ID、照合済みコピー、語・話者・スライドの元時刻|同名素材と重複発言を時刻で区別でき、引用を元音声で再生できる|
|Agent→人間|採択候補・捨てる区間・理由・合計尺・字幕付きプレビュー|決定前にローカルで比較可能。発言を削る前に対象区間への承認を記録|
|人間→編集|「2番目の引用だけ変更」という一件の修正、親recipeと時刻写像|ASR・取込を再利用。変更区間に依存する字幕・合成・音声・QCだけ再計算し、全編依存の音量測定は再度実行|
|字幕→ミックス|校正済み日本語cue、良好ch番号、音声目標|字幕の人名・数値を人が確認。PCM左右一致と選択ch比約−3.01 dBを確認。必要な場合だけ承認済み納品目標で正規化|
|export→QC→納品|probe結果、尺、フレーム数、音声stream、音量、TP、無音・cut点、視聴票|合意した尺を1出力フレーム以内で満たす。想定外の無音と子音切れを区別し、指摘時刻から該当工程に戻れる。プレビュー合格後に公開承認を別途取得|

**制作ポリシーの採用案。** 以下はOpen PRの提案を踏まえたStep 2の基準であり、mainでの実装状況は各アダプターの試験で追跡する。

- 異なる画角ではショットの先頭・中央・末尾を見て固定cropを決め、動きの重心は調査するフレーム選択に使う。顔が切れる区間はpad／blurと比較して承認を得る。[PR #164](https://github.com/kajisho5/Velisa/pull/164/files)
- 無音削除は先にsilences、keep、前後マージン、cut warnings、字幕の時刻写像を提示する。強い息や弱い子音に近い境界は試聴し、選んだ区間だけ承認後に切る。[PR #165](https://github.com/kajisho5/Velisa/pull/165/files)
- 基本順は取込→Transcript→粗編集→画→字幕→グラフィックス→音→書出・検証。長尺は短い試作で確認する。順序変更時は依存を壊さない理由をPlanに記録。出力寸法や音量の技術判定と、字幕内容・構図・完成物の承認を別に記録する。[PR #166](https://github.com/kajisho5/Velisa/pull/166/files)
- 尺合わせは指定区間を保存しcutを先に検討。速度変更は明示選択し両方向1.25倍以内（再生倍率0.8〜1.25）。1.15倍超の警告をレビューに出す。fitのmethodは明示し、speed時は上限も渡す。達成不能・意図が曖昧なら選択を返す。[PR #171](https://github.com/kajisho5/Velisa/pull/171/files)

証拠は同じジョブIDのrecipe v1/v2、変更した引用、無効化ステージ、出力、QC結果、人間承認。途中で止めて再開し、未承認の削除・再投稿が起きないことまで試す。[#167](https://github.com/kajisho5/Velisa/issues/167) · [#168](https://github.com/kajisho5/Velisa/issues/168) · [#169](https://github.com/kajisho5/Velisa/issues/169) · [#170](https://github.com/kajisho5/Velisa/issues/170)

## 2　ブランド付き放送マスター（P0のalphaを含む・L）

同じkit@1、半透明ロゴ、タイトル、音声原本から静止画、モーション素材、番組マスターを作る。Remotionのconsumerでkitを投影し、元kitのdigest・投影結果・採用版を保存する。colour/alphaの受け入れは[専用手順書](03_blockers_and_ffmpeg_handoff.md)。白・黒の背景合成をオーナーが確認するまでalphaの受け入れは保留。

日本向け音声は−24 LKFS、TP上限−1 dBTP。書出後の独立したcheckではbroadcastのEBU既定値を上書きし、ラウドネス±1 LU、TP +0.1 dBのツール許容差を記録する。片ch修復と正規化を別行に記録し、音量のみ／TPのみ不合格のfixtureで原因を分ける。kitの未知キーによる拒否はconsumerへ、数値超過は音響へ、描画差は生成または合成へ戻す。[kit投影仕様](../specs/kit.md) · [Remotion #32](https://github.com/kajisho5/remotion-ffmpeg-skill/issues/32)

## 3　NLEへ渡し、編集者の変更を戻す（P2・M）

2素材・異なる開始TC・分数fps・字幕cueを含む短いprojectを固定。nle-bridgeで交換ファイルとrelink manifestを生成し、既知の1カットだけをtrimした返却fixtureをdiffへ渡す。素材ID、変更前後のフレーム境界、失われる要素の一覧、未変更音声の位置を照合する。Agentは差分だけのプレビューを作り、編集者の承認後にrecipeを更新する。未対応要素は元projectを保持して手動照合へ。[NLE adapter](https://github.com/kajisho5/video-production-agent/tree/main/src/video_agent/tools/nle_bridge)

**環境別ゲート**　macOS上で交換ファイルの構文・読戻しとモック投稿を先に実施。Resolve Studio／Premiereで実際に開いて再書出する試験はアプリ版と実機を、Windows GPUはGPU・driver・FFmpegを、SNS投稿は対象アカウントと単発承認を別々に記録する。ファイル試験から実機・公開成功を推定しない。物理媒体への書込みもISO検証と別の承認が必要。
