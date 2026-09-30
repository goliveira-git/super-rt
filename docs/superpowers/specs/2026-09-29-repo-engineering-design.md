# Repo engineering foundation — design

Date: 2026-09-29 · Status: approved 2026-09-29, implemented · Builds on `docs/decisions/002-bazel-monorepo.md`

## 1. Purpose and success criteria

Make the monorepo enforce readable, maintainable, fast code by machine, so no rule depends on remembering it. Built for one developer on a small token budget; more projects and languages (C++ first) will join.

Success means:
- One command, `bazelisk test //...`, runs every check: tests, format, lint, BUILD-file lint. The commit hook, CI and the developer run the same command, so they cannot disagree.
- A broken or unformatted change cannot reach `main` without an explicit bypass, and CI catches bypasses.
- Every public module, class and function has a literal docstring, and annotations are required on all non-test code (enforced by ruff `ANN`).
- Latency budgets from the AMe design spec (§9 Testing, end-to-end latency harness; §6 face frame-time budget) are executable tests, and optimisation is driven by a measurement.
- Adding a language or a dependency follows a written procedure.

Non-goals: a custom presubmit service, generated API docs, a second build tool, CODEOWNERS or formal review (the `/code-review` skill and `review-checklist` cover review), Bazel `visibility` boundaries between services (deferred until `libs/` has its first user).

## 2. Single gate: checks as Bazel targets

`bazelisk test //...` includes, besides unit tests, small hermetic check targets. A Bazel test only sees files declared as its inputs, so checks are generated per package by a macro that each package calls with its own sources (`glob(["*.py"])`), which also lets Bazel cache results per package:

| Macro | Targets per package | Fails when |
|---|---|---|
| `python_checks` (`//tools/python:defs.bzl`) | `quality_format` (`ruff format --check`), `quality_lint` (`ruff check`) | a file is unformatted or breaks a lint rule |
| `starlark_checks` (`//tools/bazel:defs.bzl`) | `starlark_check` (`buildifier` check, lint warnings on) | a BUILD or .bzl file is unformatted or has a lint warning |

A guard (`//tools/git:check_packages`, run by `pre-push` and CI) fails when a directory holds tracked `.py` files but no `BUILD.bazel`, since such a package would escape every check.

The macros are small wrappers written here, not a third-party lint framework. If they become hard to maintain, adopt Aspect `rules_lint` in their place (a new dependency, so it needs its own approval and decision record).

`bazelisk run //tools/python:ruff -- format .` and `bazelisk run //tools/bazel:buildifier -- <files>` fix what the checks report.

## 3. Test sizes replace pytest markers

Bazel `size` and `tags` express what the `hardware`, `gpu` and `cloud` markers did:

- **small** (default): hermetic, no I/O beyond temp files, seconds. Run by `//...`.
- **manual + exclusive**, with tag `hardware`, `gpu` or `cloud`: excluded from `//...`, run by name (for example `bazelisk test //ame/python/tests/eyes:test_camera`). `exclusive` stops two hardware tests using the camera at once.
- The `ame_test` macro takes `tags` and sets the `size` default (Bazel derives the timeout from the size); the pytest `-m` filter in the runner is removed.
- A test file is either all hardware or none; mixed files are split.

## 4. Annotations and lint

- **ruff** rules widened to `E, F, I, UP, B` plus `ASYNC` (services are asyncio), `PT` (pytest style), `SIM`, `C4`, `RUF`, `PERF`, `C901` with `max-complexity = 10`, and `D100`–`D104` (a docstring must exist on public modules, packages, classes, methods and functions) and `ANN` (parameters and return values must be annotated); tests are exempt from both.
- Docstring content ("literal, no aspirations") and "no comments unless necessary" stay review rules; no tool can judge them.
- **No type checker for now.** pyright was cut from this design because its first run needs network access and Node inside Bazel, which could stall the work. Annotations are still required (`ANN` rules) so a checker can be added later without rewriting code; correctness of types is left to review until then.

## 5. Hooks and CI

