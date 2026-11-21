# 所有分担の監査 B: 音 (Audio) 部門と認識 (Recognition) 部門

調査日 2026-11-12。読み取りのみ。各リポジトリは `origin/main` を `git show` / `git grep` で読んだ（作業ツリーには触れていない）。
証拠の書き方: `repo@sha:path:行`。推測は「推測」、読めなかった・確かめられなかったものは「未確認」と書く。

## 読んだもの

| repo | commit | version (pyproject / tag) | 読んだファイル | 未確認 |
|---|---|---|---|---|
| audio-production-skill | 7ab8022 | 1.2.0 / tag v1.2.0 (release 2026-11-12) | `src/audio_production/{contract,model,executor,adapter,fillers}.py`, `docs/decisions.md` (ADR-1..24 の見出しと要点), `ECOSYSTEM_ROADMAP.md` | README / SKILL.md / CLAUDE.md は通読していない（契約ソースを優先） |
| voice-enhance-skill | 9e0c150 | 0.1.0 / tag なし, release なし | `src/voice_enhance_skill/{contract,doctor,ffmpeg_skill}.py`, `engines/*.py` (licence 行), `docs/decisions.md` ADR-001, `CHANGELOG.md`, `ECOSYSTEM_ROADMAP.md` | ADR-002..009 は CHANGELOG と roadmap 経由で把握 |
| dubbing-skill | f929f4a | 0.2.1 / tag なし, release なし | `src/dubbing_skill/{contract,cli,doctor,ffmpeg_skill}.py`, `engines/*.py` (licence 行), `docs/decisions.md` ADR-001, ADR-018 と全見出し, `CHANGELOG.md`, `ECOSYSTEM_ROADMAP.md` | ADR-002..017 の本文は roadmap 経由 |
| sound-design-skill | d974c26 | 0.3.2 / tag なし, release なし | `src/sound_design_skill/contract.py`, `engines/*.py` (licence 行), `docs/decisions.md` ADR-001, 005, 007, 014 と全見出し, `ECOSYSTEM_ROADMAP.md` | ADR-016 (XL turbo) 本文 |
| transcription-skill | 99b59b8 | 0.11.4 / tag v0.11.4 (release 2026-11-12) | `src/transcription_skill/{skill,chunking,speech_events}.py`, `engines/{faster_whisper,whisperx}.py` (licence 行), `docs/engines.md`, `docs/decisions.md` (見出しと licence 行), `ECOSYSTEM_ROADMAP.md` | 既定 Whisper 重み (tiny..large-v3) の licence 記載は repo 内に見つからず |
| diarization-skill | 3254cc0 | 0.3.0 / tag なし, release なし (CHANGELOG は 0.3.0 - 2026-11-06) | `src/diarization_skill/contract.py`, `engines/pyannote_engine.py` (licence 行), `docs/decisions.md` ADR-001..003, `ECOSYSTEM_ROADMAP.md` | 実エンジンでの DER（repo 自身が未計測と明記） |
| detection-skill | 9e2f732 | 0.2.2 / tag なし, release なし (CHANGELOG は 0.2.2 - 2026-11-12) | `src/detection_skill/contract.py`, `docs/decisions.md` ADR-001, 003, 005, 008 と全見出し, `ECOSYSTEM_ROADMAP.md` | ADR-004, 006, 007 本文 |
| slide-sync-skill | 7b32715 | 0.1.0 / tag なし, release なし (CHANGELOG は `Unreleased`) | `src/slide_sync/contract.py`, `docs/decisions.md` 見出し, `ECOSYSTEM_ROADMAP.md` | ADR 本文 |
| ffmpeg-skill (重なる部分のみ) | 11c153e | package.json 3.6.5 / tag v3.6.5 | `scripts/{loudness,audio,silence,scenes,waveform,redact,denoise,pad,fit}.py` の docstring と引数, `scripts/_common/{asr,decision}.py` の該当行 | 全 42 ツールは読んでいない |
| media-analysis-skill (重なる部分のみ) | ab432c0 | 0.1.16 / tag v0.1.16 | `src/media_analysis/contract.py`, `analyzers/vad.py`, `models/silero_vad.LICENSE` | ADR-035 本文 |
| qc-skill (参照) | b7475e9 | 1.3.0 | `src/qc_skill/contract.py` の音まわりの行 | — |
| subtitle-skill (参照) | da597e5 | 0.9.1 | `src/subtitle_skill/contract.py` の translate 行 | 翻訳エンジンの ADR 本文 |
| video-production-agent (配線) | b2d4e08 | 0.1.0 | `src/video_agent/skills/{registry,ecosystem}.py`, `agent/{audio,voice,planner,decision}.py` の該当行, `tools/*/contract_*.json` の一覧 | 各 adapter の本文 |
| Velisa | 45a40f1 | tag v0.9.0 | `ecosystem.json`, `docs/ecosystem/ROADMAP.md`, `docs/CAPABILITY_MATRIX.md`, `docs/REPOSITORY_MAP.md`, `docs/ecosystem/{CROSS_REPO_STATUS,CURRENT_STATE,DECISION_LOG,HANDOFF,WORK_QUEUE}.md` (grep), `README.md` | DECISION_LOG / HANDOFF は該当語の grep のみ |

## 各スキルが実際にできること

### audio-production-skill 1.2.0
- ツールは 1 つ `audio-production/run`。型付きの操作 18 種: GAIN, TRIM, CUT, SILENCE_REMOVE, FADE_IN, FADE_OUT, NORMALIZE, MIX(duck), MONO, STEREO, DOWNMIX, NOISE_REDUCTION, DYNAMICS, CONCAT, VOICE_CLEANUP, FILLER_REMOVE, LOUDNESS_SET, STEMS（`audio-production-skill@7ab8022:src/audio_production/contract.py:25-31`）。すべて lifecycle `EXPERIMENTAL`（同 :35）。
- 実行はすべて ffmpeg-skill の `probe, audio, cut, loudness, join`（`adapter.py:52`、操作ごとの対応は `executor.py:46-69`）。SILENCE_REMOVE と FILLER_REMOVE は `cut` を使う（`silence` ではない）。
- 決めないこと: 無音の範囲は呼び出し側が渡す（`model.py:155-159`）。フィラーは呼び出し側の語の時刻と辞書で切る。文字起こしはしない（ADR-18、`docs/decisions.md:138`）。ラウドネス目標に既定値はない（ADR-3、`model.py:167-168`）。
- ラウドネスのプロファイル: `ebu_r128`, `atsc_a85`, `arib_tr_b32`（`model.py:68-71`）。
- 断っているもの: `not_provided` = 判断用のラウドネス・無音計測 (media-analysis-skill)、音声認識、映像編集、任意の ffmpeg フィルタ（`contract.py:123-124`）。未実装と宣言: CHANNEL_MAP, RESAMPLE, FORMAT_CONVERT（`model.py:233-237`）。
- 未着手の roadmap: 7 MATCH_REFERENCE、10 AUTOMIX、11 入力ごとの pan と言語別トラック（`ECOSYSTEM_ROADMAP.md` Steps）。

