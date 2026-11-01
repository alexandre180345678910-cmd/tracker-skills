#!/usr/bin/env python3
"""Tests for evidence artifact integrity helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_evidence import artifact_digest


SCRIPT = Path(__file__).with_name("validate_evidence.py")


class EvidenceArtifactTests(unittest.TestCase):
    def test_relative_artifact_is_bound_to_manifest_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "evidence.json"
            artifact = root / "lint.log"
            artifact.write_text("PASS\n", encoding="utf-8")
            resolved, digest = artifact_digest(manifest, "lint.log")
            self.assertEqual(resolved, artifact.resolve())
            self.assertEqual(digest, hashlib.sha256(b"PASS\n").hexdigest())

    def test_missing_artifact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(SystemExit):
                artifact_digest(Path(directory) / "evidence.json", "missing.log")

    def make_repository(self, root: Path) -> tuple[str, str]:
        subprocess.run(["git", "init", "-b", "test-branch"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Skill Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "skill@example.invalid"], cwd=root, check=True)
        (root / "tracked.txt").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()
        return head, "test-branch"

    def test_manifest_binds_real_artifact_and_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            head, branch = self.make_repository(root)
            artifact = root / "tests.log"
            artifact.write_text("2 tests passed\n", encoding="utf-8")
            manifest = root / "evidence.json"
            data = {
                "schema_version": 2,
                "delivery_id": "fixture",
                "head": head,
                "branch": branch,
                "verdict": "PASS",
                "risk_level": "medium",
                "verifier": {"name": "independent-reviewer", "independent": True},
                "checks": [{
                    "name": "tests",
                    "command": "fixture test command",
                    "exit_code": 0,
                    "evidence_file": "tests.log",
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }],
            }
            manifest.write_text(json.dumps(data), encoding="utf-8")
            valid = subprocess.run(
                [sys.executable, str(SCRIPT), str(manifest), "--delivery", "fixture"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(valid.returncode, 0, valid.stderr)
            artifact.write_text("tampered\n", encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(SCRIPT), str(manifest), "--delivery", "fixture"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("digest does not match", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
