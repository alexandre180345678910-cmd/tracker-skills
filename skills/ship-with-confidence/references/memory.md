# Decisions and lessons

Maintain lightweight project-local state when work spans tasks or sessions. Prefer an existing convention; otherwise use a clearly named state document approved by the repository.

Record durable facts only:

- accepted requirements and decisions;
- current task/status and verification evidence;
- unresolved risks and explicit blockers;
- rollback or operational notes;
- accepted cost budgets, baseline measurements, and optimization trade-offs;
- context-budget decisions, model/effort routing, cache assumptions, and measured LLM quality/cost trade-offs;
- reusable lessons supported by failures.

A lesson contains trigger, observed failure, root cause, corrected rule, verification, scope, and date. Promote a lesson into workflow guidance only after recurrence or strong evidence. Retire stale or contradictory guidance. Never store secrets, raw private data, or transient chain-of-thought.