### voice-enhance-skill 0.1.0
- `isolate`（DeepFilterNet3、48 kHz mono の stem）、`dereverb`（nara_wpe の WPE）、`bleed-reduce`（自前の `crosstalk`、重みなし、2〜8 トラック）、補助の `remux`（ffmpeg-skill `audio --replace`）、`doctor`, `engines`, `contract`（`voice-enhance-skill@9e0c150:src/voice_enhance_skill/contract.py:29-98`）。
- 3 つの op はすべて実装済み（`doctor.py:21` `IMPLEMENTED_OPS = {isolate: True, dereverb: True, bleed_reduce: True}`）、lifecycle は `EXPERIMENTAL`（`contract.py:122`）。
- ffmpeg-skill は `probe` と `audio` だけ（`ffmpeg_skill.py:41`）。
- 長尺はブロック処理で再開できる（ADR-009、`contract.py:19-27`）。
- 断っているもの: 従来型のノイズ低減・音量・ミックス・無音/フィラー (audio-production)、文字起こし、話者分離、TTS/吹替、音楽の分離・生成 (sound-design と書いている)、声の生成的な作り直し（`contract.py:125-131`）。

### dubbing-skill 0.2.1
- op: `narrate`, `dub`, `describe`（音声解説）。補助: `fit`（尺合わせの計画）、`terms`（読み辞書の確認）、`watermark`（Perth 透かしの読み戻し）、`doctor`, `engines`, `contract`（`dubbing-skill@f929f4a:src/dubbing_skill/cli.py:64-185`、`contract.py:189-245`）。
- capability id: `speech.narrate`, `speech.dub`, `speech.audio_description`（`contract.py:29`）。3 つとも実装済み（`doctor.py:23`）で `EXPERIMENTAL`。
- エンジン 5 つ: chatterbox（既定）、voicevox、style_bert_vits2、kokoro、qwen3_tts（`experimental=True`、`engines/qwen3_tts.py:119`）。既定は全 op で Chatterbox（`engines/__init__.py:18`）。
- ffmpeg-skill: `probe, join, audio, loudness, cut`（`ffmpeg_skill.py:52`）、任意で `pad` と `silence --list`（同 :63-67）。
- 声の複製は同意記録が必須（ADR-009）。翻訳はしない: 呼び出し側の入力（ADR-003、`contract.py:289`）。
- 断っているもの: 翻訳、文字起こし、話者分離、字幕、元音声のノイズ処理、音楽・効果音、番組の最終ミックスとラウドネス目標 (audio-production)、リップシンク（`contract.py:289-297`）。
- 制限: 音だけの tempo と pad が ffmpeg-skill に無いので、DUB は tempo 1.0 のみ、NARRATE の時刻付き cue は pad 待ち（`ECOSYSTEM_ROADMAP.md` 表と step 2, 11、`doctor.py:57-62`）。

### sound-design-skill 0.3.2
- capability id: `audio.bgm_generate`, `audio.sfx_generate`, `audio.library_import`（`sound-design-skill@d974c26:src/sound_design_skill/contract.py:23`）。
- ツール: `generate-bgm`（ACE-Step 1.5、`--bpm` で拍グリッド `<name>.beats.json` も書く）、`generate-sfx`（EzAudio、`--acknowledge-ezaudio-training-data` が必要、ADR-007）、`library-import` / `library-index` / `library-pick`、`loop-bed`、`stinger`、`seam-check`、`sfx-cues`、`doctor`, `engines`, `contract`（`contract.py:83-199`）。
- 実装済み: `IMPLEMENTED_OPS = {bgm, sfx, library, loop, stinger: True}`（`doctor.py:30`）。
- ライセンス記録: `library-import` は licence が無いファイルを断る (`LICENCE_REQUIRED`)。`sound-library.json`、`licences/<sha256>.txt`、帰属表示の行、Content ID の申告を残す（ADR-008, ADR-014、`docs/decisions.md:572-590`）。外部のストック源 (Freesound, Jamendo) は doctor に出るだけで、取得は実装していない（同 ADR-014「No source is ever called」）。
- 断っているもの: 番組へのミックス・ダッキング・ラウドネス目標 (audio-production)、声 (dubbing)、ノイズ低減 (voice-enhance)、生成音楽の権利確認（`contract.py:229-233`）。

### transcription-skill 0.11.4
- ツール 6 つ: `transcription/transcribe`, `segments`, `export`, `speakers`, `check`, `batch`（`transcription-skill@99b59b8:src/transcription_skill/skill.py:44-71`）。capability id は `transcribe.audio` の 1 つ（同 :86）。
- エンジン 5 つ: `faster_whisper`（既定）、`haas_ja`、`speechcpp`、`whisperx`、`qwen3_asr`（`ECOSYSTEM_ROADMAP.md` Where it stands、`docs/engines.md`）。
- `transcription/speakers` と `speaker_turns` 入力: diarization-skill の turns で `speaker_id` を埋める。diarization-skill の ASSIGN と同じ規則（ADR-037、`skill.py:63-68`）。
- 長尺: `chunk_seconds` / `parallel` / `speech_regions`（media-analysis の観測を受け取る、`chunking.py:8, 43-78`）。収録中: `transcribe --follow`（ADR-043）。
- 音声の取り出しは ffmpeg を直接呼ぶ（ffmpeg-skill 経由ではない。`skill.py:97` `DEPENDENCIES = []`、roadmap「Extracts audio with ffmpeg directly (by design)」）。
- 断っているもの: 話者分離・話者同定、意味の区切り、字幕の描画、メディア計測、クラウド ASR（`skill.py:101-106`）。
- 未着手: step 8 台本への強制アライメント、step 11 番組からの語彙、step 12 `--per-channel`。

### diarization-skill 0.3.0
- ツール: `diarize`, `assign`, `enroll`, `name`, `check`, `score`（`diarization-skill@3254cc0:src/diarization_skill/contract.py:21-44`）。capability id: `speech.diarize`, `speech.assign_speakers`, `speech.enroll_voice`, `speech.propose_speaker_names`（同 :80-83）。
- エンジンは pyannote.audio 4.x + `speaker-diarization-community-1` だけ（ADR-001）。重みはゲート付きで、一度だけ手で取得する。
- `name` は名簿の人だけを「提案」する。証拠は同意済みの声紋と、detection-skill の OCR（テロップ）。確定はしない（ADR-002、`contract.py:97-101`）。
- ffmpeg は直接呼ぶ（`contract.py:90` `{"id": "ffmpeg", "kind": "binary"}`）。
- 断っているもの: 名前の確定、名簿外の同定、文字起こし、テロップの OCR、重なった声の分離、字幕の話者ラベル（同 :97-101）。

### detection-skill 0.2.2
- ツール: `faces`, `text`, `objects`, `tracks`, `shots`, `reframe`, `speakers`, `pii`, `rank`, `check`（`detection-skill@9e2f732:src/detection_skill/contract.py:32-89`）。capability id 9 つ（`vision.detect_faces` ほか、同 :121-129）。
- エンジン: YuNet（顔）、Tesseract 5（OCR、既定）と PP-OCRv6（任意）、YOLOX（物体、既定）と RF-DETR S/M（任意）、PySceneDetect（ショット、既定）と TransNetV2（任意）（ADR-001, 003, 008）。
- フレームは ffmpeg-skill `probe` / `scenes` / `look` から取る。自分ではデコードしない（`contract.py:175`）。
- 断っているもの: 顔認識・個人の同定、ぼかし (ffmpeg-skill redact)、スライド切替検出 (slide-sync-skill)、OCR テキストの訂正、reframe の適用、カメラ切替の実行、話者分離（同 :174-182）。

