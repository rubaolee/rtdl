# Goal3728 Segment-Pair Exact Count Front Door

Date: 2026-06-07

## Purpose

Goal3725 found a fast, app-agnostic OptiX route for exact 2-D segment-pair count: keep generic segment records as identity ranges by default, evaluate the exact predicate inside the custom intersection program, and avoid the any-hit callback path.

The measured route was still exposed through a diagnostic method name:

`count_prepared_left_grouped_range_direct_intersection(...)`

Goal3728 adds a thin Python front door with contract-oriented naming:

`PreparedOptixSegmentPairIntersection.count_prepared_left_exact_intersections(...)`

This does not add a native symbol. It does not change the existing `count_prepared_left(...)` any-hit route. It gives benchmark apps and learner examples a generic, traceable way to request the measured exact-count contract without importing RayJoin or LSI vocabulary into the runtime API.

## Contract

The new front door returns metadata:

- `schema`: `rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1`
- `primitive`: `SEGMENT_PAIR_INTERSECTION_ROWS_2D`
- `output_contract`: `scalar_exact_count`
- `backend`: `optix`
- `route`: `intersection_program_identity_or_ranged_primitive_records`
- `count`
- `right_group_count`
- `native_symbol`
- `implementation_contract`
- `route_selection`
- `claim_boundary`

The route selection records the default identity-range policy and the environment knobs that can override it:

- `RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_MAX_SIZE`
- `RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_AREA_ENLARGE`

## App-Agnostic Boundary

The front door is intentionally contract-shaped:

- It names only segment pairs, prepared left/right sets, exact count, output contract, route, and backend.
- It does not mention RayJoin, LSI, maps, counties, soils, polygons, or paper-system semantics.
- App-specific interpretations remain in benchmark code and reports.
- The primitive catalog already records `rows.segment_pair_intersection_rows_2d` with aliases such as `segment_pair_intersection_count`, `line_segment_intersection`, and `lsi_count`; Goal3728 does not create a duplicate primitive family.

## Claim Boundary

The method is an experimental front door over a validated route. It does not authorize:

- Public speedup claims.
- RTDL-beats-RayJoin claims.
- RayJoin paper reproduction claims.
- Broad RT-core speedup claims.
- Release claims.
- True zero-copy claims.
- Whole-app acceleration claims.

## Next Step

Use this front door in the RayJoin benchmark reference path for scalar/count contracts, then add grouped count/Boolean continuation contracts only if they remain generic and are backed by pod evidence.
