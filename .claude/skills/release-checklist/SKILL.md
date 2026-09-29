---
name: release-checklist
description: Execution checklist for releases — the pre-release gate, clean build verification, CI/CD setup, versioning and changelog mechanics, release notes format, and the approval rules for any action that leaves the local machine. Use when setting up delivery automation or cutting a release.
---

# Release checklist

Execution guidance for releases. Read `CLAUDE.md` for build commands, branching, versioning, and commit format.

## The approval rule

**Ask the user and wait for an explicit yes before:** `git push` (any branch, any remote), creating or pushing a tag, publishing to any registry, creating a GitHub release, triggering a deploy, or touching production or any shared environment.

Ask with specifics: the exact command, the target, the version. Approval for one release is never approval for the next. If the user isn't available, stop and report that you're blocked — don't proceed on an assumption.

Local commits and CI config edits need no approval. Crossing the machine boundary does.

## Pre-release gate

Check in this order and stop at the first failure.

1. **Both checks passed** — `test-plan` *and* `review-checklist` each ended in an explicit **PASS** for this change. If either is missing, run it first. This is not waivable under time pressure.
2. **Clean build** — fresh clone or cleaned tree, clean dependency install, full build. Not an incremental rebuild on a warm tree. A build that only works on your machine is not a build.
3. **Full test suite** — run it, paste the real output.
4. **Lint and type checks** — per CLAUDE.md.
5. **Working tree clean**, on the expected branch, up to date with its remote.
6. **Version and changelog consistent** with what is actually shipping.
7. **No secrets in the diff** — scan for keys, tokens, credentials, internal URLs.
8. **Dependencies** — nothing added without approval; no known-vulnerable versions.

Never release past a red build. If something fails, stop and report it with the output.

## CI/CD setup

- Build, lint, and test on every change; fail loudly and specifically.
- Keep it fast enough that people don't route around it. A pipeline everyone skips protects nothing.
- Cache dependencies; don't cache build output that could go stale.
- **Secrets come from the platform's secret store**, never from a file in the repo, and never echoed into a log.
- Pin action and tool versions so the pipeline is reproducible.
- Deploys are separate from builds and gated on approval.
- Get any new CI action or tool approved first — name it, say what it does and why.

## Versioning

Apply the versioning scheme in CLAUDE.md consistently. Under semantic versioning: **major** for breaking changes, **minor** for backward-compatible additions, **patch** for backward-compatible fixes. When in doubt about whether something breaks, it breaks — say so.

The version lives in one place, and everything else reads it from there.

## Changelog

Keep an unreleased section that accumulates entries as work lands; cutting a release renames it to the version with a date. Group by **Added / Changed / Deprecated / Removed / Fixed / Security**. Entries describe user-visible impact, not commits. Write the prose with the `doc-style` skill.

## Release notes

For someone deciding whether to upgrade. In order:

1. **Breaking changes first**, each with its migration step. Never bury one.
2. **New capabilities** — what they let someone do.
3. **Fixes** — what was broken, and whether they were affected.
4. **Known issues** and anything deferred.
5. **Upgrade instructions** when they're more than "update the version".

## Cutting the release

1. Run the pre-release gate.
2. Update version and changelog; commit locally using the project's commit format.
3. Write the release notes.
4. **Ask for approval**, stating the exact commands and targets.
5. On approval: tag, push, publish, deploy — in that order, verifying each.
6. Confirm the published artifact actually installs and runs.
7. Report what shipped and where.

## If a release goes wrong

Say so immediately and plainly. State what's broken, what the blast radius is, and the options — roll back, patch forward, or pull the release. Never quietly re-push over a bad release; people may already have it.

## Related plugin skills

Invoke these when the situation matches; this skill still sets the bar.

- `superpowers:verification-before-completion` — for the pre-release gate.
- `superpowers:finishing-a-development-branch` — to decide how the finished branch is integrated. The approval rule above still applies to any push.
