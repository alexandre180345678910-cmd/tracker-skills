#!/usr/bin/env python3
"""Report deterministic context size and duplicated guidance for a skill."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def metrics(text: str) -> dict[str, int]:
    return {"characters": len(text), "words": len(text.split()), "approx_tokens": (len(text) + 3) // 4}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", nargs="?", default=str(Path(__file__).parent.parent))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.skill).resolve()
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    parts = skill.split("---\n", 2)
    frontmatter = parts[1] if len(parts) == 3 else ""
    body = parts[2] if len(parts) == 3 else skill
    entries = {"frontmatter": metrics(frontmatter), "skill_body": metrics(body)}
    all_text = [skill]
    for path in sorted((root / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        entries[f"references/{path.name}"] = metrics(text)
        all_text.append(text)

    occurrences: dict[str, list[str]] = defaultdict(list)
    for label, text in [("SKILL.md", skill), *[(f"references/{p.name}", p.read_text(encoding="utf-8")) for p in sorted((root / "references").glob("*.md"))]]:
        for line in text.splitlines():
            normalized = re.sub(r"\s+", " ", line.strip().lower())
            if len(normalized) >= 50:
                occurrences[normalized].append(label)
    duplicates = [{"text": line, "locations": places} for line, places in occurrences.items() if len(set(places)) > 1]
    combined = "\n".join(all_text)
    report = {
        "estimation": "approx_tokens uses characters/4; provider tokenizer and billable context differ",
        "files": entries,
        "total": metrics(combined),
        "cross_file_duplicate_lines": duplicates,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(report["estimation"])
        for name, value in entries.items():
            print(f"{name}: {value['words']} words; ~{value['approx_tokens']} tokens")
        print(f"total possible loaded context: ~{report['total']['approx_tokens']} tokens")
        print(f"cross-file duplicate long lines: {len(duplicates)}")


if __name__ == "__main__":
    main()
