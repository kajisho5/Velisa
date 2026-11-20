#!/usr/bin/env python3
"""List the open steps of a Velisa repository's roadmap (used by the /roadmap command).

    python3 roadmap.py qc-skill                 open steps of kajisho5/qc-skill's ECOSYSTEM_ROADMAP.md (through `gh api`)
    python3 roadmap.py qc-skill --all           every step, done ones marked
    python3 roadmap.py path/to/ROADMAP.md       a local file instead
    python3 roadmap.py qc-skill --json          the steps as JSON

A step is a top-level checkbox item (`- [ ] **7. Title** — what`), with its indented lines: "Done when:", "Needs:",
"Why:" / "なぜ要るか", and status notes. Nested checkboxes are parts of the step above them. Standard library only;
the network is reached through the `gh` CLI (REST), never GraphQL.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

OWNER = "kajisho5"
# where a repository keeps its roadmap, first match wins; Velisa's ecosystem map is docs/ecosystem/ROADMAP.md
CANDIDATES = ("ECOSYSTEM_ROADMAP.md", "docs/ecosystem/ROADMAP.md", "ROADMAP.md")
STEP = re.compile(r"^- \[(?P<mark>[ xX])\] (?P<text>.+)$")
TITLE = re.compile(r"^\*\*(?:(?P<num>[0-9]+[a-z]?)\.\s*)?(?P<title>.+?)\*\*\s*(?:[—–-]\s*(?P<what>.*))?$")
NOTE = re.compile(r"^\s+- (?P<key>Done when|Needs|Why|なぜ要るか|Status[^:]*|Not met[^:]*|Open|Partly done[^:]*)\s*[:：]\s*(?P<value>.*)$")


def parse(text: str) -> List[Dict[str, object]]:
    """Every top-level checkbox step, in order, with its notes."""
    steps: List[Dict[str, object]] = []
    section = ""
    current: Optional[Dict[str, object]] = None
    for line in text.splitlines():
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            current = None
            continue
        m = STEP.match(line)
        if m:
            t = TITLE.match(m.group("text").strip())
            step: Dict[str, object] = {
                "done": m.group("mark") != " ",
                "section": section,
                "number": t.group("num") if t else None,
                "title": (t.group("title") if t else m.group("text")).strip(),
                "what": ((t.group("what") or "") if t else "").strip(),
                "notes": {},
                "parts": [],
            }
            steps.append(step)
            current = step
            continue
        if current is None:
            continue
        if line and not line.startswith((" ", "\t")):
            current = None
            continue
        sub = re.match(r"^\s+- \[(?P<mark>[ xX])\] (?P<text>.+)$", line)
        if sub:
            current["parts"].append({"done": sub.group("mark") != " ", "text": sub.group("text").strip()})  # type: ignore[union-attr]
            continue
        n = NOTE.match(line)
        if n:
            notes = current["notes"]  # type: ignore[assignment]
            key = n.group("key")
            notes[key] = (notes[key] + " " if key in notes else "") + n.group("value").strip()  # type: ignore[index,operator]
    return steps


def fetch(repo: str) -> str:
    """The roadmap of kajisho5/<repo> on its default branch, through the REST contents API."""
    last = ""
    for path in CANDIDATES:
        r = subprocess.run(["gh", "api", f"repos/{OWNER}/{repo}/contents/{path}", "-q", ".content"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return base64.b64decode(r.stdout).decode("utf-8")
        last = (r.stderr or r.stdout).strip()
    raise SystemExit(f"no roadmap found in {OWNER}/{repo} ({', '.join(CANDIDATES)}): {last}")


def render(steps: Sequence[Dict[str, object]], show_all: bool) -> str:
    out: List[str] = []
    section = None
    for s in steps:
        if s["done"] and not show_all:
            continue
        if s["section"] != section:
            section = s["section"]
            out.append(f"\n## {section}" if section else "")
        num = f"{s['number']}. " if s["number"] else ""
        out.append(f"- [{'x' if s['done'] else ' '}] {num}{s['title']}")
        notes = s["notes"]
        for key in ("Done when", "Needs"):
            if key in notes:  # type: ignore[operator]
                out.append(f"    {key}: {notes[key]}")  # type: ignore[index]
        open_parts = [p for p in s["parts"] if not p["done"]]  # type: ignore[union-attr,index]
        for p in open_parts:
            out.append(f"    - [ ] {p['text']}")
    total = len(steps)
    if not total:
        return "no checkbox steps in this roadmap (it is written as prose or numbered lists); read it directly\n"
    left = sum(1 for s in steps if not s["done"])
    out.append(f"\n{left} open of {total} steps")
    return "\n".join(out).strip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="a repository name under kajisho5, or a local Markdown file")
    ap.add_argument("--all", action="store_true", help="also list the steps that are done")
    ap.add_argument("--json", action="store_true", help="print the steps as JSON")
    a = ap.parse_args(argv)
    path = Path(a.target)
    text = path.read_text(encoding="utf-8") if path.suffix == ".md" and path.is_file() else fetch(a.target)
    steps = parse(text)
    if a.json:
        chosen = steps if a.all else [s for s in steps if not s["done"]]
        print(json.dumps(chosen, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(render(steps, a.all))
    return 0


if __name__ == "__main__":
    sys.exit(main())
