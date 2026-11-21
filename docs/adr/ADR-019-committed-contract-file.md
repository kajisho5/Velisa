# ADR-019: Every Skill Commits Its Contract as contract/contract.json

Status: Accepted

## Context

video-production-agent pins each Skill's machine-readable contract byte for byte (`src/video_agent/tools/<name>/contract_<version>.json`, `src/video_agent/skills/pins/<skill>_<version>.json`). Until now each pin was taken by checking out the Skill at its release tag and running its CLI (`contract --json`, `skill --json`, `node bin/... contract --json`, `python3 scripts/_contract.py --json`), then formatting the output the way that Skill's earlier pins were written. That is slow. Running cloned tag code was also once refused by a permission check. The next step, an automatic re-pin, needs the contract of a tag without running anything.

## Decision

1. **One path everywhere: `contract/contract.json`** at the root of every Skill repository that has a contract command. A repository with no contract command has no file.
2. **The bytes are what the agent pins.** The file is the Skill's contract output, formatted the way video-production-agent pins that Skill:
   - unchanged CLI output (for example video-editing, audio-production, color-grading, qc, subtitle, thumbnail, motion-graphics, media-analysis);
   - one line with sorted keys, compact separators, no ASCII escapes and a final newline (for example artifacts, publish, imagemagick, remotion-ffmpeg, blender, hyperframes, ingest, nle-bridge, detection, diarization);
   - transcription: indent 1 with every engine entry in its machine-independent form (availability stripped), so the file does not depend on what the machine has installed.

   A Skill the agent does not pin commits its unchanged `contract --json` output.
3. **The repository generates and checks it.** `contract/generate.py` (`contract/generate.mjs` in a Node repository) runs the repository's own contract command, applies the format and writes the file. `--check` exits 1 when the committed file differs. A test in the repository's own runner calls the check, so CI fails on a stale file. `.gitattributes` marks the file `-text`, so a Windows checkout keeps the bytes.
4. **The invariant: at every release tag, the committed file equals that tag's own contract output.** The contract carries the version, so every release flow regenerates the file after the version bump and commits it with the release:
   - push-to-main release jobs run the generator after the bump and add the file to the release commit;
   - release-please repositories list the file in `extra-files` with `jsonpath` `$.version`; release-please rewrites a JSON file with its detected indent, which for these files gives the generator's bytes;
   - repositories that release a hand-bumped version regenerate the file in the bump PR, and their release job runs the check (or the tests) before it tags.
5. **How the agent reads it.** For a Skill and a tag, `git show <tag>:contract/contract.json` (or the GitHub contents API at that ref) gives the bytes to pin. Nothing is installed or run. A tag made before the file existed has no file; the agent then falls back to running the CLI at the tag, as before.

## Consequences

- An automatic re-pin can fetch any release's contract with one read and compare it byte for byte with the pin, without executing a cloned repository.
- A contract change that is not regenerated fails that repository's CI, so the committed file cannot drift from the code.
- ffmpeg-skill is not covered: it commits no contract file (its contract is about 950 KB, and the agent pins a contract check, not a JSON copy).
- Repositories without a release flow (ingest, nle-bridge, detection, diarization) carry the file on main. Their tags, once they release, follow the same invariant through the test.
