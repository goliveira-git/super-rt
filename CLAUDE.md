# Project

> **Status: kicked off 2026-09-29.** Conventions below are binding. Design: `docs/superpowers/specs/2026-09-29-ame-design.md`.

**What this is:** AMe — a local, pt-BR-speaking conversational companion for one person. It sees them through an Intel RealSense depth camera, shows a 3D face scanned from them, speaks in a clone of their voice, and learns who they are from conversation, acting as a sparring partner that thinks like them at their best. Perception, speech, face, and memory run on their PC; only conversation text goes to a Claude model.

---

## Workflow

Each stage has a skill. Load it when you reach that stage, and use the installed plugin skills it lists under "Related plugin skills" when they fit the task.

| Stage | Skill | Output |
|---|---|---|
| Kickoff, major feature, structural decision | `architecture-kickoff` | `CLAUDE.md` Conventions, `docs/architecture.md`, `docs/decisions/` |
| UI design (only if the feature has a UI) | `ux-spec` | `docs/ux/<feature>.md` |
| Build | `superpowers:test-driven-development`, `superpowers:executing-plans`; UI: `frontend-design:frontend-design`, charts: `dataviz` | code + unit tests, per Conventions |
| Test | `test-plan` | tests, suite result, coverage, **PASS**/**BLOCK** |
| Review | `review-checklist` | findings, **PASS**/**BLOCK** |
| Docs (only if the public surface changed) | `doc-style` | README, API docs, changelog entry |
| Release | `release-checklist` | verified build, release notes |

**Rules:**

1. **Nothing starts before kickoff.** If the Conventions section still has placeholders, stop and run kickoff first.
2. **UI work needs a spec.** Build UI from a `docs/ux/` spec, not from imagination. No spec → write one with `ux-spec` first.
3. **Both checks must pass before release.** `test-plan` and `review-checklist` must each end in an explicit **PASS**. Not waivable under time pressure.
4. **Ask before crossing the machine boundary.** Push, tag, publish, deploy, or anything touching a shared environment requires explicit user approval each time.
5. **No new dependency, library, or tool without the user's approval.** Name it, say what it's for and why existing tools won't do, and wait for a yes. This includes third-party skills and plugins, and pip packages a spike installs. Already approved: the Codex plugin (rule 8).
6. **Git: branch per feature, clean history.** Work on a branch, not on `main`, following Branching and Commit history below. Never push, tag, or merge into `main` without asking (rule 4).
7. **Spend tokens where judgment is needed.** The user is on a small monthly plan.
   - **Opus** only for complex or creative work: kickoff, brainstorming, specs, writing plans, UX specs, the final whole-branch review. Claude cannot switch models itself: when work crosses between Opus and Sonnet territory, tell the user to run `/model opus` or `/model sonnet`.
   - **Sonnet** (the default) for executing a written plan, tests, docs, and release steps.
   - **Haiku** for any subagent that only searches or reads.
   - Keep context small: redirect long command output to a file and read its tail; read only the part of a file you need; don't re-read files you just wrote.
   - The global ruflo instruction (swarm and MCP tools for multi-file tasks) does not apply here; use the agents in rule 8.
