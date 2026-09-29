---
name: test-plan
description: Execution checklist for testing — bootstrapping the chosen framework, what to test and at which level, an edge-case taxonomy to work through, how to read coverage honestly, and the failure report format with reproduction steps. Use when setting up the test harness or verifying a change.
---

# Test plan

Execution guidance for testing. Read `CLAUDE.md` first for the framework, test location, naming, and run command.

## Bootstrap (first run only)

Set up **the framework CLAUDE.md names**, not a preferred one.

1. Install per CLAUDE.md — get user approval for anything not already listed.
2. Config file, minimal and matching the project's conventions.
3. Test directory layout as CLAUDE.md specifies.
4. Runner wired into the project's scripts so the command in CLAUDE.md works verbatim.
5. **One real test that passes**, exercising actual project code — not `expect(true).toBe(true)`. Proves the harness reaches the source.
6. Run the exact command from CLAUDE.md and confirm it works. If it doesn't, correct CLAUDE.md so it does.
7. Add coverage reporting if the project expects it.

## What to test, at which level

- **Unit** — pure logic, transformations, validation, calculations, parsing. Fast, no I/O. Most of your tests.
- **Integration** — components against real collaborators: data layer against a real test database, handlers through the real routing. Where most genuine bugs surface.
- **End-to-end** — a few critical user journeys only. Slow and brittle; spend them on what would be catastrophic to break.

Prioritize by risk: what breaks silently, what handles money or identity or permissions, what has already broken once, what is hardest to reason about.

## Edge-case taxonomy

Work through deliberately — the happy path is the least interesting test in the file.

- **Cardinality** — zero, one, two, many, more than fits in memory.
- **Numbers** — zero, negative, one over and one under a boundary, maximum, overflow, float precision, division by zero.
- **Strings** — empty, whitespace-only, very long, unicode, emoji, right-to-left, quotes, newlines, injection payloads.
- **Absence** — null, undefined, missing field, missing optional vs. missing required.
- **Structure** — malformed input, wrong type, extra fields, deeply nested, cyclic.
- **Time** — timezones, DST transitions, leap years, clock skew, expiry exactly at the boundary.
- **Concurrency** — simultaneous writes, double submit, out-of-order arrival, partial failure mid-sequence.
- **Failure of things you depend on** — network down, timeout, slow response, malformed response, partial write, permission denied, disk full.
- **Authorization** — the wrong user, no user, an expired session, a valid user without this permission.

## Test quality rules

- **Test behavior, not implementation.** Tests coupled to internals break on every refactor and teach the team to delete tests.
- **Name so the failure line explains itself** without opening the file.
- **One reason to fail per test.** A test asserting six unrelated things reports one confusing failure.
- **Independent and deterministic** — no shared mutable state, no ordering dependency, no wall-clock or live-network reliance. A flaky test is a broken test; report it as one, never retry it into green.
- **Arrange / act / assert**, visibly separated.
- **Assert the actual value**, not merely that something was truthy or that no exception was thrown.
- **Never weaken a test to make it pass.** Loosening an assertion, deleting a case, or blanket-skipping is a failure reported as a success.

## Coverage

Report the number, then say what it hides. Name the paths that are *not* covered and whether that matters. 90% over trivial getters with the payment path untested is worse than an honest 60%. Coverage is a signal, never a target.

## Failure report format

Most severe first. For each:

```
[severity] Short title
What I ran:      <exact command>
Expected:        <the behavior the code should have>
Actual:          <what happened>
Output:          <the real output, trimmed to the relevant lines>
Reproduce:       1. <minimal step>
                 2. <minimal step>
Type:            product bug | test bug | flaky
Location:        file:line if known
```

Minimal reproduction means stripped to the smallest input that still fails. "It fails sometimes when I run the suite" is not a reproduction.

## Result

Report bugs before fixing them, so each fix is deliberate and re-tested. End with an explicit **PASS** or **BLOCK**, the full suite result, and the coverage number.

## Related plugin skills

Invoke these when the situation matches; this skill still sets the bar.

- `superpowers:test-driven-development` — when tests are written before the implementation.
- `superpowers:systematic-debugging` — when a failure's cause is not obvious, before proposing a fix.
- `superpowers:verification-before-completion` — before reporting **PASS**.
