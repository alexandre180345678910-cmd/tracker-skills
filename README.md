![tracker-skills banner](assets/banner.svg)

# tracker-skills: evidence-first skills for AI coding agents

Three open skills that make Claude Code, Codex and other coding agents work like a careful senior engineer: plan before building, prove before claiming, review before shipping, and spend tokens and cloud money on purpose. They were written and refined in daily production use on a real SaaS, then stripped down to the reusable method.

[![validate](https://github.com/alexandre180345678910-cmd/tracker-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/alexandre180345678910-cmd/tracker-skills/actions/workflows/validate.yml)
![License: MIT](https://img.shields.io/badge/license-MIT-4FC3A1)
![Works with Claude Code](https://img.shields.io/badge/Claude%20Code-skill-FF7A59)
![Works with Codex](https://img.shields.io/badge/Codex-skill-F5B83D)

![ship-with-confidence workflow](assets/ship-with-confidence.svg)

## Key capabilities

- **Ceremony that scales with risk**: a typo fix takes a short path; a production migration gets a threat model, a cost model, a rollback plan and explicit approval.
- **Evidence over confidence**: no step is "done" without a command, an exit code and a result. A missing check counts as a failure, never as partial credit.
- **Security as a release gate**: every code change gets a security delta check, not an optional cleanup pass at the end.
- **Unit economics for paid APIs**: any LLM, cloud or third-party call gets a budget per business outcome and a regression test against runaway cost.
- **LLM efficiency**: optimize cost per *successful verified outcome*, not raw tokens. A cheaper run that fails and retries is not cheaper.
- **Safe git by default**: atomic local commits per task, never pushed as checkpoints; one final push only after every gate is green.
- **Independent verification**: the author is never the only verifier on medium or high-risk work when a second agent is available.

## The skills

| Skill | What it does | When it triggers |
| --- | --- | --- |
| [**ship-with-confidence**](skills/ship-with-confidence/SKILL.md) | Spec-to-delivery workflow: discuss, plan, design, implement, debug, review, secure, verify and ship a change. | Features, fixes, refactors, migrations, APIs, UI work, code review. |
| [**claude-codex-pair**](skills/claude-codex-pair/SKILL.md) | Runs two agents on one task as writer and read-only challenger, with explicit ownership transfers. | You ask Claude and Codex to work together, review each other, delegate or hand off. |
| [**code-health-audit**](skills/code-health-audit/SKILL.md) | Read-only audit of dead code, duplication, bundle size, slow routes and queries, cold start and running cost. | You explicitly ask for a quality, performance or cost audit of existing code. |

They are designed to work together: `code-health-audit` finds the problems, `ship-with-confidence` delivers the fixes, and `claude-codex-pair` keeps two agents from stepping on each other while doing it.

## Quick start

Copy the skills you want into your agent's skills folder.

**Claude Code**

```sh
git clone https://github.com/alexandre180345678910-cmd/tracker-skills.git
mkdir -p ~/.claude/skills
cp -r tracker-skills/skills/* ~/.claude/skills/
```

**Codex**

```sh
mkdir -p ~/.agents/skills
cp -r tracker-skills/skills/* ~/.agents/skills/
```

To install for a single project only, copy into `.claude/skills/` (or `.agents/skills/`) inside that repository instead.

Then just ask for the work. The skill descriptions tell the agent when to load them, for example:

```text
Add team invitations to this app.            -> ship-with-confidence
Have Codex review what you just built.       -> claude-codex-pair
Audit this codebase for dead code and cost.  -> code-health-audit
```

Check that `ship-with-confidence` installed correctly:

```sh
bash ~/.claude/skills/ship-with-confidence/scripts/validate-install.sh
```

## How each skill was designed

### ship-with-confidence

The main skill. Most agent failures in real projects are not bad code; they are skipped steps: guessing at a bug instead of reproducing it, calling work finished without running the tests, pushing half-done work, or quietly adding an API call that costs money on every request. This skill turns those lessons into gates.

- **Small core, references on demand.** `SKILL.md` holds only the non-negotiables and a routing table. The 16 files in `references/` (security, API cost, contracts, resilience, supply chain, UI/UX, LLM efficiency and more) are read only when the task needs them, so a tiny change does not pay for the whole manual in context.
- **Orchestrator, not replacement.** It routes to specialist skills already installed for your stack and never overrides the repository's own instructions or design system.
- **Deterministic helpers.** `scripts/` contains tested Python and shell tools: a secret guard for diffs, a project risk profiler, an evidence validator, a context-size auditor, and git scripts that commit only explicit paths and refuse to push automatically.
- **Measured, not assumed.** `evals/` holds trigger and behavior scenarios (including negative controls such as "What does HTTP 204 mean?", which must *not* load the skill) used to compare each revision against the previous one.
- **Credited sources.** [`references/sources.md`](skills/ship-with-confidence/references/sources.md) lists every public method it learned from, with license and audited commit.

### claude-codex-pair

![claude-codex-pair roles](assets/claude-codex-pair.svg)

Two capable agents in one repository usually fail in one of two ways: they overwrite each other, or they politely agree with each other. This skill fixes both. Exactly one agent holds write access at a time; the other is a read-only challenger whose job is to *disprove* the result with reproducible evidence. Ownership changes hands only through a written handoff that records branch, HEAD, every dirty path and the next action, and the receiving agent re-checks git state instead of trusting the note. After two failed review cycles on the same symptom, the pair must change hypothesis rather than loop.

It uses the official `codex@openai-codex` plugin for Claude Code when installed (`/codex:review`, `/codex:adversarial-review`, `/codex:rescue`, `/codex:transfer`).

### code-health-audit

![code-health-audit pipeline](assets/code-health-audit.svg)

Static analysis tools are noisy and "this looks slow" is not a finding. This audit keeps the evidence bar of a security audit: it records a baseline first (billing, p95 latency, bundle size, query time), keeps a coverage ledger so a partial run never implies the rest is healthy, and hands every candidate to a fresh verifier whose only job is to prove it wrong. What survives is reported with a measured saving and the smallest safe change. Rejected candidates are kept so the next run does not rediscover them. It never edits code; fixes go through `ship-with-confidence`.

## Repository layout

```text
tracker-skills/
├── skills/
│   ├── ship-with-confidence/
│   │   ├── SKILL.md          core rules and routing
│   │   ├── references/       loaded only when relevant
│   │   ├── scripts/          tested helpers (Python stdlib + bash)
│   │   ├── evals/            trigger and behavior scenarios
│   │   └── agents/           Codex display metadata
│   ├── claude-codex-pair/
│   └── code-health-audit/
├── assets/                   diagrams used in this README
└── .github/workflows/        validation on every push
```

## Running the checks

The helpers use only the Python standard library.

```sh
cd skills/ship-with-confidence/scripts
python3 -m unittest -q
bash validate-install.sh
```

## Contributing

Bug reports, eval cases and clearer wording are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first: every behavior change should come with an eval or test that fails without it.

If these skills save you time, a ⭐ helps other people find them.

## License

[MIT](LICENSE) © Alexandre Correia. Concepts adapted from other projects are credited in [`sources.md`](skills/ship-with-confidence/references/sources.md) under their own licenses.

## Why "tracker"?

These skills grew up inside a private product built with AI agents every day. That work showed exactly where agents cut corners, and each rule here exists because skipping it once cost real time. The product stays private; the method is shared here.
