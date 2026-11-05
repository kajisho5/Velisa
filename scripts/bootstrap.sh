#!/usr/bin/env bash
# Install the whole Velisa ecosystem into one workspace directory, driven by
# ../ecosystem.json (the single list of repositories). Normally reached through ../install.sh;
# running it directly from an OS checkout works the same.
#
# Usage:
#   ./scripts/bootstrap.sh [--dir DIR] [--with-optional] [--no-update] [--no-claude-skills] [--no-codex-skills] [--dry-run]
#
#   --dir DIR            workspace (default: $VELISA_HOME, else $AVOS_HOME, else ~/velisa-workspace;
#                        ~/ai-video-os instead when only that pre-rename workspace exists)
#   --with-optional      also install components marked "optional" (DVD/Blu-ray authoring)
#   --no-update          do not `git pull` repositories that are already cloned
#   --no-claude-skills   do not link Skills into ~/.claude/skills
#   --no-codex-skills    do not link Skills into ~/.agents/skills (where Codex looks)
#   --dry-run            print what would be done, change nothing
#
# What it does, per repository in ecosystem.json (except "planned" ones, which have no
# repository yet and are only reported):
#   1. Clone it under DIR, or fast-forward an existing clone to the latest origin (a clone
#      with local changes or diverged history is left alone and reported, never reset).
#   2. install=pip: `pip install -e` into DIR/.venv (or the already-active virtualenv).
#      A repository that has no pyproject.toml yet is reported as "no package yet", not failed.
#      install=npm: `npm ci` in the checkout (needs Node.js; reported if missing).
#      install=checkout: nothing to install; the agent runs it from the checkout.
#      "path": the package lives in that subdirectory of the repository.
#   3. If it has a SKILL.md (at its root, or skills/<name>/SKILL.md), symlink it to
#      ~/.claude/skills/<name from SKILL.md> (Claude Code) and ~/.agents/skills/<name> (Codex).
#      An existing entry there that points somewhere else is reported, never replaced.
# Then checks ffmpeg/ffprobe (6.1+), Python (3.10+) and Blender -- a missing or too old one is a note,
# never installed or fatal -- and runs `video-agent doctor` from the agent checkout.
#
# Safe to interrupt and re-run: nothing is deleted, no remote is changed, nothing is forced.
set -euo pipefail

OS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$OS_ROOT/ecosystem.json"
# Workspace: $VELISA_HOME; else $AVOS_HOME (its name before the rename to Velisa); else ~/velisa-workspace,
# unless only the pre-rename default ~/ai-video-os exists -- then that one, so an existing install keeps
# being updated in place (docs/RENAMING.md, ADR-015). ../install.sh resolves it the same way.
if [ -n "${VELISA_HOME:-}" ]; then
  WORKSPACE="$VELISA_HOME"
elif [ -n "${AVOS_HOME:-}" ]; then
  WORKSPACE="$AVOS_HOME"
elif [ ! -e "$HOME/velisa-workspace" ] && [ -d "$HOME/ai-video-os" ]; then
  WORKSPACE="$HOME/ai-video-os"
else
  WORKSPACE="$HOME/velisa-workspace"
fi
UPDATE=1
LINK_SKILLS=1
LINK_CODEX=1
DRY_RUN=0
WITH_OPTIONAL=0
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) WORKSPACE="${2:?--dir needs a directory}"; shift 2 ;;
    --dir=*) WORKSPACE="${1#--dir=}"; shift ;;
    --no-update) UPDATE=0; shift ;;
    --no-claude-skills) LINK_SKILLS=0; shift ;;
    --no-codex-skills) LINK_CODEX=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --with-optional) WITH_OPTIONAL=1; shift ;;
    -h|--help) sed -n '2,32p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
done

for cmd in git python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "!! $cmd is required but not on PATH" >&2; exit 1; }
done
[ -f "$MANIFEST" ] || { echo "!! manifest not found: $MANIFEST" >&2; exit 1; }

run() {
  if [ "$DRY_RUN" = 1 ]; then echo "   [dry-run] $*"; else "$@"; fi
}

