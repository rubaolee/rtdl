# Handoff: Claude Review for Compact Grouped-Count / RayJoin Chain

Date: 2026-06-03

Please perform an independent review of the recent compact device-column /
RayJoin app-route chain and write the review to:

`docs/reviews/goal3202_claude_review_compact_grouped_count_rayjoin_chain_2026-06-03.md`

## Scope

Review Goals 3189, 3191, 3193, 3195, 3197, 3199, 3200, and 3201.

Primary files:

- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `docs/reports/goal3189_pair_column_grouped_count_continuation_2026-06-03.md`
- `docs/reports/goal3191_dense_grouped_count_device_columns_2026-06-03.md`
- `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`
- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md`
- `docs/reports/goal3199_rayjoin_compact_route_app_timing_2026-06-03.md`
- `docs/reports/goal3201_rayjoin_compact_route_steady_state_timing_2026-06-03.md`
- `docs/reviews/goal3200_gemini_review_goal3199_rayjoin_compact_route_app_timing_2026-06-03.md`
- Related tests: `tests/goal3189_*`, `tests/goal3191_*`, `tests/goal3193_*`, `tests/goal3195_*`, `tests/goal3197_*`, `tests/goal3199_*`, `tests/goal3201_*`.

## Review Questions

1. Does the native/runtime chain remain app-agnostic after adding dense and
   compact grouped-count device columns?
2. Is the compact grouped-count primitive genuinely a generic continuation over
   pair-column rows, rather than RayJoin-specific engine logic?
3. Does the RayJoin app route keep RayJoin naming, left-ID remapping, route
   policy, and benchmark interpretation in Python/app code?
4. Do the timing reports correctly distinguish:
   - primitive timing probe,
   - app-route timing probe,
   - steady-state after warm-up,
   - no release/public speedup/paper reproduction/true-zero-copy claim?
5. Are the tests adequate for the bounded evidence, and what must be fixed
   before using this route in a stronger RayJoin performance comparison?
6. Are there app-specific terms, stale release flags, claim-boundary leaks, or
   machine-checkability gaps that should be corrected before the next goal?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Please lead with findings by severity. If accepted, prefer
`accept-with-boundary` unless you believe all release-gate concerns are closed.
This review must not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, or RayJoin paper reproduction claims.

If you run tests, record the exact command and result. If you cannot run tests,
say so explicitly and keep the review static.