8. **Delegate execution, keep judgment.** The main session decides, plans, and verifies; delegated agents do the volume. Subagents start cold, so delegate only work worth that startup cost, with a self-contained prompt that names the files, the plan step, and the skill to load.
   - **Codex** (`codex:codex-rescue`, runs on the user's ChatGPT plan, not Claude tokens), without asking: implementing a written plan step, multi-file refactors, mechanical bulk work, a root-cause second opinion after two failed fix attempts, and a review of the diff before commit.
   - **Haiku subagent**: searches and reads that would flood the main context.
   - **Keep in the main session**: kickoff, specs, plans, UX, anything ambiguous or needing back-and-forth with the user, `ame.mind` prompt and cloud-API work, and edits under ~30 lines.
   - Delegated output is not done until the main session has checked the diff and `bazelisk test //...` passes; it then follows Commit history like any other change.
9. **Get smarter as we go.** At each stage boundary (starting a task, before a review, when something fails), name the installed skill that applies and any that was skipped. Flag a recurring task that has no skill and suggest writing one with `anthropic-skills:skill-creator` (a new third-party skill still needs approval, rule 5). When a plan finishes, add a short retrospective to the final report: what cost the most turns or tokens, and what to automate or change next time.

---

# Conventions

## Stack
- **Bazel** (via Bazelisk, version pinned in `.bazelversion`) builds and tests the whole monorepo. **Python 3.12** is the hermetic interpreter Bazel downloads (`rules_python`); pip dependencies are pinned in `requirements_lock.txt`. No `.venv` and no uv.
- More languages may join as sibling folders under a project; C++ is the likeliest (`rules_cc` ships with Bazel).
- Services are **asyncio** programs. Hub transport: WebSocket on `127.0.0.1` (spec §3).
- Cloud model: Anthropic Claude via the official `anthropic` SDK — **only** in `ame.mind`.
- Quality tooling: ruff (with annotation and docstring rules), buildifier, pytest-benchmark; see `docs/decisions/003-single-bazel-gate.md`.
- Rejected: Node/TypeScript (weaker camera and ML ecosystem), uv, pip/Poetry (they keep a `.venv`; Bazel already owns the toolchain), black + flake8 (ruff does both).
- Why: see `docs/decisions/001-stack.md` and `docs/decisions/002-bazel-monorepo.md`.

## Directory layout
```
<project>/<language>/   one folder per project, then per language (ame/python/, later ame/cpp/)
libs/<name>/             code shared by two or more projects (created when first needed)
tools/<language>/        shared build tooling: test macro, ruff wrapper, pytest runner
                          (tools/python/, tools/bazel/, tools/git/)
docs/                    docs shared across the repo
  spikes/                 one findings doc per spike
  decisions/              NNN-short-title.md decision records
  superpowers/            specs/ and plans/
.githooks/                repo git hooks (pre-commit, commit-msg, pre-push)

Inside ame/python/:
  src/ame/<service>/      one package per service: hub, mind, voice, eyes, face, console
  src/ame/common/         helpers used by two or more services (created when first needed)
  tests/                  mirrors src/ame: tests/<service>/test_<module>.py
  spikes/                 throwaway experiments; never imported by src/, excluded from lint and tests
```
Every folder with code has a `BUILD.bazel`. Windows Developer Mode must be on (rules_python creates symlinks).
User data (memory, logs, recordings, scans, models) lives in `%LOCALAPPDATA%\AMe\` — never in the repo.

## Style
- Formatter and linter: **ruff** (config in the root `ruff.toml`), enforced by `bazelisk test //...` (format, lint, BUILD lint) — the single gate for hooks, CI and local runs. Fix with the commands in `docs/engineering.md`.
- Hooks (enable once per clone: `git config core.hooksPath .githooks`): `pre-commit` checks the format of staged Python and Starlark files, `commit-msg` checks the commit format, `pre-push` runs the full gate.
- **Simplest code that keeps quality:** choose the most direct solution; no speculative abstractions, layers, or options until a real need exists.
- **Docstrings are literal and short:** one line stating what it does — inputs, outputs, side effects — unless more is needed to use it correctly. No aspirations, no marketing.
- **No comments.** Code must explain itself through names and structure; a non-obvious *why* goes in the docstring or in `docs/`.

## Naming
- Modules and packages: `snake_case`. Classes: `PascalCase`. Functions and variables: `snake_case`. Constants: `UPPER_SNAKE_CASE`.
- Hub message types: lowercase dotted `service.event_name` (e.g. `voice.user_said`), matching `^[a-z]+(\.[a-z_]+)+$`.
- Tests: `test_<behavior_in_words>`.

## Error handling
- Use exceptions. Each module defines a narrow exception type for its own failures (e.g. `MessageError`).
- Catch at service boundaries (the hub connection loop, a service's main loop): log and continue. A bad message or a failed call never crashes a service or the hub.
- Logs are English, via stdlib `logging`. What AMe says to the user about a failure is pt-BR and goes through voice or the console.
- Secrets are never logged. Transcripts and memory contents are logged only at DEBUG, never at INFO or higher.

## Testing
- Framework: **pytest**. Tests live in `ame/python/tests/`, mirroring `ame/python/src/ame/`; each file gets an `ame_test` target in that folder's `BUILD.bazel`.
- **Keep unit tests very light:** a few tests per module — the main behaviour and the one or two failures that would actually hurt. No exhaustive case tables.
- Tests needing hardware, the GPU, or the network use `ame_test(kind = "hardware" | "gpu" | "cloud")`: they are manual and run by name. Latency budgets use `ame_perf_test`. See `docs/engineering.md`.
- No coverage target.

## Build and run
- Test: `bazelisk test //...`
- Lint: `bazelisk run //tools/python:ruff -- check .` · Format check: `bazelisk run //tools/python:ruff -- format --check .`
- Run AMe: added in slice 1 (`bazelisk run //ame/python:ame`).
- Spikes: run with the system Python 3.12, `python ame/python/spikes/<script>.py`; each script lists its pip dependencies in its docstring and installs them with `pip install --user`. No venv.

## Branching
- `main` holds reviewed work only. All work happens on `feature/<short-name>` branches.
- Keep a branch current by rebasing it onto `main` (`git rebase main`), never by merging `main` into it.
- A branch merges into `main` only after `test-plan` and `review-checklist` both end in **PASS**, only with the user's approval, and only as a fast-forward (`git merge --ff-only`), so `main` stays linear.

## Commit history
- **One logical change per commit.** Each commit passes `bazelisk test //...` and the ruff checks on its own.
- **No noise commits.** Fix-ups ("fix typo", "address review", "WIP") are folded into the commit they fix before the branch merges: `git commit --amend` for the latest commit, or `git commit --fixup <sha>` then `git rebase --autosquash main`.
- **Never rewrite pushed commits.** Amend and autosquash only what exists solely on this machine.
- Formatting-only changes to existing code go in their own commit, never mixed into a behaviour change.
- Never commit generated files, recordings, or files unrelated to the commit's change.

## Commit format
Imperative subject, 72 characters max, no trailing period; blank line; body explaining why when it isn't obvious.
```
Add hub message envelope

Every service exchanges the same JSON envelope (spec §3); validating
it in one place keeps a malformed message from crashing the hub.
```

## Configuration and secrets
- Runtime config: `%LOCALAPPDATA%\AMe\config.toml` (created in slice 1).
- The Anthropic API key comes from the `ANTHROPIC_API_KEY` environment variable. Never in a file in the repo, never logged.
- Never commit: secrets (`.env*`, `*.pem`, `*.key`, `secrets.*`), recordings (`*.wav`, `*.flac`, `*.mp3`, `*.m4a`, `*.ogg`, `*.mp4`, `*.mov`, `*.avi`, `*.webm`), captures and arrays (`*.bag`, `*.npz`, `*.npy`), meshes (`*.ply`, `*.glb`), models (`*.onnx`, `*.pth`, `*.pt`, `*.safetensors`, `*.gguf`, `*.ckpt`, `*.pkl`), databases (`*.sqlite`, `*.db`), and images under `spikes/` and `recordings/` folders.
