# RTDL Local Operating Refresh

This file is stable operating memory for RTDL work. Read it regularly after
context compaction. Keep project, machine, environment, tool, review-flow, and
claim-boundary rules here. Do not use this file as a running goal ledger or
progress report; write goal progress to `docs/reports/`.

## Project Identity

- Primary repo:
  - `/Users/rl2025/rtdl_python_only`
- Project: RTDL, a Python-facing ray-tracing DSL/runtime for expressing
  RT-accelerated app kernels with strict claim boundaries.
- Development focus: make public examples/apps useful, correct, documented,
  and honest about which RT engine/path is actually used.
- Stable repo convention:
  - source under `src/`
  - examples/apps under `examples/`
  - tests under `tests/`
  - scripts under `scripts/`
  - reports/reviews under `docs/reports/`
  - handoff prompts under `docs/handoff/`
- Current release/version facts belong in release docs and reports, not in this
  refresh file.

## Local Machine And Environment

- Local macOS machine:
  - main bounded-correctness, documentation, Apple RT/MPS RT, and release-flow
    work platform.
  - not an NVIDIA/OptiX validation platform.
- Linux / RTX cloud pods:
  - primary NVIDIA/OptiX and RT-core validation platforms.
  - use consolidated pod batches; do not start/stop cloud per app.
  - install GEOS before strict correctness gates:
    `apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config`.
  - install/point OptiX headers and CUDA explicitly before benchmarks.
- Windows:
  - bounded correctness/performance platform when available.
  - coordinate via files/reports, not ad hoc verbal relay.
- Shared/network/remote machines:
  - write self-contained handoff files when another agent/machine should act.
  - do not assume another machine has the same credentials, keys, branches, or
    dependencies.

## Tool Availability

- Shell:
  - prefer `rg`/`rg --files` for search.
  - use `apply_patch` for manual edits.
  - avoid destructive git commands unless explicitly approved.
- Claude CLI:
  - may work with:
    `claude --print --dangerously-skip-permissions "<prompt>"`
  - if Claude hits quota/auth/tool failure, do not stop; use Gemini.
- Gemini CLI:
  - available at `/opt/homebrew/bin/gemini`.
  - headless review:
    `gemini -p "<prompt>" --yolo`
  - if Gemini prints an attempted write action but no file appears, save the
    stdout verdict manually into the required `docs/reports/` file and note the
    capture.
- Cloud SSH keys:
  - user-provided key paths may differ from local Codex availability.
  - verify key existence before assuming a pod is unreachable.
- Pod setup:
  - always log bootstrap, environment, commands, and copy-back paths.
  - preserve failed artifacts/logs; do not overwrite failure history without a
    supersession report.

## Review and closure discipline

- Every bounded goal should have `2+` AI consensus before it is called closed.
- For this project, `2-AI consensus` means Codex plus at least one external AI:
  Claude or Gemini. An internal Codex subagent does not satisfy the external-AI
  side of this rule.
- `3-AI consensus` means Codex plus both Claude and Gemini.
- External-style AI review should be saved into repo files. If an external AI
  returns a verdict in stdout but cannot write the file itself, save the stdout
  verdict into a repo report and note that capture path explicitly.
- Codex consensus is still required in addition to external-style review.
- Prefer file-based handoff and response-file review trails.
- Do not rewrite historical external reviews. If later evidence changes a
  conclusion, add a supersession report and update current public docs.
- For required `2-AI consensus`, if Claude is unavailable, immediately use
  Gemini and save its verdict under `docs/reports/`.
- Important planning, public claim changes, release decisions, or architecture
  changes should seek `3-AI consensus` unless the user explicitly narrows scope.
- A review failure from Claude/Gemini is evidence to handle, not a reason to
  ignore the review requirement.

## Platform honesty

- Linux and RTX cloud runs are the primary NVIDIA/OptiX validation platforms.
- Local macOS is a bounded correctness, Apple RT/MPS RT, documentation, and
  release-flow platform.
- Windows is a bounded correctness/performance platform when available.
- Do not overclaim backend or GPU correctness if row parity is not proven.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Distinguish:
  - backend ran
  - native RT traversal ran
  - RT-core hardware was plausibly exercised
  - same-semantics baseline comparison supports a public speedup claim
- Do not quote same-backend warm/prepared ratios as RTX-vs-baseline speedups.
- Public RTX wording must follow the repo's current public wording matrix and
  saved review reports.

## Documentation And Report Rules

- Front-page docs, tutorials, examples, feature guides, architecture docs, and
  app docs must be consistent with current code before release.
- Public docs must be useful and attractive, but never overclaim performance,
  backend support, or release authorization.
- Goal/progress information belongs in `docs/reports/` and history/release
  docs, not in this refresh file.
- If a new external report arrives, read it, summarize defects, fix or rebut
  with evidence, and save a response report.
- For cloud runs, copy artifacts back and run local intake before interpreting
  results.
- Release-level work requires total tests, total docs update, total audit, and
  review-flow evidence.

## Working style for this review

- Audit the current repo state.
- Prefer concrete findings over politeness.
- Keep the review grounded in saved docs, tests, and reports.
- Use generated audits where available, then save Claude/Gemini-style reviews
  and a two-AI consensus report for bounded goal closure.
- Before significant work, inspect current files; do not assume stale memory is
  current.
- Keep user updates concise but frequent during long-running work.
- When a task uses paid cloud, maximize local preparation first and batch cloud
  operations efficiently.
