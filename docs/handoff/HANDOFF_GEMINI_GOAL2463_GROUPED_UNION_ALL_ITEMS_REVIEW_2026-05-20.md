# Gemini Review Task - Goal2463 grouped-union all-items path

Please perform an independent read-only review of Goal2463 and write your
review to:

`docs/reviews/goal2464_gemini_review_goal2463_grouped_union_all_items_2026-05-20.md`

If you prefer a more explicit filename, use:

`docs/reviews/goal2464_gemini_review_goal2463_grouped_union_all_items_path_2026-05-20.md`

## Context

RTDL native engines must remain app-agnostic. We are improving the RT-DBSCAN
benchmark through generic fixed-radius/grouped-continuation primitives, not
through DBSCAN-specific native ABI.

Goal2461 added a prepared self-query device path for generic fixed-radius
grouped union. Goal2463 adds a generic all-items-eligible mode for dense rows
where the threshold-capped count pass proves every item is predicate-true.

## Files to inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_adapters.py`
- `tests/goal2463_grouped_union_all_items_path_test.py`
- `docs/reports/goal2463_grouped_union_all_items_path_2026-05-20.md`
- `docs/reports/goal2463_grouped_union_baseline_pod/summary.json`
- `docs/reports/goal2463_grouped_union_all_items_pod/summary.json`

## Questions to answer

1. Does Goal2463 preserve the app-agnostic native-engine boundary?
2. Is the all-items path generic and correctly gated on uniformly true predicate flags?
3. Does the non-uniform predicate path remain intact?
4. Do the pod artifacts support the claimed scoped performance improvement for the 65,536-point clustered row?
5. Are the claim boundaries in the report appropriately narrow?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
If accepted with a boundary, state the exact boundary. Do not make release claims.
