# LLM efficiency and context engineering

Use this when the delivery uses Claude, Codex, another coding agent, an LLM API, tool calling, or subagents. Optimize **cost per successful verified outcome**, not tokens per request. A shorter run that fails, retries, or needs rework is not cheaper.

## What a skill can and cannot change

A well-routed skill can reduce repeated discovery, irrelevant context, tool calls, retries, and output. Progressive disclosure keeps only metadata always visible, loads the body on trigger, and loads references on demand. It does not change provider prices or guarantee how a Claude/Codex subscription counts usage. Separate API dollar billing, plan quota, and indirect engineering cost in every claim.

## Context budget

Account for instruction metadata, triggered skill body, loaded references, repository files, tool schemas, tool output, conversation history, reasoning, generated output, retries, and subagent calls. Use `python3 scripts/audit_context.py` to spot oversized or duplicated guidance; its token figure is an estimate, not provider billing.

Optimize in this order:

1. Do deterministic parsing, filtering, validation, and formatting without an LLM.
2. Trigger this skill only for delivery work; test negative prompts so factual lookups stay lightweight.
3. Keep routing concise and progressively disclose only the relevant reference.
4. Retrieve exact files/snippets (`rg` first), respect repository indexes, and do not reread unchanged content.
5. Bound and filter logs, diffs, test output, search results, and tool schemas. Preserve exact code, errors, contracts, and security evidence when lossy summaries could mislead an edit.
6. Put stable instructions and reusable material before variable content when provider prompt caching supports prefix reuse. Avoid needless changes to tool definitions, model, or reasoning settings that invalidate caches.
7. Reuse provider-supported conversation state or persisted reasoning. Compact only after a measured threshold; retain decisions, requirements, exact failures, changed files, and evidence anchors.
8. Select model and reasoning effort by task risk and representative evals. Compare at least one lower-cost/lower-effort candidate; accept it only when quality is non-inferior at the agreed floor.
9. Bound retries, tool steps, output length, subagents, and parallel branches. Delegate only independent work large enough to repay duplicated context.
10. Stop when the acceptance contract is proven. Do not repeat a successful tool call without a changed hypothesis or state.

## API metering and cache safety

At the provider boundary record input, cached input/read, cache writes, output, reasoning where reported, tool calls, attempts, subagent calls, latency, model, price/version, and outcome—without logging sensitive content. Reconcile estimates with provider usage or billing. Cache only content whose privacy, retention, tenant isolation, and invalidation rules are acceptable; a cached secret is still a secret.

Evaluate baseline versus candidate on the same representative fixtures: pass rate/quality, successful outcomes, input/output/cached tokens, calls, retries, latency, and monetary cost when available. Treat unavailable token or billing data as unavailable, never zero. Reject an optimization whose quality, security, or reliability drops below the accepted floor or whose measurement cost exceeds likely savings.

Avoid giant always-visible “optimization” prompts, blind context compression before editing, fabricated token counts, cheapest-model routing without quality evals, recursive summarization, or third-party compression software without provenance and privacy review.
