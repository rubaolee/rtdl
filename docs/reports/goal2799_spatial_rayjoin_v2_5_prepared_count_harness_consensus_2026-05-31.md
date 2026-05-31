# Goal2799 Spatial RayJoin v2.5 Prepared Count Harness Consensus

Date: 2026-05-31

Consensus status: accept-with-boundary.

AI reviewers:

- Codex: implemented the harness, manifest update, report, and first OptiX pod artifact.
- Claude: independent external review saved at `docs/reviews/goal2799_claude_review_spatial_rayjoin_prepared_count_harness_2026-05-31.md`, verdict `accept-with-boundary`.

Gemini note: Gemini Flash was attempted for this review, but the first job wrote only an incomplete template and the follow-up jobs failed with empty/malformed output or plan-mode write restrictions. No Gemini review is counted for this goal.

## Consensus

Goal2799 is accepted with a boundary:

- the Spatial RayJoin v2.5 Tier A count/parity route now has a canonical prepared OptiX harness;
- the harness covers `pip`, `lsi`, and `overlay_seed`;
- all three workloads match CPU reference counts in the first RTX A5000 pod artifact;
- the v2.5 manifest now records the Goal2799 harness as the current Spatial RayJoin count/parity evidence;
- the report and artifact do not claim public speedup, whole-app RayJoin reproduction, RTDL beating the RayJoin paper, Triton speedup, true zero-copy, or row/overlay continuation closure.

## Boundary

The first artifact was produced on a pod checkout reset to `origin/main` at `72f6d8de15cd915c2e58323b95d7a029631b1367`, with the new Goal2799 harness copied into that checkout. That first-run boundary was closed by a clean-from-Git pod rerun after the Goal2799 commit was pushed.

Clean-from-Git validation:

- commit: `0ecac36df0118b3080b7925f5cee9e2e6fd90727`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- OptiX build: pass
- Goal2799 harness: pass, 3 rows
- Focused pod test slice: 47 tests run, 46 passed, 1 skipped

The row materialization and overlay continuation path remains deferred Tier B work. Goal2799 closes only the primitive-first prepared count/parity gap.
