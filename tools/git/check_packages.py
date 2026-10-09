"""Fails when a directory holds tracked Python files but no BUILD.bazel calling python_checks.

A Python package without a BUILD.bazel, or whose BUILD.bazel never calls `python_checks(`, is
skipped by the format, lint and type checks, so it must not exist.
Directories named `spikes` at any depth and the top-level `docs` tree are exempt.
"""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path, PurePosixPath

EXEMPT_ANYWHERE = "spikes"
EXEMPT_TOP_LEVEL = "docs"


def is_exempt(path: str) -> bool:
    """Returns True for a path under a `spikes` directory or under the top-level `docs` tree."""
    parts = PurePosixPath(path).parts
    return EXEMPT_ANYWHERE in parts or parts[0] == EXEMPT_TOP_LEVEL


def find_unchecked_packages(paths: list[str], read_text: Callable[[str], str | None]) -> list[str]:
    """Returns sorted `<directory>: <problem>` lines for directories holding .py files in `paths`.

    A problem is a missing BUILD.bazel or a BUILD.bazel without a `python_checks(` call.
    `read_text` maps a BUILD.bazel path to its text, or to None when it cannot be read.
    """
    build_dirs = {
        str(PurePosixPath(p).parent) for p in paths if PurePosixPath(p).name == "BUILD.bazel"
    }
    python_dirs = {
        str(PurePosixPath(p).parent) for p in paths if p.endswith(".py") and not is_exempt(p)
    }
    problems = []
    for directory in sorted(python_dirs):
        if directory not in build_dirs:
            problems.append(f"{directory}: no BUILD.bazel")
        elif "python_checks(" not in (
            read_text(str(PurePosixPath(directory, "BUILD.bazel"))) or ""
        ):
            problems.append(f"{directory}: BUILD.bazel has no python_checks(")
    return problems


def split_ls_files_output(raw: bytes) -> list[str]:
    """Splits the NUL-separated output of `git ls-files -z` into UTF-8 paths, dropping empties."""
    return [entry.decode("utf-8") for entry in raw.split(b"\0") if entry]


def main() -> int:
    """Checks the tracked files of the workspace; prints offenders and returns 1 if any."""
    workspace = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z"],
            capture_output=True,
            check=True,
            cwd=workspace,
        ).stdout
        paths = split_ls_files_output(output)
    except subprocess.CalledProcessError as error:
        print(
            f"check_packages: git ls-files failed with exit code {error.returncode}",
            file=sys.stderr,
        )
        return 1
    except UnicodeDecodeError:
        print("check_packages: git ls-files output is not valid UTF-8", file=sys.stderr)
        return 1

    def read_text(path: str) -> str | None:
        try:
            return Path(workspace or ".", path).read_text(encoding="utf-8-sig")
        except OSError:
            return None

    problems = find_unchecked_packages(paths, read_text)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
