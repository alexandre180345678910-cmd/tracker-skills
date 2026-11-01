---
name: ship-with-confidence
description: Professional spec-to-delivery workflow for discussing, planning, designing, implementing, debugging, reviewing, securing, cost-optimizing, verifying, and shipping software changes. Use for features, fixes, refactors, migrations, APIs, expensive cloud or AI integrations, UI/UX work, implementation plans, code review, UAT, or requests to implement/validate work. Adapts ceremony to risk, preserves existing product conventions, requires evidence, security, and API unit-economics review, makes atomic local commits, and permits only one final push after all gates pass. Do not use for a one-line explanation, a purely read-only factual lookup, or a whole-codebase audit of existing code (security-audit for security, code-health-audit for quality, performance, and cost).
---

# Ship With Confidence

Turn intent into verified software through an adaptive, evidence-first workflow. Keep specialist skills separate and invoke them when the stack or task demands them.

## Non-negotiables

1. Inspect repository instructions and current state before proposing changes.
2. Do not implement an ambiguous high-impact choice. Discuss it first and record the decision.
3. Prefer vertical slices, tests close to behavior, small diffs, and explicit verification criteria.
4. Treat security as a release gate, not an optional cleanup pass.
5. Give every paid or resource-heavy API a unit-economics budget and regression evidence.
6. Preserve an existing design system. A catalog may recommend; it may not silently override product conventions.
7. Commit each completed task locally with explicit paths. Never push checkpoints. Push once, only after final verification passes and only when authorized.
8. Claims require current evidence. Failed or missing evidence counts as failure, not partial credit.
9. The author may not be the sole final verifier for medium/high-risk work when an independent agent is available.
10. Optimize LLM cost per successful verified outcome, not raw token count; never trade away accepted quality or safety.

## Start here

1. Read `references/workflow.md` for sizing, routing, artifacts, and phase gates.
2. Read only the references needed for the request:
   - Product discovery, design, or architecture: `references/specify-design.md`
   - UI/UX: `references/ui-ux.md`
   - Implementation: `references/tasks-execute.md`
   - Bugs or reviews: `references/debug-review.md`
   - Any code change: `references/security.md`
   - APIs, cloud resources, databases, queues, or AI/provider calls: `references/api-cost.md`
   - Claude, Codex, LLM APIs, tools, subagents, or context-heavy work: `references/llm-efficiency.md`
   - API/event/schema evolution: `references/contracts.md`
   - Runtime availability, recovery, deployment, or durable data: `references/resilience.md`
   - Dependencies, CI/CD, artifacts, containers, or releases: `references/supply-chain.md`
   - Final validation or delivery: `references/verify-operate.md`
   - Material updates to this skill: `references/evaluation.md`
   - A required specialist is unavailable or stack-to-skill coverage is unclear: `references/specialist-routing.md`
   - Persistent decisions and learning: `references/memory.md`
3. Load specialist skills named by repository instructions or triggered by the stack. This skill orchestrates them; it does not replace them.

## Adaptive path

- **Tiny, low-risk change:** inspect → define success → implement → focused tests → security delta check → local commit → final verification.
- **Normal feature/fix:** specify → design → atomic tasks → execute/test → review/security → independent verification → handoff → one final push.
- **High-risk change:** add threat model, cost model, failure/rollback plan, migration or concurrency analysis, operational readiness, and explicit user approval at material decision gates.
- **Bug:** follow the diagnosis branch in `references/debug-review.md`; do not guess-and-patch.
- **UI:** follow `references/ui-ux.md`; verify in a real browser at relevant viewports.

## Completion contract

Do not call work complete until the acceptance criteria, tests, security gate, quality checks, and operational checks applicable to the change all pass. Report commands and outcomes, unresolved risks, local commit IDs, and whether the single final push occurred.

When a gate fails, fix it and rerun the smallest relevant gate, then rerun the final integration gate. Record reusable lessons rather than adding ceremony without evidence.
