# 002. Bazel monorepo, no virtual environments
Status: accepted
Date: 2026-09-29

## Context
The repo will hold several projects and possibly several languages (C++ is expected). The user does not want a `.venv`. Decision 001 chose uv, which keeps a `.venv` in the repo.

## Options
- **uv** — fast, but a `.venv` per project and Python-only.
- **Bazel + rules_python** — one build and test tool for every language, hermetic Python 3.12, pinned pip lock. rules_python's Windows launcher creates a short-lived venv in `%TEMP%` at run time and needs symlink rights.
- **Bare system Python** — no isolation, no reproducibility.

## Decision
Bazel via Bazelisk, rules_python with a hermetic Python 3.12, one root `MODULE.bazel`. Layout is `<project>/<language>/`, with shared code in `libs/` and tooling in `tools/`. GPU and camera spikes run outside Bazel with the system Python, because CUDA torch and pyrealsense2 wheels do not fit Bazel's pip lock cleanly.

## Consequences
- Windows Developer Mode is required.
- Bazel keeps its cache in `C:\bzl`, outside OneDrive.
- Windows Application Control blocks `.exe` launchers such as `pytest.exe`; tools run through `bazelisk` instead.
- Adding a language means adding its rules to `MODULE.bazel` and a folder under the project.
- Plan `2026-09-29-ame-slice-0.md` still holds uv commands and old paths in its later tasks; they are corrected as each task is executed.
