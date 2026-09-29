---
name: review-checklist
description: Pass structure and reporting format for code review — convention adherence against CLAUDE.md, naming, duplication, readability, dead weight, comments, and obvious safety problems, plus how to rank and phrase findings. Use when reviewing a diff before it goes to release.
---

# Review checklist

Execution guidance for code review. Read `CLAUDE.md` before the diff — most findings are conventions the change ignored, and you cannot enforce what you have not read.

## Gathering context

`git diff`, `git log`, `git show`, `git status` only. Never a command that writes to the working tree, the index, or a remote.

Read the full files around the change, not just the diff hunks. A hunk can look fine and still be wrong for where it sits.

## The pass

### Conventions (against CLAUDE.md, not your taste)
Style and formatting, naming rules, file and directory placement, error-handling pattern, test placement and naming, commit message format, configuration and secret handling. If CLAUDE.md is silent, the surrounding code is the convention — flag inconsistency with it, not with your preference.

### Naming
Does each name say what the thing is and what it does? Flag misleading names hard — a name that lies is worse than one that's vague. Watch for booleans that don't read as predicates, functions whose names hide a side effect, and abbreviations nobody outside this file would expand correctly.

### Duplication
Logic repeated within the diff, or re-implementing something that already exists. **Search before you claim either direction** — grep for the function, the constant, the pattern. A duplication finding that turns out to be wrong costs your credibility on the next one.

Three similar-looking things are not automatically duplication; check whether they actually change together.

### Readability
Functions doing several unrelated things. Nesting deep enough to obscure flow. Control flow you have to simulate in your head. Long parameter lists. Boolean parameters that make every call site unreadable. Clever one-liners where three plain lines would do.

### Dead weight
Unused code, unused imports, commented-out blocks, leftover debug output or TODOs with no owner, abstractions with a single caller and no second one in sight.

### Comments
Present where the code is genuinely non-obvious, absent where they restate it, and **true**. A comment contradicting its code is a must-fix — someone will trust the wrong one.

### Obvious correctness and safety
Not a deep bug hunt — that's `test-plan`. But never pass something visibly broken: unvalidated external input, swallowed exceptions, hardcoded secrets or credentials, resource leaks, off-by-one on a boundary, mutation of shared state, a race in obviously concurrent code, missing null/empty handling on a path that can produce it.

For changes touching auth, secrets, or payments, also run the `security-review` skill.

### Tests
Do tests exist for this change, per CLAUDE.md? Do they test behavior rather than internals? Would they actually fail if the code were wrong? A test that passes against a broken implementation is a finding.

## Reporting

Most severe first. For each finding:

- **`file:line`**
- **What** is wrong — one sentence.
- **Why** it matters — the concrete consequence.
- **Fix** — specific enough to act on without asking you a follow-up.

Separate the two buckets and be honest about which is which:

- **Must fix** — blocks the gate.
- **Suggestion** — worth doing, does not block.

Inflating a preference into a blocker wastes time and teaches everyone to discount the next review.

End with an explicit **PASS** or **BLOCK**, plus what you reviewed and what you did not.

If the change is clean, say so and pass it. Do not manufacture findings to look thorough — a short honest review is more valuable than a padded one.

## Related plugin skills

Invoke these when the situation matches; this skill still sets the bar.

- `code-review:code-review` — when the change is a GitHub pull request.
- `superpowers:receiving-code-review` — when acting on findings, to weigh each one before changing code.
- `security-review` — for changes touching auth, secrets, or payments.
