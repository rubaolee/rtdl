# External Review Handoff - Goals 4134-4135 RT-DBSCAN 524k Factor-0.25 Extension

Date: 2026-06-09

## Request

Please perform a read-only external review of Goals 4134 and 4135 on current `main`.

Expected review output:

- Claude: `docs/reviews/goal4136_claude_review_goal4134_4135_rtdbscan_524k_factor025_2026-06-09.md`
- Gemini: `docs/reviews/goal4137_gemini_review_goal4134_4135_rtdbscan_524k_factor025_2026-06-09.md`

Use verdicts from the established set: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Files To Inspect

- `docs/reports/goal4134_tuned_direct_status_524k_factor025_probe_2026-06-09.md`
- `docs/reports/goal4134_tuned_direct_status_warm_one_shot_524k_factor025_pod.json`
- `tests/goal4134_tuned_direct_status_524k_factor025_probe_test.py`
- `docs/reports/goal4135_current_route_decision_after_524k_factor025_probe_2026-06-09.md`
- `tests/goal4135_current_route_decision_after_524k_factor025_probe_test.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- Prior accepted context:
  - `docs/reviews/goal4132_claude_review_goal4130_4131_rtdbscan_warm_one_shot_guidance_2026-06-09.md`
  - `docs/reviews/goal4133_gemini_review_goal4130_4131_rtdbscan_warm_one_shot_guidance_2026-06-09.md`

## Questions To Answer

1. Does Goal4134 fairly run a bounded 524,288-point extension probe with only `partition_cell_factor=0.25`, and is the artifact cleanly commit-pinned to `93c52cb1` with dirty flag false?
2. Are the reported 524k replay and one-shot total speedups exactly supported by the JSON artifact?
   - clustered3d: `3.291x` replay / `3.250x` one-shot total
   - road3d: `1.367x` replay / `1.910x` one-shot total
   - ngsim_dense: `1.769x` replay / `2.489x` one-shot total
3. Do all factor rows preserve the current grouped-stream route's component-size signature?
4. Does Goal4135 correctly state that the 524k packet is a factor-0.25 extension, not a full 524k factor sweep or universal factor claim?
5. Does the advisor correctly distinguish repeated replay ranking from one-shot total ranking, especially the 65k `ngsim_dense` asymmetry (`0.5` for repeated replay, `0.25` for one-shot total)?
6. Does the current route registry remain advisory-only, with no hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?
7. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?
8. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

## Boundary

This is not a release review. It should not authorize release, public speedup claims, broad RT-core claims, paper-reproduction claims, automatic dispatch, automatic partner/factor selection, app-specific native-engine logic, AMD claims, or true-zero-copy claims.
