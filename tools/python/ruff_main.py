"""Runs the ruff executable shipped in the ruff wheel from the workspace root.

Forwards command-line arguments. Used through `bazelisk run //tools/python:ruff -- <args>`.
"""

import os
import subprocess
import sys

from ruff_bin import find_ruff

workspace = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
sys.exit(subprocess.call([str(find_ruff()), *sys.argv[1:]], cwd=workspace))
