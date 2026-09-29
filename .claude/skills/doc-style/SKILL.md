---
name: doc-style
description: Structure and writing standards for project documentation — README skeleton, API reference format, doc comment rules, guides, changelog entries, and the prose style to use. Use when writing or updating any documentation.
---

# Doc style

Execution guidance for documentation. Read `CLAUDE.md` for the project's documentation conventions and doc-comment format before writing.

## The rule above all others

**Document what is true.** Read the code before describing it. Never document intended behavior, planned behavior, or behavior inferred from a function's name. Verify every example against the actual implementation. If you can't verify something, ask the user — a confidently wrong doc is worse than a missing one.

## README

The only file some readers will ever open. In this order:

1. **What this is** — one or two sentences. What it does and who it's for. No mission statement.
2. **Why you'd use it** — the problem it solves, briefly. Skip for internal tools where that's obvious.
3. **Requirements** — runtime versions, system dependencies, accounts needed.
4. **Install** — exact commands, copy-pasteable.
5. **Quick start** — the smallest complete example that *works*. A reader should reach a running system without opening another file. Show the expected output.
6. **Usage** — the common cases. Link out rather than inlining everything.
7. **Configuration** — options, defaults, and where they're set.
8. **Development** — how to run it locally, run tests, and build.
9. **Where to go next** — links to deeper docs.

## API documentation

For each public endpoint or exported function:

- **Name and signature.**
- **What it does** — one sentence, and any side effect stated explicitly.
- **Parameters** — type, whether required, constraints, default, meaning. Not just a restatement of the name.
- **Returns** — the shape, and what varies.
- **Errors** — every error it can raise, what causes each, and what a caller should do. Document these as carefully as the success case; this is where most API docs fail.
- **Example** — a realistic call with realistic values and its output.
- **Notes** — rate limits, auth requirements, idempotency, pagination, deprecation.

## Doc comments

On every public interface, in the project's native doc format.

Explain **why** and the non-obvious contract — preconditions, invariants, ownership, thread-safety, performance characteristics, why an unexpected approach was taken. Do not restate the signature in prose: `// Sets the name` above `setName(name)` is noise.

Private internals get a comment only where the code is genuinely non-obvious.

When you touch code whose comment is now wrong, fix the comment. A stale comment actively misleads.

## Guides

For anything multi-step or where the obvious approach is wrong. State the goal and the prerequisites up front, number the steps, show real commands and real output, and end with how to verify it worked plus what to do if it didn't.

## Changelog entries

Group by **Added / Changed / Deprecated / Removed / Fixed / Security**. Write the user-visible impact, not the commit: "Fixed a crash when importing a file with no header row", not "fix null check in parser". Breaking changes get their migration step in the entry itself.

## Prose style

- **Plain words.** Short sentences. Active voice. Present tense.
- **Second person** for instructions: "Run the migration", not "The migration should be run".
- **Cut the filler** — "simply", "just", "easily", "obviously", "note that", "it should be noted". They add length and "simply" quietly insults a reader who is stuck.
- **Lead with the action**, then the explanation. People scan for what to do.
- **One idea per paragraph.** Break up walls of text.
- **Code formatting** for anything typed: commands, filenames, identifiers, values.
- **Say the thing.** "This does not support X" beats "support for X is currently limited".
- **Assume intelligence, never assume context.** The reader is smart and has never seen this project.

## While documenting

If you find a bug, a contract mismatch, or code you cannot make sense of, report it and fix it first. Never document around a defect — you would be turning a bug into a specification.
