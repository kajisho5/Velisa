"""The reusable checks of ADR-022 (decision D36): changelog-check.yml, release-guard.yml and
contract-file-check.yml. The inline checkers of the first two are taken out of the workflow files
and run against scratch files and scratch git repositories, offline.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
GIT = shutil.which("git")


def inline_script(workflow: str) -> str:
    text = (WORKFLOWS / workflow).read_text(encoding="utf-8")
    m = re.search(r"python3 - <<'PY'\n(.*?)\n +PY\n", text, re.S)
    assert m, f"no inline script in {workflow}"
    return textwrap.dedent(m.group(1)) + "\n"


class Scratch(unittest.TestCase):
    """A scratch directory with the velisa-test- prefix, removed on every path out (ADR-021)."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="velisa-test-"))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def write(self, name: str, text: str) -> None:
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args: str) -> str:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid", GIT_CONFIG_GLOBAL=os.devnull)
        out = subprocess.run(["git", *args], cwd=self.dir, env=env, check=True, capture_output=True, text=True)
        return out.stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run_script(self, workflow: str, **env: str) -> subprocess.CompletedProcess:
        script = self.dir.parent / f"{self.dir.name}.py"
        script.write_text(inline_script(workflow), encoding="utf-8")
        self.addCleanup(script.unlink, missing_ok=True)
        full = {k: v for k, v in os.environ.items() if not k.startswith(("CHANGELOG", "TAG", "REF_"))}
        full.update(env)
        return subprocess.run([sys.executable, "-I", str(script)], cwd=self.dir, env=full,
                              capture_output=True, text=True)


FORMS = """# Changelog

## Unreleased

- something

## v1.3.0 - 2026-11-19
## 1.2.0 - 2026-11-13
## v1.1.0 — 2026-11-12
## v1.0.2 (2026-11-11)
## [1.0.1](https://github.com/o/r/compare/v1.0.0...v1.0.1) (2026-11-10)
## 1.0.0
## v0.1.0 — Initial release

```
## not a heading inside a fence
```
"""


