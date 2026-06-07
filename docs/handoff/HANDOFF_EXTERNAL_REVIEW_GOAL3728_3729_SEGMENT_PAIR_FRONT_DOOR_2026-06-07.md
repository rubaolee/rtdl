# External Review Handoff: Goals 3728-3729 Segment-Pair Exact Count Front Door

Date: 2026-06-07

## Reviewer Task

Please perform a read-only external review of Goals 3728-3729 on current `main`.

Write the review to one of these exact paths:

- Claude: `docs/reviews/goal3730_claude_review_goal3728_3729_segment_pair_front_door_2026-06-07.md`
- Gemini: `docs/reviews/goal3731_gemini_review_goal3728_3729_segment_pair_front_door_2026-06-07.md`

Use one verdict only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Context

Goal3725 validated a fast generic OptiX exact segment-pair count route for the RayJoin bundled Brazil LSI count contract. Goal3728 added a clean Python front door over that route:

`PreparedOptixSegmentPairIntersection.count_prepared_left_exact_intersections(...)`

Goal3729 adopted that front door in the RayJoin benchmark app's LSI scalar/count prepared-left path and validated it on the A5000 pod.

Latest pushed commits:

- `fe72a5b0` - Goal3728 add segment-pair exact count front door.
- `a546fa58` - Goal3729 adopt segment-pair exact count front door in RayJoin app.
- `09c4323d` - Goal3729 add RayJoin LSI front-door pod validation.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `docs/reports/goal3728_segment_pair_exact_count_front_door_2026-06-07.md`
- `docs/reports/goal3729_rayjoin_lsi_exact_count_front_door_adoption_2026-06-07.md`
- `docs/reports/goal3729_rayjoin_lsi_exact_count_front_door_app_a5000/summary.json`
- `tests/goal3728_segment_pair_exact_count_front_door_test.py`
- `tests/goal3729_rayjoin_lsi_exact_count_front_door_adoption_test.py`
- `tests/goal3704_segment_pair_prepared_left_exact_count_route_test.py`

## Evidence To Verify

Goal3729 pod app validation:

- GPU: NVIDIA RTX A5000, driver 580.126.09.
- Commit: `a546fa58`.
- Dataset: RayJoin bundled Brazil soil + county CDB pair.
- Count: 20,860.
- Prepared query median: 0.000269813 s.
- Native phase mode: `count_prepared_left_grouped_range_direct_intersection`.
- Front-door schema: `rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1`.
- Primitive: `SEGMENT_PAIR_INTERSECTION_ROWS_2D`.
- Output contract: `scalar_exact_count`.
- All claim-boundary flags false.

## Questions

1. Is the front-door API generic and contract-shaped, or does it leak RayJoin/app semantics into the runtime?
2. Is it appropriate that the front door routes to `count_prepared_left_grouped_range_direct_intersection(...)` while keeping the older `count_prepared_left(...)` route unchanged?
3. Does the RayJoin benchmark app adoption preserve app/engine separation?
4. Does the pod artifact prove the app used the front door at runtime?
5. Are the claim boundaries strong enough, given the strong single-contract timing from Goal3725?
6. What should the next engineering target be after this adoption: grouped count/Boolean continuations, additional RayJoin contracts/datasets, or a non-diagnostic API promotion gate?

## Validation Command

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3728_segment_pair_exact_count_front_door_test tests.goal3729_rayjoin_lsi_exact_count_front_door_adoption_test tests.goal3704_segment_pair_prepared_left_exact_count_route_test
```

## Boundaries

This review must not authorize release, public speedup, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, or whole-app acceleration claims.
