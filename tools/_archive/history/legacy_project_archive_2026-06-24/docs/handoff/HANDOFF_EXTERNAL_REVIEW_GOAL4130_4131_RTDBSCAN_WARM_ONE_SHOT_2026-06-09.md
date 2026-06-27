# External Review Handoff - Goals 4130-4131 RT-DBSCAN Warmed One-Shot Guidance

Date: 2026-06-09

## Request

Please perform a read-only external review of Goals 4130 and 4131 on current `main`.

Expected review output:

- Claude: `docs/reviews/goal4132_claude_review_goal4130_4131_rtdbscan_warm_one_shot_guidance_2026-06-09.md`
- Gemini: `docs/reviews/goal4133_gemini_review_goal4130_4131_rtdbscan_warm_one_shot_guidance_2026-06-09.md`

Use verdicts from the established set: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Files To Inspect

- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_probe_2026-06-09.md`
- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_65k_pod.json`
- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_131k_pod.json`
- `docs/reports/goal4130_tuned_direct_status_warm_one_shot_262k_pod.json`
- `tests/goal4130_tuned_direct_status_warm_one_shot_probe_test.py`
- `docs/reports/goal4131_current_route_decision_after_warm_one_shot_probe_2026-06-09.md`
- `tests/goal4131_current_route_decision_after_warm_one_shot_probe_test.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- Prior accepted context:
  - `docs/reviews/goal4128_claude_review_goal4126_4127_rtdbscan_262k_scale_guidance_2026-06-09.md`
  - `docs/reviews/goal4129_gemini_review_goal4126_4127_rtdbscan_262k_scale_guidance_2026-06-09.md`

## Questions To Answer

1. Does Goal4130 fairly reuse the Goal4117 factor-sweep runner for a warmed one-shot probe (`repeat=2`, `warmup=1`), and are the artifacts cleanly commit-pinned to `f9f1b82b` with dirty flag false?
2. Does the one-shot total calculation make sense for the stated boundary: `current_route_prepare_sec + current_route_replay_sec` versus `direct_status_prepare_sec + direct_status_replay_sec`?
3. Are the reported one-shot total speedups exactly supported by the JSON artifacts?
   - 65k: clustered3d `2.506x`, road3d `2.609x`, ngsim_dense `1.819x`
   - 131k: clustered3d `3.110x`, road3d `2.606x`, ngsim_dense `3.410x`
   - 262k: clustered3d `3.192x`, road3d `2.272x`, ngsim_dense `2.939x`
4. Do all factor rows preserve the current grouped-stream route's component-size signature?
5. Does Goal4131 update the route advisor to expose prepared direct-status as an explicit user-selectable option for tested one-shot and repeated component-signature workloads without hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?
6. Is it correct that `plan_rt_dbscan_execution` remains a separate older planning surface and is not silently changed into an auto-dispatcher?
7. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?
8. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

## Boundary

This is not a release review. It should not authorize release, public speedup claims, broad RT-core claims, paper-reproduction claims, automatic dispatch, automatic partner/factor selection, app-specific native-engine logic, AMD claims, or true-zero-copy claims.
