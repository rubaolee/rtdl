# RayJoin Overlay Point-Location Optimization Report

Date: 2026-06-14

## Bottom Line

The Block x Water reversal is fixed for the RTDL OptiX no-output overlay benchmark.

The optimized RTDL OptiX path now uses a generic directed-segment point-location face-id device-column primitive and an automatic large-stream grouping policy. This keeps the system design app-agnostic: the optimized primitive is `directed_segment_point_location_2d`, not a RayJoin-only or Block/Water-only kernel.

Result on the two currently available Section 5.7 rows:

| Pair | Author RT | RTDL OptiX before | RTDL OptiX optimized | RTDL Embree | Optimized OptiX vs author | Optimized OptiX vs Embree |
|---|---:|---:|---:|---:|---:|---:|
| County x Zipcode | 5.614s | 5.819s | 5.767s | 9.954s | 1.03x slower | 1.73x faster |
| Block x Water | 28.088s | 42.380s | 28.471s | 34.905s | 1.01x slower | 1.23x faster |

The new Block x Water result is near parity with the author RT executable and faster than the RTDL Embree CPU path.

## What Changed

Implemented:

- generic OptiX ABI: `rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids`
- legacy-compatible ABI: `rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids`
- Python runtime method: `PreparedOptixRayjoinCdbPointLocation2D.write_face_ids_device_points()`
- overlay no-output path now classifies face IDs as a device column instead of forcing a scalar positive-face count
- generic env names for point-location grouping:
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE`
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE`
  - `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE`
- auto policy for large directed-segment point-location streams:
  - if the max query point stream is at least 32M points and no user grouping env is set, use adaptive grouping
  - mode `adaptive`
  - max group size `16`
  - area enlarge `1.2`

Old count APIs remain available for PIP count diagnostics. The optimized overlay no-output route avoids unnecessary host download and avoids unnecessary scalar count materialization.

## Why This Fixes Block x Water

The previous Block x Water result was not a data movement problem:

- old RTDL OptiX load/pack was about 0.05s
- the gap was inside point-location traversal/classification

The first attempted fix, face-id device columns, removed the unnecessary positive-face scalar count but did not materially reduce Block time by itself:

| Variant | Block x Water RTDL OptiX |
|---|---:|
| old count route | 42.380s |
| face-id columns, fixed8 grouping | 42.240s |

The real performance lever was BVH/range grouping for large point-location streams:

| Variant | Block x Water RTDL OptiX |
|---|---:|
| face-id columns, fixed8 grouping | 42.240s |
| face-id columns, adaptive 16 / 1.5 | 31.455s |
| face-id columns, adaptive 16 / 1.2 | 28.766s |
| final auto policy | 28.471s |

The optimized Block x Water phase breakdown:

| Phase | Time |
|---|---:|
| LSI hot call | 9.556s |
| point-location prepare | 5.631s |
| map0 vertices in map1 | 6.061s |
| map1 vertices in map0 | 5.329s |
| midpoint point-location total | 0.061s |
| total | 28.471s |

The old Block vertex point-location calls were 13.902s and 11.816s. The optimized calls are 6.061s and 5.329s.

## Correct Public Wording

Use:

> On the two currently available RayJoin Section 5.7 overlay rows, the optimized RTDL OptiX route is near parity with the author RT implementation and faster than the RTDL Embree CPU route. County x Zipcode is 5.77s for RTDL OptiX versus 5.61s for author RT and 9.95s for Embree. Block x Water is 28.47s for RTDL OptiX versus 28.09s for author RT and 34.90s for Embree.

Do not use:

> RTDL OptiX beats the author RayJoin implementation.

Also do not claim full 8/8 Section 5.7 reproduction yet. The six Lakes/Parks rows remain blocked by missing exact paper inputs.

## Evidence Files

Primary artifacts:

```text
docs/reports/goal4376_overlay_face_id_columns_2026-06-14/overlay_county_zipcode_optix_auto_face_ids.json
docs/reports/goal4376_overlay_face_id_columns_2026-06-14/overlay_block_water_optix_auto_face_ids.json
docs/reports/goal4376_overlay_face_id_columns_2026-06-14/block_water_pointloc_group_sweep.json
docs/reports/goal4376_overlay_face_id_columns_2026-06-14/block_water_pointloc_group_refine_sweep.json
```

Validation:

```text
py -3 -m py_compile src\rtdsl\rayjoin_overlay.py src\rtdsl\optix_runtime.py
py -3 -m unittest tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test
make build-optix
python3 -m unittest tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test
```

Local and pod tests passed. Pod rebuild exported both new face-id symbols.

## Remaining Boundary

This closes the specific optimization debt that made Block x Water unfairly Embree-faster.

It does not close the full Section 5.7 reproduction because 6/8 exact Lakes/Parks input pairs are still unavailable from the paper's public data links. When the exact inputs are available, the same 8/8 runner can execute them with the optimized route.