### slide-sync-skill 0.1.0
- ツール: `detect`（`--follow` あり）、`chapters`, `import`, `match`, `insert`, `layout`, `clean`（`slide-sync-skill@7b32715:src/slide_sync/contract.py:24-74`）。capability id 7 つ（`slides.*`、同 :100-106）。
- `detect` は ffmpeg-skill `scenes` の結果に最小滞在時間のフィルタを掛ける。`import` は PDF のテキスト層と画像（pypdfium2、PPTX/KEY は LibreOffice）。`match` は画像の相関で、文字は使わない。
- 断っているもの: 画像やスキャンからの文字 (OCR は detection-skill)、文字による照合（同 :118-119）。

### ffmpeg-skill 3.6.5（重なる部分）
- `loudness.py`: 2 パス loudnorm、`--measure-only`、`--versions`（`streaming`, `ebu-r128`, `broadcast-jp`）（`ffmpeg-skill@11c153e:scripts/loudness.py` docstring と :221-229）。
- `audio.py`: `--denoise`, `--voice [light|medium|strong]`, `--music --duck`, `--effects`, `--compress/--limit/--gate`, `--replace`, `--downmix`（同 `scripts/audio.py:165-222`）。`--sample-rate` と `--channel` は無い（grep で 0 件）。
- `silence.py`: 無音の検出と削除を 1 回で行う。`--list`, `--speech-aware`, `--filler`（内蔵の語リスト en/ja/es/de/fr/pt/it）、`--words`, `--transcribe`（自前の ASR ブリッジ: Parakeet / whisper-cli / faster_whisper、`scripts/_common/asr.py:250-275, 417, 779`）（`scripts/silence.py:540-603`、語リストは `_common/decision.py:1630-1640`）。
- `scenes.py`: scdet のカット、`--beats`, `--speech`（ゼロ交差率の代用値で「分類ではない」と明記、:140-142）、`--shots`, `--audio-peaks`。
- `denoise.py` は映像専用（hqdn3d）。音は `audio.py --denoise`。`redact.py` は矩形を受け取るだけで検出しない。`waveform.py` は波形・スペクトルの映像化。
- `pad.py:45`, `fit.py:123`, `speedramp.py:74` は「input has no video stream」で断る（音だけの pad / tempo は無い）。

### media-analysis-skill 0.1.16（重なる部分）
- 計測の kind 13 種。音は `silence`, `loudness`, `noise_floor`, `speech_regions`、映像は `scene_detection`, `edit_style` など（`media-analysis-skill@ab432c0:src/media_analysis/contract.py:30-98`）。
- `speech_regions` は silero-vad（ONNX をパッケージに同梱、任意 extra `vad`）。extra が無いと `UNKNOWN`（`analyzers/vad.py:1-13`）。

## 重複

