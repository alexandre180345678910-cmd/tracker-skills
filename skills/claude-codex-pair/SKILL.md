---
name: claude-codex-pair
description: Coordinate Claude Code and Codex on the same software task with one active writer, an independent read-only reviewer, explicit ownership transfers, evidence-based handoffs, and safe use of the official Codex plugin for Claude Code. Use when the user asks Claude and Codex to work together, delegate to each other, review or challenge each other's work, transfer a session, rescue a task, or continue work across both agents. Do not use for ordinary single-agent implementation or factual questions.
license: MIT
metadata:
  author: Alexandre Correia
  version: 1.0.0
---

# Claude–Codex Pair

Treat Claude Code and Codex as a writer–challenger pair. The roles rotate by task; neither
agent is permanently the lead. Optimize for independent evidence, not agreement.

## Non-Negotiable Invariant

Exactly one agent owns write access to the current worktree at a time.

- The **writer** may inspect, edit, test, and create local commits within the accepted scope.
- The **challenger** is read-only. It attempts to falsify the writer's result with code,
  tests, specs, logs, documentation, and reproducible commands.
- A review verdict never grants permission to edit.
- Do not run two write-capable agents concurrently in the same worktree.
- True parallel implementation requires separate git worktrees, disjoint file ownership,
  and an integration owner named before work starts.

If ownership is unclear, stop writes, inspect git state, and establish the writer before
continuing.

## Select the Smallest Collaboration Mode

### 1. Independent review — default

Use for completed or risky work. The current agent remains writer; the other agent reviews
read-only. The review target must remain stable until the verdict returns:

- Prefer an immutable commit SHA or a dedicated review worktree.
- For working-tree review, the writer must pause edits to every reviewed path until the
  challenger finishes, including when the review runs in the background.
- If the target changes, discard the stale verdict or report the exact reviewed SHA/state
  and review the new delta separately.

The challenger must report:

1. Findings ordered by severity, with file and line evidence.
2. Commands or observations that reproduce each material finding.
3. Assumptions and unverified residual risks.
4. An explicit “no material findings” verdict when appropriate.

The writer may assess the findings, but must not silently weaken requirements or tests to
make the review green.

### 2. Bounded delegation

Use when the other agent is better placed to investigate or implement one concrete task.
Before delegation, the current writer pauses edits and sends:

- objective and exact scope;
- allowed files or ownership boundary;
- acceptance criteria and applicable spec IDs;
- required verification commands;
- relevant constraints from `AGENTS.md`, the active spec, and project conventions;
- expected return contract: status, changed files, test evidence, deviations, and risks.

The delegated agent becomes the writer for that scope. The delegating agent becomes the
challenger after the result returns.

### 3. Ownership transfer

Use when work continues in the other agent or another session. Write `.specs/HANDOFF.md`
using the contract below, then stop editing. A transfer moves ownership; it does not clone
ownership. A dirty worktree is allowed when every dirty path is listed accurately; commit or
stash is a safety option, not a universal prerequisite.

### 4. Separate-worktree parallelism — exceptional

Use only when tasks have no shared files or hidden dependency. Record for each agent:
worktree path, branch, owned files, verification command, and integration order. If either
task touches shared schemas, migrations, lockfiles, generated artifacts, or central config,
keep execution sequential.

## Claude Code → Codex Bridge

When the official `codex@openai-codex` Claude Code plugin is installed, prefer its
built-in operations instead of constructing ad-hoc Codex CLI commands:

- `/codex:review` for a standard read-only review.
- `/codex:adversarial-review` to challenge assumptions, design, safety, cost, or rollback.
- `/codex:rescue` for a bounded investigation or implementation delegation.
- `/codex:transfer` to continue the current Claude session in a persistent Codex thread.
- `/codex:status`, `/codex:result`, and `/codex:cancel` for background work.

Safety rules:

- State “read-only” explicitly for diagnosis or research delegated through `rescue`; the
  plugin otherwise supports write-capable work.
