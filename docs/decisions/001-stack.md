# 001. Python 3.12 with pytest and ruff
Status: accepted (uv part superseded by 002)
Date: 2026-09-29

## Context
AMe drives an Intel RealSense camera, GPU speech models, voice cloning, and a Claude model on Windows 11 with an RTX 5080. It is a single-developer, single-user project.

## Options
- **Python** — first-class RealSense bindings, every candidate speech and vision library, asyncio for services. Packaging on Windows is the historical pain point.
- **Node/TypeScript** — good for the console and face UI, but weak for camera and ML work; would need Python anyway.
- **Mixed Python + TS** — more moving parts than the project needs now.

## Decision
Python 3.12 for all services; Bazel-managed Python (see 002); pytest; ruff for formatting and linting, enforced by a repo pre-commit hook. 3.12 rather than 3.13 because GPU and camera wheels lag new Python releases.

## Consequences
- One language and one toolchain. The face renderer may still need JavaScript (decided in the face slice).
