# Goal4341: External Review Consensus And Optimized Comparison Closeout

Date: 2026-06-11

## Verdict

`accept-with-boundary` for closing the Goal4339/Goal4340 Embree AABB
optimization review and publishing the Goal4341 internal optimized
Embree-vs-OptiX comparison packet.

This is not release authorization and not public speedup authorization.

## Review Inputs

- `docs/reviews/goal4341_gemini_review_goal4339_4340_embree_aabb_optimization_2026-06-11.md`
- `docs/reviews/goal4341_claude_review_goal4339_4340_embree_aabb_optimization_2026-06-11.md`
- `docs/reports/goal4340_embree_native_aabb_index_route_2026-06-11.md`
- `docs/reports/goal4341_optimized_embree_optix_comparison_packet_2026-06-11.md`
- `docs/reports/goal4341_optimized_embree_optix_comparison_packet_2026-06-11.json`

## External Review Summary

Gemini verdict: `accept`.

Gemini agreed that:

- the native Embree `AABB_INDEX_QUERY_2D` route is app-agnostic;
- the exact predicates are correct;
- `std::atomic<size_t>` is sufficient for parallel `rtcCollide(...)` callback
  counts;
- the fallback route and claim boundaries are acceptable.

Claude verdict: `accept-with-boundary`.

Claude agreed with the same core findings and identified one non-blocking
follow-up: an Embree 3 build could expose the new symbols but still lack Embree
4 `rtcCollide(...)` support, making symbol-only availability misleading.

## Follow-Up Fix

The Embree 3 availability quirk is fixed locally:

- `src/rtdsl/embree_runtime.py` now derives the loaded library version through
  `_embree_version_from_library(...)`.
- `embree_aabb_index_2d_available()` now requires Embree major version `>= 4`
  in addition to the native symbols.
- Direct `PreparedEmbreeAabbIndex2D(...)` construction fails early with a clear
  Embree-4 requirement on older libraries.
- `tests/goal4340_embree_native_aabb_index_route_test.py` includes a fake
  Embree 3 library guard for this behavior.

## Goal4341 Packet Boundary

Goal4341 records exactly one measured optimized comparison row:

- app: `librts_spatial_index`;
- contract: `generic_prepared_aabb_index_query_2d`;
- scale: 1024 indexed boxes x 1024 queries, `operation=all`, skip-counts;
- optimized Embree CPU query median: `0.011698941s`;
- OptiX RT query median: `0.000622335s`;
- query-median ratio: OptiX is about `18.8x` faster than optimized Embree for
  this prepared-query phase.

Goal4341 also records the old pre-Goal4340 Embree columnar fallback query
median, `43.764849884s`, making the optimized Embree route about `3740.9x`
faster than the old fallback on this row.

All other benchmark apps remain planning rows with explicit reasons and next
actions. They do not have Goal4341 backend ratios.

## Validation

Focused Windows validation:

```text
py -3 -m unittest tests.goal4338_current_optix_embree_comparison_index_test tests.goal4341_optimized_embree_optix_comparison_packet_test tests.goal4339_librts_skip_counts_native_perf_guard_test tests.goal4340_embree_native_aabb_index_route_test tests.goal2574_librts_spatial_index_benchmark_app_test

Ran 26 tests in 2.287s
OK
```

Linux/native timing evidence is unchanged from Goal4340. The post-review fix is
a Python availability guard and unit-level behavior correction.

## Claim Boundary

This consensus does not authorize release action, package-install wording,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
paper reproduction wording, true-zero-copy wording, automatic partner
selection, or app-specific native-engine logic.