| # | 仕事 | 誰ができるか（証拠） | 実際の違い | agent の今の経路 |
|---|---|---|---|---|
| D1 | ラウドネス正規化 | audio-production `NORMALIZE` / `LOUDNESS_SET`（`model.py:166, 215`）。ffmpeg-skill `loudness`（`--versions` 含む）。dubbing NARRATE も声プロファイルの目標へ `loudness` で合わせる（dubbing roadmap step 13）。 | audio-production は音だけ・目標に既定なし・許容差で再計測して失敗にできる・来歴つき。ffmpeg-skill は映像を stream copy して既定 -14 LUFS。 | SkillSpec が 2 本ある。映像の経路は `loudness_normalization` → `ffmpeg-skill/loudness`（AUTO）、音の経路は `audio_normalize` → `audio-production/run`（CONFIRM）（`video-production-agent@b2d4e08:src/video_agent/skills/registry.py:269-270, 316`、`agent/planner.py:573-585`）。LOUDNESS_SET は「計画しない」（`tools/audio_production/adapter.py:49`）。 |
| D2 | ラウドネス計測 | ffmpeg-skill `loudness --measure-only`、media-analysis `loudness`、qc `audio.integrated_loudness_lufs` ほか（`qc-skill@b7475e9:src/qc_skill/contract.py:69-71`）。audio-production は自分の出力だけ検証。 | media-analysis は観測、qc は合否、ffmpeg-skill はエンジンの計測。Velisa は qc と media-analysis の id 衝突を既に記録（`Velisa@45a40f1:docs/CAPABILITY_MATRIX.md:172`）。 | `loudness_analysis` の候補は `["ffmpeg-skill/loudness", "media-analysis/loudness"]` の順（`registry.py:265-266`）。 |
| D3 | ミックス・ダッキング | audio-production `MIX` + `duck`（`model.py:173-176`）。ffmpeg-skill `audio --music --duck --effects`。dubbing `dub` / `describe` は番組音を `--duck` dB 下げて声を重ねる（dubbing roadmap step 5, 7）。 | dubbing は自分の op の中で固定の重ね方をするだけで、番組の最終ミックスは audio-production と宣言（`dubbing contract.py:293`）。 | `audio_mix` → audio-production（`registry.py:323`）。BGM は sound-design の出力を MIX の最後の入力にする（同 :411-419）。`speech_dub` は dubbing が自分で重ねる（同 :520）。 |
| D4 | ノイズ低減・声の整音 | audio-production `NOISE_REDUCTION`（afftdn）と `VOICE_CLEANUP`（`audio --voice` の型付き wrapper）。ffmpeg-skill `audio --denoise / --voice`。voice-enhance `isolate`（DeepFilterNet3）。 | 従来型は決定的で重みなし。AI 分離は重みと別バイナリが要り、48 kHz 限定。コード上の線ははっきりしている（下の 9(b)）。 | 従来型は `audio_noise_reduction` / `audio_voice_cleanup`、AI は `voice_isolate` ほか（CONFIRM）。順序も固定（`agent/voice.py` 冒頭）。agent は ffmpeg-skill の `--denoise` を直接は使わない（registry に該当 SkillSpec なし）。 |
| D5 | 無音の検出 | ffmpeg-skill `silence --list`、media-analysis `silence`、qc `audio.silence_segments`。dubbing `describe --detect-gaps` は ffmpeg-skill `silence --list` を使う。 | 3 つとも silencedetect 系。media-analysis は先頭・内部・末尾の分類つき。 | `silence_analysis` の候補は `["ffmpeg-skill/silence", "media-analysis/silence"]`（`registry.py:263-264`）。 |
| D6 | 無音の削除 | ffmpeg-skill `silence`（検出と削除を一度に）。audio-production `SILENCE_REMOVE` / `CUT`（範囲は呼び出し側）。video-editing `cut`。 | ffmpeg-skill は自分で閾値を決めて切る。audio-production は決めない。 | 映像は `silence_cleanup` → `ffmpeg-skill/cut` か `video-editing/cut`、音は `audio_cut` → audio-production（`registry.py:267-268, 313`、`agent/decision.py:519`）。agent は ffmpeg-skill `silence` の削除モードを使わず、範囲を自分で決めて `cut` に渡す。 |
| D7 | フィラー除去 | audio-production `FILLER_REMOVE`（辞書 preset ja / en、既定なし、`fillers.py:25-27`）。ffmpeg-skill `silence --filler`（内蔵リスト 7 言語、`_common/decision.py:1630-1640`）。 | 日本語の辞書が違う。ffmpeg-skill は「あの・その・まあ・なんか」を含む。audio-production は含まず「あー・うーん・んー」などを含む。ffmpeg-skill は `--transcribe` で自分で語の時刻も作れる。 | `audio_filler_remove` → audio-production のみ（`registry.py:329-330`）。語の時刻は transcription-skill から（`agent/audio.py` Filler removal）。 |
| D8 | 音声認識 | transcription-skill（5 エンジン）。ffmpeg-skill の内蔵 ASR ブリッジ（`caption --transcribe`, `silence --transcribe`、`_common/asr.py`）。stepcap の音声メモ（transcription roadmap「Boundaries」）。 | ffmpeg-skill 側は Transcript スキーマも来歴も持たない補助機能。 | `speech_transcription` → `transcription/transcribe` のみ（`registry.py:355-356`）。 |
| D9 | 発話区間 (VAD) | media-analysis `speech_regions`（silero ONNX）。transcription の speechcpp が持つ `silero-vad` GGUF と whisperx 同梱の pyannote segmentation（`docs/engines.md:339, 379`）。ffmpeg-skill `scenes --speech`（代用値）と `silence --speech-aware`。diarization の turns。 | media-analysis だけが「発話区間」を観測として外に出す。他はエンジン内部の前処理か代用値。 | agent は `speech_regions` を「追加されたが計画しない」（`tools/media_analysis/adapter.py:31`）。transcription の `speech_regions` 入力も opt-in で未使用（`tools/transcription/adapter.py:48`）。 |
| D10 | 文字起こしへの話者 id の付与 | diarization `assign`（`contract.py:26`）。transcription `transcription/speakers`（同じ ASSIGN 規則、ADR-037）。 | 同じ規則の実装が 2 つある。 | agent は transcription 側の merge を使う（`agent/speakers.py:15`、ADR-096）。`diarization/assign` は agent から呼ばれていない（registry に無い）。 |
| D11 | 「今だれが話しているか」 | diarization `diarize`（声）。detection `speakers`（口の動き + 任意で turns、マルチカムの切替表、ADR-005）。ffmpeg-skill `multicam --switch energy`（音量の代用）。 | diarization は「声の区間」、detection は「画面のどの顔・どのカメラ」。目的が違う。 | `speaker_diarization` は配線済み。`detection/speakers` は未配線（registry に無い）。 |
| D12 | カット・ショット・スライド切替の検出 | ffmpeg-skill `scenes`（scdet）。media-analysis `scene_detection`（scdet）。detection `shots`（PySceneDetect / TransNetV2、フレーム番号つき、ディゾルブも）。slide-sync `detect`（ffmpeg-skill `scenes` + 最小滞在）。 | detection ADR-003 が「`scenes` は速い一覧、`shots` は計測したショット表」と線を引いている（`docs/decisions.md:98-112`）。media-analysis と ffmpeg-skill の scdet 二重は Velisa #36 が既に指摘。 | `scene_analysis` → `media-analysis/scenes`、`beat_analysis` → `ffmpeg-skill/scenes`、`slide_sync` → `slide-sync/detect`（`registry.py:346, 368-369, 399-401`）。`detection/shots` は未配線。 |
| D13 | 画面の文字を読む | detection `text`（唯一の OCR）。slide-sync `import` は PDF のテキスト層だけ。media-analysis `edit_style` は焼き込み字幕の有無・位置を測るだけで読まない。stepcap は自前で Tesseract（detection ADR-001「stepcap already runs Tesseract」）。 | 読むのは detection だけ。線は両側の `not_provided` に書いてある。 | `detection/text` は handoff のまま（`registry.py:233-234` `visual_detection`）。 |
| D14 | ループの継ぎ目・スティンガー | sound-design `loop-bed` / `seam-check` / `stinger`。qc `AudioRule.loop_seam`（`qc contract.py:73-74, 113`）と `measurements/stinger.py`。ffmpeg-skill 提案 10 `loop --crossfade`（#422）。新候補 motion-titles-skill のスティンガー映像（音つき）。 | sound-design は音を作る、qc は判定する。sound-design ADR-017 が qc 1.3.0 で確認済み。 | 未配線（効果音は agent が計画しない、`registry.py:225`）。 |
| D15 | 音を映像へ戻す | voice-enhance `remux`、dubbing `dub`、agent の `audio_mux`。どれも ffmpeg-skill `audio --replace`。 | 薄い wrapper が 3 つ。 | `audio_mux` → `ffmpeg-skill/audio`（`registry.py:336-337`）。voice の stem を映像へ戻す経路は未配線（`agent/voice.py` 冒頭）。 |
| D16 | ライセンス台帳 | sound-design の library（音だけ）。新候補 asset-library-skill（映像・写真）。artifacts-skill（帰属表示の検査）。 | 下の 9(g)。 | `bgm_library` → `sound-design/library-pick`（`registry.py:415-417`）。 |

## 隙間

| # | 仕事 | 根拠 | 現状 |
|---|---|---|---|
| G1 | 文字起こしの語句検索 | `Velisa@45a40f1:ecosystem.json:74` が transcription-skill の `owns` に入れている。`docs/ecosystem/WORK_QUEUE.md:1043`。 | transcription-skill 0.11.4 に検索ツールは無い（ツールは 6 つ、`skill.py:44-71`）。 |
| G2 | 音楽と声の分離（歌・BGM の stem 抜き） | voice-enhance は「music / BGM separation or generation (sound-design-skill)」と断る（`contract.py:127`）。 | sound-design に分離は無い（`contract.py:23`、`not_provided` にも無い）。持ち主なし。Demucs は voice-enhance ADR-001 で不採用。 |
| G3 | マイク別の文字起こし (`--per-channel`) | transcription roadmap step 12（未着手）。 | 実装なし（`git grep per-channel` 0 件）。 |
| G4 | パネル用オートミキサー、入力ごとの pan、言語別トラック、リファレンス合わせのマスタリング | audio-production roadmap step 10, 11, 7（未着手）。 | 実装なし。 |
| G5 | 台本への強制アライメント | transcription roadmap step 8（未着手）。dubbing step 11 と subtitle が使う想定。 | 実装なし。 |
| G6 | 番組・抄録・スライドからの専門語彙 | transcription roadmap step 11（未着手）。slide-sync `import` のテキストを使う想定。 | 実装なし。つなぐ役も未定。 |
| G7 | 音だけの tempo / pad | Velisa ROADMAP「Proposals to ffmpeg-skill」3。 | ffmpeg-skill 3.6.5 に無い（`pad.py:45`, `fit.py:123`）。該当の open issue はタイトル検索で見つからず（未確認: 本文検索はしていない）。DUB は tempo 1.0 のみ。 |
| G8 | `audio --sample-rate` / `--channel N` | 同 提案 4。 | 3.6.5 の `audio.py` に無い。ISOLATE は 48 kHz 以外を断る（`agent/voice.py` の RATE_REFUSAL）。 |
| G9 | 1 ファイルのマルチトラック納品 | audio-production step 8 の残り（ADR-24）。 | ffmpeg-skill #420 / #477 が open。 |
| G10 | 翻訳 → 吹替 → 字幕の一連を agent が計画 | dubbing roadmap step 11「agent side left to video-production-agent」。 | `speech_dub` は利用者が訳した cue を受け取る（`registry.py:520-523`）。翻訳との連結は agent に無い（推測: registry に連結の SkillSpec が無いため）。 |
| G11 | agent に未配線の実装済み op | registry に SkillSpec が無いもの。 | dubbing `narrate` / `describe`（handoff、`registry.py:231-232`）、sound-design `generate-sfx` / `sfx-cues` / `loop-bed` / `stinger`、detection `text` / `objects` / `shots` / `reframe` / `speakers` / `pii`、slide-sync `chapters` / `insert` / `layout` / `clean`、diarization `enroll` / `name`、audio-production `LOUDNESS_SET` / `STEMS`、media-analysis `speech_regions`。 |
| G12 | 実収録での計測 | voice-enhance step 10、diarization step 6、detection「real footage unmeasured」、sound-design「real ACE-Step 未計測」、transcription haas_ja「GPU run still to do」。 | 同意つきの試験素材を誰が用意するかは未定。 |
| G13 | 声質変換（元の話者の声で吹替） | dubbing ADR-001 の follow-up（OpenVoice V2）。 | 未登録。`owns` の「吹替・声の置換」に含まれるかは未確認。 |

