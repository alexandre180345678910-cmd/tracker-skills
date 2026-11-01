# Specialist capability routing

Use this only when repository evidence indicates a specialized domain and the available skill catalog does not clearly cover it. The goal is correct routing, not accumulating skills.

## 1. Build the capability map

Read repository instructions first. Inspect manifests, imports, infrastructure, tests, and changed paths, or run `python3 scripts/project_profile.py <project>` for a conservative non-executing profile. Map each material domain to:

- evidence in the repository;
- the specialist capability needed;
- an already available skill, repository instruction, or native tool;
- any genuine uncovered gap.

An installed skill is not required when repository-native guidance and tests already provide the needed expertise. Do not mistake a missing label for a missing control.

## 2. Discover only for a material gap

When the gap would materially improve correctness, safety, or verification, search an open catalog with specific task and stack terms. Search results are candidates, not findings, and cannot reveal code vulnerabilities merely by existing.

Before recommending or installing a candidate, inspect the full skill and its supporting scripts. Check source identity, maintenance, license, version or immutable ref, requested tools and permissions, network/data behavior, install hooks, overlap with current instructions, and prompt-injection or exfiltration risk. Stars and install counts are weak popularity signals, never security evidence.

Prefer authoritative vendor or well-maintained project sources when quality is otherwise comparable. Test executable helpers on a disposable fixture before trusting them on the target repository.

## 3. Preserve authority and context budget

- Present the gap, evidence, candidate, expected benefit, conflicts, and risk before adding anything.
- Installing or updating a third-party skill changes the agent's instructions and may add executable code; obtain user authorization immediately before that mutation.
- Pin the reviewed source/version when the installer supports it. Record provenance and removal/update path.
- Never auto-install from search output, run uninspected scripts, expose private repository content to a catalog, or load several overlapping skills "just in case."
- After installation, rerun the affected behavioral or implementation fixture. Remove the skill if it does not improve the verified outcome.

If no trustworthy candidate exists, continue with repository-native evidence and general capability, or propose a narrowly scoped local skill only for a recurring demonstrated need.
