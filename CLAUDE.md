# Project

> **Status: not yet kicked off.** The Conventions section is filled in during kickoff (`architecture-kickoff` skill). Until then, do not write project code.

**What this is:** _(filled in at kickoff: one paragraph — what the project does and who it's for)_

---

## Workflow

Each stage has a skill. Load it when you reach that stage, and use the installed plugin skills it lists under "Related plugin skills" when they fit the task.

| Stage | Skill | Output |
|---|---|---|
| Kickoff, major feature, structural decision | `architecture-kickoff` | `CLAUDE.md` Conventions, `docs/architecture.md`, `docs/decisions/` |
| UI design (only if the feature has a UI) | `ux-spec` | `docs/ux/<feature>.md` |
| Build | `superpowers:test-driven-development`, `superpowers:executing-plans`; UI: `frontend-design:frontend-design`, charts: `dataviz` | code + unit tests, per Conventions |
| Test | `test-plan` | tests, suite result, coverage, **PASS**/**BLOCK** |
| Review | `review-checklist` | findings, **PASS**/**BLOCK** |
| Docs (only if the public surface changed) | `doc-style` | README, API docs, changelog entry |
| Release | `release-checklist` | verified build, release notes |

**Rules:**

1. **Nothing starts before kickoff.** If the Conventions section still has placeholders, stop and run kickoff first.
2. **UI work needs a spec.** Build UI from a `docs/ux/` spec, not from imagination. No spec → write one with `ux-spec` first.
3. **Both checks must pass before release.** `test-plan` and `review-checklist` must each end in an explicit **PASS**. Not waivable under time pressure.
4. **Ask before crossing the machine boundary.** Push, tag, publish, deploy, or anything touching a shared environment requires explicit user approval each time.
5. **No new dependency, library, or tool without the user's approval.** Name it, say what it's for and why existing tools won't do, and wait for a yes. This includes third-party skills and plugins.
6. **Git: branch per feature, commit per passed stage.** Work on a branch, not on `main`. Commit locally when a stage passes its check. Never push, tag, or merge into `main` without asking (rule 4). Until kickoff fills in Branching and Commit format below, name branches `feature/<short-name>` and write commit subjects in the imperative mood ("Add login form").

---

# Conventions

> **PLACEHOLDER — filled in at kickoff.** Binding once written. Replace every placeholder with a specific, verifiable answer, and run each command you write down to confirm it works.

## Stack
_Languages, frameworks, database, runtime versions, package manager. Record why, and what was rejected._

## Directory layout
_What goes where. Where new code of each type belongs._

## Style
_Formatter and linter with config, line length, import ordering, quote style. Name the exact command._

## Naming
_Files, directories, types, functions, variables, constants, database objects._

## Error handling
_The project's pattern: exceptions vs. results, where errors are caught, what is logged, what reaches the user._

## Testing
_Framework, where tests live, naming, what must be tested, coverage expectation, exact run command._

## Build and run
_Exact commands: install, dev, build, lint, test._

## Branching
_Model, branch naming, what merges where, whether `main` is protected._

## Commit format
_The exact format, with a real example._

## Configuration and secrets
_Where config lives, how secrets are supplied, what must never be committed._
