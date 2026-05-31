# Goal2800 RTNN v2.5 Live Ranked-Summary Harness Consensus

Date: 2026-05-31

Consensus status: accept-with-boundary.

AI reviewers:

- Codex: implemented the live RTNN ranked-summary harness, manifest update, first pod artifact, and report.
- Claude: independent external review saved at `docs/reviews/goal2800_claude_review_rtnn_live_ranked_summary_harness_2026-05-31.md`, verdict `accept-with-boundary`.

## Consensus

Goal2800 is accepted with boundary:

- the RTNN v2.5 row now has a live harness instead of relying only on historical artifacts;
- the harness runs current RTDL/OptiX exact fixed-radius 3-D ranked-summary rows;
- the harness also runs the same-contract CuPy grid CUDA-core opponent;
- all three deterministic 65,536-point distributions pass under the explicit candidate-count boundary tolerance;
- the report honestly records that CuPy grid is faster on all three first-run fixtures;
- public speedup, whole-app speedup, RTDL-beats-RTNN, RTDL-beats-CuPy-grid, Triton speedup, true paper reproduction, and native app-customization claims remain unauthorized.

## Boundary

The first artifact was produced by copying the new Goal2800 harness into a pod checkout at commit `6da008bc`. This is valid first evidence, but a clean-from-Git pod rerun is still required after the Goal2800 commit is pushed.

The tolerance for candidate counts is a narrow float32-boundary tolerance, not a license to accept broad semantic drift. At the 65K fixture scale it is effectively a maximum delta of 2 candidates.
