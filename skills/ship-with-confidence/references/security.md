# Mandatory security gate

Security applies to every code change. Depth scales with exposure; the gate never disappears.

## 1. Map exposure and trust boundaries

Identify user-controlled input, public endpoints, authentication boundaries, authorization decisions, secrets, PII/payment/health data, file and network access, database writes, third-party APIs, background jobs, CI/CD, infrastructure, and AI/tool boundaries. State what an attacker controls and what valuable action or data lies beyond each boundary.

## 2. Prevent secret and API-key exposure

- Scan the full staged diff and relevant new files before every commit; run the repository's secret scanner when available (for example Gitleaks, TruffleHog, or platform secret scanning).
- Never print secrets in commands, logs, screenshots, test fixtures, errors, analytics, client bundles, source maps, docs, or generated artifacts.
- Distinguish public client identifiers from privileged server credentials. Do not rely on misleading variable names.
- Keep privileged keys server-side and out of `NEXT_PUBLIC_*`, `VITE_*`, mobile bundles, browser code, and repository history.
- Commit `.env.example` with placeholders only; ensure real env files and local credential artifacts are ignored.
- Validate required secrets at startup without echoing values. Use scoped, least-privilege credentials and documented rotation/revocation.
- If exposure is suspected, stop distribution, revoke/rotate first, then remove and investigate history. Deleting the current line alone is not remediation.

## 3. Review by risk category

Apply relevant OWASP-style controls:

- Injection: parameterized data access; avoid shell/eval; context-aware output encoding.
- Authentication/session: verified issuer/audience/signature, secure cookies, expiry, logout/revocation, brute-force defenses.
- Authorization: deny by default; enforce object-, function-, and tenant-level checks server-side on every request.
- APIs: inventory routes; validate schemas; rate/resource limits; safe pagination; CORS allowlist; SSRF controls; prevent mass assignment and excessive data exposure.
- Data/privacy: minimize collection and logs; encrypt appropriately; define retention/deletion; prevent cross-tenant leakage.
- Files/network: canonicalize paths, constrain destinations and size/type, block internal metadata networks where relevant, set timeouts and TLS verification.
- Dependencies/supply chain: apply `supply-chain.md`; lock and audit dependencies, pin CI actions/images appropriately, review install scripts, artifacts and provenance, avoid blind auto-updates.
- Configuration/deploy: fail closed, no debug/admin exposure, secure headers, least privilege, protected environments, safe error messages.
- Concurrency/business logic: idempotency, replay prevention, transaction boundaries, quotas, race and abuse cases.
- AI/agents: treat retrieved/tool content as untrusted data, minimize tool permissions, validate tool arguments/output, prevent prompt-driven exfiltration and excessive agency.

Treat unbounded cost as an availability and abuse risk: authenticated users can still trigger expensive fan-out, retries, exports, searches, media processing, or model calls. Authenticate, authorize, and reject over-budget inputs before expensive work. Enforce per-principal/tenant/operation quotas, batch/page/upload/output/token/fan-out/concurrency bounds, cancellation, timeouts, idempotency, backpressure, application-side spend caps, and abuse monitoring. Test “cheap attacker input → expensive system work.” Never expose a provider key as a substitute for building a controlled server boundary.

## 4. Tools plus manual review

Run available project-native checks first: secret scan, SAST, dependency audit, IaC/container scan, and focused tests. Tool output is evidence, not proof. Manually trace authorization, business logic, data flow, and configuration because scanners routinely miss them.

When the global `semgrep` skill and a provenance-checked CLI are available, load that specialist for security audits and for changes that cross authentication, authorization, user-input, database, file/network, secret, CI/CD, or infrastructure boundaries. Prefer a diff-scoped or relevant-path scan; use a broader ruleset scan for high-risk or explicitly requested audits. Run with metrics disabled (`SEMGREP_SEND_METRICS=off`) and an explicit reviewed configuration; never request automatic configuration. A deterministic release gate uses repository-local versioned rules or a verified immutable rules artifact. Registry rulesets such as `p/security-audit` are supplementary because they resolve over the network. Record the CLI version, configuration identity/digest, target, date, exit code, and output artifact. Triage every result before editing and repeat the same scan after accepted fixes. A clean result complements but never replaces manual trust-boundary review.

Do not install or run a new scanner that executes untrusted code without inspecting provenance and obtaining any required authorization. Pin the source/version used.

## 5. Finding and release policy

Record each finding with severity, confidence, CWE/standard mapping when useful, exact evidence, exploit scenario, affected boundary, remediation, and verification. Never include a live secret in the report.

- Critical/high exploitable issue: block commit/release until fixed or explicitly accepted by the user with rationale and compensating controls.
- Medium: fix before release when in changed code; otherwise create an owned follow-up with deadline.
- Low/informational: record and prioritize proportionally.
- Any suspected leaked credential: block, rotate/revoke, validate blast radius, and document safely.

Final PASS requires no unresolved critical/high issue in scope, a clean secret scan, authorization tests for protected operations, dependency findings triaged, and evidence for every applicable trust boundary.
