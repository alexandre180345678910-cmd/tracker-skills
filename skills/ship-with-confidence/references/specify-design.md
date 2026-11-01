# Specify and design

## Discovery

Do not begin with a solution. Establish:

- who experiences the problem and the desired outcome;
- present behavior and evidence;
- in scope, out of scope, constraints, and compatibility;
- happy path, empty/error/loading states, permissions, and edge cases;
- measurable acceptance criteria;
- security, privacy, accessibility, performance, unit economics, LLM context budget, contracts, observability, resilience, supply chain, data, migration, and rollback needs.

For ambiguous product work, conduct a focused grill: ask one decision-bearing question at a time, surface hidden assumptions, and stop when remaining uncertainty no longer changes implementation.

## Domain and codebase model

Trace entry points, domain concepts, state transitions, data ownership, dependencies, paid calls, resource multipliers, and existing tests. Prefer the repository's language and boundaries. Identify stable modules by responsibility, not by technical layer alone.

Design deep modules: expose a small coherent interface while hiding complexity. Avoid shallow wrappers, speculative abstractions, duplicated policy, and leaky data shapes. Define seams where behavior can be tested without recreating production internals.

## Decision record

For a material choice record:

- context and constraints;
- options considered;
- decision and rationale;
- consequences and follow-up;
- reversal trigger.

Require user approval when the choice changes product behavior, public contracts, data ownership, cost, security posture, or an irreversible migration.

## Traceability

Assign stable requirement IDs (`R1`, `R2`) and nonfunctional IDs (`N1`). Map each to design decisions, tasks, tests, and final evidence. Keep the mapping proportional: a short table is enough for normal work.
