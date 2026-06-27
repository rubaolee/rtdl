# Goal3732 RayJoin Composite LSI Route Label Cleanup

Date: 2026-06-07

## Purpose

After Goal3728/3729, the RayJoin benchmark app's LSI scalar/count path uses the generic front door:

`PreparedOptixSegmentPairIntersection.count_prepared_left_exact_intersections(...)`

The older `goal3612_rayjoin_safe_mixed_route_composite.py` helper already calls that app path through `run_rayjoin_prepared_optix_workload(..., prepare_left_for_count=True)`, so it will use the new route automatically. However, its metadata still described the LSI path as an any-hit traversal.

Goal3732 updates only the composite script metadata:

- `segment_policy` now says `device_double_exact_count_during_optix_intersection_program_identity_range`.
- The LSI recommended-route payload now carries `segment_pair_count_route` from the app summary.
- The composite interpretation now says the exact predicate runs inside the custom intersection program over identity-range primitive records.

## Boundary

This goal does not change native code, benchmark math, datasets, or existing historical artifacts. It only prevents future composite artifacts from carrying stale route language.
