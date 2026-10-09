"""Runs strict mypy on declared sources with a temporary cache."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main(files: list[str]) -> int:
    """Returns mypy's exit code for the given source files."""
    if not files:
        return 0
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(sys.path)
    environment["MYPYPATH"] = os.pathsep.join(sorted({str(Path(file).parent) for file in files}))
    with tempfile.TemporaryDirectory(dir=os.environ.get("TEST_TMPDIR")) as cache:
        return subprocess.call(
            [
                sys.executable,
                "-m",
                "mypy",
                "--config-file",
                "mypy.ini",
                "--cache-dir",
                cache,
                "--no-incremental",
                *files,
            ],
            env=environment,
        )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
