---
name: architecture-kickoff
description: Structure for running a project kickoff — the interview questions to ask, how to choose and record a stack, the CLAUDE.md conventions template to fill in, the decision-record format, and how to break a feature into tasks. Use at project start, when adding a major feature, or when recording an architectural decision.
---

# Architecture kickoff

Execution guidance for kickoff. The goal is that any later session can build without asking a question CLAUDE.md should have answered.

## 1. Interview

Ask in batches of three or four. Stop when you could describe the project back to the user without hedging.

**Goal** — What does this do? What does "working" look like in one sentence? What happens today without it?

**Users** — Who uses it? How many, and is that growing? How technical are they? Internal or external?

**Surface** — UI, HTTP API, CLI, library, background service, or several? (If there is a UI, write a spec with `ux-spec` before building it.)

**Constraints** — Where does it deploy? What must it integrate with? What languages does the team already know? Any compliance, privacy, or data-residency requirements? Real deadline? Expected scale and latency?

**Non-goals** — What is explicitly out of scope? What are you deliberately not building?

Where the user has no opinion, decide and say so: "I'm picking X because Y — tell me if you'd rather not." Never stall a kickoff on a preference the user does not have.

## 2. Choose the stack

Record the choice *and the rejected alternatives*. Weight in this order:

1. **Fit for the constraints** — deployment target, integrations, scale, compliance.
2. **Team familiarity** — a boring stack the team knows beats an elegant one it doesn't.
3. **Maturity** — is it maintained, documented, and hireable for?
4. **Operational cost** — what does running this actually take?

Prefer fewer moving parts. Every additional service, language, or framework is a permanent tax on everyone who touches the project. Reach for a database, a queue, or a cache when there is a stated need, not because a real system is assumed to have one.

Propose dependencies to the user and wait for approval. Do not install anything.

## 3. Write `docs/architecture.md`

- **Overview** — what the system is, in a paragraph.
- **Components** — each one's single responsibility and what it owns.
- **Data flow** — how a representative request moves through the system, end to end.
- **Data model** — entities, relationships, and where they live.
- **External interfaces** — APIs consumed and exposed, with their contracts.
- **Cross-cutting** — auth, error handling, logging, configuration, secrets.
- **Deliberate omissions** — what you are not doing yet, and the signal that would change that.

Diagram only where a diagram beats prose.

## 4. Scaffold

`mkdir` the directory structure, with a `.gitkeep` in any directory that would otherwise be empty. Directories only — no source files, no config files, no placeholder code.

## 5. Fill in CLAUDE.md conventions

Replace **every** placeholder. Specific enough that two sessions produce the same-looking code:

- **Stack** — languages, frameworks, database, runtime versions, package manager.
- **Directory layout** — what goes where, and where new code of each type belongs.
- **Style** — formatter and linter with their config, line length, import ordering, quote style. Name the tool and the exact command.
- **Naming** — files, directories, types, functions, variables, constants, database objects.
- **Error handling** — the project's pattern: exceptions vs. results, where errors are caught, what gets logged, what reaches the user.
- **Testing** — framework, where tests live, naming, what must be tested, coverage expectation, the exact run command.
- **Build and run** — exact commands for install, dev, build, lint, test.
- **Branching** — model, branch naming, what merges where, whether main is protected.
- **Commit format** — the exact format with a real example.
- **Configuration and secrets** — where config lives, how secrets are supplied, what must never be committed.

Then verify: run each command you wrote down and confirm it works. A convention nobody can execute is a convention nobody follows.

## 6. Decision records

One file per significant decision in `docs/decisions/NNN-short-title.md`:

```
# NNN. Title
Status: accepted | superseded by NNN
Date: YYYY-MM-DD

## Context
What forced a decision. The constraints in play.

## Options
What was considered, with the real tradeoff of each.

## Decision
What was chosen, and why this one.

## Consequences
What this makes easy, what it makes hard, what it forecloses.
```

Write one whenever a choice would be expensive to reverse or would puzzle someone in six months.

## 7. Break work into tasks

One task = one outcome. Each task states:

- **Outcome** — what is true when it's done.
- **Acceptance criteria** — how anyone can check that, concretely.
- **Scope** — files or modules it touches, and what it must not touch.
- **Dependencies** — what must land first; mark tasks that can run in parallel.

Size a task so its outcome is verifiable in one pass. If you cannot state the acceptance criteria, the task is not yet defined — split it until you can.

## Related plugin skills

Invoke these when the situation matches; this skill still sets the bar.

- `superpowers:brainstorming` — during the interview, to explore intent and design options before committing to one.
- `superpowers:writing-plans` — when breaking a feature into tasks (step 7).
