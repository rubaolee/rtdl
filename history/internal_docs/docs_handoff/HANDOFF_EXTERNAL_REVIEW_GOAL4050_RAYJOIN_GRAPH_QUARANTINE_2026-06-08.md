# Handoff: External Review Goal4050 RayJoin Graph Quarantine

Please perform a read-only independent review of Goal4050.

## Context

RTDL's RayJoin-style PIP path has three relevant generic lanes:

- working single prepared point/closed-shape count;
- working prepared batch-count executor for repeated requests;
- blocked prepared-points CUDA graph replay.

Goal3312 previously showed the graph replay lane returning zeros. Goal3842 kept
the batch executor as the useful repeated-request lane. Goal4050 reran a
current-main pod probe and found that trusted non-graph lanes still return
correct counts while the graph lane now fails during OptiX/CUDA graph prepare
with `OptiX error: CUDA error`.

## Files To Inspect

- `docs/reports/goal4050_rayjoin_pip_graph_replay_quarantine_2026-06-08.md`
- `docs/reports/goal4050_rayjoin_pip_graph_current_negative_probe_pod.json`
- `tests/goal4050_rayjoin_pip_graph_replay_quarantine_test.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`
- optionally compare with:
  - `docs/reports/goal3312_prepared_point_batch_graph_negative_probe_2026-06-04.md`
  - `docs/reports/goal3842_rayjoin_pip_batch_executor_current_refresh_2026-06-08.md`
  - `tests/goal3312_prepared_point_batch_graph_count_test.py`
  - `tests/goal3842_rayjoin_pip_batch_executor_current_refresh_test.py`

## Required Checks

1. Verify that Goal4050 does not overclaim: no release, public speedup, RayJoin
   paper reproduction, RTDL-beats-RayJoin, broad RT-core, true-zero-copy, or
   automatic partner/backend-selection claims.
2. Verify the route decision is technically sensible: graph replay should be
   quarantined, while the working batch executor / scalar-count executor lanes
   remain the recommended RTDL/OptiX paths for their explicit contracts.
3. Verify the artifact is internally consistent: single, batch, and batch
   executor counts are `[6]`/`[6, 6, 6, 6, 6]`, graph validation fails closed,
   raw graph is not usable, and all claim-boundary flags are false.
4. Verify the tests cover the regression boundary without requiring hidden app
   semantics or app-specific native engine logic.
5. State whether the verdict is `accept`, `accept-with-boundary`,
   `needs-more-evidence`, or `reject`, and list any required fixes before this
   route guidance can be used.

## Output Paths

Please write your review to one of:

- Claude: `docs/reviews/goal4051_claude_review_goal4050_rayjoin_graph_quarantine_2026-06-08.md`
- Gemini: `docs/reviews/goal4051_gemini_review_goal4050_rayjoin_graph_quarantine_2026-06-08.md`

Do not edit source files for this review.