- While a write-capable rescue is active, Claude must not edit the same worktree.
- Prefer background execution for long reviews, but freeze the reviewed paths until it
  returns and never start another writer in the same worktree meanwhile.
- Do not enable an automatic review loop unless the user explicitly requests and monitors
  it; recursive agent loops can consume time and usage without improving the hypothesis.
- Review and correction are separate operations. A review never becomes write-capable;
  accepted fixes require a new, explicitly authorized delegation or ownership transfer.

## Compatibility with TLC Spec-Driven

When `tlc-spec-driven` and this skill are active together, this skill controls multi-agent
ownership and extends TLC's execution protocol:

- TLC task marker `[P]` means “dependency-independent,” not permission to create concurrent
  writers in one worktree. Run `[P]` implementations sequentially unless each writer has a
  separate worktree and disjoint ownership under this skill.
- Every delegated task context must include the applicable `AGENTS.md` collaboration rules,
  in addition to the task, spec, coding principles, conventions, and test commands required
  by TLC.
- During Claude–Codex collaboration, the handoff contract below supersedes TLC's minimal
  handoff fields and incorporates them as a superset. A TLC pause/resume must preserve the
  ownership, git-state, and verification fields; never overwrite them with the smaller
  template.
- TLC's one-task/one-commit rule still applies to the active writer. This skill does not
  authorize extra commits, pushes, or changes outside that task.

## Shared Sources of Truth

Resolve conflicts in this order:

1. The user's current instruction and authorization.
2. Repository instructions (`AGENTS.md`, included by `CLAUDE.md`).
3. Accepted feature spec and project decisions under `.specs/`.
4. The latest `.specs/HANDOFF.md` and verified git state.
5. Conversation summaries or either agent's memory.

Never treat a chat summary as stronger evidence than the repository or executed checks.

## Handoff Contract

Use `.specs/HANDOFF.md` as an ephemeral ownership record. Overwrite stale handoffs; durable
decisions belong in the feature spec or project state.

```markdown
# Handoff

**From:** Claude Code | Codex
**To:** Claude Code | Codex
**Mode:** review | delegation | transfer | integration
**Writer after handoff:** Claude Code | Codex | none
**Date:** <ISO timestamp>
**Feature:** <feature or quick task>
**Task:** <task identifier and status>
**Branch:** <branch>
**Base commit:** <sha>
**Working tree:** clean | list every uncommitted path

## Objective and accepted scope
- <task, spec IDs, allowed files>

## Completed
- <observable result and commit, if any>

## In progress
- <current work and exact file/line, if any>

## Pending
- <next required work>

## Blockers
- <blocker and impact, or none>

## Verification evidence
- `<command>` → <exit code and meaningful result>

## Open findings and residual risks
- <severity, evidence, uncertainty>

## Next action
- <one concrete action and stop condition>
```

Before accepting a handoff, independently verify branch, HEAD, and working-tree state.
Do not assume the filesystem still matches the handoff text.

## Review Loop

1. Writer states scope, success criteria, owned files, and verification plan.
2. Writer implements and records evidence.
3. Challenger reviews read-only and tries to disprove the result.
4. Writer classifies every material finding as accepted, rejected with evidence, or blocked.
5. Writer fixes accepted findings and reruns the relevant gates.
6. Challenger performs one focused recheck of the affected claims.

After two unsuccessful revise–review cycles on the same symptom, stop repeating the same
approach. Change the hypothesis, gather new evidence, or ask the user for a material choice.

## Completion Gate

The pair may call work complete only when:

- ownership is unambiguous and no background writer remains active;
- accepted requirements are mapped to evidence;
- applicable tests and gates pass with real exit codes;
- high and medium findings are resolved or explicitly accepted by the user;
- git state and changed files are reported accurately;
- no push, deploy, migration, external write, or auto-fix exceeded the user's authority.

The useful Batman-and-Robin dynamic is role separation: one builds, the other finds the
reason it might fail. The role that matters is the one needed by the current task.
