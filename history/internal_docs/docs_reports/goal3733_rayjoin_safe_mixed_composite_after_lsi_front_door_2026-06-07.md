# Goal3733 RayJoin Safe Mixed Composite After LSI Front Door

Date: 2026-06-07

## Purpose

Goal3729 moved the RayJoin benchmark app's LSI scalar/count prepared-left path onto the generic segment-pair exact-count front door. Goal3732 cleaned the safe mixed composite's route labels so future artifacts describe that route correctly.

Goal3733 reruns the safe mixed RayJoin composite on the A5000 pod for the public-CDB 4096-chain slice.

## Artifact

`docs/reports/goal3733_rayjoin_safe_mixed_composite_after_lsi_front_door_a5000/summary.json`

Environment:

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000, driver 580.126.09 |
| RTDL commit | `7a1c3248` |
| Tracked git status | clean |
| Count slice | 4,096 chains |
| Repeat / warmup | 20 / 5 |

## Result

| Workload | Baseline | Recommended route | Baseline seconds | Recommended seconds | Speedup |
| --- | --- | --- | ---: | ---: | ---: |
| PIP | CuPy dense all-pairs | CuPy dense all-pairs | 0.000889172 | 0.000889172 | 1.000x |
| LSI | CuPy dense all-pairs | RTDL/OptiX exact segment-pair front door | 1.266139643 | 0.000101308 | 12497.882x |
| Overlay seed | CuPy dense all-pairs | RTDL/OptiX active count | 0.164648724 | 0.004832825 | 34.069x |
| Composite sum | all-CuPy | safe mixed route | 1.430677 | 0.005818 | 245.853x |

All workload counts matched.

## Interpretation

The composite result is now dominated by the remaining overlay active-count route, not LSI. The LSI row moved from a previously repaired but slower exact route to the generic exact-count front door:

- `front_door_schema`: `rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1`
- `primitive`: `SEGMENT_PAIR_INTERSECTION_ROWS_2D`
- `output_contract`: `scalar_exact_count`
- native mode: `count_prepared_left_grouped_range_direct_intersection`
- right group count: 114,534 on the 4096-chain public-CDB slice

PIP remains CuPy in the safe mixed composite by policy, because the native PIP route still has boundary/robustness work before it can replace the dense CuPy path in this mixed recommendation.

## Claim Boundary

This artifact is internal benchmark evidence only. It does not authorize:

- Public RayJoin speedup claims.
- RayJoin paper reproduction claims.
- Release claims.
- Broad RT-core speedup claims.
- True zero-copy claims.
- Whole-app acceleration claims.

## Next Engineering Target

The next RayJoin performance target is overlay active-count, because it is now the largest recommended-route component in the safe mixed composite.
