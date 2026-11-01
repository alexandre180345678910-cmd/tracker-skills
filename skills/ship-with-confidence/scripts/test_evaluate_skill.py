#!/usr/bin/env python3
"""Unit tests for deterministic evaluation bookkeeping."""

from __future__ import annotations

import unittest

from evaluate_skill import score


class EvaluateSkillTests(unittest.TestCase):
    def test_missing_negative_control_fails_closed(self) -> None:
        spec = {"scenarios": [{"id": "negative", "should_trigger": False, "must": []}]}
        result = score(spec, [])
        self.assertEqual(result["pass_rate"], 0.0)
        self.assertFalse(result["scenarios"][0]["pass"])

    def test_present_negative_control_can_pass(self) -> None:
        spec = {"scenarios": [{"id": "negative", "should_trigger": False, "must": []}]}
        result = score(spec, [{"id": "negative", "triggered": False, "response": ""}])
        self.assertEqual(result["pass_rate"], 1.0)

    def test_duplicate_records_are_rejected(self) -> None:
        spec = {"scenarios": [{"id": "one", "should_trigger": True, "must": []}]}
        with self.assertRaises(ValueError):
            score(spec, [{"id": "one"}, {"id": "one"}])


if __name__ == "__main__":
    unittest.main()
