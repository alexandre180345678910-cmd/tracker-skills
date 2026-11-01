# Diagnosis and review

## Diagnose before fixing

Use this loop:

1. Reproduce the failure with the smallest reliable case.
2. Separate symptoms from the failing contract.
3. Minimize the input, route, state, or revision.
4. Rank hypotheses by evidence and discriminating power.
5. Instrument or test one hypothesis at a time.
6. Identify the root cause and affected invariant.
7. Add a regression test, implement the narrow fix, and remove temporary instrumentation.
8. Check adjacent paths that share the root cause.

Do not stack speculative fixes. If three attempts fail, stop, rebuild the model from evidence, and reconsider the boundary or assumptions.

## Two-axis review

Review specification compliance separately from code quality. Produce findings first, ordered by severity, with file/line evidence, user impact, and a concrete reproduction or reasoning chain. Do not inflate style preferences into defects.

Engineering review covers correctness, simplicity, compatibility, tests, error handling, accessibility, performance, observability, and security. The dedicated security gate remains mandatory.

## Receiving feedback

For each review comment:

1. Restate the technical claim and verify it against the code.
2. Classify it as correct, context-dependent, preference, duplicate, or incorrect.
3. Ask when intent is ambiguous or behavior would materially change.
4. Apply valid feedback in isolated commits or clearly scoped changes.
5. Re-run the evidence affected by the change.
6. Respond with evidence, not performative agreement.

Never implement mutually inconsistent comments silently. Surface the conflict and resolve the governing requirement.
