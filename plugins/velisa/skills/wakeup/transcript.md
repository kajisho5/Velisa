# Transcript search, retakes, and what is not provided

Recipes for jobs no skill does in one command yet. Searching and proposing are safe (they only read a transcript);
cutting is not, so every range below goes to a person before anything is cut. Owners (from `ecosystem.json`):
文字起こし and 文字起こしの語句検索 are `transcription-skill`'s, 言い直し・重複の候補提示 is `video-production-agent`'s,
cutting runs on `ffmpeg-skill`. Until those owners ship the commands, do these steps yourself and say so (level 3).

## 1. Transcribe once, keep the word-timed JSON

```bash
transcription transcribe talk.mp4 --language ja --word-timestamps --json -o talk.transcript.json
transcription export talk.transcript.json --format srt -o talk.srt      # optional, for people
```

- Keep `talk.transcript.json`: every later step reads it, and the transcript cache makes a re-run a hit, not a second
  pass over hours of audio. Times are seconds on the source's own timeline.
- Words are `segments[].words[]` with `start`, `end`, `text`. `words: null` (no `--word-timestamps`, or an engine
  without word timing) leaves segment times only: say that hits are segment-accurate.
- ffmpeg-skill alone: `caption.py talk.mp4 --transcribe --write-srt talk.srt` gives cue times only; `silence.py
  --transcribe` times words for its own filler pass. The transcript is ASR evidence: quote it as it is, homophone
  errors included, and expect the phrase the user remembers to be spelled differently.

## 2. Find a phrase (voice: "where in three hours did I say X")

1. **Exact** first: the phrase as a substring of each segment's `text`.
2. **Normalised** when exact misses, always for Japanese and Chinese: NFKC, casefold, drop whitespace and punctuation
   (Unicode categories Z* and P*), then match on the joined word texts so a phrase split across words or segments
   still matches. CJK text has no spaces, so never match word-by-word on whitespace.
3. **Fuzzy** last: slide a window of the phrase's normalised length (±20%) over the normalised text and keep windows
   with `difflib.SequenceMatcher` ratio ≥ 0.8. Label these "approximate".
4. Map each match back to the first and last word it covers, and report every hit, never only the best:
   `#3  01:12:04.31–01:12:06.02  match: exact|normalised|approximate (0.86)  …previous sentence | hit | next sentence…`
   with the file name when several transcripts were searched.

Then the person picks the hit. Hand that one range to ffmpeg-skill with a margin:

```bash
python3 cut.py talk.mp4 --start 4323.81 --end 4326.52 --accurate -o hit.mp4
```

- Margin: 0.5 s before the first word and after the last, but not past the midpoint of the gap to the neighbouring
  word. Word times can be off by up to about a second (transcription-skill's own note), so watch the clip before using it.
- `--accurate` because a copy cut snaps to a keyframe (`keyframe_snapped`, `duration_error_ms` in the result).
- Several hits as one reel: `--segments "a-b,c-d"`.

## 3. Retakes, repeated sentences, misspeaks: candidates, not cuts (voice: "transcript cutting leaves my retakes in")

From the word-timed transcript:

1. Split into sentences: segment boundaries, sentence punctuation (`。！？.?!`), or a pause between words ≥ 0.7 s.
2. Compare each sentence with the next one to three (within 30 s), normalised as in step 2:
   - **repeat**: similarity ≥ 0.6 (the speaker said it again);
   - **restart**: the earlier sentence is a prefix of the later one, or stops mid-phrase and the later one starts with
     the same first 3+ characters (「今日は、今日はですね」);
   - **stutter**: the same word or 2–3 word run twice in a row inside one sentence.
3. Present a numbered list and let the person decide each item (a CONFIRM decision; nothing is cut by default):
   `R4  restart  01:02.10–01:03.40 「今日は」  then 01:03.90–01:07.20 「今日はですね…」  proposal: remove the first take`
   Default proposal: keep the last take. Which take is better is the person's call, not yours.
4. Cut only the confirmed ranges, with the same margin rule:
   `python3 cut.py talk.mp4 --remove "62.0-63.8,301.2-305.0" --accurate`.
   To combine with silence removal: `silence.py talk.mp4 --list --edl keep.txt`, subtract the confirmed ranges from
   those kept ranges, and cut once with `cut.py talk.mp4 --segments "<the result>" --accurate`.
5. After any cut, transcript and subtitle times are source times: re-transcribe the result, or re-time the cues
   (`silence.py --timemap` writes the map; no tool applies it yet).

Fillers are a different job (無音・フィラー除去, `audio-production-skill`; at the engine `silence.py --filler`, which
needs word timings). Its Chinese list is 嗯 / 嗯嗯 / 呃 / 呃呃 / 唔; 啊 is excluded by design because it is also a
sentence particle: add it with `--filler-extra 啊` only after the person agrees. Check first with `--filler-list`.

## 4. Not provided, or not how it sounds

| Heard as | What exists |
|---|---|
| BGM ducking | Yes: `audio.py talk.mp4 --music bed.mp3 --duck` (sidechain on the voice track). |
| Multicam switching by speaker | No. `multicam.py --switch energy` cuts to the loudest camera's audio, which is not speaker identification. Speaker turns come from `diarization-skill` (optional); turning them into a `--switch START-END:CAM` list needs the person to say which camera shows whom. |
| Automatic CJK caption fonts | Yes: `caption.py` picks a font that covers the text's script; pass `--lang zh`/`ja`/`ko` so Han-only text gets the right regional font; `--font` overrides. |
| Chinese filler removal (嗯/啊) | Partly: needs word timings, 嗯/呃/唔 by default, 啊 only with `--filler-extra 啊`. |
| Transcript phrase search, retake detection | Not a command in any skill yet: the recipes above. |
