# Handoff: Gemini Review Goal3984-3985 Hot-Query Summary Chain

Please perform an independent read-only review of the Goal3984/Goal3985 current-scale measurement chain.

## Files To Review

- `docs/reports/goal3984_resident_hot_query_summary_contract_2026-06-08.md`
- `docs/reports/goal3985_current_scale_after_hot_query_summary_2026-06-08.md`
- `docs/reports/goal3985_current_scale_after_hot_query_summary_2026-06-08/summary.json`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `tests/goal3984_resident_hot_query_summary_contract_test.py`
- `tests/goal3985_current_scale_after_hot_query_summary_test.py`

## Questions

1. Do the `--summary-only-iterations` and `--summary-only-runs` options preserve default runner behavior while enabling compact high-repeat hot-path evidence?
2. Does Goal3985 prove the two former short rows now expose seconds-level aggregate hot-path summaries without per-iteration JSON bloat?
3. Does the registry still keep wrapper elapsed as pod-budget evidence, not a hot-path or public-speedup metric?
4. Are all release, public speedup, broad RT-core, true-zero-copy, paper reproduction, automatic partner-selection, and app-specific engine-logic claims still blocked?
5. What should the next runtime-performance target be after this measurement-quality fix?

## Expected Output

Write the review to:

`docs/reviews/goal3986_gemini_review_goal3984_3985_hot_query_summary_chain_2026-06-08.md`

Use one of the project verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
