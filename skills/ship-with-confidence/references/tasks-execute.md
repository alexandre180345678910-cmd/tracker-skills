# Tasks and execution

## Task contract

Each task must be small enough for one coherent local commit and contain:

- requirement IDs and intended behavior;
- exact boundary/files likely affected;
- test or evidence that fails before and passes after;
- security and data considerations;
- expected API/resource call count and cost-budget effect when metered;
- focused verification command;
- commit message intent.

Prefer vertical behavior over batches such as “all models,” “all APIs,” then “all UI.” Start with a tracer bullet when integration assumptions are uncertain.

## Test-first loop

1. Write or identify the smallest behavioral test.
2. Run it and confirm the expected failure for the right reason.
3. Implement the smallest coherent change.
4. Run focused tests and quality checks.
5. Refactor while green.
6. Inspect the diff for scope, accidental files, generated noise, and secrets.
7. Run the task's security delta check.
8. Commit explicit paths locally.

If a test cannot reasonably precede the change, state why and define equivalent evidence before implementation.

## Git checkpoint policy

- One local commit per completed task; use clear conventional messages when the repository supports them.
- Stage explicit files only. Never use broad staging as a convenience in a dirty tree.
- Before committing, inspect `git status --short`, staged names, staged diff, and secret-scan result.
- Never amend, reset, discard, or rewrite user work without explicit authorization.
- Never push task checkpoints.
- After every final gate passes, perform at most one authorized push containing all local commits.
- If there is no remote, record that fact; installation does not invent one.

`scripts/git-checkpoint.sh` uses literal pathspecs for local checkpoints. After all evidence passes, `scripts/final-gate.sh --delivery DELIVERY_ID --evidence PATH` validates and hashes an evidence declaration against the clean HEAD. This is a tamper-evident audit aid, not proof that commands ran, that a verifier is independent, or that the user authorized a push. `scripts/final-push.sh` deliberately blocks automated pushes; after explicit authorization in the current interaction, the active writer performs one ordinary `git push` directly.
