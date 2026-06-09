# External Review Handoff - Goals 4121-4123 RT-DBSCAN Scale-Aware Advisor

Date: 2026-06-09

## Requested Review

Please perform a read-only external review of the Goal4121-4123 RT-DBSCAN advisor and scale-probe correction.

Expected outputs:

- Claude: `docs/reviews/goal4124_claude_review_goal4121_4123_scale_aware_advisor_2026-06-09.md`
- Gemini: `docs/reviews/goal4125_gemini_review_goal4121_4123_scale_aware_advisor_2026-06-09.md`

Use verdict values only from: `accept`, `accept-with-boundary`, `reject`, `needs-more-evidence`.

## Scope

Review these deliverables:

- Goal4121 advisor:
  - `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
  - `docs/reports/goal4121_rt_dbscan_explicit_route_choice_advisor_2026-06-09.md`
  - `tests/goal4121_rt_dbscan_explicit_route_choice_advisor_test.py`
- Goal4122 scale probe:
  - `docs/reports/goal4122_tuned_direct_status_scale_probe_2026-06-09.md`
  - `docs/reports/goal4122_tuned_direct_status_scale_probe_pod.json`
  - `tests/goal4122_tuned_direct_status_scale_probe_test.py`
- Goal4123 route refresh:
  - `src/rtdsl/current_benchmark_route_decisions.py`
  - `docs/reports/goal4123_current_route_decision_after_scale_aware_advisor_2026-06-09.md`
  - `tests/goal4123_current_route_decision_after_scale_aware_advisor_test.py`
- Prior external reviews:
  - `docs/reviews/goal4119_claude_review_goal4116_4118_tuned_direct_status_2026-06-09.md`
  - `docs/reviews/goal4120_gemini_review_goal4116_4118_tuned_direct_status_2026-06-09.md`

## Questions To Answer

1. Does Goal4121's advisor remain advisory-only, with no hidden dispatch, no automatic partner selection, and no automatic factor selection?
2. Does the advisor correctly expose scale-aware NGSIM evidence: `0.5` at 65k from Goal4117 and `0.25` at 131k from Goal4122?
3. Does Goal4122 fairly reuse the Goal4117 runner for a 131,072-point scale probe, and are the key measured results correctly stated?
   - `clustered3d`: factor `0.25`, replay speedup `3.211x`
   - `road3d`: factor `0.25`, replay speedup `1.545x`
   - `ngsim_dense`: factor `0.25`, replay speedup `1.399x`
4. Does Goal4123 correctly update current route guidance to scale-aware evidence without claiming a universal dense-profile factor?
5. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?
6. Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

## Required Boundary

Do not edit source code. A review file may be written to the expected output path. Do not authorize release or public claims. Treat this as internal route-guidance and benchmark-development evidence only.