## ecosystem.json との食い違い

| repo | ecosystem.json（`Velisa@45a40f1:ecosystem.json`） | 実際 |
|---|---|---|
| voice-enhance-skill | `status: scaffold`、`plugin` なし（:59） | 3 op + remux が実装済みで CI に実エンジンのジョブあり。`EXPERIMENTAL`。agent に配線済み（agent #88）。tag と release は無い。 |
| dubbing-skill | `status: scaffold`（:63）。`engines` は 4 つ | 3 op 実装済み、エンジンは 5 つ（qwen3_tts が抜けている）。role の「voice replacement」は実際には「訳した cue を TTS で話して差し替える」で、声質変換は無い。 |
| sound-design-skill | `status: scaffold`（:67）。`engines` は ACE-Step 1.5 だけ。role「BGM and sound-effect generation」、`owns` は BGM生成・効果音 | EzAudio（SFX）が抜けている。library モード、ライセンス記録、loop-bed、stinger、seam-check、sfx-cues は `owns` にも role にも無い。 |
| transcription-skill | `engines` は faster-whisper だけ、role「local faster-whisper」。`owns` に 文字起こしの語句検索 | エンジンは 5 つ。語句検索は未実装（G1）。 |
| diarization-skill | `status: active`, `optional` | repo 自身の `ECOSYSTEM_ROADMAP.md` は status `scaffold` と書いている（古い）。ASSIGN と名前の提案 (`enroll` / `name`) は `owns`（話者識別のみ）に明記なし。 |
| detection-skill | `owns`: 顔検出・文字検出(OCR)・物体検出。`engines` 3 つ | ショット検出、reframe の経路、アクティブスピーカー、個人情報の検出、顔フレームの順位付けは `owns` に無い。任意エンジン PP-OCRv6 / RF-DETR / PySceneDetect / TransNetV2 が `engines` に無い。 |
| slide-sync-skill | role「Slide import, slide-change detection, slide text」。`owns` 2 つ | 「slide text」は PDF のテキスト層だけで OCR ではない。`chapters`, `match`, `insert`, `layout`, `clean` は `owns` に無い。`layout` / `clean` は映像を書き出す（ffmpeg-skill `overlay` / `broll` / `insert`）。 |
| audio-production-skill | `owns` 5 つ | LOUDNESS_SET は「音量・ラウドネス」に入るが、STEMS（ステム納品）は `owns` に名前が無い。 |

## Velisa 文書との食い違い

| 場所 | 書いてあること | 実際 |
|---|---|---|
| `docs/ecosystem/ROADMAP.md:16` | voice-enhance, dubbing, sound-design は「0.1.0」 | dubbing 0.2.1、sound-design 0.3.2（voice-enhance は 0.1.0 のまま）。 |
| `docs/ecosystem/ROADMAP.md:433` | status の食い違いは「Velisa #132 が編集中なので変えない」 | 今も `scaffold` のまま。#132 は open PR 一覧に無い（マージ済みか閉じたかは未確認）。 |
| `README.md:185-188` | ecosystem.json の `scaffold` は「空のリポジトリ」 | 3 つとも空ではない。 |
| `docs/CAPABILITY_MATRIX.md` 全体 | 音は audio-production、認識は transcription だけを載せている | `voice.*`, `speech.*`, `audio.bgm_generate` ほか, `vision.*`, `slides.*` の行が 1 つも無い（grep 0 件）。`audio.filler_remove` の行も無い。 |
| `docs/CAPABILITY_MATRIX.md:288` | 「15 audio capabilities」 | 契約は 18 id（`contract.py:25-31`）。同じ文書の表は 17 行。 |
| `docs/CAPABILITY_MATRIX.md:68, 250` | `audio.silence_remove` は ffmpeg-skill `silence` を使う | 実際は `cut`（`executor.py:51`）。 |
| `docs/CAPABILITY_MATRIX.md:77` | NOISE_REDUCTION `strength_db` 10〜19 が通る既知の不具合 | ADR-17 で 20〜60 に直っている（`docs/decisions.md:123`）。 |
| `docs/CAPABILITY_MATRIX.md:155, 294` | transcription は faster-whisper だけ、`speaker_id` は常に null | エンジン 5 つ。`transcription/speakers` が `speaker_id` を埋める。 |
| `docs/REPOSITORY_MAP.md:35, 42` | audio-production 0.1.0、transcription 0.2.0 | 1.2.0、0.11.4。 |
| `docs/ecosystem/CROSS_REPO_STATUS.md:8-22` | 名簿は 12 repo | 私の担当 8 つのうち 6 つ（voice-enhance, dubbing, sound-design, diarization, detection, slide-sync）が載っていない。 |
| 各 repo の `ECOSYSTEM_ROADMAP.md` | audio-production「v0.4.8」、transcription「0.11.0」、detection「0.2.0」、dubbing「0.1.0」 | 1.2.0、0.11.4、0.2.2、0.2.1。dubbing の表の「nobody translates today」も古い（subtitle-skill `translate` がある）。 |
| agent の pin | sound-design `contract_0.3.0.json`、transcription `contract_0.11.3.json` | repo は 0.3.2、0.11.4。 |

## 進行中の作業

- 担当の 8 repo には open PR も open issue も無い（`gh api .../pulls`, `.../issues` とも 0 件）。
- ffmpeg-skill: #420 / #477 マルチトラック音声（G9）、#449 語の時刻でのカット（D7 に関係）、#476 `audio.py --limit` の遅延、#478 `audio.py` の pad/trim の丸め、監査 #459（audio, scenes, waveform）, #462（silence）, #464（loudness）、PR #484。
- Velisa: #36（`ffmpeg-skill.scenes` と `media-analysis.scene_detection` の衝突、D12）、#35（CAPABILITY_MATRIX が古い）、#38（tag / release / CI が無い repo、6 つが該当）。
- video-production-agent: PR #105（handoff に `/plugin install` を出す）。音・認識の重複を直す PR は無い。
- qc-skill: PR #28（roadmap）、issue #7。subtitle-skill: issue #37。

## 選択肢

各行の 5 項目: agent 配線 / ffmpeg-skill への依頼 / 依存 / ライセンス / 決定性。★ が推奨。

