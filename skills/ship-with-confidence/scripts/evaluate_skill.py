#!/usr/bin/env python3
"""Compare baseline and with-skill forward-test response files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def reported_sum(records, fields):
    values = []
    for item in records:
        for field in fields:
            value = item.get(field)
            if value is not None:
                values.append(int(value))
    return sum(values) if values else None


def score(spec, records):
    ids = [record.get("id") for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scenario id in response records")
    by_id = {record["id"]: record for record in records}
    rows = []
    for scenario in spec["scenarios"]:
        if scenario["id"] not in by_id:
            rows.append({
                "id": scenario["id"],
                "pass": False,
                "coverage": 0.0,
                "trigger_ok": False,
                "missing": ["response record"],
            })
            continue
        record = by_id[scenario["id"]]
        response = str(record.get("response", "")).casefold()
        required = scenario.get("must", [])
        concepts = []
        matched = []
        for item in required:
            if isinstance(item, str):
                label, variants = item, [item]
            else:
                label, variants = item["concept"], item.get("any", [item["concept"]])
            concepts.append(label)
            if any(variant.casefold() in response for variant in variants):
                matched.append(label)
        coverage = len(matched) / len(required) if required else 1.0
        trigger_ok = bool(record.get("triggered")) == bool(scenario.get("should_trigger", True))
        rows.append({
            "id": scenario["id"],
            "pass": coverage >= 0.8 and trigger_ok,
            "coverage": round(coverage, 3),
            "trigger_ok": trigger_ok,
            "missing": [concept for concept in concepts if concept not in matched],
        })

    count = len(rows)
    return {
        "pass_rate": sum(row["pass"] for row in rows) / count if count else 0.0,
        "trigger_accuracy": sum(row["trigger_ok"] for row in rows) / count if count else 0.0,
        "elapsed_ms": reported_sum(records, ("elapsed_ms",)),
        "tokens": reported_sum(records, ("input_tokens", "output_tokens")),
        "scenarios": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--with-skill", type=Path, required=True)
    parser.add_argument("--min-pass-rate", type=float, default=0.8)
    parser.add_argument("--min-trigger-accuracy", type=float, default=0.9)
    args = parser.parse_args()

    spec = load(args.spec)
    baseline = score(spec, load(args.baseline))
    with_skill = score(spec, load(args.with_skill))
    def delta(metric):
        left, right = baseline[metric], with_skill[metric]
        return right - left if left is not None and right is not None else None

    report = {
        "baseline": baseline,
        "with_skill": with_skill,
        "delta": {
            "pass_rate": with_skill["pass_rate"] - baseline["pass_rate"],
            "trigger_accuracy": with_skill["trigger_accuracy"] - baseline["trigger_accuracy"],
            "elapsed_ms": delta("elapsed_ms"),
            "tokens": delta("tokens"),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if with_skill["pass_rate"] < args.min_pass_rate:
        return 1
    if with_skill["trigger_accuracy"] < args.min_trigger_accuracy:
        return 1
    if with_skill["pass_rate"] < baseline["pass_rate"]:
        return 1
    if with_skill["trigger_accuracy"] < baseline["trigger_accuracy"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
