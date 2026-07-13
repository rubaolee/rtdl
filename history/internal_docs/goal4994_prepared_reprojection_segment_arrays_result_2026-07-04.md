# Goal4994 - Prepared Reprojection Segment Device Arrays

Date: 2026-07-04

## Objective

After Goal4993, the top4 prepared/query-many route had median `0.553s`. The remaining visible downstream cost included:

```text
intersection_reprojection_device_columnar_sec ~0.19-0.21s
```

Inspection showed that reprojection copied all left/right segment coordinate arrays to GPU every measured run:

```text
left/right x0,y0,x1,y1 -> cuda.to_device(...)
```

For top4, this is hundreds of MB of repeated device upload. Goal4994 moves those segment device arrays into the prepared operator session and reuses them for Numba reprojection.

## Boundary

This is still app-layer prepared/query-many infrastructure:

- no RTDL core change;
- no RayJoin-specific core primitive;
- no paper text writer claim;
- no fresh one-shot headline.

The optimization is generic in shape:

```text
prepared geometry arrays + repeated numeric continuation -> reuse device arrays
```

## Code Changes

File changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

Changes:

- `_numeric_xsect_columns_from_device_pair_arrays(...)` now accepts optional `left_device` and `right_device`.
- `numeric_xsect_columns_from_pairs_numba_device(...)` and `numeric_xsect_columns_from_pair_device_columns_numba_device(...)` pass through optional prepared device arrays.
- `--prepared-operator-session` now records:
  - `session_prepare_reprojection_left_segment_device_arrays_sec`
  - `session_prepare_reprojection_right_segment_device_arrays_sec`
- measured runs reuse these arrays for reprojection.

Test updated:

- `tests/goal4990_binary_repeat_protocol_test.py`

Validation:

```text
py_compile: OK
tests.goal4990_binary_repeat_protocol_test: OK
tests.goal4988_lsi_device_columns_direct_numba_handoff_test: OK
POD tests.goal4990_binary_repeat_protocol_test: OK
```

## POD Evidence - Top4 County x Zipcode

Artifact:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4994_prepared_reprojection_arrays_repeat_top4.json
```

Session prepare phases now include reprojection segment device arrays:

| Phase | Seconds |
| --- | ---: |
| session_prepare_reprojection_left_segment_device_arrays | 0.030539 |
| session_prepare_reprojection_right_segment_device_arrays | 0.159170 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | reprojection | sort0 | sort1 | carrier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| measured 1 | 0.357781 | 0.003388 | 0.354392 | 0.004508 | 0.032208 | 0.120922 | 0.116828 |
| measured 2 | 0.370688 | 0.009418 | 0.361270 | 0.013913 | 0.042377 | 0.117090 | 0.114626 |
| measured 3 | 0.366520 | 0.003043 | 0.363476 | 0.004356 | 0.030200 | 0.138089 | 0.115268 |

Median:

```text
median_writer_free_hot_sec  = 0.3665195722132921
median_lsi_phase_sec        = 0.0033884719014167786
median_downstream_floor_sec = 0.36127020977437496
```

## Performance Progression

Top4 representative route:

| Stage | Median / representative time | Meaning |
| --- | ---: | --- |
| Goal4991, no prepared operator session | 2.417124s | recreated LSI/PIP prepared state |
| Goal4992, prepared LSI/PIP sessions | 0.902481s | LSI setup removed |
| Goal4993, prepared vertex query points | 0.553184s | repeated vertex point prep removed |
| Goal4994, prepared reprojection segment arrays | 0.366520s | repeated segment array upload removed |

Improvements:

```text
Goal4994 vs Goal4993: 0.553184 / 0.366520 = ~1.51x
Goal4994 vs Goal4991: 2.417124 / 0.366520 = ~6.59x
Goal4994 vs warmup/fresh-like top4 row: 4.411411 / 0.366520 = ~12.04x
```

## Root Cause Closed

The prior reprojection cost was not mainly the arithmetic kernel. It was repeated preparation of segment coordinate arrays.

After moving those arrays into the prepared operator session:

```text
intersection_reprojection_device_columnar_sec ~0.19-0.21s
                                         -> ~0.004-0.014s
```

## Remaining Bottleneck

Top4 steady-state is now dominated by:

- device sort/run ordering:
  - map0 `~0.03-0.04s`
  - map1 `~0.12-0.14s`
- carrier construction:
  - `~0.115s`
- descriptor consumer:
  - `~0.015s`
- smaller midpoint/PIP/assignment pieces.

LSI and reprojection are no longer the bottlenecks.

Next plausible targets:

1. sort/run metadata route, especially map1;
2. carrier construction;
3. only then deeper device-resident carrier/consumer fusion.

## Claim Boundary

Allowed:

- "Prepared/query-many top4 writer-free binary median reached `0.367s`."
- "Reusing prepared segment device arrays removed the repeated reprojection upload cost."
- "This is an app-level prepared operator route, not a one-shot headline."

Not allowed:

- "One-shot overlay is `0.367s`."
- "Paper text route is `0.367s`."
- "RTDL matches author performance."
- "The route is fully device-resident end to end."

## Exit Label

```text
completed_prepared_reprojection_arrays__top4_prepared_binary_route_median_0p367s__sort_and_carrier_remain
```
