# Goals 641-643: v0.9.5 Pre-Release Test/Doc/Flow — External Review

Date: 2026-04-19
Reviewer: External (Claude Sonnet 4.6)

## Verdict: ACCEPT

The combined test, documentation, and flow evidence is sufficient for a
v0.9.5 release-candidate decision.

## Evidence Summary

**Test gate (Goal 641)**

- 1201 tests, 0 failures, 179 expected skips on local macOS (no OptiX/Vulkan/HIPRT
  libraries available there — expected and disclosed).
- 23 focused backend tests, 0 failures, 2 expected skips on Linux with all four
  non-Apple backends probed live (Embree 4.3.0, OptiX 9.0, Vulkan 0.1.0, HIPRT 2.2).
- All six new v0.9.5 test files (Goals 632, 633, 636, 637, 638, 639) are included
  in both runs.

**Documentation gate (Goal 642)**

- Stale "CPU-only" visibility wording corrected in `feature_quickstart_cookbook.md`.
- Stale-phrase grep (`rg`) returns zero matches across README, docs, examples, and
  `visibility_runtime.py`.
- Runnable examples (`rtdl_ray_triangle_any_hit.py`, `rtdl_visibility_rows.py`)
  execute cleanly.
- Public-doc smoke tests (Goals 515, 513, 632, 633) all pass.

**Flow audit (Goal 643)**

- Goal ladder 631-643 is coherent and fully evidenced.
- All upstream reviews (Goals 632/633, 635, 636, 637, 638, 639, 640) carried
  ACCEPT verdicts from Claude and/or Gemini external-style review.
- No whitespace errors in working tree (`git diff --check` clean).
- Dirty worktree is active development, not a release artifact — non-blocking.

## Overclaim Check

No overclaims found:

- Vulkan and Apple RT are labelled "compatibility dispatch" (real backend execution,
  no native early-exit claim) — correct.
- HIPRT is validated on NVIDIA/Orochi path; no AMD GPU claim — disclosed.
- HIPRT whole-call timing shows no speedup; the report explicitly notes JIT/setup
  overhead dominates and flags this as non-blocking — correct.
- No claim that v0.9.5 is already released.

## Remaining Required Action

Obtain this review (done), then proceed with release-candidate packaging from a
reviewed commit at the user's discretion.
