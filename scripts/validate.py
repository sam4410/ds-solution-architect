#!/usr/bin/env python3
"""Structural validation for the ds-solution-architect plugin.

Checks:
  - plugin.json / marketplace.json are valid JSON with required fields
  - every skill folder has SKILL.md with frontmatter name == folder name, kebab-case,
    description present and <= 1024 characters
  - SKILL.md body length (warn > 500 lines)
  - every `references/<file>` and `scripts/<file>` mentioned in a SKILL.md exists in that skill
  - shared reference copies are in sync (scripts/build.py --check)
  - agents have frontmatter with name + description
  - the Word converter runs on the template example

Usage: python scripts/validate.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warnings: list[str] = []


def frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def check_manifests() -> None:
    for rel, req in ((".claude-plugin/plugin.json", ["name", "version", "description"]),
                     (".claude-plugin/marketplace.json", ["name", "owner", "plugins"])):
        p = ROOT / rel
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{rel}: invalid JSON ({e})")
            continue
        for k in req:
            if k not in data:
                errors.append(f"{rel}: missing '{k}'")
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", plugin.get("name", "")):
        errors.append("plugin.json: name must be kebab-case")


def check_skills() -> None:
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        sk = skill_dir / "SKILL.md"
        if not sk.exists():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        text = sk.read_text(encoding="utf-8")
        meta, body = frontmatter(text)
        if meta.get("name") != skill_dir.name:
            errors.append(f"{skill_dir.name}: frontmatter name '{meta.get('name')}' != folder name")
        desc = meta.get("description", "")
        if not desc:
            errors.append(f"{skill_dir.name}: missing description")
        elif len(desc) > 1024:
            errors.append(f"{skill_dir.name}: description {len(desc)} chars (> 1024)")
        n = len(body.splitlines())
        if n > 500:
            warnings.append(f"{skill_dir.name}: SKILL.md body is {n} lines (> 500)")
        for ref in set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", body)):
            if not (skill_dir / ref).exists():
                errors.append(f"{skill_dir.name}: referenced file missing: {ref}")


def check_agents() -> None:
    for a in (ROOT / "agents").glob("*.md"):
        meta, _ = frontmatter(a.read_text(encoding="utf-8"))
        for k in ("name", "description"):
            if k not in meta:
                errors.append(f"agents/{a.name}: missing '{k}'")


def check_sync() -> None:
    r = subprocess.run([sys.executable, str(ROOT / "scripts/build.py"), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        errors.append("shared references out of sync — run: python scripts/build.py\n" + r.stdout)


def check_docx() -> None:
    sample = ROOT / "evals" / "fixtures" / "sample-plan.md"
    if not sample.exists():
        warnings.append("evals/fixtures/sample-plan.md not found; skipped converter test")
        return
    conv = ROOT / "skills/ds-solution-plan/scripts/md_to_docx.py"
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "sample.docx"
        r = subprocess.run([sys.executable, str(conv), str(sample), str(out)], capture_output=True, text=True)
        if r.returncode != 0 or not out.exists() or out.stat().st_size < 5000:
            errors.append(f"md_to_docx.py failed on sample: {r.stderr or r.stdout}")


def main() -> int:
    check_manifests()
    check_skills()
    check_agents()
    check_sync()
    check_docx()
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{'FAILED' if errors else 'PASSED'}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
