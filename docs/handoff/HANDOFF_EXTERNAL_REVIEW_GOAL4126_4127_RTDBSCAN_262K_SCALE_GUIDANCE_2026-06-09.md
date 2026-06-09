# External Review Handoff - Goals 4126-4127 RT-DBSCAN 262k Scale Guidance

Date: 2026-06-09

## Request

Please perform a read-only external review of Goals 4126 and 4127 on current `main`.

Expected review output:

- Claude: `docs/reviews/goal4128_claude_review_goal4126_4127_rtdbscan_262k_scale_guidance_2026-06-09.md`
- Gemini: `docs/reviews/goal4129_gemini_review_goal4126_4127_rtdbscan_262k_scale_guidance_2026-06-09.md`

Use verdicts from the established set: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Files To Inspect

- `docs/reports/goal4126_tuned_direct_status_262k_scale_probe_2026-06-09.md`
- `docs/reports/goal4126_tuned_direct_status_262k_scale_probe_pod.json`
- `tests/goal4126_tuned_direct_status_262k_scale_probe_test.py`
- `docs/reports/goal4127_current_route_decision_after_262k_direct_status_probe_2026-06-09.md`
- `tests/goal4127_current_route_decision_after_262k_direct_status_probe_test.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- The older comparison context:
  - `docs/reports/goal4117_partition_cell_factor_route_sweep_2026-06-09.md`
  - `docs/reports/goal4122_tuned_direct_status_scale_probe_2026-06-09.md`
  - `docs/reviews/goal4124_claude_review_goal4121_4123_scale_aware_advisor_2026-06-09.md`
  - `docs/reviews/goal4125_gemini_review_goal4121_4123_scale_aware_advisor_2026-06-09.md`

## Questions To Answer

1. Does Goal4126 fairly reuse the Goal4117 factor-sweep runner for the 262,144-point probe, and is the pod artifact cleanly commit-pinned?
2. Are the reported 262k results exactly supported by the JSON artifact?
   - clustered3d: factor `0.25`, `3.118x` replay speedup
   - road3d: factor `0.25`, `1.428x` replay speedup
   - ngsim_dense: factor `0.25`, `1.642x` replay speedup
3. Do all factor rows preserve the current grouped-stream route's component-size signature?
4. Does Goal4127 update the advisor and current route registry in an advisory-only way, without hidden dispatch, automatic partner selection, or automatic factor selection?
5. Does the new guidance avoid claiming a universal dense-profile factor, while correctly stating that `ngsim_dense` used `0.5` at 65k and `0.25` at 131k/262k?
6. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?
7. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

## Boundary

This is not a release review. It should not authorize release, public speedup claims, broad RT-core claims, paper-reproduction claims, automatic dispatch, automatic partner/factor selection, app-specific native-engine logic, AMD claims, or true-zero-copy claims.
