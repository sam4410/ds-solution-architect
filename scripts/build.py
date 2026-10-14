#!/usr/bin/env python3
"""Sync shared reference files into each skill's references/ folder.

shared/references/*.md is the single source of truth. Each skill gets its own copy of the
files it needs (mapping in shared/skill-references.json) so that every skill is self-contained:
it works inside the plugin, and when uploaded on its own.

Usage:
    python scripts/build.py          # sync copies
    python scripts/build.py --check  # exit 1 if any copy is missing or out of date
"""
from __future__ import annotations

import filecmp
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared" / "references"
MAPPING = ROOT / "shared" / "skill-references.json"
SKILLS = ROOT / "skills"


def main(check: bool) -> int:
    mapping = {k: v for k, v in json.loads(MAPPING.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    problems = 0
    for skill, files in mapping.items():
        dest_dir = SKILLS / skill / "references"
        if not (SKILLS / skill / "SKILL.md").exists():
            print(f"ERROR: skill '{skill}' in mapping has no SKILL.md")
            problems += 1
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name in files:
            src = SHARED / name
            dst = dest_dir / name
            if not src.exists():
                print(f"ERROR: shared reference missing: {src.relative_to(ROOT)}")
                problems += 1
                continue
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue
            if check:
                print(f"OUT OF DATE: {dst.relative_to(ROOT)}")
                problems += 1
            else:
                shutil.copy2(src, dst)
                print(f"synced  {dst.relative_to(ROOT)}")
    if check and problems == 0:
        print("All skill reference copies are in sync.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
