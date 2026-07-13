# Goal4969 Prepared-Hot Downstream Breakdown

Date: 2026-07-04

## Exit Label

`completed_prepared_hot_breakdown__next_targets_are_downstream_numeric_phases`

## Purpose

Goal4968 made planar-map LSI workspace preparation explicit and showed that the
prepared-hot LSI replay is about `0.0015s`.

Goal4969 answers the next question:

> Once LSI is prepared, what remains inside the `~0.09s` writer-free binary
> route?

This goal does not implement another optimization. It measures and ranks the
prepared-hot downstream phases so the next implementation does not chase the
wrong target.

## Boundary

This is still a generic-system line:

- RTDL core owns generic planar-map LSI/PIP/workspace primitives.
- RayJoin remains an app-level workload.
- No RayJoin overlay text/output-chain semantics were added to core.
- The app's prepared-hot route uses the public `PLANAR_MAP_LSI_2D`
  `prepare_workspace()` boundary from Goal4968.

## POD Measurement

POD:

```text
root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
```

Input:

```text
left:  br_county_clean_25_odyssey_final.txt
right: br_soil_ascii_odyssey_final.txt
author_overlay_compute_sec: 0.0421
```

Command shape:

```bash
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left ...br_county_clean_25_odyssey_final.txt \
  --right ...br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --prepared-lsi-replay \
  --author-overlay-compute-sec 0.0421 \
  --summary /tmp/goal4969_prepared_hot_downstream_runN.json
```

Artifacts:

```text
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run1.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run2.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run3.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run4.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run5.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_run6.json
history/internal_docs/goal4955_artifacts/goal4969_prepared_hot_downstream_summary.json
```

## Result

Semantic fingerprint was stable:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

Prepared-hot median:

```text
writer_free_hot_sec = 0.090454s
ratio vs 0.0421s   = 2.15x
```

Setup medians, reported separately and excluded from `writer_free_hot_sec`:

| Setup phase | Median |
|---|---:|
| `prepare_lsi_session_sec` | `0.273701s` |
| `lsi_prepare_workspace_sec` | `0.513670s` |
| `prepare_point_location_map0_in_map1_sec` | `0.557102s` |
| `prepare_point_location_map1_in_map0_sec` | `0.080672s` |

Prepared-hot phase medians:

| Rank | Phase | Median |
|---:|---|---:|
| 1 | `vertex_pip_map0_in_map1_sec` | `0.016410s` |
| 2 | `intersection_reprojection_device_columnar_sec` | `0.014259s` |
| 3 | `sort_map0_device_columnar_sec` | `0.012008s` |
| 4 | `sort_map1_device_columnar_sec` | `0.011609s` |
| 5 | `grouped_compiled_columnar_carrier_construction_sec` | `0.010285s` |
| 6 | `vertex_pip_map1_in_map0_sec` | `0.007099s` |
| 7 | `midpoint_points_map1_columnar_sec` | `0.006698s` |
| 8 | `grouped_descriptor_pair_count_consumer_sec` | `0.005862s` |
| 9 | `midpoint_points_map0_columnar_sec` | `0.002283s` |
| 10 | `lsi_prepared_replay_rows_sec` | `0.001401s` |
| 11 | `midpoint_pip_map0_sec` | `0.000485s` |
| 12 | `midpoint_pip_map1_sec` | `0.000408s` |

The two face-assignment phases were microsecond-level and not material.

## Interpretation

### I1. LSI is no longer the prepared-hot bottleneck

Prepared-hot LSI replay is around:

```text
0.0014s
```

That is about `1.5%` of the `~0.090s` prepared-hot route.

So the next prepared-hot performance work should not target LSI.

### I2. The remaining cost is distributed, not one giant phase

The top five prepared-hot phases are:

```text
vertex PIP map0      ~16ms
reprojection         ~14ms
sort map0            ~12ms
sort map1            ~12ms
group construction   ~10ms
```

This means the next useful optimization probably needs to reduce several
downstream numeric phases, not just one line of Python.

### I3. The biggest single phase is public point-location/PIP

`vertex_pip_map0_in_map1_sec` is the largest hot phase.

It is already a public generic planar-map point-location/PIP primitive, not a
RayJoin-specific helper. Future work can target its prepared-hot execution,
batching, or workspace reuse while preserving the generic primitive boundary.

### I4. Device-columnar reprojection/sort still matter

Goal4957 already moved reprojection and sort onto the device-columnar route.
They are still the second/third/fourth largest phases.

This does not mean the previous work failed. It means those are now visible
steady-state costs after LSI was removed from the hot path.

### I5. Group construction is the next app-boundary risk

`grouped_compiled_columnar_carrier_construction_sec` is about `10ms`.

It is app-owned in the current RayJoin paper route because it builds the
projected descriptor carrier. If RTDL generalizes this, it must do so as a
generic columnar group/segment/reduce facility, not as a RayJoin output-chain
primitive.

## Recommended Next Goals

### Goal4970: Prepared Point-Location Workspace And Batch Reuse

Purpose:

- apply the same explicit workspace discipline to planar-map point-location/PIP,
- separate point-location session preparation from hot query execution,
- test whether the `~16ms + ~7ms` vertex PIP phases can be reduced without
  app-specific logic.

Boundary:

- generic `PLANAR_MAP_POINT_LOCATION_2D`,
- no overlay/output-chain semantics in core.

### Goal4971: Downstream Columnar Numeric Fusion Probe

Purpose:

- fuse or batch reprojection + sort preparation where possible,
- reduce the combined `~38ms` reprojection/sort block,
- keep the output as generic numeric columns.

Boundary:

- generic numeric column transforms/sort,
- no RayJoin-specific midpoint/output-chain primitive in RTDL core.

### Goal4972: Generic Columnar Group/Descriptor Carrier Review

Purpose:

- decide whether the `~10ms` group construction can become a generic RTDL
  grouped columnar reduction,
- or whether it must remain app-owned.

Boundary:

- no RayJoin text writer,
- no output-chain semantics in core,
- prove genericity on a non-RayJoin workload before promotion.

## Not Authorized

- No claim that the prepared-hot route is fresh one-shot overlay performance.
- No claim that LSI remains the prepared-hot bottleneck.
- No RayJoin-specific core primitive.
- No larger representative data claim.
- No broad high-performance claim beyond this public sample and boundary.
