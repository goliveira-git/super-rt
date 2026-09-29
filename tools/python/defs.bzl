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
