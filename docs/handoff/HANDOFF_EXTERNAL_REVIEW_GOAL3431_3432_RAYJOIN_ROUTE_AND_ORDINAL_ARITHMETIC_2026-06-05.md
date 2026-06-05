# External Review Handoff: Goal3431/3432 RayJoin Route and Ordinal Arithmetic

Please perform an independent read-only review of latest `main` after Goal3432.

## Scope

Review:

- Goal3431 Spatial RayJoin prepared OptiX + CuPy refined PIP app route.
- Goal3432 widened ordinal addition follow-up to the Goal3429 Claude residual note.

Primary files:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `tests/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test.py`
- `tests/goal3424_closed_shape_instance_identity_refinement_test.py`
- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_2026-06-05.md`
- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.json`
- `docs/reports/goal3432_closed_shape_ordinal_widened_addition_2026-06-05.md`
- `docs/reviews/goal3429_claude_review_goal3427_3428_prepared_refiner_and_chunk_guard_2026-06-05.md`
- `docs/reviews/goal3430_gemini_review_goal3427_3428_prepared_refiner_and_chunk_guard_2026-06-05.md`

## Questions

1. Does Goal3431 expose the prepared OptiX candidate-stream plus prepared CuPy refiner route as explicit user/app code without hiding partner selection or moving RayJoin/CDB semantics into the native engine?
2. Does the Goal3431 route preserve claim boundaries while still being useful as a benchmark-app reference route?
3. Is the Goal3431 pod artifact coherent? Key expected values: route `prepared_optix_cupy_refined_pip`, row count `47262`, candidate row count `47570`, dropped candidates `308`, `candidate_columns.runtime.instance_identity_columns.present: true`, all claim flags false.
4. Does the v2.8 benchmark-runtime gap row update accurately reflect the improved PIP exact continuation while still naming unresolved Spatial RayJoin gaps?
5. Does Goal3432 close the residual Goal3429/Goal3425 widened-addition concern without changing public point IDs or app behavior?
6. Are there any bugs, overclaims, missing tests, or boundary wording issues that should be fixed before the next v2.8 step?

## Required Output Paths

Claude:

- `docs/reviews/goal3433_claude_review_goal3431_3432_rayjoin_route_and_ordinal_arithmetic_2026-06-05.md`

Gemini:

- `docs/reviews/goal3434_gemini_review_goal3431_3432_rayjoin_route_and_ordinal_arithmetic_2026-06-05.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not edit source code. If you find a bug, record it with exact file/line evidence and required-before-next-step guidance.