# One line per component: repo<TAB>install<TAB>extras(comma-separated)<TAB>package subdirectory,
# "-" for an empty field (read collapses empty tab-separated fields). "planned" components
# (no repository yet) are not installed; they are listed on stderr and reported at the end.
TMP_PLANNED="$(mktemp)"
trap 'rm -f "$TMP_PLANNED"' EXIT
COMPONENTS="$(python3 - "$MANIFEST" "$WITH_OPTIONAL" 2>"$TMP_PLANNED" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
for c in m["components"]:
    if c.get("status") == "planned":
        print("planned: " + c["repo"], file=sys.stderr)
        continue
    if c.get("optional") and sys.argv[2] != "1":
        continue
    print("\t".join([c["repo"], c["install"], ",".join(c.get("extras", [])) or "-", c.get("path") or "-"]))
EOF
)" || { cat "$TMP_PLANNED" >&2; echo "!! could not read $MANIFEST" >&2; exit 1; }
ORG="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["org"])' "$MANIFEST")"

if [ "$DRY_RUN" = 0 ]; then mkdir -p "$WORKSPACE"; WORKSPACE="$(cd "$WORKSPACE" && pwd)"; fi
echo "==> Workspace: $WORKSPACE"

declare -a SUMMARY=()
note() { SUMMARY+=("$1"); }
while read -r _ planned; do
  [ -n "$planned" ] && note "$planned: planned, repository not created yet"
done < "$TMP_PLANNED"

echo "--- 1. Repositories ---"
while IFS=$'\t' read -r repo _ _; do
  dir="$WORKSPACE/$repo"
  if [ -d "$dir/.git" ]; then
    if [ "$UPDATE" = 0 ]; then
      echo "   $repo: present (not updated, --no-update)"
    elif [ -n "$(git -C "$dir" status --porcelain 2>/dev/null)" ]; then
      echo "!! $repo: local changes, not updated"; note "$repo: local changes, left as is"
    elif run git -C "$dir" pull --ff-only -q; then
      echo "   $repo: up to date ($(git -C "$dir" log -1 --format='%h %ad' --date=short 2>/dev/null))"
    else
      echo "!! $repo: could not fast-forward (diverged or offline), left as is"; note "$repo: not updated"
    fi
  else
    echo "   $repo: cloning"
    run git clone -q "https://github.com/$ORG/$repo" "$dir" || { echo "!! $repo: clone failed"; note "$repo: clone failed"; }
  fi
done <<< "$COMPONENTS"

# "MAJOR MINOR" of a version string such as "n6.1", "6.1.1-3ubuntu5" or "3.12.4", or nothing when
# it does not start with a release number (an FFmpeg git build: "N-115000-g...", "2024-05-01-git-...").
major_minor() {
  printf '%s\n' "$1" | sed -n 's/^n\{0,1\}\([0-9][0-9]*\)\.\([0-9][0-9]*\).*/\1 \2/p'
}
# True when version "$1 $2" (major minor) is older than "$3 $4".
older_than() {
  [ "$1" -lt "$3" ] || { [ "$1" -eq "$3" ] && [ "$2" -lt "$4" ]; }
}

echo "--- 2. Python environment ---"
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PY="$VIRTUAL_ENV/bin/python"
  echo "   using the active virtualenv: $VIRTUAL_ENV"
else
  VENV="$WORKSPACE/.venv"
  [ -x "$VENV/bin/python" ] || run python3 -m venv "$VENV"
  PY="$VENV/bin/python"
  echo "   virtualenv: $VENV"
fi
# The interpreter the packages will run on: the virtualenv's once it exists, else the python3 it is made from.
py_check="python3"; [ -x "$PY" ] && py_check="$PY"
py_version="$("$py_check" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
# shellcheck disable=SC2046  # word splitting of "MAJOR MINOR" is the point
if [ -n "$(major_minor "$py_version")" ] && older_than $(major_minor "$py_version") 3 10; then
  echo "!! Python $py_version ($py_check) is older than 3.10, which ffmpeg-skill and the Python Skills require:"
  echo "   install Python 3.10+ and re-run (or activate a 3.10+ virtualenv first)"
  note "Python $py_version is older than 3.10 (required)"
fi
run "$PY" -m pip install -q --upgrade pip || true

