# Field test kit

**Status: CURRENT** (decision D43).

Some roadmap steps cannot be finished by CI or by a cloud session: their "Done when" needs a GPU with model weights, a commercial NLE, a test account on a video platform, a set-top disc player, or consented recordings of real people. This kit lists those steps, says how to run each one, and records the result in a file the owner commits.

- [`steps.json`](steps.json): the steps (repository, step, "Done when", what is needed, the conditions and metrics to measure). Read from each repository's roadmap on `main` on 2026-11-20.
- [`../../scripts/field_test.py`](../../scripts/field_test.py): `list`, `show <id>`, `record <id> ...`, `check`.
- [`results/`](results/): the committed results, one JSON record and one Markdown page per run.

## The steps

| Id | Repository, step | Needs | People in the media |
|---|---|---|---|
| `diarization-der` | diarization-skill 6 | the pyannote weights; reference turns labelled by a person | yes |
| `voice-enhance-venue` | voice-enhance-skill 10 | the engines; transcription-skill for WER; real venues | yes |
| `nle-bridge-real-nle` | nle-bridge-skill 8 | Premiere Pro 25.x, DaVinci Resolve Studio | no |
| `publish-real-upload` | publish-skill 7 | a test account per platform | no |
| `sound-design-real-engine` | sound-design-skill 8 (and the real-engine loop of 7) | a GPU with ACE-Step 1.5; ffmpeg-skill 3.2.2+; qc-skill 1.3.0+ | no |
| `transcription-haas-gpu` | transcription-skill 5 ("GPU run still to do") | Linux with an NVIDIA GPU; the Haas-ja weights | no |
| `transcription-whisperx` | transcription-skill 7 ("a real run still to do") | whisperX and its alignment weights | no |
| `transcription-ja-dictionary` | transcription-skill 13 ("a run on real Japanese recognition output still to do") | the `[ja]` extra; a recognition engine | yes |
| `oncemore-player-disc` | oncemore docs/ROADMAP "Player test disc" | a set-top DVD / Blu-ray player; a burner | no |

No roadmap marks a step with the words 確認待ち or "awaiting confirmation" (searched on 2026-11-20 in every repository's roadmap on `main`). The list above is the open steps, and the ticked steps with a "still to do" note, whose "Done when" or note names real hardware, software, accounts or media. A step added to a roadmap later is added to `steps.json` by hand.

## Before you start

1. Read the step in its repository (`/roadmap <repo>` from the velisa-maintainer plugin, or the file itself) and `python3 scripts/field_test.py show <id>`.
2. Install the repository at its latest release and note the versions you test (`--version`).
3. **Media of people.** Record only people who agreed, in writing, that the recording is used to measure this software and that numbers from it are published. Keep the consent with the recordings, outside every repository. Never commit the recordings, transcripts of them, names or faces. The recorder writes a label, the sha256 and the size of each file, and nothing else; `--consent` states that consent exists and is required for the steps marked "yes" above.
4. **Accounts.** Use test accounts, private visibility, and delete the uploads afterwards. Credentials stay where the tool reads them; the recorder refuses a value that looks like a token or password.
5. Use fictional material wherever people are not the point (NLE exports, uploads, discs, generated music).

## Running a step

Run each condition the step lists. Measure exactly what its "Done when" names, with the tool it names; write down anything you looked at but did not measure as a note, not as a number. A step that cannot be run (a missing licence, a refused account) is recorded as `blocked` with the reason.

```bash
python3 scripts/field_test.py record nle-bridge-real-nle --verdict partial \
  --env nle="Premiere Pro 25.1" --env os_host="macOS 15.2" --version nle-bridge-skill=0.1.2 \
  --measure premiere-pro.imports=yes --measure premiere-pro.start_timecode_kept=yes \
  --measure premiere-pro.edl_marker_colours_kept=no \
  --media fcp7-export=exports/edit.xml --note "Resolve not tested yet"
```

- A measurement is `<condition>.<metric>=<value>`; the conditions and metrics come from `show`. A condition may carry a detail after a colon: `lecture-hall:dereverb.wer_after_pct=12.4` (voice-enhance, per op). `yes` / `no` become booleans, numbers stay numbers.
- `--verdict`: `pass` (the "Done when" is met, with the measurements that show it), `partial` (some conditions), `fail` (run, and not met), `blocked` (could not run).
- The result names the conditions not measured, so a partial run says what is left.

## After the run

1. `python3 scripts/field_test.py check` (CI runs the same on every committed result).
2. Commit the two files from `results/` in a pull request to Velisa (`docs:` title).
3. In the step's own repository: add what its "Done when" asks for (a report, a fixture), link the result, and tick the step only when the verdict is `pass`. The coordinator or a session can do this part from the committed result.
