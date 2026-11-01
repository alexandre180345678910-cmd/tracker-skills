#!/usr/bin/env python3
"""Behavior tests for the conservative project profiler."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("project_profile.py")


class ProjectProfileTests(unittest.TestCase):
    def profile(self, files: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout)

    def test_detects_runtime_capabilities_without_documentation_false_positives(self) -> None:
        profile = self.profile({
            "package.json": json.dumps({
                "dependencies": {"next": "1", "@clerk/nextjs": "1", "mercadopago": "1"},
                "devDependencies": {"@playwright/test": "1"},
            }),
            ".agents/skills/example/SKILL.md": "Use openai and stripe.",
            ".specs/features/product-migration/spec.md": "Migration design.",
            "tests/auth/state.json": "anthropic",
            "src/provider.test.ts": "import OpenAI from 'openai';",
            "documentation/provider-example.ts": "import OpenAI from 'openai';",
            "skills/payments/example.ts": "const provider = 'stripe';",
            "guides/migrations/example.sql": "create table example(id int);",
            "integration/migrations/setup.sql": "create table example(id int);",
            "__tests__/provider.ts": "import OpenAI from 'openai';",
            "playwright/provider.ts": "const provider = 'stripe';",
            "specs/migrations/setup.sql": "create table example(id int);",
            "testdata/migrations/setup.sql": "create table example(id int);",
            "unit-tests/provider.ts": "import OpenAI from 'openai';",
            "playwright-tests/provider.ts": "const provider = 'stripe';",
            "integration_tests/migrations/setup.sql": "create table example(id int);",
            "samples/migrations/setup.sql": "create table example(id int);",
            "src/provider_test.go": "const provider = `openai`",
            "src/test_provider.py": "provider = 'openai'",
            "src/provider.stories.tsx": "const provider = 'openai';",
            "src/provider.story.tsx": "const provider = 'openai';",
            "src/provider.e2e.ts": "const provider = 'openai';",
            "src/integrationTest/java/PaymentIT.java": "String provider = \"stripe\";",
            "src/integrationTest/resources/migrations/fixture.sql": "create table example(id int);",
            "src/testFixtures/java/OpenAiFixture.java": "String provider = \"openai\";",
            "src/testFixtures/resources/migrations/fixture.sql": "create table example(id int);",
            "src/unitTests/provider.ts": "const provider = 'openai';",
            "src/e2eTests/provider.ts": "const provider = 'stripe';",
            "src/ProviderTest.java": "String provider = \"openai\";",
            "src/PaymentIT.java": "String provider = \"stripe\";",
            "storybook-static/provider.ts": "const provider = 'openai';",
            "src/theme.ts": "export const stripePattern = true;",
        })
        capabilities = {item["capability"] for item in profile["specialist_capability_needs"]}
        self.assertEqual(capabilities, {"nextjs", "authentication", "payments", "browser-testing"})
        self.assertEqual(profile["billable_api_indicators"], ["package.json:mercadopago"])
        self.assertEqual(profile["llm_api_indicators"], [])
        self.assertEqual(profile["migrations"], [])

    def test_detects_real_database_migration_and_runtime_provider_import(self) -> None:
        profile = self.profile({
            "package.json": "{}",
            "db/migrations/0001.sql": "create table example(id int);",
            "src/provider.ts": "import OpenAI from 'openai';",
        })
        self.assertEqual(profile["migrations"], ["db/migrations/0001.sql"])
        self.assertEqual(profile["billable_api_indicators"], ["src/provider.ts"])
        self.assertEqual(profile["llm_api_indicators"], ["src/provider.ts"])
        self.assertIn("llm-efficiency", profile["required_reviews"])

    def test_keeps_runtime_agents_and_integration_directories(self) -> None:
        profile = self.profile({
            "package.json": "{}",
            "src/agents/provider.ts": "import OpenAI from 'openai';",
            "src/integration/payments.ts": "const provider = 'stripe';",
        })
        self.assertEqual(
            profile["billable_api_indicators"],
            ["src/agents/provider.ts", "src/integration/payments.ts"],
        )
        self.assertEqual(profile["llm_api_indicators"], ["src/agents/provider.ts"])

    def test_detects_framework_migration_conventions(self) -> None:
        profile = self.profile({
            "package.json": "{}",
            "app/migrations/0001_initial.py": "operations = []",
            "src/migrations/001-add-user.ts": "export class AddUser {}",
            "db/migrate/001_create_users.rb": "class CreateUsers; end",
            "alembic/versions/001_init.py": "def upgrade(): pass",
        })
        self.assertEqual(profile["migrations"], [
            "alembic/versions/001_init.py",
            "app/migrations/0001_initial.py",
            "db/migrate/001_create_users.rb",
            "src/migrations/001-add-user.ts",
        ])
        self.assertIn("data-migration", profile["required_reviews"])

    def test_reads_nested_manifests_and_uses_declared_package_manager(self) -> None:
        profile = self.profile({
            "package.json": json.dumps({
                "packageManager": "pnpm@10.0.0",
                "scripts": {"test": "vitest"},
            }),
            "packages/web/package.json": json.dumps({
                "dependencies": {"@supabase/supabase-js": "1"},
            }),
            "pnpm-lock.yaml": "lockfileVersion: '9.0'",
        })
        self.assertIn(
            {
                "capability": "supabase",
                "evidence": ["packages/web/package.json:@supabase/supabase-js"],
                "status": "CHECK_AVAILABLE_SKILLS_OR_NATIVE_GUIDANCE",
            },
            profile["specialist_capability_needs"],
        )
        self.assertIn({"gate": "test", "command": "pnpm run test", "status": "PROPOSED"}, profile["gates"])
        self.assertEqual(profile["risk_level"], "medium")

    def test_authentication_dependency_raises_risk(self) -> None:
        profile = self.profile({
            "package.json": json.dumps({"dependencies": {"@clerk/nextjs": "1"}}),
        })
        self.assertEqual(profile["risk_level"], "medium")


if __name__ == "__main__":
    unittest.main()