echo "--- 3. Packages ---"
while IFS=$'\t' read -r repo install extras sub; do
  dir="$WORKSPACE/$repo"
  [ "$sub" = "-" ] || dir="$dir/$sub"
  [ "$DRY_RUN" = 1 ] || [ -d "$dir" ] || continue
  case "$install" in
    pip)
      if [ "$DRY_RUN" = 0 ] && [ ! -f "$dir/pyproject.toml" ]; then
        echo "   $repo: no package yet (no pyproject.toml), cloned only"; note "$repo: no package yet"
        continue
      fi
      target="$dir"; [ "$extras" = "-" ] || target="${dir}[$extras]"
      echo "   $repo: pip install -e"
      run "$PY" -m pip install -q -e "$target" || { echo "!! $repo: install failed"; note "$repo: pip install failed"; }
      ;;
    npm)
      if ! command -v npm >/dev/null 2>&1; then
        echo "!! $repo: npm not found (install Node.js), not installed"; note "$repo: needs Node.js/npm"
        continue
      fi
      echo "   $repo: npm ci"
      if [ "$DRY_RUN" = 1 ] || [ -f "$dir/package-lock.json" ]; then
        run npm --prefix "$dir" ci --no-audit --no-fund --loglevel=error || { echo "!! $repo: npm ci failed"; note "$repo: npm install failed"; }
      else
        run npm --prefix "$dir" install --no-audit --no-fund --loglevel=error || { echo "!! $repo: npm install failed"; note "$repo: npm install failed"; }
      fi
      ;;
    checkout) echo "   $repo: checkout only (run from the checkout)" ;;
    *) echo "!! $repo: unknown install kind '$install' in ecosystem.json"; note "$repo: unknown install kind" ;;
  esac
done <<< "$COMPONENTS"

