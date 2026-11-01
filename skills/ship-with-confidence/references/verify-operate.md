# Verification and operational readiness

## Evidence matrix

Map each requirement and nonfunctional risk to an evidence item: test name, command result, browser journey, diff inspection, scan, migration rehearsal, or operational check. Missing evidence is FAIL.

Use the narrowest check during iteration, then run the repository's full relevant integration gate from a known state. Record command, exit status, and meaningful result; never report “all tests pass” from stale output.

## Independent verification

For medium/high-risk work, a fresh verifier must inspect the accepted requirements, diff, and evidence without inheriting the author's conclusion. The verifier attempts to falsify claims, exercises boundaries and negative cases, and reports PASS/FAIL with evidence. The author fixes failures; the verifier rechecks them.

For critical algorithms or security controls, add mutation or adversarial testing: deliberately weaken the implementation or test fixture and confirm the tests fail. Restore the code and rerun.

## Operational gate

When runtime behavior, schema, infrastructure, jobs, or external integrations change, verify:

- deployment/config compatibility and required environment variables;
- migration forward/backward compatibility, backup, rehearsal, and rollback;
- public/event/schema contract compatibility and consumer evidence;
- timeouts, retries, idempotency, concurrency, rate/resource bounds;
- SLO, RTO/RPO, tested restore/recovery, dependency degradation, and rollout/rollback rehearsal;
- locked dependencies, artifact/SBOM/provenance and pinned CI review when release/supply-chain exposure changes;
- logs, metrics, traces, alerts, and safe redaction;
- per-route/feature/tenant unit-cost metrics, budgets, anomaly alerts, and billing reconciliation for metered dependencies;
- feature flag, staged rollout, health criteria, and rollback trigger;
- runbook/ownership for predictable failure modes.

## Final integration and push

1. Confirm working tree contents and preserve unrelated changes.
2. Run final tests, build/type/lint as relevant, applicable security, contract, resilience, supply-chain, API cost, LLM-efficiency gates, and complete user journeys.
3. Check commit history and traceability.
4. Obtain independent PASS when required.
5. Summarize residual risks and rollback.
6. Record checks in a schema-v2 evidence manifest bound to delivery ID, HEAD, branch, risk, and verifier. Every check must include its command, declared zero exit code, an output artifact path, and that artifact's SHA-256 digest. The receipt makes the declaration tamper-evident; it does not prove that the command ran or that the verifier is independent. Treat it as an audit aid, never as release or authorization proof.
7. Only now, if the user explicitly authorizes it in the current interaction and a remote exists, the active writer may run one ordinary `git push`. `final-push.sh` intentionally blocks automation because local files cannot prove user identity or current authorization.

If the push fails, report it without rewriting history or retrying destructive alternatives.
