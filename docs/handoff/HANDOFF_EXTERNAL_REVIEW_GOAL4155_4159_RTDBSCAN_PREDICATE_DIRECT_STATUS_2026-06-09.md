# External Review Handoff: Goals4155-4159 RT-DBSCAN Predicate Direct-Status Chain

Please perform an independent read-only review of the current `main` branch work from Goals4155-4159.

## Scope

Review these source changes and artifacts:

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `docs/reports/goal4155_predicate_aware_direct_status_implementation_plan_2026-06-09.md`
- `docs/reports/goal4156_predicate_direct_status_candidate_surface_2026-06-09.md`
- `docs/reports/goal4157_predicate_direct_status_scale_probe_2026-06-09.md`
- `docs/reports/goal4157_predicate_direct_status_scale_factor025_pod.json`
- `docs/reports/goal4158_predicate_all_true_fast_path_pod_result_2026-06-09.md`
- `docs/reports/goal4158_predicate_all_true_fast_path_scale_factor025_pod.json`
- `docs/reports/goal4159_mixed_predicate_direct_status_gap_2026-06-09.md`
- `docs/reports/goal4159_mixed_predicate_direct_status_scale_pod.json`
- Tests `tests/goal4155*` through `tests/goal4159*` if present.

## Questions

1. Is the native/runtime surface still app-agnostic? The route should expose generic predicate flags, fixed-radius component signatures, and explicit policies only; it must not smuggle DBSCAN-specific native logic into the engine.
2. Does Goal4158 genuinely prove the all-predicate fast path after the placement fix at commit `b1d220ed`, with artifact commit `b1d220ed` and report commit chain ending at `63cfbc9a`?
3. Does Goal4159 correctly classify the mixed-predicate state as a blocked promotion, separating component-label permutation from a real border-assignment policy gap?
4. Are the claim boundaries intact? No route promotion, release, public speedup, broad RT-core, whole-app, zero-copy, or hidden-dispatch claim should be authorized.
5. What is the next engineering recommendation: canonical component-size signature, explicit generic border-assignment policy, route selector with explicit user opt-in, or another path?

## Expected Output

Write a Markdown review under `docs/reviews/`:

- Claude: `docs/reviews/goal4160_claude_review_goal4155_4159_rtdbscan_predicate_direct_status_2026-06-09.md`
- Gemini: `docs/reviews/goal4160_gemini_review_goal4155_4159_rtdbscan_predicate_direct_status_2026-06-09.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source files. If you run tests, include the exact commands and outcomes.
