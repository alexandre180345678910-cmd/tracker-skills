#!/usr/bin/env python3
"""Portable, read-only structural validation for this skill."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise SystemExit(f"skill validation failed: {message}")


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent).resolve()
    skill_file = root / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail("SKILL.md needs YAML frontmatter")
    frontmatter = text.split("---\n", 2)[1]
    fields = {}
    for line in frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"\'')
    if set(fields) != {"name", "description"}:
        fail("frontmatter must contain exactly name and description")
    if not NAME_RE.fullmatch(fields["name"]):
        fail("invalid skill name")
    if not fields["description"] or len(fields["description"]) > 1024:
        fail("description must contain 1-1024 characters")

    for match in re.finditer(r"\[[^]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0]
        if target and "://" not in target and not (root / target).is_file():
            fail(f"broken local link: {target}")

    for path in root.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in root.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    forbidden = ("/" + "home/", "/" + "Users/", "C:" + "\\\\Users\\\\")
    for path in [skill_file, *root.glob("scripts/*"), *root.glob("references/*")]:
        if path.is_file() and any(value in path.read_text(encoding="utf-8", errors="ignore") for value in forbidden):
            fail(f"machine-specific absolute path in {path.relative_to(root)}")
    print("skill metadata and portable structure: PASS")


if __name__ == "__main__":
    main()
