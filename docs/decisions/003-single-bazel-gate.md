# 003. One Bazel gate with per-package check targets
Status: accepted
Date: 2026-09-29

## Context
Style and lint rules only bind if a tool enforces them. Hooks, CI and the developer must not disagree about what "passing" means.

## Options
- **Separate scripts per tool** — drift between hook, CI and local runs.
- **One workspace-wide check target** — a Bazel test cannot see undeclared files, so it would either miss changes or need `local` and uncached execution.
- **Per-package check targets from a macro** — hermetic, cached per package, one command.
- **Aspect `rules_lint`** — the mature form of the previous option; adds a dependency and has less proven Windows support.

## Decision
Per-package macros (`python_checks`, `starlark_checks`) generate format, lint and BUILD checks as small tests. `bazelisk test //...` is the gate for hooks, CI and the developer. Adopt `rules_lint` only if the wrappers become hard to maintain.

## Consequences
- Every package needs a BUILD file with the macro calls; `//tools/git:check_packages` guards against forgetting.
- There is no type checker; ruff `ANN` requires annotations so one can be added later as a `<name>_types` check. Pyright was evaluated and cut because its first run needs network access and Node inside Bazel.
- Hardware, GPU, cloud and perf tests are manual targets and are never part of the gate.
