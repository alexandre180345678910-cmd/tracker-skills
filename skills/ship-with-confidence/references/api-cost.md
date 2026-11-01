# API performance and unit-economics gate

Use this for application endpoints, serverless functions, databases, queues, storage, search, paid third-party services, AI models, and any path whose cost grows with traffic. Optimize measured cost without weakening correctness, security, reliability, or product quality.

## 1. Establish the economic contract

Define both technical and business units. Treat variable/billable consumption as at least medium risk; a public endpoint that directly triggers material spend is high risk. At minimum track:

- cost per request and **cost per successful business outcome**;
- calls/queries/tokens/bytes/compute time per outcome;
- p50, p95, and worst credible fan-out, not only averages;
- cost by route, feature, environment, tenant/customer tier, and provider where cardinality is controlled;
- daily/monthly forecast, hard application budget, alert threshold, kill switch/feature flag, and owner;
- pricing source, currency, version/effective date, and assumptions.

Use an explicit model: `unit cost = Σ(consumption units × effective unit price) / successful business operations`; `projected monthly cost = expected volume × unit cost + fixed cost`. Define both an absolute ceiling and an allowed regression delta—do not invent a universal percentage.

Record the current baseline using production-like traffic or billing/usage evidence. If exact pricing is unavailable, use a versioned estimate with explicit assumptions. Never claim savings from latency alone.

## 2. Draw the request cost graph

For one user outcome, enumerate synchronous and asynchronous work: route invocations, database reads/writes, third-party calls, model input/output tokens, retries/fallbacks, queue messages, storage operations, egress bytes, CPU/memory duration, logs/traces, and background fan-out.

Mark multipliers: loops, N+1 queries, pagination, nested resolvers, recursive agents, per-item provider calls, retry storms, polling, duplicate events, cache misses/stampedes, cold starts, and unbounded concurrency. Include attempts and failure paths; they are often more expensive than success.

## 3. Optimize in this order

1. **Eliminate** unnecessary, duplicate, speculative, or client-triggerable calls.
2. **Bound** work with pagination, quotas, maximum items/tokens/tool steps, timeouts, cancellation, and concurrency limits.
3. **Reduce** payload, selected fields, query work, context, output size, serialization, logging volume, and cross-region egress.
4. **Reuse** safe results through request coalescing, memoization, caching, precomputation, or materialized views with explicit TTL, key, invalidation, tenancy, privacy, and staleness rules.
5. **Batch** compatible operations and remove N+1 behavior. Parallelize only inside provider/database limits; concurrency improves latency but may increase spend.
6. **Control failure amplification** with idempotency, one owning retry layer, bounded exponential backoff plus full jitter, retry budgets, circuit breakers, backpressure, capped queues/dead-letter handling, and non-recursive fallbacks.
7. **Choose an efficient tier** (model, region, instance, storage class, query/index) only after quality and reliability thresholds are protected.
8. **Right-size infrastructure** and use scale-to-zero/reservations/commitments only when workload evidence and rollback justify them.

Do not add a cache blindly. Sensitive or tenant-scoped data needs isolated keys and authorization on cache hits. Do not trade a small bill reduction for silent quality loss, stale financial data, or a security bypass.

## 4. Provider and AI calls

Apply `llm-efficiency.md` to agent/context behavior in addition to this economic gate.

- Wrap provider calls behind one metered boundary that records operation, model/tier, input/output units, cache status, attempts, latency, status, and estimated/actual cost without logging sensitive content.
- Attribute child calls to a request/workflow ID and feature; prevent double counting.
- Cap iterations, tools, tokens, result count, and fallback chain. Cancel downstream work when the caller disconnects or the outcome is already known.
- Use deterministic/local code for deterministic work. Use smaller/cheaper models only after representative quality evals prove the accepted floor.
- Reconcile internal estimates with provider invoices/usage exports; pricing and token accounting change.

## 5. Verification

Create representative fixed fixtures at `N` and `10N` and fail on unintended superlinear growth or when a change exceeds the accepted tolerance without an approved rationale. Assert call/query/job/token/payload counts where stable; use load tests with explicit error, latency, throughput, and resource/cost thresholds for critical paths. Exercise normal, spike, soak, 429/5xx/timeout, warm/cold cache, stampede, stale-data, tenant isolation, and success/failure modes. Use mocks/replays or an isolated budgeted sandbox; never hit a billable production endpoint from automated tests.

Production evidence should include dashboards and alerts for request volume, success rate, p95/p99 latency, provider attempts, cache hit ratio, DB/query count, tokens/bytes, compute duration, cost per 1k successful outcomes, forecast/budget burn, and anomalies. Use low-cardinality route templates, feature, tenant tier, provider, and model—not raw user/request IDs. Reconcile estimates with real billing/usage data. Keep telemetry cardinality, sampling, and retention bounded so observability does not become the new cost problem. Provider spending limits are defense in depth, not a guaranteed application cap.

## 6. Release policy

Block release when a new or changed metered path lacks attribution, baseline, contract, budget, bounded fan-out/retries/queues, production-safe observability, application-side cap/kill switch, rollback, or regression evidence. Also block a material cost regression unless the user explicitly accepts the business trade-off and records owner, projected monthly delta, mitigation, and review date. A provider estimate alone cannot support a dollar-PASS when real billing remains unvalidated.

For infrastructure-as-code, run a cost-diff tool when supported. For Kubernetes/cloud allocation, use provider billing or an OpenCost-style allocation view. For API performance, use a k6-style threshold test or the repository equivalent. Route to stack specialists (Vercel Observability/caching, database performance, AI generation persistence, queues) rather than inventing vendor details.
