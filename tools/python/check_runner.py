"""Runs one quality check on the files given as arguments, from the test's runfiles root.

Usage: check_runner.py <format|lint> <files...>
Exits with the exit code of the underlying tool; exits 0 when no files are given.
"""

import subprocess
import sys

from ruff_bin import find_ruff

RUFF_CONFIG = "ruff.toml"


def run_ruff(mode: str, files: list[str]) -> int:
    """Runs `ruff format --check` (mode "format") or `ruff check` (mode "lint") on `files`."""
    ruff = str(find_ruff())
    if mode == "format":
        command = [ruff, "format", "--check", "--no-cache", "--config", RUFF_CONFIG, *files]
    else:
        command = [ruff, "check", "--no-cache", "--config", RUFF_CONFIG, *files]
    return subprocess.call(command)


def main(argv: list[str]) -> int:
    """Dispatches on the first argument; returns the process exit code."""
    mode, *files = argv
    if not files:
        return 0
    if mode in ("format", "lint"):
        return run_ruff(mode, files)
    print(f"unknown check: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
