#!/usr/bin/env python3
"""Infer a conservative, non-executing project quality-gate profile."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKIP = {".git", "node_modules", ".next", "dist", "build", "vendor", ".venv"}
ROOT_NON_RUNTIME_DIRS = {
    ".agents", ".claude", ".codex", ".specs", "doc", "docs", "documentation",
    "guides", "example", "examples", "samples", "skills", "spec", "specs",
    "test", "tests", "testdata", "fixtures", "e2e", "integration", "playwright",
    "cypress", "stories", "storybook", "unit-tests", "playwright-tests",
    "integration_tests",
}
NESTED_NON_RUNTIME_DIRS = {"fixtures", "testdata", "stories", "storybook", "samples", "examples"}
NON_RUNTIME_DIR_TOKENS = {"test", "tests", "spec", "specs", "e2e"}
MIGRATION_DIRS = {"migrate", "migration", "migrations", "drizzle"}
MIGRATION_SUFFIXES = {".sql", ".py", ".js", ".ts", ".rb"}
SOURCE_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".py", ".go", ".rs", ".java", ".kt", ".rb", ".php"}

SPECIALIST_PACKAGES = {
    "nextjs": {"next"},
    "react": {"react", "react-dom"},
    "authentication": {"@clerk/nextjs", "@auth/core", "next-auth"},
    "postgres-database": {"pg", "postgres", "drizzle-orm", "prisma", "@prisma/client"},
    "supabase": {"@supabase/supabase-js", "@supabase/ssr"},
    "payments": {"stripe", "mercadopago", "mercadopago-sdk"},
    "observability": {"@sentry/nextjs", "@sentry/node", "@opentelemetry/api"},
    "browser-testing": {"@playwright/test", "playwright", "cypress"},
}

BILLABLE_PACKAGES = {
    "openai", "@anthropic-ai/sdk", "stripe", "mercadopago", "mercadopago-sdk",
    "twilio", "@aws-sdk/client-bedrock-runtime", "@google-cloud/vertexai",
}
LLM_PACKAGES = {"openai", "@anthropic-ai/sdk", "@aws-sdk/client-bedrock-runtime", "@google-cloud/vertexai"}
PAYMENT_TERMS = ("mercadopago", "stripe")
LLM_TERMS = ("openai", "anthropic", "bedrock", "vertexai")


def files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP for part in path.relative_to(root).parts):
            yield path


def is_runtime_source(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    name = path.name.casefold()
    stem = path.stem
    is_test_file = (
        any(marker in name for marker in (".test.", ".spec.", ".story.", ".stories.", ".e2e.", ".cy."))
        or re.search(r"(^test[_-]|[_-](?:test|spec)\.)", name) is not None
        or (path.suffix.casefold() in {".java", ".kt"} and re.search(r"(?:Test|IT)$", stem) is not None)
    )
    return (
        path.suffix.lower() in SOURCE_SUFFIXES
        and not is_test_file
        and not has_non_runtime_part(relative)
    )


def has_non_runtime_part(path: Path) -> bool:
    directories = path.parts[:-1] if path.suffix else path.parts
    if not directories:
        return False
    root_name = directories[0].casefold()
    if root_name in ROOT_NON_RUNTIME_DIRS or root_name.strip("._-") in ROOT_NON_RUNTIME_DIRS:
        return True
    for part in directories:
        camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", part)
        normalized = camel_split.casefold().strip("._-")
        tokens = {token for token in re.split(r"[^a-z0-9]+", normalized) if token}
        if (
            normalized in NESTED_NON_RUNTIME_DIRS
            or not tokens.isdisjoint(NESTED_NON_RUNTIME_DIRS)
            or not tokens.isdisjoint(NON_RUNTIME_DIR_TOKENS)
        ):
            return True
    return False


def contains_term(content: str, term: str) -> bool:
    """Match provider identifiers without accepting identifier substrings."""
    return re.search(rf"(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])", content) is not None


def package_runner(root: Path, manifest: dict) -> str:
    declared = str(manifest.get("packageManager", "")).split("@", 1)[0]
    if declared in {"npm", "pnpm", "yarn", "bun"}:
        return declared
    if (root / "pnpm-lock.yaml").is_file():
        return "pnpm"
    if (root / "yarn.lock").is_file():
        return "yarn"
    if (root / "bun.lock").is_file() or (root / "bun.lockb").is_file():
        return "bun"
    return "npm"


def script_command(runner: str, name: str) -> str:
    return f"{runner} {name}" if runner in {"yarn", "bun"} else f"{runner} run {name}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--output")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        parser.error("project must be a directory")
    paths = list(files(root))
    rels = {str(p.relative_to(root)) for p in paths}
    names = {p.name for p in paths}
    stack, commands = [], []
    dependencies: set[str] = set()
    dependency_sources: dict[str, set[str]] = {}

    package_files = sorted(
        (path for path in paths if path.name == "package.json" and not has_non_runtime_part(path.relative_to(root))),
        key=lambda path: (len(path.relative_to(root).parts), str(path)),
    )
    for package in package_files:
        stack.append("node")
        try:
            manifest = json.loads(package.read_text(encoding="utf-8"))
            scripts = manifest.get("scripts", {})
            manifest_dependencies = set(manifest.get("dependencies", {})) | set(manifest.get("devDependencies", {}))
            dependencies.update(manifest_dependencies)
            relative_manifest = str(package.relative_to(root))
            for dependency in manifest_dependencies:
                dependency_sources.setdefault(dependency, set()).add(relative_manifest)
            if package == root / "package.json":
                runner = package_runner(root, manifest)
                for name in ("lint", "typecheck", "test", "build"):
                    if name in scripts:
                        commands.append({"gate": name, "command": script_command(runner, name), "status": "PROPOSED"})
        except (json.JSONDecodeError, OSError):
            commands.append({"gate": "manifest", "command": f"validate {package.relative_to(root)}", "status": "NEEDS_REVIEW"})
    for marker, language, suggestions in (
        ("pyproject.toml", "python", (("test", "pytest"), ("lint", "ruff check ."))),
        ("Cargo.toml", "rust", (("test", "cargo test"), ("lint", "cargo clippy"))),
        ("go.mod", "go", (("test", "go test ./..."), ("vet", "go vet ./..."))),
    ):
        if marker in names:
            stack.append(language)
            commands.extend({"gate": gate, "command": command, "status": "PROPOSED"} for gate, command in suggestions)

    contracts = sorted(p for p in rels if p.endswith(("openapi.json", "openapi.yaml", "openapi.yml", ".proto", ".graphql", ".gql")))
    supply = sorted(p for p in rels if Path(p).name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Cargo.lock", "go.sum"})
    migrations = []
    for relative in rels:
        path = Path(relative)
        parts = {part.casefold() for part in path.parts}
        in_migration_dir = not parts.isdisjoint(MIGRATION_DIRS)
        in_alembic_versions = "alembic" in parts and "versions" in parts
        if (
            not has_non_runtime_part(path)
            and path.suffix.casefold() in MIGRATION_SUFFIXES
            and (in_migration_dir or in_alembic_versions)
        ):
            migrations.append(relative)
    migrations.sort()
    iac = sorted(p for p in rels if p.endswith(".tf") or Path(p).name in {"Dockerfile", "docker-compose.yml", "vercel.json"})
    def dependency_evidence(packages: set[str]) -> list[str]:
        return [
            f"{manifest}:{name}"
            for name in sorted(dependencies & packages)
            for manifest in sorted(dependency_sources.get(name, {"package.json"}))
        ]

    billable = dependency_evidence(BILLABLE_PACKAGES)
    llm = dependency_evidence(LLM_PACKAGES)
    billable_import_terms = tuple(BILLABLE_PACKAGES)
    payment_source_evidence = []
    for path in paths:
        if not is_runtime_source(path, root) or path.stat().st_size > 1_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(contains_term(content, term) for term in billable_import_terms):
            relative = str(path.relative_to(root))
            billable.append(relative)
            if any(contains_term(content, term) for term in PAYMENT_TERMS):
                payment_source_evidence.append(relative)
            if any(contains_term(content, term) for term in LLM_TERMS):
                llm.append(relative)
    billable = sorted(set(billable))[:50]
    llm = sorted(set(llm))[:50]

    specialist_needs = []
    for capability, packages in SPECIALIST_PACKAGES.items():
        evidence = sorted(dependencies & packages)
        if evidence:
            specialist_needs.append({
                "capability": capability,
                "evidence": [
                    f"{manifest}:{name}"
                    for name in evidence
                    for manifest in sorted(dependency_sources.get(name, {"package.json"}))
                ],
                "status": "CHECK_AVAILABLE_SKILLS_OR_NATIVE_GUIDANCE",
            })
    if payment_source_evidence and not dependencies.intersection(SPECIALIST_PACKAGES["payments"]):
        specialist_needs.append({
            "capability": "payments",
            "evidence": sorted(set(payment_source_evidence))[:10],
            "status": "CHECK_AVAILABLE_SKILLS_OR_NATIVE_GUIDANCE",
        })
    if iac:
        specialist_needs.append({
            "capability": "infrastructure-deployment",
            "evidence": iac[:10],
            "status": "CHECK_AVAILABLE_SKILLS_OR_NATIVE_GUIDANCE",
        })

    sensitive_capabilities = {"authentication", "postgres-database", "supabase", "payments"}
    has_sensitive_stack = any(item["capability"] in sensitive_capabilities for item in specialist_needs)
    risk = "high" if billable else "medium" if contracts or migrations or iac or has_sensitive_stack else "low"
    profile = {
        "schema_version": 1,
        "project": str(root),
        "assessment": "PROPOSED_NOT_EXECUTED",
        "risk_level": risk,
        "stack": sorted(set(stack)),
        "gates": commands,
        "contracts": contracts,
        "supply_chain_lockfiles": supply,
        "migrations": migrations,
        "infrastructure": iac,
        "billable_api_indicators": billable,
        "llm_api_indicators": llm,
        "specialist_capability_needs": specialist_needs,
        "required_reviews": sorted({
            "security",
            *( ["api-cost"] if billable else [] ),
            *( ["llm-efficiency"] if llm else [] ),
            *( ["contract-compatibility"] if contracts else [] ),
            *( ["data-migration"] if migrations else [] ),
            *( ["supply-chain"] if supply or iac else [] ),
        }),
        "notes": [
            "Commands and capability needs are inferred only; validate them against repository instructions.",
            "A capability need is not proof that a skill is missing; prefer available skills and native controls before external discovery.",
        ],
    }
    rendered = json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = Path(args.output)
        if output.exists() and not args.force:
            parser.error("output exists; pass --force to replace it")
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
