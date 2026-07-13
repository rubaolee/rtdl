# Goal4993 - Prepared Vertex Query Points in Prepared Operator Session

Date: 2026-07-04

## Objective

Goal4992 removed the top4 steady-state LSI setup bottleneck by introducing an explicit prepared operator session. A full downstream decomposition then showed the largest remaining visible phase:

```text
vertex_pip_map1_in_map0_sec                 ~0.321s
vertex_pip_map1_in_map0_prepare_device_points_sec ~0.295s
```

That means the hot route was still preparing the same vertex query points every measured iteration.

Goal4993 moves vertex query-point preparation into the prepared operator session:

- prepare `left.points` for `map0_in_map1` once;
- prepare `right.points` for `map1_in_map0` once;
- reuse those prepared point handles during warmup/measured iterations;
- keep midpoint query points per-run, because midpoints depend on the current LSI output.

## Boundary

This remains an app-layer prepared/query-many route. It does not change RTDL core and does not add a RayJoin-specific primitive.

The optimization is generic in shape:

```text
prepared point-location map + repeated fixed vertex query set -> reusable prepared query points
```

The RayJoin app uses it for vertex PIP; another app with repeated point-location over the same query points could use the same pattern.

## Code Changes

File changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

Changes:

- `run_point_location_face_id_device_columns(...)` now accepts optional `prepared_points`.
- If `prepared_points` is supplied, the helper does not create or close it.
- `--prepared-operator-session` now prepares:
  - `session_prepare_vertex_points_map0_in_map1_sec`
  - `session_prepare_vertex_points_map1_in_map0_sec`
- `run_pipeline` reuses these prepared vertex point handles for vertex PIP phases.

Test updated:

- `tests/goal4990_binary_repeat_protocol_test.py`

Local validation:

```text
py_compile: OK
tests.goal4990_binary_repeat_protocol_test: OK
tests.goal4988_lsi_device_columns_direct_numba_handoff_test: OK
```

POD validation:

```text
tests.goal4990_binary_repeat_protocol_test: OK
```

## POD Evidence - Top4 County x Zipcode

Artifact:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4993_prepared_vertex_points_repeat_top4.json
```

Session prepare phases now include vertex point preparation:

| Phase | Seconds |
| --- | ---: |
| session_prepare_lsi_right | 1.588426 |
| session_prepare_lsi_left_query | 0.086379 |
| session_prepare_point_location_map0_in_map1 | 3.421039 |
| session_prepare_point_location_map1_in_map0 | 0.441587 |
| session_prepare_vertex_points_map0_in_map1 | 0.053136 |
| session_prepare_vertex_points_map1_in_map0 | 0.329662 |

Warmup row, reported but excluded:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| warmup 1 | 4.203572 | 2.890785 | 1.312787 | 0.848710 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| measured 1 | 0.553184 | 0.003740 | 0.549443 | 0.119379 |
| measured 2 | 0.551159 | 0.003302 | 0.547857 | 0.121525 |
| measured 3 | 0.594733 | 0.003368 | 0.591366 | 0.122994 |

Median:

```text
median_writer_free_hot_sec  = 0.5531838703900576
median_lsi_phase_sec        = 0.0033676400780677795
median_downstream_floor_sec = 0.5494433902204037
```

Structural consistency:

```text
lsi_row_count = 428322
descriptor_pair_count = 15014
single_lsi_row_count = true
single_descriptor_pair_count = true
```

## Performance Progression

Top4 representative route:

| Stage | Median / representative time | Meaning |
| --- | ---: | --- |
| Goal4991, no prepared operator session | 2.417124s | repeated route still recreated LSI/PIP prepared state |
| Goal4992, prepared LSI/PIP sessions | 0.902481s | LSI setup bottleneck removed |
| Goal4993, prepared vertex query points | 0.553184s | repeated vertex point preparation removed |

Improvements:

```text
Goal4992 vs Goal4991: 2.417124 / 0.902481 = ~2.68x
Goal4993 vs Goal4992: 0.902481 / 0.553184 = ~1.63x
Goal4993 vs Goal4991: 2.417124 / 0.553184 = ~4.37x
```

Compared to the top4 warmup/fresh-like row:

```text
4.411411 / 0.553184 = ~7.97x
```

This is not a fresh one-shot claim; it is the prepared/query-many binary operator route.

## Remaining Bottleneck

After Goal4993, LSI is no longer a steady-state bottleneck:

```text
median_lsi_phase_sec ~0.0034s
```

The remaining top4 steady-state floor is downstream:

```text
median_downstream_floor_sec ~0.549s
```

Visible measured components:

- intersection reprojection: `~0.19-0.21s`
- sort map0 + map1: `~0.16-0.18s`
- carrier construction: `~0.12s`
- descriptor consumer: `~0.016s`
- midpoint/PIP/assignment remainder: smaller pieces

So the next real target is not LSI and not vertex point preparation. It is the columnar continuation itself:

1. reprojection device kernel cost;
2. device sort/run metadata;
3. carrier construction;
4. remaining host/Numba boundaries in the downstream floor.

## Claim Boundary

Allowed:

- "v2.14.3 has an app-level prepared/query-many binary overlay route."
- "On top4 County x Zipcode, this route measured median `0.553s` writer-free after one reported warmup row."
- "The previous LSI and vertex query preparation costs are moved into explicit session preparation and no longer dominate measured repeats."

Not allowed:

- "One-shot overlay is `0.553s`."
- "Paper text output is `0.553s`."
- "RTDL matches author performance."
- "The pipeline is fully device-resident end to end."

## Exit Label

```text
completed_prepared_vertex_points__top4_prepared_binary_route_median_0p553s__downstream_columnar_floor_remains
```