class ChangelogCheckTests(Scratch):
    def check(self, **env):
        env.setdefault("REQUIRE_VERSION_HEADING", "never")
        return self.run_script("changelog-check.yml", **env)

    def test_every_heading_form_the_skills_use_passes(self):
        self.write("CHANGELOG.md", FORMS)
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("7 version heading(s), newest 1.3.0", result.stdout)

    def test_a_malformed_version_heading_fails(self):
        self.write("CHANGELOG.md", "## v1.1.0 - 2026-11-19\n## v1.0 - 2026-11-01\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("CHANGELOG.md:2: version heading in the wrong form", result.stdout)

    def test_an_unknown_heading_fails_unless_allowed(self):
        self.write("CHANGELOG.md", "## v1.0.0 (2026-11-19)\n\n## What's Changed\n")
        self.assertEqual(self.check().returncode, 1)
        self.assertEqual(self.check(OTHER_HEADINGS=r"^## ").returncode, 0)

    def test_a_malformed_version_heading_fails_even_when_other_headings_allow_anything(self):
        self.write("CHANGELOG.md", "## v1.0.0 (2026-11-19)\n## 1.0 later\n")
        self.assertEqual(self.check(OTHER_HEADINGS=r"^## ").returncode, 1)

    def test_versions_appear_once_newest_first(self):
        self.write("CHANGELOG.md", "## 1.0.0\n## 1.1.0\n## 1.0.0\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("1.1.0 comes after 1.0.0", result.stdout)
        self.assertIn("1.0.0 again (first at line 1)", result.stdout)
        self.assertEqual(self.check(REQUIRE_DESCENDING="false").returncode, 1)  # duplicates still fail

    def test_stop_at_leaves_older_history_alone(self):
        self.write("CHANGELOG.md", "## 0.2.0\n## Changelog\n## 0.2.0\n## odd\n")
        self.assertEqual(self.check().returncode, 1)
        self.assertEqual(self.check(STOP_AT=r"^## Changelog$").returncode, 0)

    def test_a_missing_changelog_fails(self):
        self.assertEqual(self.check().returncode, 1)

    @unittest.skipUnless(GIT, "git is not installed")
    def test_a_version_bump_needs_its_heading(self):
        self.git("init", "-q")
        self.write("pyproject.toml", '[project]\nname = "x"\nversion = "0.2.0"\n')
        self.write("CHANGELOG.md", "## 0.2.0 - 2026-11-01\n")
        base = self.commit("base")
        self.write("pyproject.toml", '[project]\nname = "x"\nversion = "0.3.0"\n')
        self.commit("bump")
        result = self.check(REQUIRE_VERSION_HEADING="bump", BASE_REF=base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("version 0.2.0 -> 0.3.0", result.stdout)
        self.assertIn("no heading for 0.3.0, the version in pyproject.toml", result.stdout)
        self.write("CHANGELOG.md", "## 0.3.0 - 2026-11-19\n## 0.2.0 - 2026-11-01\n")
        self.commit("changelog")
        result = self.check(REQUIRE_VERSION_HEADING="bump", BASE_REF=base)
        self.assertEqual(result.returncode, 0, result.stdout)

    @unittest.skipUnless(GIT, "git is not installed")
    def test_an_unchanged_version_needs_no_new_heading_unless_always(self):
        self.git("init", "-q")
        self.write("package.json", json.dumps({"name": "x", "version": "1.0.0"}))
        self.write("CHANGELOG.md", "## Unreleased\n")
        base = self.commit("base")
        self.assertEqual(self.check(REQUIRE_VERSION_HEADING="bump", BASE_REF=base).returncode, 0)
        self.assertEqual(self.check(REQUIRE_VERSION_HEADING="always", BASE_REF=base).returncode, 1)

    @unittest.skipUnless(GIT, "git is not installed")
    def test_the_version_must_not_go_down(self):
        self.git("init", "-q")
        self.write("VERSION", "1.2.0\n")
        self.write("CHANGELOG.md", "## 1.2.0\n## 1.1.0\n")
        base = self.commit("base")
        self.write("VERSION", "1.1.0\n")
        self.commit("down")
        result = self.check(REQUIRE_VERSION_HEADING="bump", BASE_REF=base)
        self.assertEqual(result.returncode, 1)
        self.assertIn("the version goes down, 1.2.0 -> 1.1.0", result.stdout)

    def test_version_pattern_reads_any_file(self):
        self.write("src/pkg/__init__.py", '__version__ = "0.4.0"\n')
        self.write("CHANGELOG.md", "## 0.4.0\n")
        result = self.check(REQUIRE_VERSION_HEADING="always", VERSION_FILE="src/pkg/__init__.py",
                            VERSION_PATTERN=r'^__version__ = "(?P<version>[^"]+)"')
        self.assertEqual(result.returncode, 0, result.stdout)


@unittest.skipUnless(GIT, "git is not installed")
class ReleaseGuardTests(Scratch):
    def setUp(self):
        super().setUp()
        self.git("init", "-q")

    def release(self, tag: str, version: str | None) -> None:
        if version is not None:
            self.write("contract/contract.json", json.dumps({"skill_id": "x", "version": version}) + "\n")
        else:
            self.write("README.md", tag)
        self.commit(tag)
        self.git("tag", tag)

    def guard(self, **env):
        return self.run_script("release-guard.yml", **env)

    def test_the_newest_tag_is_checked(self):
        self.release("v0.9.0", "0.8.0")  # old and wrong, but not the newest
        self.release("v0.10.0", "0.10.0")
        result = self.guard()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("latest release tag: v0.10.0", result.stdout)

    def test_a_mismatch_fails(self):
        self.release("v1.0.0", "0.9.0")
        result = self.guard()
        self.assertEqual(result.returncode, 1)
        self.assertIn("says version '0.9.0', the tag says '1.0.0'", result.stdout)

    def test_the_pushed_tag_or_the_given_tag(self):
        self.release("v1.0.0", "0.9.0")
        self.release("v1.1.0", "1.1.0")
        self.assertEqual(self.guard(REF_TYPE="tag", REF_NAME="v1.0.0").returncode, 1)
        self.assertEqual(self.guard(TAG="v1.0.0").returncode, 1)
        self.assertEqual(self.guard(REF_TYPE="branch", REF_NAME="main").returncode, 0)

    def test_a_tag_pattern_with_a_prefix(self):
        self.release("blender-skill-v0.31.1", "0.31.1")
        self.assertIn("nothing to check", self.guard().stdout)
        result = self.guard(TAG_PATTERN=r"^blender-skill-v(?P<version>\d+\.\d+\.\d+)$")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_tag_without_the_contract_file(self):
        self.release("v0.1.0", None)
        self.assertEqual(self.guard().returncode, 1)
        result = self.guard(ALLOW_MISSING="true")
        self.assertEqual(result.returncode, 0)
        self.assertIn("::warning::", result.stdout)


class WorkflowShapeTests(unittest.TestCase):
    def read(self, name: str) -> str:
        return (WORKFLOWS / name).read_text(encoding="utf-8")

    def test_all_three_are_reusable_and_read_only(self):
        for name in ("changelog-check.yml", "release-guard.yml", "contract-file-check.yml"):
            text = self.read(name)
            self.assertRegex(text, r"(?m)^on:\n  workflow_call:", name)
            self.assertRegex(text, r"(?m)^permissions:\n  contents: read\n", name)
            self.assertNotIn("write", text.split("\njobs:", 1)[1].split("run:", 1)[0], name)
            self.assertIn("persist-credentials: false", text, name)

    def test_inputs_reach_scripts_through_env_only(self):
        for name in ("changelog-check.yml", "release-guard.yml", "contract-file-check.yml"):
            for block in re.findall(r"run: \|\n(.*?)(?=\n      - |\Z)", self.read(name), re.S):
                self.assertNotIn("${{", block, name)

    def test_contract_file_check_runs_the_generator_with_check(self):
        text = self.read("contract-file-check.yml")
        self.assertIn('python "$SCRIPT" --check', text)
        self.assertIn('node "$SCRIPT" --check', text)
        self.assertIn("python) default=contract/generate.py", text)
        self.assertIn("node) default=contract/generate.mjs", text)


if __name__ == "__main__":
    unittest.main()
