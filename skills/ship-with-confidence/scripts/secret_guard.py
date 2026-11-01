#!/usr/bin/env python3
"""Fail closed when staged additions resemble secrets, without printing values."""

from __future__ import annotations

import re
import subprocess
import sys


PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "provider-token": re.compile(
        r"(?:AKIA[0-9A-Z]{16}|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{30,}|"
        r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}|sk_(?:live|test)_[A-Za-z0-9]{20,}|"
        r"AIza[0-9A-Za-z_-]{30,}|sntrys_[A-Za-z0-9_-]{20,})"
    ),
    "credential-url": re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s:/]+:[^\s/@]+@"),
}

CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)(?P<key>[A-Z0-9_.-]*(?:api[_-]?key|auth[_-]?token|access[_-]?key|secret|token|password|passwd|"
    r"private[_-]?key|service[_-]?role[_-]?key)[A-Z0-9_.-]*)\s*[:=]\s*['\"]?(?P<value>[^\s'\",;#]{12,})"
)
PLACEHOLDER = re.compile(
    r"(?i)(?:"
    r"(?:placeholder|example|sample|changeme|dummy|fake|test[_-]?only)(?:[_-](?:key|token|secret|password|value|here))*|"
    r"your[_-](?:api[_-]?key|auth[_-]?token|access[_-]?key|secret|token|password|sentry[_-]?token|"
    r"aws[_-]?secret[_-]?access[_-]?key)(?:[_-]?here)?|"
    r"replace[_-]?me(?:[_-]with[_-](?:secret|token|key))?|"
    r"x{8,}|\$\{[A-Z0-9_]+\}|<[^>]+>"
    r")"
)


def staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print("secret-guard: unable to inspect staged diff", file=sys.stderr)
        raise SystemExit(2)
    return result.stdout


def scan_diff(diff: str) -> list[tuple[str, str]]:
    current_file = "unknown"
    findings: list[tuple[str, str]] = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:]
        for kind, pattern in PATTERNS.items():
            if pattern.search(content):
                findings.append((current_file, kind))
        assignment = CREDENTIAL_ASSIGNMENT.search(content)
        if assignment and not PLACEHOLDER.fullmatch(assignment.group("value")):
            findings.append((current_file, "credential-assignment"))

    return sorted(set(findings))


def main() -> int:
    findings = scan_diff(staged_diff())

    if findings:
        print("secret-guard: BLOCKED; possible secret-like additions:", file=sys.stderr)
        for filename, kind in findings:
            print(f"- {filename}: {kind}", file=sys.stderr)
        print("Values were intentionally suppressed. Review, remove, and rotate if real.", file=sys.stderr)
        return 1

    print("secret-guard: PASS (heuristic staged-diff scan)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
