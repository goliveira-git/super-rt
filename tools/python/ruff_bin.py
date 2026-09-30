"""Locates the ruff executable inside the Bazel pip repository."""

import importlib.util
from pathlib import Path


def find_ruff() -> Path:
    """Returns the path of the ruff executable shipped in the ruff wheel.

    The wheel puts `bin/ruff.exe` next to `site-packages`, which `ruff.__main__` does not search.
    Raises FileNotFoundError when the ruff package or its executable is missing.
    """
    spec = importlib.util.find_spec("ruff")
    if spec is None or spec.origin is None:
        raise FileNotFoundError("ruff package not found on the import path")
    package_dir = Path(spec.origin).resolve().parent
    for root in (package_dir.parent.parent, package_dir.parent):
        candidate = root / "bin" / "ruff.exe"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"ruff executable not found next to {package_dir}")
