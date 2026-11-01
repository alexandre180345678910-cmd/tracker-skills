# Contributing

Thanks for helping improve these skills. They follow their own rules, so contributions do too.

## Ground rules

1. **Evidence first.** A change in behavior needs an eval case or test that fails before the change and passes after it. Wording-only fixes are exempt.
2. **Keep the core small.** `SKILL.md` holds rules and routing; detail belongs in `references/`. Every line in a skill costs context on every run, so explain what it buys.
3. **No project-specific content.** Skills here must work in any repository. Do not add product names, internal URLs, credentials or private data, even in examples.
4. **Credit sources.** If an idea comes from another project, add it to `skills/ship-with-confidence/references/sources.md` with its license. Do not copy share-alike or restricted text.
5. **Standard library only** for scripts, so the skills install with a plain copy.

## Before opening a pull request

```sh
cd skills/ship-with-confidence/scripts
python3 -m unittest -q
bash validate-install.sh
```

Describe the failure you saw, the change, and the evidence that it now works.

## Reporting a problem

Open an issue with the prompt you gave the agent, what the skill did, and what you expected. A transcript excerpt is the most useful evidence. Remove anything private first.
