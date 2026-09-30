# Engineering guide

## The gate
`bazelisk test //...` runs unit tests, format, lint and BUILD-file lint. It must be green before every commit that changes code, and the `pre-push` hook and CI run it. Fix what it reports:
- Python format: `bazelisk run //tools/python:ruff -- format .`
- Python lint: `bazelisk run //tools/python:ruff -- check . --fix`
- BUILD and .bzl: `bazelisk run //tools/bazel:buildifier -- -lint=fix <repo-relative file paths>`, run from the workspace root

Enable the hooks once per clone: `git config core.hooksPath .githooks`.
- `pre-commit` checks the format of staged `.py` files with ruff and of staged `.bazel` and `.bzl` files with buildifier.
- `commit-msg` checks the message against CLAUDE.md "Commit format".
- `pre-push` runs `bazelisk run //tools/git:check_packages`, then `bazelisk test //...`.

## Definition of done
1. `bazelisk test //...` is green.
2. Public modules, classes and functions have literal docstrings and full annotations (ruff `D` and `ANN` enforce this). There is no type checker: nothing verifies that annotations are correct.
3. Code that has a latency budget in the AMe spec has a perf test.
4. One logical change per commit; the message follows CLAUDE.md "Commit format".

## Add a Python package
1. Put the code in `<project>/python/src/<package>/` and tests in `<project>/python/tests/`.
2. Add a `BUILD.bazel` with `python_checks(name = "quality", srcs = glob(["*.py"]), deps = [...])` and `starlark_checks(srcs = ["BUILD.bazel"] + glob(["*.bzl"], allow_empty = True))`. `python_checks` creates `quality_format` and `quality_lint`; `starlark_checks` creates `starlark_check`. A directory with Python files and no `BUILD.bazel` fails `//tools/git:check_packages`.
3. Add an `ame_test` target per test file.

## Test kinds and where they run
- Small tests (no `kind`) are hermetic and run under `bazelisk test //...`.
- `kind = "hardware" | "gpu" | "cloud"` tests are manual, exclusive and large. Run one by name: `bazelisk test //ame/python/tests:<target>`. List what `//...` skips: `bazelisk query "attr(tags, manual, //...)"`.
- Perf tests use `ame_perf_test`, are manual, and are not run in CI (hosted runners are too noisy). Run one by name, for example `bazelisk test //ame/python/tests:test_perf_smoke`.

## Add a dependency
Ask the user first (CLAUDE.md rule 5). Then pin it in `requirements_lock.txt` (exact version, including transitive packages), reference it with `requirement("name")` in the BUILD file, and record the reason in the commit body.

## Add a language
Add its Bazel rules to `MODULE.bazel` (approval needed), create `<project>/<language>/`, and add matching check macros under `tools/<language>/`. Keep the rule: one gate, `bazelisk test //...`. For C++, use `-Wall -Wextra -Werror`, clang-tidy, clang-format and an ASan/UBSan `--config`.

## Profile before optimising
Optimise only what a perf test or a profile flags, and put before and after numbers in the commit body.
- CPU: `python -m cProfile -o profile.out script.py`, then `python -c "import pstats; pstats.Stats('profile.out').sort_stats('cumulative').print_stats(20)"`.
- Memory: `tracemalloc.start()` at the top of the code under test, then `tracemalloc.take_snapshot().statistics('lineno')[:10]`.
