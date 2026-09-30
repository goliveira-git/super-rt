"""Bazel macros shared by all test targets."""

load("@pip//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_test")

def ame_test(name, src, deps = [], **kwargs):
    """A py_test that runs `src` under pytest with the default marker filter."""
    py_test(
        name = name,
        srcs = [src, "//tools/python:pytest_runner.py"],
        main = "//tools/python:pytest_runner.py",
        args = ["$(rootpath %s)" % src],
        data = [src],
        deps = deps + [requirement("pytest")],
        **kwargs
    )

def python_checks(name, srcs, deps = []):
    """Adds format and lint checks for `srcs` as small tests named `<name>_format` and `<name>_lint`.

    Call once per package with `srcs = glob(["*.py"])`. `deps` are the libraries `srcs` import.
    """
    for mode in ["format", "lint"]:
        py_test(
            name = "%s_%s" % (name, mode),
            srcs = ["//tools/python:check_runner.py"],
            main = "//tools/python:check_runner.py",
            args = [mode] + ["$(rootpath %s)" % src for src in srcs],
            data = srcs + ["//:ruff.toml"],
            deps = deps + ["//tools/python:ruff_bin"],
            size = "small",
            tags = ["quality"],
        )
