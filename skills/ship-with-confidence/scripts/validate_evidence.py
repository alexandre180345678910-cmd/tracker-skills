#!/usr/bin/env python3
"""Validate a final-delivery evidence manifest against the current Git state."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, text=True, capture_output=True).stdout.strip()


def reject(message: str) -> None:
    raise SystemExit(f"evidence: BLOCKED; {message}")


def artifact_digest(manifest: Path, artifact: str) -> tuple[Path, str]:
    path = Path(artifact)
    if not path.is_absolute():
        path = manifest.parent / path
    path = path.resolve()
    if not path.is_file():
        reject(f"evidence artifact is missing: {artifact}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--delivery", required=True)
    args = parser.parse_args()
    try:
        manifest = Path(args.manifest).resolve()
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        reject(f"cannot read valid JSON: {exc}")

    expected = {
        "schema_version": 2,
        "delivery_id": args.delivery,
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "verdict": "PASS",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            reject(f"{key} does not match required value")
    risk = data.get("risk_level")
    if risk not in {"low", "medium", "high"}:
        reject("risk_level must be low, medium, or high")
    verifier = data.get("verifier")
    if not isinstance(verifier, dict) or not str(verifier.get("name", "")).strip():
        reject("named verifier is required")
    if risk in {"medium", "high"} and verifier.get("independent") is not True:
        reject("medium/high risk requires an independent verifier")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        reject("at least one check is required")
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            reject(f"check {index} is not an object")
        for field in ("name", "command", "evidence_file", "sha256"):
            if not str(check.get(field, "")).strip():
                reject(f"check {index} lacks {field}")
        if check.get("exit_code") != 0:
            reject(f"check {index} exit_code is not zero")
        artifact, digest = artifact_digest(manifest, check["evidence_file"])
        if artifact == manifest:
            reject(f"check {index} cannot use the manifest as its evidence artifact")
        if check["sha256"].casefold() != digest:
            reject(f"check {index} evidence artifact digest does not match")
    print(f"evidence: ATTESTATION VALID ({len(checks)} checks, risk={risk}); not execution or authorization proof")


if __name__ == "__main__":
    main()