Hooks (`.githooks/`, shell scripts run by Git Bash, enabled once per clone with `git config core.hooksPath .githooks`):
- `pre-commit`: `ruff format --check` on staged Python files and `buildifier -mode=check` on staged BUILD and .bzl files. Fast on purpose so commits stay quick.
- `commit-msg`: subject at most 72 characters, no trailing period, blank line after the subject; trailers pass through.
- `pre-push`: `bazelisk test //...` and the package guard (cached, so quick after the first run).

CI (`.github/workflows/ci.yml`, GitHub Actions, `windows-latest`), on every push and pull request:
1. checkout, restore the Bazel disk cache;
2. `bazelisk test //...`;
3. commit-message check over the commits of the branch.

CI is the authority; hooks are a convenience and can be bypassed. The workflow file is committed locally. Pushing it and enabling branch protection on `main` (require CI, linear history) each need the user's approval (`CLAUDE.md` rule 4).

## 6. Performance

- Latency budgets in the AMe spec become `perf` tests. Each is an `ame_perf_test` target tagged `manual`, `perf` and, if it needs hardware, `hardware`. It runs on the developer's PC on demand; CI does not run it because hosted runners are too noisy to measure latency.
- **pytest-benchmark** provides timing statistics inside perf tests (new tool; needs approval, §9). A budget assertion fails the test when the median exceeds it.
- Profiling uses the standard library: `cProfile` for CPU, `tracemalloc` for memory. `docs/engineering.md` gives a short recipe for each. No dependency.
- Rule: optimise only what a budget test or a profile flags, and record the before and after numbers in the commit body.
- When C++ arrives: `-Wall -Wextra -Werror`, clang-tidy, clang-format, and ASan/UBSan Bazel configs (`--config=asan`), in the same test-target style. Not built now.

## 7. Housekeeping

- `.editorconfig` (UTF-8, LF, 4-space indent for Python, 2 for Bazel, YAML and TOML) and `.gitattributes` (`* text=auto eol=lf`, binary types declared). Removes the CRLF warnings; any line-ending normalisation of existing files is its own commit.
- Commit `MODULE.bazel.lock` (remove it from `.gitignore`) so dependency resolution is reproducible.
- `docs/engineering.md`: definition of done (`bazelisk test //...` green, docstrings present, budget tests for latency-sensitive code), how to add a dependency (rule 5, pin in `requirements_lock.txt`), how to add a language (MODULE.bazel rules, a folder under the project, matching lint and test targets), how to profile.
- `CLAUDE.md` Conventions updated to point at the single gate, test sizes, and the hooks.

## 8. Build order (one commit each; hooks first so later commits are checked by them)

1. `.editorconfig`, `.gitattributes`, `MODULE.bazel.lock` tracked.
2. `.githooks/` and enabling instructions.
3. Wider ruff rules, and the fixes the new rules require.
4. `python_checks` (`quality_format`, `quality_lint`).
5. `buildifier_prebuilt` and the `starlark_checks` macro.
6. Test sizes: `ame_test` gains `tags`, hardware and GPU tests become manual, the pytest marker filter is removed.
7. Perf tooling: `pytest-benchmark`, `ame_perf_test`.
8. CI workflow.
9. `docs/engineering.md` and the `CLAUDE.md` update.

Each step keeps `bazelisk test //...` green.

## 9. New tools needing user approval (CLAUDE.md rule 5)

| Tool | Purpose | Why existing tools will not do |
|---|---|---|
| `pytest-benchmark` (pip) | timing statistics for perf tests | requested by the user; `timeit` lacks statistics and pytest integration |
| `buildifier_prebuilt` (Bazel module) | format and lint BUILD and .bzl files | nothing else understands Starlark |
| `actions/checkout`, `actions/cache` (GitHub Actions) | get the source and keep the Bazel cache in CI | required by any workflow |

The user chose pytest-benchmark in conversation on 2026-09-29. Approval of `buildifier_prebuilt` and the GitHub Actions is given by approving this spec.

## 10. Open items

- Whether `rules_lint` should replace the wrappers is decided only if the wrappers prove painful (§2).
- Branch protection settings are decided when the repo is first pushed.
- A type checker (pyright, mypy or ty) can be added later as a `<name>_types` check in `python_checks`; it was cut because it risked blocking progress.
