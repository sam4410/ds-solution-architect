#!/usr/bin/env python3
"""Package the plugin for distribution.

Creates in dist/:
  ds-solution-architect-<version>.plugin   Claude Desktop plugin upload (zip of the plugin root)
  ds-solution-architect-<version>.zip      Same content, .zip extension
  skills/<skill>.zip                       One zip per skill, for uploading individual skills
                                           (Claude app > Settings > Capabilities > Skills)

Usage: python scripts/package.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INCLUDE = [".claude-plugin", "skills", "agents", "README.md", "CHANGELOG.md", "LICENSE"]
EXCLUDE_PARTS = {"__pycache__", ".DS_Store"}


def files_under(path: Path):
    if path.is_file():
        yield path
        return
    for p in sorted(path.rglob("*")):
        if p.is_file() and not (set(p.parts) & EXCLUDE_PARTS) and p.suffix != ".pyc":
            yield p


def main() -> int:
    if subprocess.run([sys.executable, str(ROOT / "scripts/build.py"), "--check"]).returncode != 0:
        print("Run `python scripts/build.py` first.")
        return 1
    version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    name = "ds-solution-architect"
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "skills").mkdir(parents=True)

    plugin_zip = DIST / f"{name}-{version}.zip"
    with zipfile.ZipFile(plugin_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = ROOT / item
            if not p.exists():
                continue
            for f in files_under(p):
                z.write(f, f.relative_to(ROOT).as_posix())
    shutil.copy2(plugin_zip, DIST / f"{name}-{version}.plugin")

    for skill in sorted((ROOT / "skills").iterdir()):
        if not (skill / "SKILL.md").exists():
            continue
        with zipfile.ZipFile(DIST / "skills" / f"{skill.name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in files_under(skill):
                z.write(f, (Path(skill.name) / f.relative_to(skill)).as_posix())

    for f in sorted(DIST.rglob("*.*")):
        print(f"{f.relative_to(ROOT)}  ({f.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
