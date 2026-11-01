# Adaptive workflow

## 1. Intake and baseline

Read repository instructions, status, recent history, manifests, relevant tests, and the code paths in scope. Detect unrelated user changes and preserve them. Establish a clean baseline for the affected area; if the baseline is already failing, document it before editing. Identify specialist capabilities implied by repository evidence and map them to skills or native controls already available; use `specialist-routing.md` only for a material uncovered gap.

Classify the change:

| Dimension | Low | Medium | High |
| --- | --- | --- | --- |
| Scope | isolated | several modules | cross-system/migration |
| Reversibility | trivial | moderate | destructive or hard to roll back |
| Data/security | none | authenticated/internal | secrets, money, PII, permissions |
| Cost exposure | negligible/local | metered service | paid API, LLM, high-volume compute/data |
| UX | small correction | new flow | redesign/critical journey |
| Operations | no runtime effect | deploy/config change | outage, concurrency, irreversible data |

Use the highest observed level. Increase rigor when uncertain.

## 2. Align

Define the problem, user outcome, in-scope/out-of-scope behavior, acceptance criteria, constraints, edge cases, and nonfunctional requirements. For metered work, define a cost budget and business unit (request, successful workflow, tenant, document, token, or transaction). Ask only questions that materially alter the result. Record assumptions that allow safe progress.

Gate: each requirement is observable and testable.

## 3. Design

Map current architecture, trust boundaries, paid/resource-heavy call graph, and specialist capability needs. Choose seams, data flow, failure behavior, rollback, and economic guardrails. For meaningful choices, compare options and consequences. Route UI, APIs, contracts, resilience, supply chain, and LLM context to their focused references. If a necessary specialist is not already available, follow `specialist-routing.md`; do not treat catalog popularity as proof or install a skill without authorization.

Gate: the design explains how every requirement is satisfied without bypassing repository conventions.

## 4. Tasks

Break work into small vertical slices. Each task states files or boundaries, behavior, tests, security considerations, verification command, and local commit intent. Order tracer bullets early to expose integration risk.

Gate: every acceptance criterion maps to at least one task and verification.

## 5. Execute

Use `tasks-execute.md`. Keep one task in progress, test first where practical, inspect the diff, run focused verification, then create one atomic local commit. Never push a checkpoint.

## 6. Review and secure

Review on two independent axes:

1. **Specification:** does the behavior match the accepted requirements?
2. **Engineering:** is it correct, secure, maintainable, accessible, performant, and consistent?

Use the security, cost, contract, resilience, supply-chain, and LLM-efficiency references when applicable. A green test suite does not waive review.

## 7. Verify and operate

Use `verify-operate.md`. Re-run integration gates from a known state. Medium/high-risk work gets independent verification. UI gets browser evidence. Operational changes get rollout, monitoring, and rollback evidence.

Gate: evidence-or-zero. Only after PASS may an authorized final push occur.

## 8. Learn and hand off

Update decision state and capture a reusable lesson only when evidence shows a recurring failure mode. Report outcomes, evidence, commits, remaining risks, and push status.

## Isolation

Use a worktree or equivalent isolated workspace when parallel work, risky experiments, broad refactors, or an unclean working tree could mix unrelated changes. Verify the baseline inside the isolated workspace before implementation.
