# Handoff: Gemini Review for Goal2995 RayDB Numba Min/Max

Please perform an independent read-only review of Goal2995 and write the review
to:

`docs/reviews/goal2996_gemini_review_goal2995_raydb_numba_minmax_l4_2026-06-01.md`

## Scope

Review the current `main` branch after commit `c1d00789`.

Primary artifacts:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/goal2995_raydb_numba_minmax_pod_runner.py`
- `docs/reports/goal2995_raydb_numba_segmented_minmax_prepared_2026-06-01.md`
- `docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md`
- `docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json`
- `tests/goal2995_raydb_numba_segmented_minmax_test.py`
- `tests/goal2995_raydb_numba_minmax_l4_pod_test.py`
- `src/rtdsl/v2_6_roadmap.py`
- `src/rtdsl/v2_5_internal_readiness.py`

## Questions To Answer

1. Do the new `segmented_min_f64` and `segmented_max_f64` Numba operations
   remain generic grouped reductions, without RayDB/app-specific engine logic?
2. Does the `partner="numba"` front door still require accepted v2.6 neutral
   handoff before launching Numba, and does it avoid torch carrier/conversion?
3. Does the RayDB-style app now correctly support all five scalar modes using
   user-selected Numba while keeping query encoding in app Python?
4. Is the L4 pod evidence valid runtime conformance evidence for those modes?
   Please check rows/groups, source commit, toolchain metadata, CPU parity, and
   claim-boundary fields.
5. Are the roadmap/readiness updates honest, especially the point that Goal2995
   is not release evidence or speedup evidence?

## Expected Review Format

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Please lead with findings if any. If accepted, still list residual boundaries.
Do not authorize v2.6 release, public speedup claims, whole-app speedup claims,
broad RT-core claims, true-zero-copy claims, automatic partner selection claims,
or RayDB paper reproduction claims.

Run this focused test slice if available:

`PYTHONPATH=src:. python -m unittest tests.goal2995_raydb_numba_minmax_l4_pod_test tests.goal2995_raydb_numba_segmented_minmax_test tests.goal2994_raydb_numba_neutral_demo_test`