### D1 ラウドネス正規化の二重経路

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 所有は audio-production、ffmpeg-skill は「エンジン」と明記。映像の経路も audio-production を通す（音を NORMALIZE して `audio_mux`） | `loudness_normalization` の候補を `audio_normalize` + `audio_mux` に寄せる。pin は 1.2.0 のまま | 依頼なし | 増えない | 自前 MIT のみ | 許容差で再計測するので保証が強くなる。映像は stream copy のまま |
| B 現状維持を文書化（映像 = ffmpeg-skill 直、音 = audio-production） | 変更なし。CAPABILITY_MATRIX に 2 経路を書く | なし | なし | なし | 映像の経路は許容差の検証が無いまま |
| C LOUDNESS_SET を ffmpeg-skill `--versions` に任せ、audio-production から外す | SkillSpec を作り直す | 提案 9（#421）で実装済みの機能を使う | なし | なし | audio-production の「上限を超えない」検証を失う |

### D5 / D6 / D7 無音とフィラー

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 「測る = media-analysis、決める = agent、切る = audio-production（音）/ ffmpeg-skill cut（映像）」を明文化。ffmpeg-skill `silence --filler` と `--transcribe` は単体利用者向けの近道とし、agent は使わない | `silence_analysis` の第 1 候補を media-analysis にする。ほかは今のまま | 依頼なし。フィラー辞書が 2 つあることだけ文書化 | なし | なし | 範囲と辞書が計画に残るので再現できる |
| B フィラー辞書を 1 つにする（audio-production の preset を ffmpeg-skill の内蔵リストに合わせる、または逆） | audio-production の契約 pin を更新 | 新規の依頼になる（ffmpeg-skill は「完成」扱い） | なし | なし | 同じ入力で両者の結果が揃う |
| C フィラー除去を ffmpeg-skill `silence --filler --words` に寄せる | `audio_filler_remove` を付け替え | #449 に乗る | なし | なし | 「なんか」など内容語を既定で切る危険が入る |

### D8 / D9 音声認識と発話区間

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 発話区間の持ち主は media-analysis `speech_regions`。transcription は入力として受けるだけ（既にそう）。agent が長尺のとき `speech_regions` → `transcribe(speech_regions=...)` を計画 | SkillSpec `speech_region_analysis` を足す。pin は media-analysis 0.1.16、transcription 0.11.x | なし（`scenes --speech` は代用値のまま） | onnxruntime + numpy（extra `vad`）、GPU 不要 | silero-vad は MIT（コード・重み、`models/silero_vad.LICENSE`） | モデル推論だが CPU の ONNX で固定。重みの sha を来歴に |
| B 今のまま（agent は計画しない） | なし | なし | なし | なし | 長尺の切れ目が音量だけで決まる |
| C VAD を transcription-skill の中に持つ | transcription の契約変更 | なし | 同じ | 同じ | 「計測は media-analysis」の線が崩れる |

### D10 話者 id の付与が 2 実装

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 規則の持ち主は diarization-skill（turns スキーマと ASSIGN 規則）、transcription の merge は「同じ規則の写し」と両方の契約に書き、適合テストを共有する | 変更なし（agent は transcription の merge を使い続ける） | なし | なし | なし | 両実装が同じ結果になることをテストで保証 |
| B `diarization/assign` を廃止し transcription だけに | diarization の契約から `speech.assign_speakers` を外す（破壊的） | なし | なし | なし | 実装が 1 つになる |
| C transcription の merge を廃止し agent が `diarization/assign` を呼ぶ | adapter と ADR-096 を作り直す | なし | なし | なし | 同上。手戻りが大きい |

### D12 カット・ショット・スライド切替

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 3 層を明記: 速い一覧 = ffmpeg-skill `scenes`、観測 = media-analysis `scene_detection`、フレーム精度のショット表 = detection `shots`、スライド = slide-sync `detect`。`owns` に「ショット検出」を detection へ足す | `detection/shots` の SkillSpec を足す（編集ビュー用）。pin 0.2.2 | なし（Velisa #36 を「衝突ではなく層」として閉じる） | PySceneDetect（BSD-3-Clause、重みなし）。TransNetV2 は任意 | TransNetV2 は MIT、重みは同じ LICENSE、学習データの条件は未確認 | 既定エンジンは重みなしで決定的 |
| B media-analysis `scene_detection` を廃止 | `scene_analysis` を付け替え | なし | なし | なし | 観測の kind が 1 つ減る。`edit_style` が内部で使うので難しい |
| C 現状維持 | なし | なし | なし | なし | 変わらない |

### D13 画面の文字（OCR）

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A OCR は detection-skill だけ。agent に `detection/text` を配線し、diarization `name` と transcription の語彙（G6）へ渡す | `visual_detection` handoff を `text_detection` SkillSpec に置き換える | なし | Tesseract 5 バイナリ + tessdata（GPU 不要） | Tesseract / tessdata_best は Apache-2.0。PP-OCRv6 は Apache-2.0 | Tesseract は決定的。モデルの sha を記録 |
| B slide-sync に OCR を持たせる | slide-sync の契約変更 | なし | OCR が 2 か所になる | 同じ | 境界（slide-sync「Slide text OCR comes from detection-skill」）に反する |

### D16 / 9(g) ライセンス台帳

| 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|
| ★A 素材の種類ごとに「記録」を持つ（音 = sound-design、映像・画像 = asset-library）。レコードの形（licence, author, source URL, attribution line, sha256, content_id）を 1 つの共通スキーマにし、プロジェクトの台帳（クレジット作成）は asset-library が両方を読んで作る。検査は artifacts-skill | `bgm_library` はそのまま。台帳の SkillSpec を 1 つ足す | なし | ネットワークは asset-library の取得だけ。sound-design は今のとおりオフライン | 自前 MIT。素材ごとの条件はレコードに | 記録は申告どおりで `verified: false`（sound-design ADR-014）。同じ入力で同じ台帳 |
| B 台帳をすべて asset-library に移す | `bgm_library` を付け替え。sound-design の契約から library を外す（破壊的） | なし | sound-design の「実行時ネットワークなし」の規則を asset-library が破る形になる | 同じ | 実装済みの記録とテストを捨てる |
| C 台帳をすべて sound-design に寄せる | asset-library を作らない | なし | なし | 同じ | 映像素材が `owns`（BGM生成・効果音）と合わない |

### G1 語句検索 / G2 音楽分離 / G7-G8 ffmpeg-skill 待ち

| 項目 | 案 | agent 配線 | ffmpeg-skill | 依存 | ライセンス | 決定性 |
|---|---|---|---|---|---|---|
| G1 | ★A transcription-skill に `transcription/find` を足す（WORK_QUEUE の決定どおり） | SkillSpec 1 つ、pin 更新 | なし | なし（標準ライブラリ） | MIT | 文書への決定的な問い合わせ |
| G1 | B `owns` から外し、routing skill の手順書のままにする | なし | なし | なし | なし | 手作業 |
| G2 | ★A 「持ち主なし」と明記し、voice-enhance の `not_provided` の「(sound-design-skill)」を直す。必要になったら ADR から | なし | なし | なし | Demucs は重みの学習データが不明（voice-enhance ADR-001） | — |
| G2 | B sound-design か voice-enhance に SEPARATE op を足す | SkillSpec 追加 | なし | PyTorch + 重み | 重みの licence 確認が先 | 推論、seed 固定が要る |
| G7/G8 | ★A ffmpeg-skill に issue を立てる（提案 3, 4。今は対応する open issue が見当たらない） | dubbing / voice-enhance は能力検出なので pin 変更だけ | 提案 3（音だけの tempo / pad）、提案 4（`audio --sample-rate`, `--channel`） | なし | なし | tempo > 1.0 の吹替と 48 kHz 以外の ISOLATE が可能になる |
| G7/G8 | B 各スキルが自前で ffmpeg を呼ぶ | なし | なし | なし | なし | 「メディア処理は ffmpeg-skill だけ」の規則（各 ADR）に反する |