echo "--- 4. Claude Code / Codex skills ---"
# Each Skill is a folder with SKILL.md: the repository root, or skills/<name>/ inside it. It is linked into
# every target directory: Claude Code reads ~/.claude/skills, Codex reads ~/.agents/skills.
link_skill() {   # $1 skill folder, $2 target directory
  local src="$1" target="$2" name link
  name="$(sed -n 's/^name:[[:space:]]*//p' "$src/SKILL.md" | head -1 | tr -d "\"'\r")"
  name="${name:-$(basename "$src")}"
  link="$target/$name"
  if [ -L "$link" ] && [ "$(readlink "$link")" = "$src" ]; then
    echo "   $name: linked ($target)"
  elif [ -e "$link" ] || [ -L "$link" ]; then
    local shown="$target"
    case "$target" in "$HOME"/*) shown="~${target#"$HOME"}" ;; esac   # bash 3.2 (macOS) keeps a backslash in ${x/#$HOME/\~}
    echo "!! $name: $link already exists and is not this checkout, left as is"; note "$name: $shown entry not replaced"
  else
    run ln -s "$src" "$link" && echo "   $name: linked -> $src ($target)"
  fi
}
TARGETS=()
[ "$LINK_SKILLS" = 1 ] && TARGETS+=("$CLAUDE_SKILLS_DIR")
[ "$LINK_CODEX" = 1 ] && TARGETS+=("$CODEX_SKILLS_DIR")
if [ "${#TARGETS[@]}" = 0 ]; then
  echo "   skipped (--no-claude-skills --no-codex-skills)"
else
  for target in "${TARGETS[@]}"; do run mkdir -p "$target"; done
  while IFS=$'\t' read -r repo _ _; do
    dir="$WORKSPACE/$repo"
    for src in "$dir" "$dir"/skills/*; do
      [ -f "$src/SKILL.md" ] || continue
      for target in "${TARGETS[@]}"; do link_skill "$src" "$target"; done
    done
  done <<< "$COMPONENTS"
fi

echo "--- 5. ffmpeg / ffprobe / blender ---"
# The ffmpeg ffmpeg-skill will run: what PATH gives, except that on macOS a Homebrew lean `ffmpeg`
# is replaced by the keg-only `ffmpeg-full` of the same prefix when that is installed, as
# ffmpeg-skill itself does (scripts/_common/runner.py there).
find_ffmpeg() {   # $1 ffmpeg or ffprobe
  local found real prefix formula
  found="$(command -v "$1" 2>/dev/null)" || return 1
  if [ "$(uname -s)" = Darwin ]; then
    real="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$found" 2>/dev/null || true)"
    case "$real" in
      */Cellar/*)
        prefix="${real%%/Cellar/*}"; formula="${real#*/Cellar/}"; formula="${formula%%/*}"
        case "$formula" in
          ffmpeg|ffmpeg@[0-9]*) [ -x "$prefix/opt/ffmpeg-full/bin/$1" ] && found="$prefix/opt/ffmpeg-full/bin/$1" ;;
        esac ;;
    esac
  fi
  printf '%s\n' "$found"
}
ffmpeg_hints() {
  echo "     Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y ffmpeg fonts-dejavu-core"
  echo "     macOS:          brew install ffmpeg-full   # not the plain ffmpeg formula: it lacks subtitles/drawtext/zscale"
  # shellcheck disable=SC2016  # printed for the user to run, not expanded here
  echo '                     (keg-only; ffmpeg-skill prefers it over a Homebrew ffmpeg on PATH. With none on PATH:'
  # shellcheck disable=SC2016
  echo '                      export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH" in your shell profile)'
  echo "     Windows:        winget install Gyan.FFmpeg   (see the Windows note in README.md)"
}
FFMPEG="$(find_ffmpeg ffmpeg || true)"
FFPROBE="$(find_ffmpeg ffprobe || true)"
if [ -n "$FFMPEG" ] && [ -n "$FFPROBE" ]; then
  ff_line="$("$FFMPEG" -version 2>/dev/null | sed -n '1p' || true)"
  ff_version="$(printf '%s\n' "$ff_line" | sed -n 's/^ffmpeg version \([^ ]*\).*/\1/p')"
  echo "   found: ${ff_line:-no version line} ($FFMPEG)"
  if [ "$(uname -s)" = Darwin ]; then
    case "$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$FFMPEG" 2>/dev/null || true)" in
      */Cellar/ffmpeg/*|*/Cellar/ffmpeg@[0-9]*/*)   # find_ffmpeg would have taken ffmpeg-full if it were installed
        echo "!! this is Homebrew's lean ffmpeg, without the subtitles/drawtext/zscale filters: brew install ffmpeg-full"
        note "Homebrew lean ffmpeg: brew install ffmpeg-full" ;;
    esac
  fi
  # shellcheck disable=SC2046  # word splitting of "MAJOR MINOR" is the point
  if [ -z "$(major_minor "$ff_version")" ]; then
    echo "   note: ffmpeg version '${ff_version:-?}' is not a release number (a git build?), so 6.1+ was not checked;"
    echo "         npx ffmpeg-skill doctor reports what this build can do"
  elif older_than $(major_minor "$ff_version") 6 1; then
    echo "!! ffmpeg $ff_version is older than 6.1, which ffmpeg-skill requires (its tools refuse it). Install a newer one:"
    ffmpeg_hints
    echo "   Then run: npx ffmpeg-skill doctor   (checks the filters and libass the tools need)"
    note "ffmpeg $ff_version is older than 6.1 (required by ffmpeg-skill)"
  fi
else
  missing=""
  [ -n "$FFMPEG" ] || missing="ffmpeg"
  [ -n "$FFPROBE" ] || missing="${missing:+$missing and }ffprobe"
  echo "!! $missing not found on PATH: every ffmpeg-skill tool stops with exit 127 (missing_tool) until"
  echo "   FFmpeg 6.1+ is installed. This script never installs system packages; install it yourself, e.g.:"
  ffmpeg_hints
  if [ "$(uname -s)" = Darwin ] && command -v brew >/dev/null 2>&1 \
     && [ -x "$(brew --prefix 2>/dev/null)/opt/ffmpeg-full/bin/ffmpeg" ]; then
    # shellcheck disable=SC2016  # printed for the user to run
    echo '   ffmpeg-full is installed but keg-only, so not on PATH: add export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH" to your shell profile'
  fi
  echo "   Then run: npx ffmpeg-skill doctor   (checks the filters and libass the tools need)"
  note "$missing missing (FFmpeg 6.1+ needed)"
fi

if [ -d "$WORKSPACE/blender-skill" ] && ! command -v blender >/dev/null 2>&1; then
  echo "!! blender not found: blender-skill needs it (https://www.blender.org/download/, or: brew install --cask blender)"
  note "blender missing (blender-skill)"
fi

echo "--- 6. video-agent doctor ---"
AGENT_DIR="$WORKSPACE/video-production-agent"
if [ "$DRY_RUN" = 1 ]; then
  echo "   [dry-run] (cd $AGENT_DIR && $PY -m video_agent.cli doctor)"
elif [ -d "$AGENT_DIR" ]; then
  (cd "$AGENT_DIR" && "$PY" -m video_agent.cli doctor) || note "video-agent doctor reported problems (see above)"
fi

echo
if [ ${#SUMMARY[@]} -eq 0 ]; then
  echo "==> Done. Everything in ecosystem.json is installed."
else
  echo "==> Done, with notes:"
  printf '   - %s\n' "${SUMMARY[@]}"
fi
[ -n "${VIRTUAL_ENV:-}" ] || echo "    Use it: source \"$WORKSPACE/.venv/bin/activate\" && video-agent doctor"
