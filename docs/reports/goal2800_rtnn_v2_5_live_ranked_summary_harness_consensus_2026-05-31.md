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

The first artifact was produced by copying the new Goal2800 harness into a pod checkout at commit `6da008bc`. That first-run boundary was closed by a clean-from-Git pod rerun after the Goal2800 commit was pushed.

Clean-from-Git validation:

- commit: `a22d388f1826c9e892f8b8a26196c8f0963c90e4`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- OptiX build: pass
- Goal2800 harness: pass, 3 rows
- Focused pod test slice: 18 tests run, 18 passed

The tolerance for candidate counts is a narrow float32-boundary tolerance, not a license to accept broad semantic drift. At the 65K fixture scale it is effectively a maximum delta of 2 candidates.

Goal2804 later refreshed the clean artifact metadata at commit
`6ae202919c2af07ae8d8a9c662edd656ae77aa87`; the refreshed artifact remains
`pass` and records `source_dirty: []`.
