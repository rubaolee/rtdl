# External Review Request: Goal3938 Current Benchmark Route Decision Registry

Date: 2026-06-08

Please perform a read-only review of Goal3938 on current `main`.

## Files To Inspect

- `src/rtdsl/current_benchmark_route_decisions.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal3938_current_benchmark_route_decision_registry_2026-06-08.md`
- `tests/goal3938_current_benchmark_route_decision_registry_test.py`
- Supporting latest evidence:
  - `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md`
  - `docs/reports/goal3937_current_benchmark_adequacy_after_clean_cubin_rerun_2026-06-08.md`

## Review Questions

1. Does the registry correctly encode the current route doctrine: primitive-first when a fused generic RTDL primitive wins, Numba when custom scalar/row-stream logic wins, CuPy only where honestly fastest with a Numba reference, and explicit user route choice throughout?
2. Does the `spatial_rayjoin` row correctly reflect Goal3936: Numba for bounded PIP one-shot, RTDL/OptiX for repeated PIP, LSI scalar count, and overlay active count, without auto-dispatch or RayJoin paper-reproduction claims?
3. Does the `rt_dbscan` row correctly keep the blocked grouped-stream candidate unpromoted after Goal3936?
4. Are claim boundaries intact: no release, public speedup, whole-app acceleration, broad RT-core, true-zero-copy, automatic partner selection, paper reproduction, AMD performance, or app-specific native-engine logic claims?
5. Are there required fixes before Goal3938 can be treated as accepted internal route-governance evidence?

## Required Output

Use one of these verdicts only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Save your review as one of:

- Gemini: `docs/reviews/goal3939_gemini_review_goal3938_route_decision_registry_2026-06-08.md`
- Claude: `docs/reviews/goal3940_claude_review_goal3938_route_decision_registry_2026-06-08.md`

Do not authorize release or public claims. This is internal route-governance review only.
