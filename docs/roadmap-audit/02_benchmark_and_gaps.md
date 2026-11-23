# 競合15件と制作体験の差

2026-11-23のStep 1の観測値を採用。GitHubで「"video editing" skill」「ffmpeg skill」「ffmpeg mcp」「video mcp」「remotion skill」「"davinci resolve" mcp」を各スター降順・最大100件で検索し、owner/repoで重複排除。kajisho5は比較枠、Skill／MCPを確認できなかった画面収録アプリvidemo（49★）は対象外。取得集合内の順位であり、動作試験・市場占有率の調査ではない。比較枠はVelisa 12★、FF約1.01万★。

|順位|一次資料|★|利用者が得る体験|Velisaで対応する場所|
|---:|---|---:|---|---|
|1|[claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill)|1276|短いルールと完成デモから制作依頼を選ぶ|用途別導入とRemotion|
|2|[flow-agent](https://github.com/kodelyx/flow-agent)|280|接続確認から最初の画像・動画生成へ進む|将来の任意Provider導入|
|3|[remotion-skills](https://github.com/buainoai/remotion-skills)|162|時間・文字・メディアに分けた知識を参照|モーション制作資料|
|4|[ffmpeg-mcp](https://github.com/video-creator/ffmpeg-mcp)|155|検索・再生・編集を同じ対話で実行|ingestと編集候補の連続プレビュー|
|5|[ffmpeg-mcp](https://github.com/egoist/ffmpeg-mcp)|122|ローカル実行ファイルを指定してMCPを起動|初回診断とセットアップ|
|6|[heditor](https://github.com/pycodebr/heditor)|117|ブランドと声を中心にした縦動画レシピ|kitと短尺納品|
|7|[Motion-graphics-skill](https://github.com/mattypark/Motion-graphics-skill)|105|計画・字幕・モーション・サウンドを一つの依頼にする|Plan上の部門間連携|
|8|[eva-video-style](https://github.com/RoverEva/eva-video-style)|82|話者動画のスタイルを実例から選ぶ|参考プレビュー・選択履歴|
|9|[claude-ffmpeg-skill](https://github.com/ychoi-kr/claude-ffmpeg-skill)|71|依頼文例から最初の変換へ進む|初回の入力例|
|10|[yby6-crawling-short-video-mcp](https://github.com/yangbuyiya/yby6-crawling-short-video-mcp)|65|URLから素材・メタデータ・文字起こしへ進む|ingestとライセンス記録|
|11|[video-editing-skill](https://github.com/6missedcalls/video-editing-skill)|56|無音カットと字幕の初回操作が短い|確認付き無音編集|
|12|[cutcraft](https://github.com/chang416/cutcraft)|53|依頼・文字起こしから完成案件の成果物まで示す|recipe・修正再開・Receipt|
|13|[seedance-2-5-video-mcp](https://github.com/eudoramarlowe/seedance-2-5-video-mcp)|43|生成依頼・ジョブ状態・費用・取得を明示|外部生成時の承認・再試行|
|14|[JJKoubo](https://github.com/darrenli6/JJKoubo)|42|話す人を中心とした素材から一式を生成|日本語対談の看板工程|
|15|[unofficial-davinci-mcp](https://github.com/wassermanproductions/unofficial-davinci-mcp)|38|ライブ制御とファイル経由の編集を版に応じて選ぶ|NLE実機ゲートと交換ファイル|

## 次に比較する動作

同じ許諾済み対談から「発言を選び60秒にする」を初見で実施。プレビュー到達までの人間操作数・経過時間・追加質問を記録する。次に一箇所だけ引用を変更し、再実行した工程数、再計算時間、意図せず変化した区間、最終納品時の根拠欠落を数える。異なるモデル・機材の所要時間は混ぜず、失敗した試行も残す。今回の順位から性能値は推定しない。

P1は既存の #167〜#170 に「入力例→根拠付き選択→明示承認→局所修正→QC」の通し証拠を加えること。ブランドの一貫性はkit投影、診断表示はControl Roomで扱う。P2ではNLEのライブ操作とファイル往復、生成Providerの課金・再開・ライセンスを上位で比較する。日本語ASR、ステム分離、ローカルVideo-RAGの品質は別タスクで実測する。下位FFには既存 #453・#721・#722 の参照だけを残す。
