# Goal4992 - Prepared Operator Session for Writer-Free Binary Overlay

Date: 2026-07-04

## Objective

Goal4991 showed that top4 prepared/query-many repeats still spent median `~1.57s` in LSI producer. A direct decomposition showed the native OptiX launch was only `~0.002s`; the cost was mostly repeated setup:

```text
grouped_range_ensure ~0.93s
scaled_cache_ensure  ~0.63s
optix_launch         ~0.002s
```

Goal4992 attacks that root cause by introducing an explicit prepared operator session in the RayJoin paper reproduction app:

```bash
--prepared-operator-session
```

The session loads datasets and prepares reusable LSI/PIP handles once, then runs the writer-free binary operator for warmup/measured iterations against those prepared handles.

## Boundary

This is an app-layer product route for the paper reproduction app. It does not add a RayJoin-specific RTDL core primitive.

Allowed interpretation:

- prepared/query-many binary overlay operator route;
- session setup reported separately;
- warmup run reported separately;
- measured runs are steady same-process prepared evidence.

Not allowed:

- fresh one-shot headline;
- warm-only headline;
- author-performance parity claim;
- paper text writer performance claim;
- full end-to-end zero-copy claim.

## Code Changes

File changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

Key additions:

- `--prepared-operator-session`
- reusable LSI prepared session/query passed into `run_pipeline`
- reusable point-location sessions passed into `run_pipeline`
- preloaded datasets/bounds passed into `run_pipeline`
- session prepare phase table in repeat summary
- summary parent directory auto-created before writing JSON

Tests updated:

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

## POD Evidence - Public County x Soil

Artifact:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_prepared_session_repeat_public_sample.json
```

Session prepare phases:

| Phase | Seconds |
| --- | ---: |
| session_load_pack_left | 0.005844 |
| session_load_pack_right | 0.004395 |
| session_prepare_lsi_right | 0.251274 |
| session_prepare_lsi_left_query | 0.017874 |
| session_prepare_point_location_map0_in_map1 | 0.560181 |
| session_prepare_point_location_map1_in_map0 | 0.091672 |

Warmup row, reported but excluded:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| warmup 1 | 1.647886 | 0.869660 | 0.778226 | 0.719446 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| measured 1 | 0.066340 | 0.001332 | 0.065009 | 0.005228 |
| measured 2 | 0.075659 | 0.005988 | 0.069671 | 0.005224 |
| measured 3 | 0.054785 | 0.001087 | 0.053698 | 0.005344 |

Median:

```text
median_writer_free_hot_sec  = 0.06634041108191013
median_lsi_phase_sec        = 0.0013317279517650604
median_downstream_floor_sec = 0.06500868313014507
```

Before prepared operator session, Goal4990 measured public sample median:

```text
0.12284692749381065s
```

Prepared operator session improvement on public sample:

```text
0.12284692749381065 / 0.06634041108191013 = ~1.85x
```

## POD Evidence - Top4 County x Zipcode

Artifacts:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_prepared_session_repeat_top4.json
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_lsi_decomposition_top4_full_measured.json
```

Session prepare phases:

| Phase | Seconds |
| --- | ---: |
| session_load_pack_left | 0.011552 |
| session_load_pack_right | 0.043953 |
| session_prepare_lsi_right | 1.575404 |
| session_prepare_lsi_left_query | 0.085561 |
| session_prepare_point_location_map0_in_map1 | 3.377941 |
| session_prepare_point_location_map1_in_map0 | 0.445009 |

Warmup row, reported but excluded:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| warmup 1 | 3.743467 | 2.791218 | 0.952250 | 0.117656 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| measured 1 | 0.902481 | 0.003815 | 0.898666 | 0.109157 |
| measured 2 | 0.901680 | 0.003054 | 0.898625 | 0.107773 |
| measured 3 | 0.905731 | 0.003525 | 0.902206 | 0.109259 |

Median:

```text
median_writer_free_hot_sec  = 0.9024808872491121
median_lsi_phase_sec        = 0.0035249311476945877
median_downstream_floor_sec = 0.8986660744994879
```

Before prepared operator session, Goal4991 measured top4 median:

```text
2.41712380386889s
```

Prepared operator session improvement on top4:

```text
2.41712380386889 / 0.9024808872491121 = ~2.68x
```

Compared to the top4 warmup/fresh-like row:

```text
4.411410769447684 / 0.9024808872491121 = ~4.89x
```

## Root Cause Closed

The previous top4 LSI producer cost was not traversal-bound:

```text
top4 measured without prepared operator session:
  LSI phase       ~1.57s
  OptiX launch    ~0.002s
  grouped_range_ensure + scaled_cache_ensure dominate
```

With a prepared operator session:

```text
top4 measured with prepared operator session:
  LSI phase median ~0.0035s
```

So the LSI producer bottleneck is resolved for the prepared/query-many route by reusing the prepared LSI session and query handles.

## Remaining Bottleneck

After Goal4992, top4 steady-state is no longer LSI dominated.

Top4 measured median:

```text
writer_free_hot_sec      ~0.902s
LSI phase                ~0.0035s
downstream floor         ~0.899s
```

The new bottleneck is downstream:

- intersection reprojection: `~0.19s`
- sort map0/map1: `~0.15s` combined
- carrier construction: `~0.108s`
- descriptor consumer: `~0.015s`
- remaining midpoint/PIP/assignment phases make up the rest of the downstream floor

This means the next performance work is not more LSI setup. It is the remaining device-resident continuation path:

1. keep sorted/run metadata and midpoint/PIP continuation closer to device/columnar form;
2. reduce CPU/Numba downstream floor;
3. only after that consider deeper fusion work.

## Claim Boundary

Allowed:

- "v2.14.3 now has an explicit prepared/query-many writer-free binary overlay route."
- "On top4 County x Zipcode, the prepared operator session route reduced measured writer-free median from `2.417s` to `0.902s`."
- "The previous top4 LSI producer cost was setup/ensure dominated and is no longer the steady-state bottleneck under prepared session reuse."

Not allowed:

- "One-shot top4 overlay is `0.902s`."
- "RTDL matches the author implementation."
- "The paper text output route is `0.902s`."
- "All device-resident work is complete."

## Exit Label

```text
completed_prepared_operator_session__top4_lsi_setup_bottleneck_removed__downstream_now_dominates
```
