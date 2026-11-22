# 英語（と主要な国際言語）を既定にしたときのエンジン選定調査（2026-11）

調査日: 2026-11-21。調査のみで、コードは変えていない。対象は transcription-skill / diarization-skill / voice-enhance-skill / dubbing-skill / subtitle-skill（字幕翻訳）の 5 つ。

## 0. 前提と調べ方

- **判断の基準**（依頼どおり）
  - ローカル・オフラインで動くこと（モデルの取得は初回だけ）。
  - コードと重みの両方が商用利用を許す、寛容なライセンスであること。
  - ノート PC の CPU で動くこと（GPU は任意）。
  - モデルのサイズが手頃であること（ディスクに余裕がない前提）。
  - 2026 年後半の時点で保守が続いていること。
- **現状の読み取り元**: 各リポジトリの README・SKILL.md・ADR（`docs/decisions.md`、`docs/adr/`）とエンジン実装（`src/*/engines/`）、および `/home/user/AI-video-production-OS/ecosystem.json`。
- **外部の事実の出典**
  - ライセンス・更新日・ファイルサイズ: Hugging Face のモデル API（`https://huggingface.co/api/models/<id>`。`cardData.license`、`lastModified`、`siblings[].size`）。
  - 最新版と公開日: PyPI の JSON API（`https://pypi.org/pypi/<pkg>/json`。最新ファイルの `upload_time`）。
  - 性能: モデルカードと各プロジェクトの README・ドキュメント。
  - 引用した数値は、断りがない限り**ベンダー自身の測定**で、ここでは再現していない。
- **制約**
  - この環境からは GitHub の API・atom フィードにアクセスできなかった（403）。そのため GitHub のリリース日は、WebFetch で読めたページと PyPI の公開日で代用した。
  - Open ASR Leaderboard の結果データセット（`hf-audio/open-asr-leaderboard-results`）は認証なしでは読めなかった。そのため WER はモデルカードの値を使った。
- **「未確認」の意味**: 一次資料で確かめられなかった事実には **未確認** と書いた。

---

## 1. 結論の一覧

> **オーナーの決定（2026-11-21）: 既定は変えない。** 下の表の「推奨する既定」は、測定してから検討する**候補**であり、今は採用しない。当面は「推奨する既定」と「推奨する opt-in」の列のエンジンをすべて opt-in として追加し、既定（transcription の `base`、dubbing の Chatterbox、subtitle の Argos）はそのまま残す。既定を切り替えるかは、実際の素材で同じ機械で測り比べたあとに、オーナーが改めて決める。

| スキル | いまの既定（英語のとき） | 推奨する既定 | 推奨する opt-in | 主な理由 |
|---|---|---|---|---|
| transcription-skill | `faster_whisper` / `base` | **`faster_whisper` / `large-v3-turbo`**（既定モデルを変える） | `speechcpp` / `parakeet-tdt-0.6b-v3:q8_0`（英語と欧州言語の高速経路）、Moonshine（英語・軽量、後日） | `base` は精度が足りない。turbo は MIT で 99 言語、言語検出あり。Parakeet は CPU で最速級だが帰属表示が要り、言語も必須 |
| diarization-skill | pyannote community-1 | **据え置き** | sherpa-onnx（PyTorch なしの軽量経路。埋め込みモデルのライセンス確認が前提） | 言語に依存しない。4.1.1 が 2026-11-19 に出ており保守は活発。Python 3.11 以上が必要になった点だけ直す |
| voice-enhance-skill | DeepFilterNet3 / nara_wpe | **据え置き** | DPDFNet（Apache-2.0、ONNX、48 kHz） | DFN3 はライセンスが明確で動くが、2024-10 以降コードが更新されていない。後継候補を測定してから入れ替えを判断する |
| dubbing-skill | Chatterbox Multilingual | **Kokoro-82M**（英語のナレーション・音声解説。プリセット声） | Pocket TTS（声の複製、同意必須）、Qwen3-TTS 0.6B CustomVoice（プリセット声・10 言語）。Chatterbox は「凍結した旧エンジン」へ格下げ | **Chatterbox は 2026 年 8 月に「保守終了」と宣言された** |
| subtitle-skill（翻訳） | Argos | **OPUS-MT（tc-big 系、CC-BY-4.0）**。英語↔主要言語のペアで | Ollama の既定モデルを `qwen3:8b` から `qwen3.5:9b` へ（ディスクが厳しければ `qwen3.5:4b`）、Gemma 4 E4B | Argos の重みライセンスは今も未記載。英語起点の OPUS-MT は多数のペアでライセンスが明記されている |

日本語専用のエンジン（`haas_ja`、`speechcpp` の `reazonspeech-v2`、VOICEVOX、Style-Bert-VITS2）は、すべて **opt-in のまま残す**。既定を変える候補の 3 件（transcription の既定モデル、dubbing の既定エンジン、subtitle の既定エンジン）は、どれも既存の呼び出し側の出力を変える。上の決定により今は切り替えない。将来切り替える場合は、各リポジトリで ADR を書き、video-production-agent の再ピン留めが必要になる（ADR-004 の決定 11、dubbing ADR-001 と同じ扱い）。

---

## 2. transcription-skill

### 2.1 いま組み込まれているもの

出典: `/home/user/transcription-skill/docs/engines.md`、`docs/decisions.md`（ADR-033/035/038/040/041）

