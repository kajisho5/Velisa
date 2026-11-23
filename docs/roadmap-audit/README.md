# Velisa 次期ロードマップ監査

2026-11-23。基準は [Velisa 181b782](https://github.com/kajisho5/Velisa/tree/181b782)、[組織台帳](../../ecosystem.json)、各ページのproducer commit、[Agent 5706360](https://github.com/kajisho5/video-production-agent/tree/5706360)。第1優先は日本語の講演から承認付き短尺を作り、一箇所直して再開する体験。放送用alphaは特定ジョブのP0として並行して受け入れる。

- [縦断3案件と承認ルール](01_cross_cutting_usecases.md)
- [外部比較と差別化](02_benchmark_and_gaps.md)
- [ブロッカーとalpha受け入れ手順](03_blockers_and_ffmpeg_handoff.md)
- [Issue本文案・既存案件の整理](04_issue_drafts.md)

## 33件の成熟度

「一致」はproducerのContractとAgentにあるpinのバイト一致。起動・バージョンゲート通過は別途試験する。「あり」は該当ソースがあることを指し、全操作の接続を意味しない。09はhandoff、11はレイヤー生成が実行可能、24はdiff読戻しがある。25〜29・31〜33は独立用途で合格できる。合成E2Eと実素材の列はこの監査で確認した実行証跡の有無。未確認を失敗として集計しない。各ページの acceptance/ は将来の証拠パスである。

P0は回避不能な実ジョブ、P1は品質・安全・看板工程、P2は改善・将来設計。工数は1担当の概算（S＝1〜3日、M＝4〜10日、L＝11日以上、実機待ちを除く）。

|No.・個票|部門|台帳|Contractあり|Agent pin受理|adapterあり|合成E2E合格|実素材合格|優先度／工数|
|---|---|---|---|---|---|---|---|---|
|[01_video-production-agent](components/01_video-production-agent.md)|司令塔|active|実装定義|対象外|対象外|未確認|未確認|P1/M|
|[02_ingest-skill](components/02_ingest-skill.md)|取込|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[03_ffmpeg-skill](components/03_ffmpeg-skill.md)|エンジン|active|実装定義|動的・実行未確認|あり|未確認|未確認|P0/M|
|[04_video-editing-skill](components/04_video-editing-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[05_color-grading-skill](components/05_color-grading-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P0/M|
|[06_motion-graphics-skill](components/06_motion-graphics-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[07_subtitle-skill](components/07_subtitle-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[08_thumbnail-skill](components/08_thumbnail-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P2/S|
|[09_blender-skill](components/09_blender-skill.md)|映像|active|あり|一致・実行未確認|引渡し|未確認|未確認|P2/M|
|[10_remotion-ffmpeg-skill](components/10_remotion-ffmpeg-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P1/S|
|[11_hyperframes-skill](components/11_hyperframes-skill.md)|映像|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[12_audio-production-skill](components/12_audio-production-skill.md)|音|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[13_voice-enhance-skill](components/13_voice-enhance-skill.md)|音|active|あり|一致・実行未確認|あり|未確認|未確認|P2/M|
|[14_dubbing-skill](components/14_dubbing-skill.md)|音|active|あり|一致・実行未確認|あり|未確認|未確認|P2/M|
|[15_sound-design-skill](components/15_sound-design-skill.md)|音|active|あり|一致・実行未確認|あり|未確認|未確認|P2/M|
|[16_transcription-skill](components/16_transcription-skill.md)|認識|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[17_diarization-skill](components/17_diarization-skill.md)|認識|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[18_detection-skill](components/18_detection-skill.md)|認識|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[19_slide-sync-skill](components/19_slide-sync-skill.md)|認識|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[20_qc-skill](components/20_qc-skill.md)|検証|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[21_media-analysis-skill](components/21_media-analysis-skill.md)|検証|active|あり|一致・実行未確認|あり|未確認|未確認|P1/S|
|[22_artifacts-skill](components/22_artifacts-skill.md)|検証|active|あり|一致・実行未確認|あり|未確認|未確認|P1/S|
|[23_publish-skill](components/23_publish-skill.md)|納品|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[24_nle-bridge-skill](components/24_nle-bridge-skill.md)|納品|active|あり|一致・実行未確認|あり|未確認|未確認|P1/M|
|[25_bdmvkit](components/25_bdmvkit.md)|納品|active|あり|対象外|対象外|未確認|未確認|P2/M|
|[26_vtskit](components/26_vtskit.md)|納品|active|あり|対象外|対象外|未確認|未確認|P2/M|
|[27_udfkit](components/27_udfkit.md)|納品|active|あり|対象外|対象外|未確認|未確認|P2/S|
|[28_dvdcc](components/28_dvdcc.md)|納品|active|あり|対象外|対象外|未確認|未確認|P2/S|
|[29_oncemore](components/29_oncemore.md)|納品|active|あり|対象外|引渡し|未確認|未確認|P2/M|
|[30_imagemagick-skill](components/30_imagemagick-skill.md)|補助|active|あり|一致・実行未確認|あり|未確認|未確認|P2/S|
|[31_stepcap](components/31_stepcap.md)|補助|active|あり|対象外|対象外|未確認|未確認|P2/S|
|[32_skillpact](components/32_skillpact.md)|統制|active|自己宣言未確認|対象外|対象外|未確認|未確認|P1/M|
|[33_system-intelligence](components/33_system-intelligence.md)|統制|active|自己宣言未確認|対象外|対象外|未確認|未確認|P1/M|
