# Skill evaluation and release

Every material skill update needs paired forward tests with fresh contexts: baseline receives the raw task; treatment receives the same task plus this skill. Do not reveal either answer or hidden tests to the other condition.

Evaluate positive triggers and negative controls, implementation behavior where feasible, security/adversarial cases, and the exact regression being changed. Record quality/pass rate, trigger precision, elapsed time, retries/tool calls, and tokens/cost only when the platform reports them. Unavailable is not zero.

`scripts/evaluate_skill.py` provides a deterministic phrase-based smoke test; it fails closed when a baseline or treatment record is missing, but it cannot replace semantic review. `scripts/validate-install.sh` proves only portable structure and deterministic helper behavior. Never present either command as proof that fresh-context or implementation evaluation occurred. `scripts/audit_context.py` reports approximate context size and duplication. For implementation fixtures, run project-native tests and inspect diff/evidence/commit behavior with an independent reviewer.

Release only when treatment quality is non-inferior on critical cases, negative prompts do not over-trigger, security/cost gates hold adversarially, portable validation passes, and an independent verifier attempts to falsify the claims.
