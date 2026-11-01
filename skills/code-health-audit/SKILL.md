---
name: code-health-audit
description: "Read-only AUDIT of code quality, performance, and running cost of an existing codebase: dead code and unused exports/dependencies, duplication, oversized client bundles, slow or chatty routes and queries, cold start, function CPU/memory, and observability volume. Use ONLY when the user explicitly asks for a quality, cleanup, performance, cost, or 'auditoria de qualidade/performance/custo' review of code that already exists. Produces measured, independently verified findings; never edits code. Do NOT use to implement or review a change (use ship-with-confidence), for security (use security-audit), or for a single known bug."
---

# Code Health Audit

Find where the existing code is dead, duplicated, slow, or expensive, prove each claim with a
measurement or a complete reachability trace, and hand the owner small, ordered changes. This
is the quality and performance counterpart of `security-audit`, with the same evidence bar:
an unproven candidate is not a finding.

The audit is read-only. Fixes are a separate task delivered through `ship-with-confidence`.

## Authority

1. The user's request sets scope and budget.
2. The repository's own instructions (`AGENTS.md`, `CLAUDE.md`, a project team skill) override
   anything generic here. Read them first; they usually hold measured lessons that a generic
   optimization would undo.
3. Installed framework docs beat memory of older versions.

## Execution safety

- Source inspection is read-only. Analysis tools (Knip, bundle analyzers, type checker) may
  run against a disposable worktree or the clean checkout; they must not write into the
  tracked tree. Pin the tool version and record it.
- Platform metrics (hosting usage, function metrics, APM volumes, database statistics) are read
  through read-only commands or connectors. Never change configuration, sampling, firewall,
  environment variables, or data to "test" a hypothesis.
- Database timing: run `EXPLAIN (ANALYZE, BUFFERS)` only for `SELECT`, never on production
  writes, and repeat it. A single managed-database timing can vary by more than an order of
  magnitude; report median and spread of at least 5 runs, never one number.
- Never print environment values, connection strings, tokens, or user data into the report.

## Output

Write to `~/code-health-audit/<repo>/run-<N>/` (outside the repository unless the user names a
git-ignored path):

- `run-metadata.json`: repo, source ref and whether the worktree is dirty, scope, profile,
  budget, tool versions, measurement window.
- `baseline.md`: the numbers the findings will be judged against (see Phase 1).
- `findings.json`: array of records, each with `id`, `area` (`dead-code`, `duplication`,
  `bundle`, `route-latency`, `query`, `cold-start`, `compute-cost`, `observability-cost`,
  `dependency`), `verdict` (`confirmed`, `needs_validation`, `rejected`), `evidence` (paths with
  line numbers, commands, measured values with window and sample size), `impact` (only for
  confirmed: expected saving in ms, bytes, invocations, or money, with how it was derived),
  `risk` of the change, `smallest_change`, `verification` (the test or measurement that proves
  the change worked), and `blocked_by` for `needs_validation`.
- `REPORT.md`: derived from `findings.json` only, ordered by value per unit of risk.

## Workflow

### Phase 1: Baseline

Before hunting, record what the system costs and how it behaves now:

- Billing: current usage against included credits, so a "saving" is stated in real money and
  not in a metric that is already free.
- Top routes by invocations, CPU time, memory-time, and p95 duration over a stated window.
- Cold versus warm start time per route when the platform exposes it.
- Client bundle size per heavy page.
- Query count and database time per hot route, when instrumentation allows.
- APM/observability volume by type (errors, spans, logs, profiles).

No baseline, no performance finding: without it nothing can be shown to improve.

### Phase 2: Coverage ledger

List the units to inspect: each route group, each heavy page, each background job, each
package boundary, plus the dead-code and dependency sweeps. Mark each unit `planned`,
`covered`, `deferred`, or `out_of_scope`. A scoped run says so; it never implies the rest is
healthy.

### Phase 3: Hunt

Use isolated agents per unit when the platform allows; each returns structured candidates,
not prose. Candidate classes:

- **Dead code**: unused files, exports, types, dependencies. Static tools over-report in
  frameworks with implicit entrypoints (file-based routes, config files, instrumentation,
  scripts invoked from `package.json`, test configs, dynamic `import()`, string references).
  A candidate needs a reachability trace that rules each of those out.
- **Duplication**: two implementations of one contract that already diverge or will. Name the
  contract and the divergence; similar-looking code with different contracts is not a finding.
- **Bundle**: client components pulling large or server-only modules; measure the delta.
- **Route latency and chattiness**: sequential independent I/O, N+1 queries, repeated reads of
  the same data in one request, work done before the cheapest rejection check.
- **Query**: missing index for a measured slow plan, policy predicates evaluated per row that
  could be evaluated once.
- **Cold start**: heavy modules imported on the request path that could load at boot or lazily.
- **Compute cost**: functions kept alive by background work, cron frequency above need,
  memory sized far above measured peak.
- **Observability cost**: spans, logs, or profiles that answer no open question.

### Phase 4: Independent validation

Give every candidate to a fresh verifier whose job is to disprove it: find the dynamic import,
the script entrypoint, the test that depends on it, the measurement that contradicts it, the
ordering or concurrency constraint that forbids the "faster" version. Survivors become
`confirmed`; candidates whose decisive fact lives outside the repository (production traffic,
provider settings) become `needs_validation` with that exact fact; disproved ones are kept as
`rejected` so the next run does not rediscover them.

### Phase 5: Report

Order confirmed findings by measured value against change risk. Group removals into small
batches that one reviewer can check in one sitting. For each batch, name the characterization
or regression test that must exist before the change and the measurement that must move after
it.

## Anti-patterns

1. Reporting a tool's raw output as findings.
2. Claiming a saving without a baseline, or in a resource that is already within free quota
   without saying so.
3. A single timing from a shared or managed database presented as fact.
4. Parallelizing work that shares one connection, transaction, or ordered resource.
5. Recommending caching without naming the invalidation path.
6. One large cleanup change instead of small reversible batches.
7. Treating "unused by static analysis" as "safe to delete".
8. Editing code, configuration, or sampling during the audit.
