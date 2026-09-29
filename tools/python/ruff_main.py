"""Runs the ruff executable shipped in the ruff wheel from the workspace root.

Forwards command-line arguments. The wheel's `bin/ruff.exe` sits next to `site-packages` in the
Bazel pip repository, where `ruff.__main__.find_ruff_bin` does not look.
"""

import os
import subprocess
import sys
from pathlib import Path

import ruff


def find_ruff() -> Path:
    package_dir = Path(ruff.__file__).resolve().parent
    for root in (package_dir.parent.parent, package_dir.parent):
        candidate = root / "bin" / "ruff.exe"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"ruff executable not found next to {package_dir}")


workspace = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
sys.exit(subprocess.call([str(find_ruff()), *sys.argv[1:]], cwd=workspace))
