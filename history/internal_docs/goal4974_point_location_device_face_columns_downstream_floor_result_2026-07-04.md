# Goal4974 Result: Directed Point-Location Face-ID Device Columns

Date: 2026-07-04

## Verdict Requested

`completed_point_location_device_face_columns_moves_downstream_floor`

## Summary

Goal4974 connected the existing generic directed point-location/PIP device-column capability to the RayJoin Section 5.7 writer-free binary route.

The change is deliberately narrow:

- expose generic point-location device-column methods on the public planar-map point-location wrapper
- use `face_id_device_columns()` in the RayJoin binary app under an explicit flag
- copy only the `uint32 face_id` column back to NumPy for the current downstream code
- record row-buffer metadata proving the producer is generic directed point-location, not RayJoin overlay

This is **not** a true-zero-copy claim. The current downstream still consumes NumPy arrays. The win is from replacing full point-location row materialization with a narrower face-id column handoff.

## Code Changes

- `src/rtdsl/optix_runtime.py`
  - Added generic wrapper methods to `PreparedOptixPlanarMapPointLocation2D`:
    - `prepare_query_points`
    - `face_id_device_columns`
    - `segment_id_device_columns`
  - These methods preserve the existing planar-map point-location env/scale/query-map contract through `_with_env`.

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
  - Added `--point-location-device-face-columns`.
  - Added a route that calls `face_id_device_columns()` for vertex and midpoint PIP.
  - Records `point_location_device_face_column_metadata`.
  - Records explicit claim boundaries:
    - downstream NumPy copy is used
    - true-zero-copy is not authorized
    - the RTDL core change is a generic planar-map point-location wrapper change

- `tests/goal4974_point_location_device_face_columns_route_test.py`
  - Guards the app flag, wrapper API, subphase timings, and no-zero-copy wording.

## POD Evidence

POD: `root@213.173.108.6 -p 10626`

Input:

- left: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb`
- right: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb`
- LSI route: `--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000`
- downstream route: `--device-columnar --compiled-group`

Artifacts:

- `history/internal_docs/goal4974_point_location_device_face_columns_artifacts_2026-07-04/baseline_rows_summary.json`
- `history/internal_docs/goal4974_point_location_device_face_columns_artifacts_2026-07-04/device_face_columns_summary_final.json`

## Correctness / Parity

The device face-column route matched the baseline rows route on the bounded binary summary:

| Field | Baseline | Device face columns | Match |
|---|---:|---:|---|
| `vertex_positive_counts.side0_in_side1` | 812721 | 812721 | yes |
| `vertex_positive_counts.side1_in_side0` | 4527305 | 4527305 | yes |
| `grouped_carrier.group_count` | 428974 | 428974 | yes |
| `grouped_carrier.point_row_count` | 5902562 | 5902562 | yes |
| `grouped_carrier.skipped_group_count` | 439426 | 439426 | yes |
| `downstream_consumer.pair_count` | 15014 | 15014 | yes |
| `downstream_consumer.total_groups` | 428974 | 428974 | yes |
| `downstream_consumer.total_point_rows` | 5902562 | 5902562 | yes |
| `lsi_row_count` | 428322 | 428322 | yes |

## Performance Delta

| Phase | Baseline rows | Device face columns | Delta | Change |
|---|---:|---:|---:|---:|
| `writer_free_hot_sec` | 5.885168s | 5.294854s | -0.590314s | -10.03% |
| `downstream_floor_sec` | 3.243420s | 2.641307s | -0.602113s | -18.56% |
| `vertex_pip_map0_in_map1_sec` | 0.124076s | 0.059533s | -0.064544s | -52.02% |
| `vertex_pip_map1_in_map0_sec` | 0.756031s | 0.320410s | -0.435621s | -57.62% |
| `midpoint_pip_map0_sec` | 0.007718s | 0.004093s | -0.003626s | -46.97% |
| `midpoint_pip_map1_sec` | 0.006147s | 0.003792s | -0.002355s | -38.31% |
| `grouped_compiled_columnar_carrier_construction_sec` | 0.676761s | 0.590611s | -0.086149s | -12.73% |
| `midpoint_points_map0_columnar_sec` | 0.691220s | 0.689386s | -0.001833s | -0.27% |
| `midpoint_points_map1_columnar_sec` | 0.608180s | 0.601035s | -0.007144s | -1.17% |

## What This Proves

1. The point-location/PIP row materialization path was a real downstream cost.
2. A generic directed point-location `face_id` device-column output can replace full point-location rows for this binary route.
3. The improvement is material but bounded: about 0.59s on the top4 representative input.
4. The current app still copies `face_id` to NumPy, so this is not the final device-resident overlay operator.

## What This Does Not Prove

- It does not prove true zero-copy.
- It does not prove parity with the author C++ text-output route.
- It does not close the remaining gap to author overlay compute.
- It does not implement Layer 4 fusion.
- It does not move RayJoin output-chain/text writer work.

## Updated Bottleneck

After Goal4974, the largest downstream components are no longer PIP rows:

- `midpoint_points_map0_columnar_sec`: 0.689386s
- `midpoint_points_map1_columnar_sec`: 0.601035s
- `grouped_compiled_columnar_carrier_construction_sec`: 0.590611s
- `vertex_pip_map1_in_map0_sec`: 0.320410s
- `intersection_reprojection_device_columnar_sec`: 0.232909s

The next meaningful work should target actual device-resident midpoint generation and carrier/group construction, not more PIP row materialization cleanup.

## Local Validation

Commands:

```text
py -m py_compile src/rtdsl/optix_runtime.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4974_point_location_device_face_columns_route_test tests.goal4944_pip_point_location_device_column_carrier_test tests.goal4942_device_column_row_buffer_handoff_test
```

Result:

```text
Ran 15 tests in 0.031s
OK
```

## Exit Label

`completed_point_location_device_face_columns_moves_downstream_floor`