## 追加の質問

### (a) ラウドネス・正規化・ミックス・ダッキング

| 仕事 | 持ち主（実装） | エンジン | 計測 |
|---|---|---|---|
| 正規化 | audio-production `NORMALIZE` / `LOUDNESS_SET` | ffmpeg-skill `loudness` | 自分の出力だけ再計測 |
| ミックス・ダッキング | audio-production `MIX` + `duck`, `STEMS` | ffmpeg-skill `audio --music --duck` | — |
| 判断用の計測 | media-analysis `loudness`（観測） | ffmpeg 直 | — |
| 合否 | qc-skill `audio.integrated_loudness_within_tolerance` ほか | ffmpeg 直 | — |

agent の経路: 計測は `loudness_analysis`（ffmpeg-skill → media-analysis の順）。正規化は映像なら `ffmpeg-skill/loudness`（AUTO）、`audio.production=true` の音の経路なら `audio-production/run`（CONFIRM）。ミックスは audio-production だけ。qc は最後の関門。**食い違い**: 同じ「正規化」が映像と音で別のスキルに行く（D1）。

### (b) ノイズ低減と声の整音

コード上の線ははっきりしている。
- audio-production: `NOISE_REDUCTION mode` は `fft` だけ（`model.py:183`）、`VOICE_CLEANUP` は ffmpeg-skill `--voice` の固定チェーン（ADR-16）。重みなし、決定的。
- voice-enhance: `not_provided` の 1 行目が「traditional (non-AI) noise reduction ... (audio-production-skill)」（`contract.py:125`）。逆に audio-production の roadmap も「clean split」と書く。
- ffmpeg-skill `audio --denoise` は audio-production の下のエンジン。`denoise.py` は映像専用。
- agent は順序まで決めている: bleed → dereverb → isolate → (concat | mix) → voice clean-up → noise reduction（`agent/voice.py` 冒頭）。
- 残る曖昧さは 1 点: voice-enhance が音楽分離を sound-design の仕事と書いているが、sound-design には無い（G2）。

### (c) 無音・フィラー・発話区間

| 手段 | 何を測る / 切るか | 入力 | agent が使うか |
|---|---|---|---|
| media-analysis `silence` | 無音区間（先頭・内部・末尾） | 音量の閾値 | 使う（第 2 候補） |
| ffmpeg-skill `silence --list` | 無音区間 | 同上 | 使う（第 1 候補） |
| ffmpeg-skill `silence`（削除） | 検出して切る | 自分の既定値 | 使わない |
| ffmpeg-skill `silence --filler` | フィラーを切る | `--words` か `--transcribe`、内蔵リスト | 使わない |
| ffmpeg-skill `scenes --speech` | 発話らしさの代用値 | ゼロ交差率 | 使わない |
| media-analysis `speech_regions` (0.1.16) | 発話区間 | silero-vad | 計画しない（pin には入っている） |
| transcription の語の時刻 | 語ごとの開始・終了 | ASR | FILLER_REMOVE の入力として使う |
| audio-production `SILENCE_REMOVE` / `CUT` / `FILLER_REMOVE` | 渡された範囲・語を切る | 呼び出し側 | 音の経路で使う |
| agent の silence cleanup | 先頭・末尾は AUTO で切る。内部は CONFIRM | 上の観測 | `ffmpeg-skill/cut`（映像）か `audio_cut`（音） |

### (d) 話者を特定するのは誰か

- 「誰がいつ話したか」（匿名 `SPEAKER_nn`）: diarization-skill だけ。
- 「その人は誰か」: diarization `name` が名簿の中から提案するだけ。確定は人。detection は「顔の箱は身元ではない」と断る（`contract.py:174`）。
- 文字起こしへの付与: 実装が 2 つ（D10）。agent は transcription 側を使う。
- transcription `--per-channel`（マイクごとに話者を決める）は未着手（G3）。入れば「マイクがきれいなら diarization 不要」になるので、そのとき `speaker_id` の出どころを来歴に書く必要がある。
- detection `speakers` は「画面のどの顔が話しているか」で、マルチカムの切替用。話者 id は diarization の turns を渡したときだけ載る。

### (e) 画面の文字を読むのは誰か

- 読む: detection `text` だけ（Tesseract、任意で PP-OCRv6）。
- slide-sync: `import` は資料ファイルのテキスト層、`detect` は絵の切り替わり、`match` は絵の相関。OCR はしないと契約に書いてある。
- media-analysis `scene_detection` と ffmpeg-skill `scenes` は切り替わりの時刻だけ。文字は読まない。
- 配線: `detection/text` は agent では handoff のまま。slide-sync roadmap も「stepcap and slide-sync not wired yet」。

### (f) 話すスキルと翻訳

- 話す（TTS）のは dubbing-skill だけ。ほかのローカル repo に TTS エンジンは無い（grep の一致は TTML など別の語）。Velisa ROADMAP も「TTS narration: dubbing-skill NARRATE」と決めている（`ROADMAP.md:381`）。
- エンジン: Chatterbox（既定）、VOICEVOX（日本語、クレジット必須）、Style-Bert-VITS2（AGPL、別プロセス）、Kokoro-82M（日本語は弱い）、qwen3_tts（実験的、同意済みの参照音声でのみ、既定にしない、ADR-018）。
- 翻訳: subtitle-skill `translate` が持つ（argos が既定、OPUS-MT も、`subtitle-skill@da597e5:src/subtitle_skill/contract.py:148-164`）。dubbing は訳した cue を受け取るだけ（ADR-003）。持ち主の決定（2026-10-30）と一致。吹替向けの「短く訳し直す」は dubbing `fit --rate` が文字数・モーラの予算を返し、呼び出し側が `translate` に頼み直す（ADR-014）。

### (g) 音楽・効果音とライセンス台帳

- sound-design が今持っているもの: BGM 生成、SFX 生成、利用者の音素材の取り込みとライセンス記録、選曲、ループ、スティンガー、効果音の cue 表。取得（ダウンロード）はしない。
- asset-library 候補の草案は「music and sound effects stay with sound-design-skill (library mode)」と既に線を引いている（`ROADMAP.md:367`）。
- 推奨は上の D16 の A: 記録は素材の種類ごと、レコードの形は共通、プロジェクトの台帳は asset-library、検査は artifacts-skill。

### (h) `scaffold` の 3 つが実際に出しているもの

