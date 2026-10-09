"""Bazel macros shared by all test targets."""

load("@pip//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_test")

KINDS = ["hardware", "gpu", "cloud"]

def ame_test(name, src, deps = [], data = [], kind = None, tags = [], **kwargs):
    """A py_test that runs `src` under pytest.

    Without `kind` the test is small and runs with `bazelisk test //...`. `kind` is one of
    "hardware", "gpu" or "cloud": such a test is tagged manual and exclusive, sized large, and
    must be run by name, for example `bazelisk test //ame/python/tests:test_camera`.
    Do not pass `size`: it is derived from `kind`.

    Args:
      name: target name.
      src: the pytest file to run.
      deps: libraries the test imports; pytest is added.
      data: extra runtime files, added to `src`.
      kind: None, or one of KINDS.
      tags: extra tags, added to the ones `kind` implies.
      **kwargs: forwarded to py_test, except `size`.
    """
    if "size" in kwargs:
        fail("ame_test derives size from kind (small, or large when kind is set); do not pass size")
    if kind != None and kind not in KINDS:
        fail("kind must be one of %s, got %r" % (KINDS, kind))
    py_test(
        name = name,
        srcs = [src, "//tools/python:pytest_runner.py"],
        main = "//tools/python:pytest_runner.py",
        args = ["$(rootpath %s)" % src],
        data = [src] + data,
        deps = deps + [requirement("pytest")],
        size = "large" if kind else "small",
        tags = tags + ([kind, "manual", "exclusive"] if kind else []),
        **kwargs
    )

def python_checks(name, srcs, deps = []):
    """Adds format, lint and type checks for `srcs` as small quality tests.

    Call once per package with `srcs = glob(["*.py"])`; deps supplies imported libraries.
    """
    for mode in ["format", "lint"]:
        py_test(
            name = "%s_%s" % (name, mode),
            srcs = ["//tools/python:check_runner.py"],
            main = "//tools/python:check_runner.py",
            args = [mode] + ["$(rootpath %s)" % src for src in srcs],
            data = srcs + ["//:ruff.toml"],
            deps = ["//tools/python:ruff_bin"],
            size = "small",
            tags = ["quality"],
        )

    py_test(
        name = "%s_types" % name,
        srcs = ["//tools/python:types_runner.py"],
        main = "//tools/python:types_runner.py",
        args = ["$(rootpath %s)" % src for src in srcs],
        data = srcs + ["//:mypy.ini"],
        deps = deps + [requirement("mypy"), requirement("pytest")],
        size = "small",
        tags = ["quality"],
    )

def ame_perf_test(name, src, deps = [], kind = None, tags = [], **kwargs):
    """An ame_test for a latency or memory budget, run on demand and never by `//...`.

    Tagged manual, perf and exclusive so no other test competes for the CPU while it measures.
    Uses pytest-benchmark; assert the budget with `perf_budget.assert_median_under`.
    Extra `tags` are added to the fixed ones.
    """
    ame_test(
        name = name,
        src = src,
        deps = deps + [requirement("pytest-benchmark")],
        kind = kind,
        tags = tags + ["manual", "perf", "exclusive"],
        **kwargs
    )
