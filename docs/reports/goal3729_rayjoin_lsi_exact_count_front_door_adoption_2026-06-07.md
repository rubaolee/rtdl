# Goal3729 RayJoin LSI Exact-Count Front Door Adoption

Date: 2026-06-07

## Purpose

Goal3728 added a generic OptiX front door:

`PreparedOptixSegmentPairIntersection.count_prepared_left_exact_intersections(...)`

Goal3729 wires the RayJoin benchmark reference app's LSI scalar/count mode to that front door when a prepared left set is available. This keeps the benchmark app aligned with the fastest measured Goal3725 route without moving RayJoin-specific logic into the native engine.

## What Changed

In `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`:

- LSI `result_mode="count"` with `prepare_left_for_count=True` now calls `prepared.count_prepared_left_exact_intersections(prepared_left)`.
- Row-producing LSI mode still uses `prepared.run_raw(...)`.
- Unprepared count fallback still uses `prepared.count(packed_left)`.
- The summary now records `segment_pair_count_route` metadata, including front-door schema, primitive, output contract, route, native symbol, right-group count, and claim boundary status.

## Boundary

This is app-level benchmark adoption of a generic primitive front door. It does not:

- Add a RayJoin-specific native symbol.
- Rename the primitive catalog.
- Replace the older any-hit route globally.
- Authorize public RayJoin speedup claims.
- Authorize RayJoin paper reproduction claims.
- Authorize release or whole-app acceleration claims.

## Next Validation

Run the RayJoin LSI count benchmark app on the A5000 pod with `prepare_left_for_count=True` and verify that:

- Counts still match the CPU/reference or same-source expected count.
- `segment_pair_count_route.front_door_schema` is present.
- Native phase mode records the grouped-range direct intersection route.
- Claim-boundary fields remain false.
