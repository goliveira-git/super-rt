"""Bazel macros for checking Starlark files."""

load("@buildifier_prebuilt//:rules.bzl", "buildifier_test")

def starlark_checks(srcs, name = "starlark_check"):
    """Adds a small test that fails when any of `srcs` is unformatted or has a lint warning.

    Call once per package with `srcs = ["BUILD.bazel"] + glob(["*.bzl"])`. A package without
    .bzl files passes `glob(["*.bzl"], allow_empty = True)` instead.
    """
    buildifier_test(
        name = name,
        srcs = srcs,
        lint_mode = "warn",
        mode = "check",
        size = "small",
        tags = ["quality"],
    )