| エンジン | 既定モデル | 英語 | 備考 |
|---|---|---|---|
| `faster_whisper`（Reference Local Engine） | `base` | 対応（100 言語） | CPU・int8。許可リストには `large-v3`、`large-v3-turbo`、`distil-large-v3.5`（英語専用）がある |
| `whisperx` | `large-v3` | 対応（wav2vec2 で単語を整列） | 英語の整列モデルは `facebook/wav2vec2-base-960h`（Apache-2.0） |
| `qwen3_asr` | Qwen3-ASR-1.7B + ForcedAligner-0.6B | 対応（整列は 11 言語） | 重みは約 6.5 GB。CPU 速度は「不明」とドキュメントにある |
| `speechcpp` | `reazonspeech-v2`（**日本語のみ**） | `parakeet-tdt-0.6b-v3` か `qwen3-asr-*` を指定したときだけ | 言語の指定が必須（検出なし） |
| `haas_ja` | Haas-ja-v1.0 | 非対応 | Linux・NVIDIA GPU 専用 |

### 2.2 英語での弱点

- **既定の `base` は小さすぎる。** engines.md 自身が `base` での同音語の誤りを挙げ、「大きいモデルほど誤りが減る」と書いている。英語の WER を本調査では測っていないため、数値は **未確認**。
- **faster-whisper の PyPI での最新版は 1.2.1（2025-10-31）。** 約 1 年、リリースが出ていない（[PyPI](https://pypi.org/project/faster-whisper/)）。ただし `master` には 2026-11-12 までコミットが続いている（[commits](https://github.com/SYSTRAN/faster-whisper/commits/master)）。保守が止まったわけではなく、リリースの間隔が空いている状態。
- **`speechcpp` の既定は日本語専用。** `--engine speechcpp` に英語を渡すと、モデルを指定しない限り断られる。
- **`distil-large-v3.5` が Open ASR Leaderboard から外れた。** 2026-11-20 の版（1.16.2）の変更履歴に「Remove ... distil-whisper/distil-large-v3.5」とある（[init.py](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard/blob/main/init.py)）。外れた理由は書かれていない（**未確認**）。
- **`qwen3_asr` は重い。** 重みが約 6.5 GB あり、CPU での速度は測られていない（engines.md）。ディスクに余裕がない前提には合わない。

### 2.3 候補

| 候補 | ライセンス | サイズ | 英語の精度 | CPU 速度 | 最新リリース | 出典 |
|---|---|---|---|---|---|---|
| **Whisper large-v3-turbo**（faster-whisper の `large-v3-turbo`） | MIT（重み） | 809M パラメータ。CT2 の `model.bin` は 1.62 GB | 短い音声の平均 WER 7.25（large-v3 は 7.14）。長い音声は 8.82（distil-large-v3.5 は 10.04）。いずれも distil-large-v3.5 のカードにある比較表の値 | turbo そのものの CPU 実時間比は **未確認**。参考として、faster-whisper README では `small` を int8・8 スレッド（i7-12700K）で動かすと 13 分の音声が 1 分 42 秒（実時間比 約 0.13） | faster-whisper 1.2.1（2025-10-31）。CT2 の重みの最終更新は 2025-11-05 | [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)、[distil-large-v3.5 のカード](https://huggingface.co/distil-whisper/distil-large-v3.5)、[faster-whisper README](https://github.com/SYSTRAN/faster-whisper#benchmark)、[CT2 の重み](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo) |
| **NVIDIA parakeet-tdt-0.6b-v3** | CC-BY-4.0（帰属表示が必要。商用可） | 600M。`.nemo` は 2.51 GB。GGUF は q8_0 が 0.67 GB、q4_k が 0.36 GB。sherpa-onnx の int8 エンコーダは 622 MB | Open ASR の英語平均 WER 6.34%（LS-clean 1.93、AMI 11.31）。25 の欧州言語に対応。句読点と大文字小文字を出し、単語のタイムスタンプも出る | onnx-asr: Ryzen 9800X3D の CPU で RTFx 36。sherpa-onnx int8・2 スレッド: RTF 0.325（短い音声）、0.028（VAD を使う長い音声） | モデルの更新 2026-08-05。sherpa-onnx 2.0.2（2026-11-19）。onnx-asr 0.12.0（2026-07-15） | [モデルカード](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)、[onnx-asr](https://pypi.org/project/onnx-asr/)、[sherpa-onnx の NeMo transducer](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/nemo-transducer-models.html)、[PyPI sherpa-onnx](https://pypi.org/project/sherpa-onnx/) |
| **Moonshine Streaming Medium** | MIT（コードと重み。ただし英語以外の旧型非ストリーミングモデルは非商用の Community License） | 245M。safetensors（fp32）は 1.06 GB | 英語専用。Open ASR 系の平均 WER 6.65 | CPU の測定値は公開されていない（**未確認**）。設計目標は 0.1〜1 TOPS、メモリ 1 GB 未満 | moonshine-voice 0.1.6（2026-11-06） | [モデルカード](https://huggingface.co/moonshine-ai/moonshine-streaming-medium)、[LICENSE](https://github.com/moonshine-ai/moonshine/blob/main/LICENSE)、[PyPI](https://pypi.org/project/moonshine-voice/) |
| **Qwen3-ASR-0.6B**（`speechcpp` 経由、または `qwen3_asr` の小型版） | Apache-2.0 | 0.6B（HF のメタデータでは 0.9B）。`speechcpp` 経由のファイルサイズは **未確認** | Open ASR 平均 WER 6.42。30 言語。LS-clean 2.11 / other 4.55 | RTFx 166.23 は Leaderboard の値で、測定条件（GPU）は **未確認**。CPU の値は **未確認** | qwen-asr 0.0.6（2026-01-30） | [モデルカード](https://huggingface.co/Qwen/Qwen3-ASR-0.6B)、[PyPI qwen-asr](https://pypi.org/project/qwen-asr/) |

候補から外したもの（いずれも重みは商用可。外した理由は運用面）:

- [canary-1b-v2](https://huggingface.co/nvidia/canary-1b-v2)（CC-BY-4.0、約 1B）: onnx-asr の CPU RTFx は 8 で、Parakeet より遅い。
- [canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b)（CC-BY-4.0、2.56B）: サイズが大きい。
- [kyutai/stt-1b-en_fr](https://huggingface.co/kyutai/stt-1b-en_fr)（CC-BY-4.0、約 1B、英仏のみ）: 対応言語が少ない。
- [nemotron-speech-streaming-en-0.6b](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b): NVIDIA Open Model License で、CC や OSI のライセンスではない。

### 2.4 推奨

1. **新しい既定**: `faster_whisper` の `default_model` を `base` から **`large-v3-turbo`** に変える。
   - エンジンは変えず、pip extra のまま動く。重みのライセンスは MIT。MIT は出力（文字起こし）ごとのクレジットを求めないが、重みそのものやその主要部分を複製・再配布するときは、著作権表示と許諾表示を残す必要がある。
   - 99 言語に対応し、言語検出もある。既定に求められる「言語が分からない入力」を受けられる。
   - ディスクは 1.6 GB 必要になる。これが厳しい環境向けに、doctor で `small`（`model.bin` 484 MB、[Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small)）を勧める道を残す。
   - 既定が変わるとキャッシュキーと出力が変わる。そのため ADR を書き、agent を再ピン留めする。
2. **推奨 opt-in**: `speechcpp` の `parakeet-tdt-0.6b-v3:q8_0`。
   - 英語と欧州言語では、CPU 速度・句読点・単語の時刻のどれをとっても最有力。
   - 言語の指定が必須で、CC-BY の帰属表示（ADR-040 で記録済み）も要る。このため既定にはせず、「英語・欧州言語の高速経路」として案内する。
   - speech.cpp は v0.11.2 が出ている（[releases](https://github.com/nyosegawa/speech.cpp/releases)、年の表記はないので 2026-11 と推定。**未確認**）。ADR-035 が固定している 0.10.0 より新しいので、互換性を確かめる必要がある。
3. **後日の opt-in**: Moonshine Streaming。英語専用・MIT・ストリーミング向け。単語タイムスタンプを出せるかは **未確認** なので、確かめてから入れる。英語以外の旧型モデルは非商用なので登録しない。
4. **`distil-large-v3.5` は残すが、推奨しない。** Leaderboard から外れた理由が分かるまで、前面には出さない。

---

## 3. diarization-skill

### 3.1 いま組み込まれているもの

出典: `/home/user/diarization-skill/docs/decisions.md` ADR-001、`ecosystem.json`

- エンジンは pyannote.audio 4.x と `speaker-diarization-community-1`（CC-BY-4.0、ゲート付き）の 1 つだけ。
- ローカルのディレクトリから読み込み、実行時には何も取得しない。worker は `PYANNOTE_METRICS_ENABLED=0` を設定してテレメトリを切っている（`src/diarization_skill/engines/worker.py:16`）。

### 3.2 英語での弱点

- **言語の問題はない。** 話者分離は音響だけを見るので、英語でもそのまま使える。
- **初回の取得に手間がかかる。** HF アカウント・利用条件への同意・アクセストークンが要る（[モデルカード](https://huggingface.co/pyannote/speaker-diarization-community-1)）。
- **CPU 速度が公開されていない。** 公開されている速度は H100 で 1 時間の音声あたり 31 秒（AMI）・37 秒（DIHARD 3）だけ（[PyPI pyannote.audio](https://pypi.org/project/pyannote.audio/)）。
- **PyTorch が必要で重い。**
- **Python の要件がずれている。** pyannote.audio 4.1.1（2026-11-19）は **Python 3.11 以上**を求めている（[PyPI](https://pypi.org/project/pyannote.audio/)）。一方、`pyproject.toml` のコメントは「pyannote.audio 4.x itself needs Python >= 3.10」となっている。

### 3.3 候補

| 候補 | ライセンス | サイズ | 品質・速度 | 最新 | 出典 |
|---|---|---|---|---|---|
| **pyannote community-1**（いまの既定） | パイプラインは CC-BY-4.0、コードは MIT | **未確認**（カードに記載なし） | DER: AMI(IHM) 17.0、DIHARD3 20.2、VoxConverse 11.2。いずれも 3.1 と同等かそれ以上 | 4.1.1（2026-11-19） | [カード](https://huggingface.co/pyannote/speaker-diarization-community-1)、[PyPI](https://pypi.org/project/pyannote.audio/) |
| **sherpa-onnx**（pyannote segmentation-3.0 と話者埋め込み） | コードは Apache-2.0（[PyPI](https://pypi.org/project/sherpa-onnx/)）。segmentation-3.0 は MIT（[HF](https://huggingface.co/pyannote/segmentation-3.0)）。埋め込み（NeMo TitaNet small、3D-Speaker）の ONNX 版のライセンスは **未確認** | segmentation は int8 で 1.5 MB、fp32 で 5.7 MB。埋め込みは **未確認** | RTF 0.110（int8 と NeMo の組み合わせ）〜0.297。測定機は記載なし（**未確認**） | 2.0.2（2026-11-19） | [sherpa-onnx の話者分離モデル](https://k2-fsa.github.io/sherpa/onnx/speaker-diarization/models.html) |
| DiariZen meeting-base | カードは MIT。土台の WavLM のライセンスは **未確認**。上位版の `diarizen-wavlm-large-s80-md-v2` は **CC-BY-NC-4.0** | **未確認** | AMI SDM の DER 15.6（Pyannote3 は 21.1、collar 0） | カードの更新 2025-06-27 | [meeting-base](https://huggingface.co/BUT-FIT/diarizen-meeting-base)、[large-v2（NC）](https://huggingface.co/BUT-FIT/diarizen-wavlm-large-s80-md-v2) |
| Streaming Sortformer 4spk v2.1 | NVIDIA Open Model License | **未確認** | 話者 4 人まで（ADR-001 による） | カードの更新 2026-09-23 | [カード](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1) |

### 3.4 推奨

- **既定は据え置く**（pyannote community-1）。言語に依存せず、保守も活発で、DER も公開されている。
- **すぐ直すこと**: pyannote 4.1 系に合わせて、Python 3.11 以上という要件を doctor とドキュメントに反映する。`pyannote>=4.0,<5` のままだと、3.10 の環境で入れたときに失敗する恐れがある（実際に失敗するかは **未確認**）。
- **opt-in**: sherpa-onnx を第 2 のバックエンドにする（ADR-001 の follow-up と同じ方向）。PyTorch もゲートも要らない。ただし埋め込みモデルの重みライセンスを一次資料で確かめるのが前提。
- **見送り**: DiariZen は、上位版が非商用で、MIT の版も土台のライセンスが **未確認** のため。Sortformer は話者数の上限とライセンスのため。

---

## 4. voice-enhance-skill

### 4.1 いま組み込まれているもの

出典: `/home/user/voice-enhance-skill/docs/decisions.md` ADR-001/005

| 操作 | エンジン | ライセンス | 状態 |
|---|---|---|---|
| ISOLATE | DeepFilterNet3（`deep-filter` バイナリと ONNX、48 kHz） | MIT / Apache-2.0 | scaffold |
| DEREVERB | nara_wpe | MIT（重みなし） | scaffold |
| BLEED_REDUCE | crosstalk（自前） | MIT | scaffold |

### 4.2 英語での弱点

- **言語の問題はない。** DFN3 と WPE は言語に依存しない（ADR-001 の論旨のとおり）。
- **DeepFilterNet は保守の危険がある。**
  - PyPI `deepfilternet` の最新は 0.5.6（2023-08-31）（[PyPI](https://pypi.org/project/deepfilternet/)）。
  - コードの最終コミットは 2024-10-17。2026-11-06 に README のライセンス節を更新しただけで、内容は「All code and model weights in this repository are dual-licensed」（[commits](https://github.com/Rikorose/DeepFilterNet/commits/main)、[README の License](https://github.com/Rikorose/DeepFilterNet#license)）。
  - つまりライセンスは明確になったが、開発は実質止まっている。
- **nara_wpe も更新が少ない。** 0.0.11（2024-09-10）が最新（[PyPI](https://pypi.org/project/nara-wpe/)）。ただし重みのない信号処理なので、陳腐化の心配は小さい。

### 4.3 候補

| 候補 | ライセンス | サイズ | 品質・速度 | 最新 | 出典 |
|---|---|---|---|---|---|
| **DeepFilterNet3**（いまの既定） | MIT / Apache-2.0（コードと重み） | ONNX の tar。サイズは **未確認** | リアルタイム設計（ADR-001）。DFN3 の数値は本調査では **未確認** | 0.5.6（2023-08）。コードは 2024-10 | [README](https://github.com/Rikorose/DeepFilterNet) |
| **DPDFNet**（CEVA） | Apache-2.0（HF カード） | `dpdfnet2_48khz_hr` は 2.58M パラメータ・ONNX 10.5 MB。`dpdfnet8_48khz_hr` は 3.63M・14.9 MB。8・16 kHz 版もある | DeepFilterNet2 に dual-path RNN を足した構成。VoiceBank+DEMAND と DNS4 で DFN2 を一貫して上回るとの主張。DFN3 との比較は **未確認**。推奨は CPU の ONNX 推論で、ストリーミング API がある | HF の更新 2026-07-05。論文 v3 2026-06-16。sherpa-onnx も 48 kHz 版に対応 | [HF カード](https://huggingface.co/Ceva-IP/DPDFNet)、[arXiv 2512.16420](https://arxiv.org/abs/2512.16420)、[sherpa-onnx の音声強調](https://k2-fsa.github.io/sherpa/onnx/speech-enhancement/index.html) |
| **GTCRN** | MIT | 48.2K パラメータ・33 MMACs/s | VCTK-DEMAND で PESQ 2.87（DeepFilterNet は 2.81）。ストリーミング版は i5-12400 で RTF 0.07。サンプルレートは **未確認**（16 kHz と思われるが一次資料で確かめていない） | ニュースの最新は 2026-01-18 | [GitHub](https://github.com/Xiaobin-Rong/gtcrn) |
| ClearerVoice-Studio（MossFormer2_SE_48K） | コードは Apache-2.0。学習済みモデルのライセンスは **未確認** | **未確認** | 比較値は **未確認** | clearvoice 0.1.2（2025-07-11） | [GitHub](https://github.com/modelscope/ClearerVoice-Studio)、[PyPI](https://pypi.org/project/clearvoice/) |

### 4.4 推奨

- **既定は据え置く**（DFN3 と nara_wpe）。ライセンスはむしろ明確になり、バイナリは PyTorch なしで動く。英語で困ることはない。
- **opt-in**: DPDFNet の 48 kHz 版（`dpdfnet2_48khz_hr`）を、ISOLATE の第 2 エンジンとして登録する。
  - Apache-2.0 で、ONNX が 10 MB 程度。2026 年も更新が続いている。sherpa-onnx か onnxruntime で動く。
  - 既定にするかは、既存の SNR fixture と transcription の往復で DFN3 と比べてから決める。
- **見送り**
  - GTCRN: 48 kHz 対応が **未確認** で、いまの 48 kHz パイプラインと合うか分からない。軽量な 16 kHz の ASR 前処理には向く可能性がある。
  - ClearerVoice: モデルのライセンスが **未確認**。

---

## 5. dubbing-skill

### 5.1 いま組み込まれているもの

出典: `/home/user/dubbing-skill/README.md`、`docs/decisions.md` ADR-001/011/018、`src/dubbing_skill/engines/`

| エンジン | 役割 | 英語 | ライセンス（コード / 重み） |
|---|---|---|---|
| `chatterbox` Multilingual（**既定**） | NARRATE / DUB / AUDIO_DESCRIPTION、声の複製 | 対応（23 言語） | MIT / MIT。Perth 透かしを入れる |
| `voicevox` | NARRATE / AD | 非対応（日本語のみ） | LGPL・MIT / キャラクターごとの規約 |
| `style_bert_vits2` | 3 つの操作すべて | 対応（JP・EN・ZH） | AGPL / モデルごと |
| `kokoro` | NARRATE / AD | 対応（`en-us` は `af_heart`、`en-gb` は `bf_emma`） | Apache-2.0 / Apache-2.0 |
| `qwen3_tts` Base（experimental） | 3 つの操作すべて、複製のみ | 対応（10 言語） | Apache-2.0 / Apache-2.0 |

### 5.2 英語での弱点

- **既定の Chatterbox は保守が終わった。** README の冒頭に「**As of August 2026, Chatterbox is retired research and is no longer maintained.** ... The code stays public as an archive under the MIT license, with no support, updates, or paid tier.」とある（[README](https://github.com/resemble-ai/chatterbox)）。
  - `chatterbox-tts` の最新は 0.1.7（2026-03-26）（[PyPI](https://pypi.org/project/chatterbox-tts/)）。
  - 「2026 年後半に保守が続いている」という条件を満たさない。
- **Chatterbox Multilingual は重い。** `t3_mtl23ls_v3.safetensors` が 2.14 GB、`s3gen` が約 1.06 GB で、合わせて 3 GB を超える（[HF API](https://huggingface.co/api/models/ResembleAI/chatterbox?blobs=true)）。日本語の経路は pykakasi（GPL）に頼っている（ADR-001）。
- **Kokoro も更新が止まりがち。** `kokoro` 0.9.4（2025-04-05）が最新で（[PyPI](https://pypi.org/project/kokoro/)）、重みも v1.0（2025-01-27）から更新がない（[カード](https://huggingface.co/hexgrad/Kokoro-82M)）。
  - 英語の G2P（`misaki[en]`）は、辞書にない語で espeak-ng にフォールバックでき、`espeakng-loader` と `phonemizer-fork` を依存に持つ（[PyPI misaki](https://pypi.org/project/misaki/)）。
  - espeak-ng のライセンスは本調査では **未確認**。ただし worker を別の venv で動かす隔離（ADR-001）が、そのまま効く。
- **Qwen3-TTS Base はプリセットの声を持たない。** 毎回、同意記録が要る（ADR-018）。CPU では 0.6B で 1 文あたり約 15 秒（読み込み込み、クリップ長の 8.5 倍）かかった（ADR-018 の実測）。

### 5.3 候補

| 候補 | ライセンス | サイズ | 品質・速度 | 最新 | 出典 |
|---|---|---|---|---|---|
| **Kokoro-82M** | Apache-2.0（コードと重み。声も同じ） | 82M。`kokoro-v1_0.pth` は 327 MB | v1.0 は 8 言語・54 声。CPU の測定値はカードにない（**未確認**） | kokoro 0.9.4（2025-04）。kokoro-onnx 0.6.1（2026-08-19） | [カード](https://huggingface.co/hexgrad/Kokoro-82M)、[PyPI kokoro-onnx](https://pypi.org/project/kokoro-onnx/) |
| **Kyutai Pocket TTS** | コードは MIT。重みは CC-BY-4.0（帰属表示が必要）。**プリセット声はフォルダごとにライセンスが違い、Expresso と EARS は CC BY-NC（非商用）**。VCTK は CC BY 4.0、voice-donations と voice-zero は CC0。カードは同意のない声の複製を禁じている。複製できる版はゲート付き | 100M。英語モデルは 219 MB。小型の 2m・7m・18m 版（47〜112 MB）と、24 層の高品質版（1.3 GB）もある | M4 の CPU で約 6 倍速（2 コア）、最初の音声まで約 200 ms。x86 の 4 vCPU では RTF 2.3〜2.5 倍速。言語は英・仏・独・葡・伊・西（GitHub ではさらに蘭） | pocket-tts 4.0.1（2026-10-21）。重みの更新 2026-10-21 | [カード](https://huggingface.co/kyutai/pocket-tts)、[GitHub](https://github.com/kyutai-labs/pocket-tts)、[声のライセンス](https://huggingface.co/kyutai/tts-voices)、[PyPI](https://pypi.org/project/pocket-tts/) |
| **Qwen3-TTS-12Hz-0.6B-CustomVoice** | Apache-2.0 | 本体 1.81 GB と speech tokenizer 0.68 GB | プリセット話者が 9 人（英語は Ryan と Aiden、日本語は Ono_Anna など）。10 言語。品質の数値はカードにない（**未確認**）。CPU 速度は Base 0.6B と同程度と見込むが **未確認** | qwen-tts 0.1.1（2026-02-06）。重み 2026-01-29 | [カード](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice)、[PyPI](https://pypi.org/project/qwen-tts/) |
| Chatterbox Turbo / Nano（参考） | MIT | Turbo 350M（t3 1.92 GB と s3gen）。Nano 110M（t3 0.87 GB と s3gen 1.06 GB） | Nano は 8 コアの CPU で 3 倍速。英語のみ | **保守終了**（2026-08） | [README](https://github.com/resemble-ai/chatterbox)、[chatterbox-nano](https://huggingface.co/ResembleAI/chatterbox-nano) |

候補から外したもの:

- [NeuTTS Air](https://huggingface.co/neuphonic/neutts-air)（Apache-2.0、0.7B、ゲート付き、Perth 透かし）: 対応言語がカードにない（**未確認**）。
- [Supertonic 3](https://huggingface.co/Supertone/supertonic-3)（OpenRAIL、用途制限付き）: 寛容なライセンスではない。
- [Piper](https://pypi.org/project/piper-tts/)（現行の `piper-tts` 1.8.0 は GPL-3.0-or-later）: コピーレフト。
- [F5-TTS](https://huggingface.co/SWivid/F5-TTS) と XTTS-v2: 重みが非商用（ADR-001 のとおり）。

### 5.4 推奨

1. **英語の NARRATE と AUDIO_DESCRIPTION の既定を Kokoro-82M（`af_heart` / `bf_emma`）にする。**
   - Apache-2.0 で、合成した音声ごとのクレジットは求められない（重みや声のファイルを再配布するときは、ライセンス文と NOTICE を残す）。327 MB と軽い。プリセットの声なので同意の手続きが要らない。
   - エンジンはすでに組み込み済みなので、`DEFAULT_ENGINE` を言語ごとに引けるようにすればよい。
   - パッケージの更新が止まりがちな点は、kokoro-onnx（2026-08 も更新あり）を予備の実行系として見ておく。
   - espeak-ng へのフォールバックは別の venv に閉じ込め、ライセンスを確かめる。
2. **DUB（声の複製）の opt-in に Pocket TTS を足す。**
   - 保守が活発で、CPU でリアルタイムより速い。英語モデルは 219 MB と小さい。
   - 条件が 3 つある。
     - 複製は既存の同意記録（ADR-009）を必須にする。カードも同意のない複製を禁じている。
     - **プリセット声は CC BY・CC0 のものだけを許可リストに入れる**。Expresso と EARS 由来は非商用なので登録しない。
     - CC-BY-4.0 の帰属表示を provenance に記録する。
3. **Qwen3-TTS は CustomVoice 0.6B を opt-in で足す。** 同意なしでプリセット話者を使え、英語以外の主要言語（独・仏・西・伊・葡・露・中・韓・日）も 1 つのエンジンで受けられる。experimental の扱いは Base と同じにして、聞き比べてから昇格を判断する。
4. **Chatterbox は既定から外し、「凍結した旧エンジン」の opt-in にする。** 23 言語をカバーし、透かしを読み戻せる機能（ADR-017）があるので、削除はしない。ただし、新しい既定にはしない。
5. **VOICEVOX と Style-Bert-VITS2 は日本語の opt-in のまま残す。**

---

## 6. subtitle-skill（字幕翻訳）

### 6.1 いま組み込まれているもの

出典: `/home/user/subtitle-skill/README.md`、`docs/adr/ADR-004-translation-engine.md`

| `engine` | 既定 | 重みのライセンス | 実際に使えるペア |
|---|---|---|---|
| `argos` | **既定** | **未確認**（索引にもパッケージにも記載なし） | 索引にある約 100 ペア |
| `opus-mt` | opt-in | Apache-2.0 / CC-BY-4.0 | ドキュメント上は「ja→en のみ」 |
| `ollama` | opt-in | モデル次第（既定 `qwen3:8b` は Apache-2.0） | すべて |
| `deepl` | opt-in（ネットワークを使う） | API の規約 | すべて |
| `memory` | — | — | — |

### 6.2 英語での弱点

- **Argos の重みライセンスは今も書かれていない。** 2026-11-21 に索引 `index.json`（100 パッケージ）を読み直した。項目は `argos_version, code, from_code, from_name, links, package_version, to_code, to_name` だけで、ライセンスの欄はない（[argospm-index](https://github.com/argosopentech/argospm-index/blob/main/index.json)）。英語起点の en→es なども同じ。
  - つまり英語↔主要言語でも、商用の既定に向かないという ADR-004 の懸念がそのまま残る。
  - `argostranslate` の最新は 1.11.0（2026-02-02）（[PyPI](https://pypi.org/project/argostranslate/)）。
- **OPUS-MT の扱いが狭すぎる。** ADR-004 は ja↔en を中心に書かれているため、OPUS-MT を「ja→en のみ」と扱っている。しかし英語起点・英語行きでは、多くのペアで tc-big モデルが公開されている（6.3 参照）。
- **Ollama の既定モデル `qwen3:8b` は一世代前。** 後継の Qwen3.5 は 2026-02 に公開された（[Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)）。

### 6.3 候補

| 候補 | ライセンス | サイズ | 品質 | 最新 | 出典 |
|---|---|---|---|---|---|
| **OPUS-MT tc-big**（`opus-mt-tc-big-en-{es,fr,it,pt,ko,ar,tr,…}` と逆向き）。CTranslate2 で動かす | CC-BY-4.0（帰属表示が必要） | 約 0.2B（en-es は 232,760,051 パラメータ） | en-es: flores101-devtest で BLEU 28.5 / chrF 0.564 | モデルは 2022〜2023。実行系の CTranslate2 は 4.9.0（2026-11-10、MIT） | [opus-mt-tc-big-en-es](https://huggingface.co/Helsinki-NLP/opus-mt-tc-big-en-es)、[HF の一覧](https://huggingface.co/models?author=Helsinki-NLP&search=opus-mt-tc-big-en-)、[PyPI ctranslate2](https://pypi.org/project/ctranslate2/) |
| OPUS-MT の旧型（`opus-mt-en-de`、`en-es`、`en-zh`、`en-ru`、`en-hi` など。tc-big がないペア用） | ペアごとに違う。`opus-mt-en-de` は CC-BY-4.0、`opus-mt-en-es` と `opus-mt-en-zh` は Apache-2.0（各モデルカード）。他のペアは個別に **未確認**。`en-zh` は複数の出力言語を持ち、文頭に `>>cmn_Hans<<` のような言語トークンが要る | 約 0.07〜0.3B（**未確認**） | ペアごと | 2023-08（en-de） | [opus-mt-en-de](https://huggingface.co/Helsinki-NLP/opus-mt-en-de)、[opus-mt-en-es](https://huggingface.co/Helsinki-NLP/opus-mt-en-es)、[opus-mt-en-zh](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh) |
| **Qwen3.5**（Ollama の `qwen3.5:4b` / `:9b`） | Apache-2.0 | ダウンロードは 4b が 3.3〜4.0 GB、9b が 6.6〜7.6 GB | WMT24++（55 言語、XCOMET-XXL）で 9B は 72.6、4B は 66.6。201 言語。思考モードが既定 | 2026-02-27 | [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)、[Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)、[Ollama](https://ollama.com/library/qwen3.5) |
| **Gemma 4 E4B**（`gemma4:e4b`） | **Apache-2.0**（Gemma 3 の独自規約から変わった） | 実効 4.5B（埋め込み込みで 8B）。Ollama では 6.6〜9.5 GB | 35 以上の言語に対応。翻訳ベンチマークはカードにない（**未確認**） | カードの更新 2026-11-03 | [カード](https://huggingface.co/google/gemma-4-E4B-it)、[Ollama](https://ollama.com/library/gemma4) |
| EuroLLM-9B-Instruct-2512 | Apache-2.0 | 9.15B | 35 言語（欧州言語と日・中・韓など）。翻訳の数値はカードにない（**未確認**） | 2026-07-31 | [カード](https://huggingface.co/utter-project/EuroLLM-9B-Instruct-2512) |

候補から外したもの（ライセンス）:

- [NLLB-200](https://huggingface.co/facebook/nllb-200-distilled-600M)（CC-BY-NC-4.0）
- [Tower-Plus-2B](https://huggingface.co/Unbabel/Tower-Plus-2B)（CC-BY-NC-SA-4.0）
- [Aya Expanse 8B](https://huggingface.co/CohereLabs/aya-expanse-8b)（CC-BY-NC-4.0）
- [TranslateGemma 4B](https://huggingface.co/google/translategemma-4b-it)（`license: gemma`。Gemma 4 とは違い Apache ではない）

[MADLAD-400 3B](https://huggingface.co/google/madlad400-3b-mt)（Apache-2.0、2.94B、2023-11）はライセンスは問題ないが、古く大きいので見送る。

### 6.4 推奨

1. **既定を `argos` から `opus-mt` に変える。** 対象は、英語↔主要言語のうち tc-big か旧型の OPUS-MT が公開されているペア。
   - 実行系（CTranslate2）は保守が活発で、ライセンスは MIT（[LICENSE](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE)）。PyTorch なしの CPU で動き、1 ペアあたり 0.2B 程度と軽い。
   - モデルのライセンスは実行系とは別で、ペアごとに違う。tc-big は CC-BY-4.0（en-es など）。旧型は `opus-mt-en-de` が CC-BY-4.0、`opus-mt-en-es` が Apache-2.0。使うペアのモデルカードを読む。
   - 必要な作業:
     - `SUBTITLE_SKILL_OPUS_MT_DIR` の下にペアごとの変換済みディレクトリを置き、doctor が使えるペアを一覧にする。
     - CC-BY-4.0 のペアでは、帰属表示（「OPUS-MT, Helsinki-NLP」）を provenance に入れる。
     - ペアのモデルがないときは、Argos へ黙って切り替えず `DEPENDENCY_ERROR` を返す（ADR-004 の方針と同じ）。
   - en→ja は相変わらず汎用の OPUS-MT がないので、日本語は opt-in（`ollama` または `memory`）のままにする。
   - 既定が変わると既存の呼び出し側の出力が変わる（ADR-004 の決定 11）。そのため ADR と agent の再ピン留めが必要になる。
2. **`argos` は opt-in に下げる。** ライセンスが **未確認** であることを、これまでどおり doctor に表示し続ける。
3. **Ollama（opt-in）の既定モデルを `qwen3:8b` から `qwen3.5:9b` に上げる。** ディスクが厳しければ `qwen3.5:4b`（3.3 GB〜）。
   - Qwen3.5 は思考モードが既定で、`/nothink` のような切り替えは効かない（[カード](https://huggingface.co/Qwen/Qwen3.5-4B)）。
   - subtitle-skill が送っている `think: false` が Ollama 経由の Qwen3.5 に効くかは **未確認** なので、実機で確かめる。
   - Gemma 4 E4B（Apache-2.0）は第 2 候補として案内する。
4. **DeepL は opt-in のまま**（ネットワークを使うので、既定にはできない）。

---

## 7. 横断的な注意

- **帰属表示（CC-BY-4.0）が増える。** Parakeet、Pocket TTS の重み、OPUS-MT の tc-big と一部の旧型（`opus-mt-en-de` など）は CC-BY-4.0 なので、クレジットが必要になる。MIT と Apache-2.0 は出力ごとのクレジットを求めないが、コードや重みを複製・再配布するときは著作権表示と許諾表示（Apache-2.0 では NOTICE も）を残す。
  - transcription-skill の `MODELS[...]["attribution"]`（ADR-040）や dubbing-skill の `credit` と同じ形で provenance に記録し、ProductionReceipt まで運ぶ。
  - CC-BY-4.0 のモデル（変換・量子化したものを含む）を再配布するときは、帰属表示に加えて、ライセンスへの参照（CC-BY-4.0 の全文か URI）と、変更を加えたかどうかの表示が要る（CC-BY-4.0 第 3 条 (a)(1)(B)・(C)）。CTranslate2 への変換、GGUF や int8 への量子化、ONNX への書き出しは変更にあたるので、元のモデル名と、加えた変更を書く。
  - 受け取ったモデルがすでに誰かの変更を経ている（他者が変換・量子化して公開したものなど）ときは、前の改変者が付けた変更の表示も消さずに残し、自分の変更をその後に足す。第 3 条 (a)(1)(B) は "indicate if You modified the Licensed Material and retain an indication of any previous modifications" と定める。あわせて (a)(1)(A) により、ライセンサーが素材に付けて提供した表示（"a copyright notice"、"a notice that refers to this Public License"、"a notice that refers to the disclaimer of warranties"、"a URI or hyperlink to the Licensed Material to the extent reasonably practicable" など）も保持する（[CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode)）。
- **ゲート付きの取得が増える。** pyannote community-1 と Pocket TTS の複製版は、HF アカウントと同意が要る。doctor が取得手順を出す形（diarization ADR-001）に揃える。
- **既定の切り替えは 3 つのリポジトリで ADR になる**（transcription、dubbing、subtitle）。いずれも contract の `default` が変わるので、video-production-agent の再ピン留めが要る。
- **ecosystem.json** の `engines` 欄も合わせて直す（このリポジトリの管轄）。対象は次の 3 か所。
  - transcription-skill の欄は、いま faster-whisper しか載っていない。
  - dubbing-skill の Chatterbox の欄には「保守終了」を明記する。
  - subtitle-skill には `engines` 欄がない。
- **本調査で測ったものはない。** CPU の実時間比はすべてベンダーか第三者の値で、測定機もまちまち。既定を切り替える前に、各スキルの既存の fixture と heavy-tests で、同じ機械で測り直すこと。

## 8. 未確認の事項（まとめ）

- whisper-large-v3-turbo を faster-whisper（int8）の CPU で動かしたときの実時間比。
- Open ASR Leaderboard が distil-large-v3.5 を外した理由。
- speech.cpp v0.11.x の公開年（2026 と推定）と、0.10.0 との互換性。
- Moonshine Streaming の単語タイムスタンプ・句読点の有無と、CPU の実測値。
- Qwen3-ASR-0.6B の CPU 速度と、`speechcpp` 版のファイルサイズ。
- sherpa-onnx の話者埋め込みモデル（NeMo TitaNet small、3D-Speaker）の重みライセンス。
- DiariZen の土台である WavLM のライセンス。
- pyannote.audio 4.1 が Python 3.10 で実際に入れられないかどうか。
- DPDFNet と DeepFilterNet3 の直接比較、GTCRN のサンプルレート、ClearerVoice のモデルのライセンス。
- Kokoro の CPU 速度、espeak-ng のライセンス。
- Pocket TTS のプリセット声それぞれの出所（Expresso・EARS 由来かどうか）。
- Qwen3-TTS CustomVoice の品質と CPU 速度。
- NeuTTS Air の対応言語。
- OPUS-MT 旧型の各ペアのライセンスとサイズ（en-de、en-es、en-zh のライセンスは確認済み）。
- Gemma 4 と EuroLLM の翻訳ベンチマーク。
- Ollama 経由の Qwen3.5 で `think: false` が効くかどうか。
