# Goal2667: v2.5 Partner Preview Review Status

Status: Codex + Gemini accepted; Claude unavailable; no 3-AI consensus claimed.

Date: 2026-05-27

## Scope

Reviewed v2.5 partner-preview work from Goal2662 through Goal2666:

- generic partner-continuation contract;
- Triton segmented count/sum previews;
- Triton grouped pod runner;
- Numba segmented count/sum fallback preview;
- docs and claim-boundary updates.

## Codex Assessment

Codex assessment: accept for preview status.

The implementation stays within the intended v2.5 boundary:

- generic post-RT continuation only;
- no app-specific native engine vocabulary;
- no RT traversal replacement;
- no CuPy RawKernel requirement;
- no public speedup claim;
- no benchmark promotion without CUDA pod evidence.

The remaining work is validation and integration, not more local source-tree
claims.

## Gemini Review

Gemini review file:

- `docs/reports/goal2667_v2_5_partner_preview_gemini_review_2026-05-27.md`

Verdict: accept.

Gemini found no blockers. Non-blocking notes:

- Numba validation currently copies `group_ids` to host; acceptable for preview,
  but this must become device-resident before promotion.
- Triton `tl.atomic_add` for float64 sum has normal GPU floating-point
  non-determinism from reduction order; tests and docs should keep tolerance
  wording for sum paths.

## Claude Review

Claude review attempt file:

- `docs/reports/goal2667_v2_5_partner_preview_claude_review_2026-05-27.md`

Verdict: unavailable.

Claude CLI stalled for more than two minutes and wrote zero bytes. The process
was terminated. No Claude review or verdict is claimed.

## Current Decision

The v2.5 preview work is acceptable to keep on `main` and to validate on a CUDA
pod.

It is not enough for:

- public speedup claims;
- promoted benchmark status;
- v2.5 release completion;
- 3-AI consensus.

## Required Pod Work Before Promotion

1. Run the Goal2663/2664 CUDA execution tests from `origin/main`.
2. Run `scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py` at
   scale and save JSON artifacts.
3. Run the existing `--include-numba` path to compare Numba, Triton, and Torch
   device baselines when Numba is installed on the pod.
4. Integrate the Triton path into at least one real benchmark row, initially
   RayDB-style grouped count/sum.
5. Prove the end-to-end OptiX-vs-Embree basis is preserved or improved.
6. Retry Claude or use manual-forward review before any promotion or release
   wording.
