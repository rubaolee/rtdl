# Handoff: External Review for Goal3737 Shape-Pair Active-Count Executor

Please perform an independent review of Goal3737 on current `main`.

## Scope

Review implementation commit `5053d37a` plus clean-evidence refresh commit
`68b894dd`, and the Goal3737 artifacts:

- `docs/reports/goal3737_shape_pair_active_count_executor_and_rayjoin_perf_2026-06-07.md`
- `tests/goal3737_shape_pair_active_count_executor_test.py`
- `docs/reports/goal3737_shape_pair_active_count_executor_direct_a5000/summary.json`
- `docs/reports/goal3737_rayjoin_safe_mixed_prepared_left_cross_size_a5000/summary.json`
- `docs/reports/goal3737_rayjoin_safe_mixed_executor_cross_size_a5000/summary.json`
- Native/runtime/app files touched by the commit:
  - `src/native/optix/rtdl_optix_workloads.cpp`
  - `src/native/optix/rtdl_optix_api.cpp`
  - `src/native/optix/rtdl_optix_prelude.h`
  - `src/rtdsl/optix_runtime.py`
  - `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## Questions

1. Does the new executor remain app-agnostic in native naming and implementation?
2. Does the implementation actually reuse output/count/parameter buffers across repeated prepared-left active-count calls?
3. Are Python runtime ownership and destroy semantics safe enough for this internal benchmark route?
4. Does the RayJoin app keep RayJoin interpretation in Python while using the generic executor?
5. Do the A5000 artifacts support the narrow conclusion:
   - direct 4096 overlay active-count median improves from about `0.00315s` to about `0.00156s`;
   - safe-mixed cross-size geomean improves from about `211x` to about `324x` vs all-CuPy;
   - all measured counts match;
   - 8192 all-CuPy baseline OOM is correctly treated as a boundary rather than a speedup row?
6. Do the report and artifacts avoid overclaiming public RayJoin reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, whole-app speedup, or release claims?

## Required Output

Write the review to:

- Gemini: `docs/reviews/goal3738_gemini_review_goal3737_shape_pair_active_count_executor_2026-06-07.md`
- Claude: `docs/reviews/goal3739_claude_review_goal3737_shape_pair_active_count_executor_2026-06-07.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
