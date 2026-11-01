# Resilience and recovery

Use when runtime availability, durable data, queues, external dependencies, concurrency, or deployment behavior changes.

Define the service level objective, critical user journey, dependency assumptions, failure budget, RTO, and RPO. A backup is not recovery evidence: restore representative data in isolation, verify integrity and access, and measure recovery time.

Exercise dependency timeout, 429/5xx, partial response, duplicate/out-of-order event, queue backlog, worker crash, network partition where practical, resource exhaustion, and rollback. Verify bounded deadlines, one retry owner, jitter, idempotency, backpressure, degraded behavior, cancellation, and no retry/fan-out storm.

For medium/high risk, rehearse staged rollout and rollback or roll-forward with explicit health signals. Fault injection must be isolated, budgeted, observable, reversible, and authorized for the environment. Record owner, alert, runbook, escalation, kill switch, and evidence that the recovery path actually worked.
