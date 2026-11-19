# ADR-021: Temporary Directories Are Prefixed, Always Removed, Movable, and Kept Only on Request

Status: Accepted

## Context

Tests and tools across the ecosystem make temporary directories in the OS temp directory (`/tmp` on Linux and macOS). Many of them were never removed:

- On one shared development machine, `/tmp` held 11 GB in about 78,000 entries. Earlier, the real-media tests of video-production-agent had filled 14 GB with `va_*` directories (its ADR-115 and `tests/tmp_dirs.py` fixed that).
- Some of the leftovers are unprefixed `tmpXXXXXXXX` directories (about 33,000). Their contents and dates point to video-production-agent's tests before that fix.
- The others carry the prefix of the repository that made them. That prefix is what made it possible to find their owners at all.

The owner asked for a rule, and for the leaks it finds to be fixed (decision D35 in [DECISION_LOG](../ecosystem/DECISION_LOG.md)).

### Inventory (2026-11-19)

Every skill repository except ffmpeg-skill and video-production-agent was checked:

- **Source.** Every `mkdtemp`, `TemporaryDirectory`, `mkstemp`, `mkdtempSync`, `os.tmpdir()` and hard-coded `/tmp/` in its source and tests was read.
- **Run.** The repository's CI test command was run from a checkout of its default branch, with `TMPDIR` set to an empty directory. What was left there was counted, and so was anything new in `/tmp` itself.
- **What does not count.** Three kinds of entry are not counted as leftovers:
  - pytest's `pytest-of-<user>` (pytest keeps the last three runs and removes older ones);
  - Node's shared `node-compile-cache`;
  - LibreOffice's IPC pipe.

| Repository | What was left per run | Where it came from | Fix |
|---|---|---|---|
| hyperframes-skill | about 114 `hfs-*` directories (scene copies, fake tools, fixture renders) | `tests/helpers.mjs` `tmp()` never removed anything | hyperframes-skill#27 |
| video-editing-skill | 138 `ves-*` directories offline; real-media roots too when `setUpClass` failed | `make_workspace()` had no cleanup; `tearDownClass` does not run after a failed `setUpClass` | video-editing-skill#52 |
| remotion-ffmpeg-skill | 4 `rfs-brand-*` directories; real-media roots when `setUpClass` failed | `Brand.setUp` never removed its directory; same `tearDownClass` gap | remotion-ffmpeg-skill#24 |
| transcription-skill | 2 empty `ts_doc_*` directories | `mkdtemp()` passed inline as a workspace argument | transcription-skill#64 |
| artifacts-skill | 1 empty `artifacts-skill-exec-*` directory | a test that kills a child with an unhandled SIGTERM, on purpose | artifacts-skill#76 |
| system-intelligence | one shallow clone per GitHub target (`si-github-*`, up to 39 MB each; 23 found, 136 MB) | `discovery/github_target.py` keeps the clone on purpose ("cleanup is the caller's concern") | not fixed; see Consequences |

The other skill repositories leave nothing outside pytest's own retention:

- audio-production, blender, color-grading, detection, diarization, dubbing, imagemagick, ingest;
- media-analysis, motion-graphics, nle-bridge, publish, qc, slide-sync, sound-design, subtitle, thumbnail, voice-enhance.

Their product code removes its work directories in a `finally` or uses a context manager.

Velisa's own tests were not part of this run. `/tmp` also held 24 `control-room-test-*` directories, from `dashboard/control-room/test/fixtures.ts`, and 26 `registry_*` directories, from `registry/tests/`. They fall under the same rule.

## Decision

Every temporary directory made by a component, in its product code or in its tests, follows five rules.

1. **Prefixed.** The name starts with the component's prefix, for example `ves-`, `hfs-`, `rfs-` or `artifacts-skill-exec-`. A bare `mkdtemp()` / `TemporaryDirectory()` is not allowed. The prefix is how a leftover is traced to its owner.
2. **Always removed.** The code that makes a directory removes it on every path out:
   - **Product code:** a context manager (`with tempfile.TemporaryDirectory(...)`) or `try` / `finally`. A long-running process removes it on SIGTERM too, for example by turning SIGTERM into an exception (artifacts-skill's `treat_sigterm_as_interrupt`).
   - **Tests:** a test fixture (pytest `tmp_path`) or one helper that ties each directory to its owner. A TestCase instance gets `addCleanup`. A TestCase class gets `addClassCleanup`, which also runs when `setUpClass` fails. `tearDownClass` alone is not enough, because unittest skips it after a failed `setUpClass`.
   - **Backstop:** `atexit`, plus a SIGTERM handler that removes the directories and then ends the process by SIGTERM. Under `node --test`, a `process.on("exit")` and SIGINT / SIGTERM handler in the helper does the same job, because each test file runs in its own process.
   - **Never:** a path made inline, as in `f(tempfile.mkdtemp())`, because nothing keeps the path.
3. **Movable.** The tests honour `TMPDIR` (Python's `tempfile` and Node's `os.tmpdir()` already do). A test helper may also offer its own variable, `<PREFIX>_TEST_TMPDIR`. No hard-coded `/tmp/` path is written to.
4. **Kept only on request.** Keeping a directory for debugging is an explicit opt-in, such as `<PREFIX>_KEEP_TEST_TMP=1` or a `--keep-*` flag on a tool. When something is kept, its path is printed. A tool that hands a directory to its caller (a clone or a staging area that outlives the call) says so in its result and offers a way to have it removed.
5. **Tested.** Each repository has a test that runs part of its own suite with `TMPDIR` set to an empty directory and asserts that the directory is empty afterwards. Where the repository has a helper, a static check also fails on a temporary directory made any other way. Examples: `tests/test_tmp_dirs.py` in video-editing-skill and remotion-ffmpeg-skill, and `tests/tmp-dirs.test.mjs` in hyperframes-skill.

A process killed with SIGKILL cannot clean up. That is the one leftover the rules accept.

## Consequences

- A full test run of the fixed repositories now leaves nothing in the OS temp directory. Run them again with `TMPDIR` set to an empty directory to check.
- New code gets the rule from review and from each repository's own test. Velisa runs no ecosystem-wide check yet. A later decision can add one to skillpact's conformance job (ADR-014): run a skill's tests with an empty `TMPDIR` and list what is left.
- system-intelligence keeps GitHub clones by design, and its module docstring says so. Under rule 4 the clone should be removed when the command ends, unless a `--keep-clone` option is given. That is a behaviour change to system-intelligence's CLI, so it is left to that repository as a follow-up.
- Leftovers already on a machine are not removed by these fixes. Remove them by prefix (for example `/tmp/hfs-*`, `/tmp/ves-*`, `/tmp/rfs-*`), and only when no test run is in progress.
