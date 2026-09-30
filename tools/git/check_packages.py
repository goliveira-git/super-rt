"""Fails when a directory holds tracked Python files but no BUILD.bazel.

A Python package without a BUILD.bazel is skipped by every Bazel check, so it must not exist.
Directories named `spikes` and the `docs` tree are exempt.
"""

import os
import subprocess
import sys
from pathlib import PurePosixPath

EXEMPT_PARTS = ("spikes", "docs")


def find_unchecked_packages(paths: list[str]) -> list[str]:
    """Returns the sorted directories in `paths` that hold a .py file but no BUILD.bazel."""
    build_dirs = {
        str(PurePosixPath(p).parent) for p in paths if PurePosixPath(p).name == "BUILD.bazel"
    }
    python_dirs = {
        str(PurePosixPath(p).parent)
        for p in paths
        if p.endswith(".py") and not set(PurePosixPath(p).parts) & set(EXEMPT_PARTS)
    }
    return sorted(python_dirs - build_dirs)


def split_ls_files_output(raw: bytes) -> list[str]:
    """Splits the NUL-separated output of `git ls-files -z` into UTF-8 paths, dropping empties."""
    return [entry.decode("utf-8") for entry in raw.split(b"\0") if entry]


def main() -> int:
    """Checks the tracked files of the workspace; prints offenders and returns 1 if any."""
    output = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
        cwd=os.environ.get("BUILD_WORKSPACE_DIRECTORY"),
    ).stdout
    unchecked = find_unchecked_packages(split_ls_files_output(output))
    for directory in unchecked:
        print(f"no BUILD.bazel in {directory}, which holds Python files", file=sys.stderr)
    return 1 if unchecked else 0


if __name__ == "__main__":
    sys.exit(main())