| repo | version | tag / release | 動く op | エンジン | テスト | agent |
|---|---|---|---|---|---|---|
| voice-enhance-skill | 0.1.0（CHANGELOG は `0.1.0 - unreleased`） | なし | `isolate`, `dereverb`, `bleed-reduce`, `remux`（すべて実装済み、`EXPERIMENTAL`） | deepfilternet（deep-filter 0.5.6 + DeepFilterNet3 ONNX）、nara_wpe 0.0.11、crosstalk（自前） | `def test_` 149 件。CI: unit（3 OS × Py 3.9/3.12）、integration、engines（実エンジン。合成素材で ISOLATE SNR 0 → 18.2 dB、DEREVERB SRR -0.8 → 19.0 dB） | 配線済み `voice_isolate` / `voice_dereverb` / `voice_bleed_reduce`、pin 0.1.0 |
| dubbing-skill | 0.2.1（CHANGELOG は 3 版とも `unreleased`） | なし | `narrate`, `dub`, `describe`, `fit`, `terms`, `watermark`（`EXPERIMENTAL`） | chatterbox, voicevox, style_bert_vits2, kokoro, qwen3_tts（実験的） | 310 件。CI: unit、integration、engines（実 Chatterbox）、voicevox（実 VOICEVOX 0.26.0）、手動 heavy-tests（Qwen3 0.6B を CPU で） | `speech_dub` だけ配線、pin 0.2.1。narrate / describe は handoff |
| sound-design-skill | 0.3.2（CHANGELOG は全版 `unreleased`） | なし | `generate-bgm`, `generate-sfx`, `library-import/index/pick`, `loop-bed`, `stinger`, `seam-check`, `sfx-cues`（`EXPERIMENTAL`） | acestep（ACE-Step 1.5、XL turbo は opt-in）、ezaudio | 227 件。CI: unit、integration（実 ffmpeg-skill と qc-skill）。実 ACE-Step / EzAudio での計測は無い（repo が明記） | `bgm_library`, `bgm_generate` 配線、pin 0.3.0（repo は 0.3.2）。効果音は未配線 |

3 つとも「空」ではなく、動く op と CI を持つ。足りないのは tag / release と、実収録・実エンジンでの計測。`scaffold` を直すなら、ほかの `EXPERIMENTAL` なスキル（diarization, detection は `active` + `optional`）と同じ扱いが揃う。

### (i) エンジンと重みのライセンス（各 repo の ADR / コードの記載）

| skill | エンジン・モデル | コード | 重み | 注意 |
|---|---|---|---|---|
| voice-enhance | DeepFilterNet3 (`deep-filter`) | MIT OR Apache-2.0 | MIT OR Apache-2.0（同じ repo のファイル。重み単独の表記は無い、ADR-001） | — |
| voice-enhance | nara_wpe | MIT | 重みなし | — |
| voice-enhance | crosstalk | MIT（自前） | 重みなし | — |
| dubbing | Chatterbox Multilingual | MIT | MIT（HF model card） | 日本語の経路が pykakasi（GPL-3.0-or-later）に依存。別 venv で実行。全出力に Perth 透かし |
| dubbing | VOICEVOX | ENGINE LGPL-3.0、CORE MIT | OSS ではない。声ライブラリごとの規約。ずんだもん・四国めたんは商用可でクレジット必須 | **商用に条件あり**（クレジット、政治・宗教・情報商材は禁止）。**ほかのキャラクターは 未確認**（ADR-001） |
| dubbing | Style-Bert-VITS2 | AGPL-3.0（user_dict は LGPL-3.0） | モデルごと。JP-Extra base は AGPL-3.0、JVNV 声は CC BY-SA 4.0、BERT は CC BY-SA 4.0 | **CC BY-SA が生成音声に及ぶかは 未確認**（ADR-001）。import せず別サーバ |
| dubbing | Kokoro-82M | Apache-2.0 | Apache-2.0 | 日本語の一部の声は CC BY のクレジット。misaki[ja] が入れる UniDic 辞書は **未確認** |
| dubbing | Qwen3-TTS 12Hz Base 1.7B / 0.6B | Apache-2.0 | Apache-2.0（revision 固定） | 実験的。透かしなし。品質は聴取で未評価 |
| sound-design | ACE-Step 1.5（turbo、XL turbo） | MIT | MIT（HF card）。テキストエンコーダ Qwen3-Embedding-0.6B は Apache-2.0 | 出力の商用利用は model card の記載。学習データは提供元の主張で **未確認**。LM の元になる Qwen3 base の licence は **未確認**（LM は使わない設定） |
| sound-design | EzAudio (`s3_xl`) | MIT | MIT。flan-t5-xl は Apache-2.0 | 出力についての記載なし。学習データは AudioSet / VGGSound / AudioCaps（YouTube 由来）。実行前に承認フラグが必須（ADR-007） |
| transcription | faster-whisper + Whisper 重み（tiny〜large-v3 ほか） | — | **未確認**（repo の ADR / docs に既定重みの licence 記載が見つからない。`distil-large-v3.5` だけ MIT と記載、`engines/faster_whisper.py:32`） | faster-whisper 自体のコード licence も repo 内に記載なし |
| transcription | Haas-ja-v1.0 | haas-asr（記載なし、未確認） | Apache-2.0（ADR-033、`docs/engines.md:336`） | Linux + NVIDIA GPU のみ |
| transcription | speech.cpp + reazonspeech-v2 / haas / qwen3-asr | MIT（speech.cpp） | Apache-2.0 | — |
| transcription | speech.cpp + parakeet-tdt_ctc-0.6b-ja / parakeet-tdt-0.6b-v3 | MIT | **CC-BY-4.0**（帰属表示が必要、記録済み） | 学習データの licence は評価していない（`docs/engines.md:341`） |
| transcription | whisperX + wav2vec2（en, ja） | BSD-2-Clause | Apache-2.0。同梱 VAD は MIT | NLTK `punkt_tab` は licence 記載なしで **未評価** |
| transcription | Qwen3-ASR-1.7B + ForcedAligner-0.6B | Apache-2.0（qwen-asr） | Apache-2.0（revision 固定） | — |
| diarization | pyannote.audio 4.x + speaker-diarization-community-1 | MIT（`pyannote_engine.py:23`） | **CC-BY-4.0**（ゲート付き、帰属表示が必要） | 利用条件への同意が一度必要 |
| detection | YuNet | MIT | MIT | — |
| detection | Tesseract 5 + tessdata_best | Apache-2.0 | Apache-2.0 | — |
| detection | YOLOX | Apache-2.0 | Apache-2.0（契約の記載） | — |
| detection | PySceneDetect | BSD-3-Clause | 重みなし | — |
| detection | TransNetV2 | MIT | 同じ LICENSE（重み単独の表記なし） | 学習データ（ClipShots, IACC.3）の条件は **未確認**（ADR-003） |
| detection | PP-OCRv6 | Apache-2.0 | Apache-2.0 | 未計測 |
| detection | RF-DETR Small / Medium | Apache-2.0 | Apache-2.0（Nano〜Large のみ。ほかのサイズは Roboflow PML 1.0 で対象外） | ONNX 書き出しに一度だけ PyTorch |
| slide-sync | pypdfium2 / LibreOffice | Apache-2.0 OR BSD-3-Clause / MPL-2.0 | 重みなし | PyMuPDF (AGPL)、Poppler (GPL) は不採用 |
| media-analysis | silero-vad | MIT | MIT（パッケージに同梱） | — |

商用利用を「禁じる」重みは登録されていない（NC のものは各 ADR で不採用）。条件つきは VOICEVOX（クレジットと用途の禁止事項）、CC-BY-4.0 の 3 つ（parakeet 2 種、pyannote community-1）、CC BY-SA の Style-Bert-VITS2 声。
