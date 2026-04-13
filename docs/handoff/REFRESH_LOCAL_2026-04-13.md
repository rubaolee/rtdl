# Local Refresh Context For Gemini Reviews

This file mirrors the RTDL refresh constraints that matter for current
repository review work.

## Current project state

- Primary repo for this review:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
- Current released version described by the repo:
  - `v0.4.0`
- Current active development line described by the repo:
  - `v0.5 preview`

## Review and closure discipline

- Every bounded goal should have `2+` AI consensus before it is called closed.
- External-style AI review should be saved into repo files.
- Codex consensus is still required in addition to external-style review.
- Prefer file-based handoff and response-file review trails.

## Platform honesty

- Linux is the primary validation platform.
- Windows and local macOS are bounded correctness platforms in the current
  `v0.5` line.
- Do not overclaim backend or GPU correctness if row parity is not proven.

## Current public honesty boundary

- `v0.5 preview` is preview-ready, not final-release-ready.
- Linux carries the main nearest-neighbor performance story.
- Windows/local macOS are not part of the large-scale NN performance claim.
- Reviewers should prefer strict, bounded judgments over open-ended redesign.

## Working style for this review

- Audit the current repo state.
- Prefer concrete findings over politeness.
- Keep the review grounded in saved docs, tests, and reports.
