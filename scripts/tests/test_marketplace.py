"""The Claude Code marketplace is generated from ecosystem.json (scripts/marketplace.py), and update
notices come from scripts/skill-updates.py. Offline: the GitHub API and git ls-remote are faked.

    python3 -m unittest discover -s scripts/tests -v
"""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))


def load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


marketplace = load("marketplace", "marketplace.py")
updates = load("skill_updates", "skill-updates.py")


class MarketplaceTests(unittest.TestCase):
    def test_committed_files_match_ecosystem_json(self):
        self.assertEqual(marketplace.main(["--check"]), 0, "run: python3 scripts/marketplace.py")

    def test_entries(self):
        mk, meta = marketplace.build(MANIFEST)
        names = [e["name"] for e in mk["plugins"]]
        plugins = [c for c in MANIFEST["components"] if c.get("plugin") and c["status"] != "planned"]
        self.assertEqual(names, ["velisa", "velisa-maintainer"] + [c["repo"] for c in plugins])
        self.assertEqual(len(names), len(set(names)))
        for e in mk["plugins"][2:]:
            self.assertEqual(e["source"], {"source": "github", "repo": f"{MANIFEST['org']}/{e['name']}"})
            self.assertNotIn("version", e, "no version: installs follow each repository's commits")
        self.assertEqual(meta["dependencies"], [c["repo"] for c in plugins if not c.get("optional")])
        self.assertNotIn("velisa-maintainer", meta["dependencies"], "installing the OS does not install the maintainer tools")
        self.assertFalse(mk["name"].startswith(("claude", "anthropic")))

    def test_routing_skill_names_every_component(self):
        text = (ROOT / "plugins/velisa/skills/wakeup/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: wakeup\n"))
        for c in MANIFEST["components"]:
            if c["status"] != "planned":
                self.assertIn(f"`{c['repo']}`", text)

    def test_review_guide_ships_with_the_routing_skill(self):
        """review.md sits next to SKILL.md (inside the meta plugin's source, so it is installed with it), SKILL.md
        links it, and every relative link in either file resolves to a file inside the plugin."""
        mk, _ = marketplace.build(MANIFEST)
        plugin_dir = (ROOT / mk["plugins"][0]["source"]).resolve()
        skill_dir = ROOT / "plugins/velisa/skills/wakeup"
        review = skill_dir / "review.md"
        self.assertTrue(review.is_file())
        self.assertTrue(review.resolve().is_relative_to(plugin_dir))
        self.assertIn("](review.md)", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        for doc in (skill_dir / "SKILL.md", review):
            for target in re.findall(r"\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                path = (doc.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(path.is_file(), f"{doc.name}: broken link {target}")
                self.assertTrue(path.is_relative_to(plugin_dir), f"{doc.name}: {target} is outside the plugin")


class MaintainerPluginTests(unittest.TestCase):
    """plugins/velisa-maintainer (ADR-028, D42): a local plugin with one skill, its references and three commands."""
    plugin = ROOT / "plugins/velisa-maintainer"
    skill = plugin / "skills/velisa-maintainer"

    def test_marketplace_entry_points_at_the_plugin(self):
        mk, _ = marketplace.build(MANIFEST)
        entry = mk["plugins"][1]
        self.assertEqual(entry["name"], "velisa-maintainer")
        self.assertEqual((ROOT / entry["source"]).resolve(), self.plugin.resolve())
        meta = json.loads((self.plugin / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["name"], entry["name"])
        self.assertNotIn("dependencies", meta)

    def test_skill_is_short_and_links_every_reference(self):
        text = (self.skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: velisa-maintainer\ndescription: "))
        self.assertLessEqual(len(text.splitlines()), 60, "keep SKILL.md short; details go to references/")
        refs = sorted(p.name for p in (self.skill / "references").glob("*.md"))
        self.assertEqual(refs, ["contract-diff.md", "releases.md", "repin.md", "schemas.md", "session-limits.md", "specs.md"])
        for name in refs:
            self.assertIn(f"](references/{name})", text)

    def test_references_cover_the_maintenance_topics(self):
        ref = {p.name: p.read_text(encoding="utf-8") for p in (self.skill / "references").glob("*.md")}
        for word in ("ADR-117", "repin: needs review", "verify", "workflow_dispatch", "bot/repin"):
            self.assertIn(word, ref["repin.md"])
        for word in ("release_gate.py", "dependencies", "ADR-022", "ADR-023", "Test the release commit before pushing it"):
            self.assertIn(word, ref["releases.md"])
        for word in ("ADR-020", "contract:breaking", "si contract-diff"):
            self.assertIn(word, ref["contract-diff.md"])
        for word in ("ADR-026", "ADR-027", "30000/1001", "CANCELLED"):
            self.assertIn(word, ref["specs.md"])
        for word in ("ADR-024", "ADR-025", "--export", "manifest.json"):
            self.assertIn(word, ref["schemas.md"])
        for word in ("tag", "branch", "GraphQL", "ready", "PATCH", "@coderabbitai"):
            self.assertIn(word, ref["session-limits.md"])

    def test_commands_and_links(self):
        commands = sorted(p.stem for p in (self.plugin / "commands").glob("*.md"))
        self.assertEqual(commands, ["release", "repin", "roadmap"])
        for p in (self.plugin / "commands").glob("*.md"):
            text = p.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\ndescription: "), p.name)
            self.assertNotIn("graphql", text.lower().replace("never graphql", ""), p.name)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/roadmap.py", (self.plugin / "commands/roadmap.md").read_text(encoding="utf-8"))
        for doc in [self.skill / "SKILL.md", *(self.skill / "references").glob("*.md")]:
            for target in re.findall(r"\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                path = (doc.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(path.is_file(), f"{doc.name}: broken link {target}")
                self.assertTrue(path.is_relative_to(self.plugin.resolve()), f"{doc.name}: {target} is outside the plugin")


class RoadmapScriptTests(unittest.TestCase):
    roadmap = load("roadmap", "../plugins/velisa-maintainer/scripts/roadmap.py")
    TEXT = """# r

## Steps

- [x] **1. Done thing** — what ([#3](https://example.invalid/3))
  - Done when: it works
- [ ] **2. Real-NLE check** — import the files
  - なぜ要るか：理由
  - Done when: a fixture per NLE
  - Needs: step 1
- [ ] **3a. Parts** — several
  - [x] Part 1: done
  - [ ] Part 2: open
not a step line

## Boundaries
- [ ] **4. Later** — x
"""

    def test_parse(self):
        steps = self.roadmap.parse(self.TEXT)
        self.assertEqual([(s["number"], s["done"]) for s in steps], [("1", True), ("2", False), ("3a", False), ("4", False)])
        self.assertEqual(steps[1]["title"], "Real-NLE check")
        self.assertEqual(steps[1]["notes"], {"なぜ要るか": "理由", "Done when": "a fixture per NLE", "Needs": "step 1"})
        self.assertEqual(steps[2]["parts"], [{"done": True, "text": "Part 1: done"}, {"done": False, "text": "Part 2: open"}])
        self.assertEqual(steps[3]["section"], "Boundaries")

    def test_render_lists_open_steps_only(self):
        out = self.roadmap.render(self.roadmap.parse(self.TEXT), False)
        self.assertNotIn("Done thing", out)
        self.assertIn("- [ ] 2. Real-NLE check\n    Done when: a fixture per NLE\n    Needs: step 1", out)
        self.assertIn("    - [ ] Part 2: open", out)
        self.assertNotIn("Part 1", out)
        self.assertTrue(out.endswith("3 open of 4 steps\n"))
        self.assertIn("Done thing", self.roadmap.render(self.roadmap.parse(self.TEXT), True))
        self.assertIn("no checkbox steps", self.roadmap.render([], False))


class FakeAPI:
    def __init__(self, compare=None):
        self.calls = []
        self.compare = compare or {}
        self.issue = None
        self.comments = []

    def __call__(self, method, path, body=None):
        self.calls.append((method, path))
        if "/compare/" in path:
            return self.compare
        if path.startswith("/repos/o/os/issues?"):
            return [self.issue] if self.issue else []
        if method == "POST" and path.endswith("/issues"):
            self.issue = {"number": 1, "body": body["body"]}
            return self.issue
        if method == "PATCH":
            self.issue["body"] = body["body"]
            return self.issue
        if method == "POST" and path.endswith("/comments"):
            self.comments.append(body["body"])
            return {}
        raise AssertionError(path)


class SkillUpdatesTests(unittest.TestCase):
    manifest = {"org": "o", "components": [{"repo": "a", "status": "active"}, {"repo": "b", "status": "scaffold"}, {"repo": "p", "status": "planned"}]}

    def setUp(self):
        self.heads = {"a": {"branch": "main", "sha": "1" * 40, "release": "v1.0.0"}, "b": {"branch": "main", "sha": "2" * 40, "release": None}}
        self._orig = updates.ls_remote
        updates.ls_remote = lambda org, repo: dict(self.heads[repo])

    def tearDown(self):
        updates.ls_remote = self._orig

    def test_issue_flow_baseline_then_comment_with_mention(self):
        api = FakeAPI(compare={"total_commits": 2, "commits": [{"commit": {"message": "Fix loudness\n\nbody"}}, {"commit": {"message": "Add LUT"}}]})
        text, rc = updates.run_issue(api, self.manifest, "o/os", "owner")
        self.assertEqual((rc, api.comments), (0, []), "first run: baseline only")
        self.assertIn("skill-updates-state", api.issue["body"])
        self.heads["a"] = {"branch": "main", "sha": "3" * 40, "release": "v1.1.0"}
        text, rc = updates.run_issue(api, self.manifest, "o/os", "owner")
        self.assertEqual(len(api.comments), 1)
        c = api.comments[0]
        self.assertIn("@owner", c)
        self.assertIn("tag **v1.1.0** (was v1.0.0)", c)
        self.assertIn("- Fix loudness", c)
        self.assertNotIn("[b]", c)
        updates.run_issue(api, self.manifest, "o/os", "owner")
        self.assertEqual(len(api.comments), 1, "nothing new: no comment")

    def test_unreadable_repository_keeps_its_last_state(self):
        old = {"a": dict(self.heads["a"]), "b": dict(self.heads["b"])}

        def fail(org, repo):
            if repo == "b":
                raise OSError("network down")
            return dict(self.heads[repo])
        updates.ls_remote = fail
        new, found, errors = updates.collect(FakeAPI(), self.manifest, old)
        self.assertEqual(new["b"], old["b"])
        self.assertEqual(found, [])
        self.assertEqual(errors, ["b: network down"])

    def test_version_tags_sort_numerically(self):
        self.assertEqual(max(["v0.9.0", "v0.10.0", "v0.2.1"], key=updates.version_key), "v0.10.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
