# Local Refresh Context For AI Reviews

This file mirrors the RTDL refresh constraints that matter for current
repository review work. Read it regularly after context compaction.

## Current project state

- Primary repo for this review:
  - `/Users/rl2025/rtdl_python_only`
- Current working branch:
  - `codex/rtx-cloud-run-2026-04-22`
- Current released version described by the repo:
  - `v0.9.6`
- Current active development line described by the repo:
  - v1.0 RTX app readiness and claim-boundary work after the released `v0.9.6` surface

## Review and closure discipline

- Every bounded goal should have `2+` AI consensus before it is called closed.
- External-style AI review should be saved into repo files.
- Codex consensus is still required in addition to external-style review.
- Prefer file-based handoff and response-file review trails.
- Do not rewrite historical external reviews. If later evidence changes a
  conclusion, add a supersession report and update current public docs.

## Platform honesty

- Linux and RTX cloud runs are the primary NVIDIA/OptiX validation platforms.
- Local macOS is a bounded correctness, Apple RT/MPS RT, documentation, and
  release-flow platform.
- Windows is a bounded correctness/performance platform when available.
- Do not overclaim backend or GPU correctness if row parity is not proven.

## Current public honesty boundary

- `v0.9.6` is released.
- Current post-release RTX app work is not a new release authorization.
- `robot_collision_screening / prepared_pose_flags` is a real bounded
  RT-core path, but public RTX speedup wording remains blocked because larger
  RTX repeats stayed below the 100 ms public-review timing floor.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Public RTX wording must follow `rtdsl.rtx_public_wording_matrix()`.
- Reviewers should prefer strict, bounded judgments over open-ended redesign.

## Working style for this review

- Audit the current repo state.
- Prefer concrete findings over politeness.
- Keep the review grounded in saved docs, tests, and reports.
- Use generated audits where available, then save Claude/Gemini-style reviews
  and a two-AI consensus report for bounded goal closure.
