#!/usr/bin/env python3
"""Regression tests for the staged-diff secret guard."""

from __future__ import annotations

import unittest

from secret_guard import scan_diff


def added(value: str) -> str:
    return f"+++ b/.env\n+{value}\n"


def assignment(name: str, value: str) -> str:
    return f"{name}={value}"


class SecretGuardTests(unittest.TestCase):
    def test_detects_project_provider_credentials_without_printing_values(self) -> None:
        cases = (
            assignment("SENTRY_AUTH_TOKEN", "sntrys" + "_abcdefghijklmnopqrstuvwxyz012345"),
            assignment("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiJ9.payload.signature"),
            assignment("AWS_SECRET_ACCESS_KEY", "abcdefghijklmnopqrstuvwxyz0123456789ABCD"),
            assignment("DATABASE_URL", "postgresql" + "://admin:supersecretpassword@db.example.test/app"),
        )
        for case in cases:
            with self.subTest(case=case.split("=", 1)[0]):
                self.assertTrue(scan_diff(added(case)))

    def test_detects_common_provider_token(self) -> None:
        self.assertTrue(scan_diff(added(assignment("GITHUB_TOKEN", "ghp" + "_abcdefghijklmnopqrstuvwxyz1234567890"))))

    def test_allows_documented_placeholders(self) -> None:
        cases = (
            assignment("SENTRY_AUTH_TOKEN", "your_sentry_token_here"),
            assignment("SUPABASE_SERVICE_ROLE_KEY", "<service-role-key>"),
            assignment("AWS_SECRET_ACCESS_KEY", "${AWS_SECRET_ACCESS_KEY}"),
            assignment("API_KEY", "replace_me_with_secret"),
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertFalse(scan_diff(added(case)))

    def test_placeholder_words_inside_real_values_do_not_bypass(self) -> None:
        cases = (
            assignment("API_KEY", "ZZZZexampleYYYYYYYYYYYY"),
            assignment("AUTH_TOKEN", "real_dummy_token_material_12345"),
            assignment("PASSWORD", "productionfakecredential98765"),
            assignment("AWS_SECRET_ACCESS_KEY", "prefixyour_aws_secret_access_keysuffix"),
        )
        for case in cases:
            with self.subTest(case=case.split("=", 1)[0]):
                self.assertTrue(scan_diff(added(case)))

    def test_ignores_removed_and_context_lines(self) -> None:
        diff = "--- a/.env\n-" + assignment("SENTRY_AUTH_TOKEN", "sntrys" + "_abcdefghijklmnopqrstuvwxyz012345")
        diff += "\n " + assignment("API_KEY", "realvalue123456") + "\n"
        self.assertFalse(scan_diff(diff))


if __name__ == "__main__":
    unittest.main()
