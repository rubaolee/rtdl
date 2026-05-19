# Goal2424 RT-DBSCAN Prepared CuPy Fairness Baseline

Date: 2026-05-19

Status: implementation complete; pod timing pending

## Purpose

Goals 2418 and 2420 compared RTDL's prepared OptiX+CuPy DBSCAN bridge against
the existing `partner_cupy_grid_components_3d` mode. That mode was useful as a
strong CUDA-core baseline, but the repeat probe rebuilt its CuPy grid every
iteration. The prepared RT bridge reused prepared state.

That makes the old comparison useful for bridge-regression tracking, but not
the final fair CUDA-core-versus-RT-core steady-state comparison.

Goal2424 adds the missing fair baseline:

```text
partner_cupy_prepared_grid_components_3d
```

It prepares the generic CuPy radius-grid component continuation once and then
reuses that prepared state across repeat-probe iterations, matching the
prepared-state contract used by:

```text
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

## What Changed

- The RT-DBSCAN benchmark app now exposes
  `partner_cupy_prepared_grid_components_3d`.
- The repeat probe now includes a dedicated prepared-CuPy repeat path.
- The RT-DBSCAN tutorial now describes the prepared CuPy baseline as the fair
  steady-state CUDA-core comparator.

No native DBSCAN ABI was added. The new path reuses the generic CuPy
radius-graph component contract from the partner runtime.

## Claim Boundary

This goal narrows earlier performance wording:

- Goal2418 and Goal2420 remain valid for showing that the prepared RT bridge
  improves over the older fresh-grid RT bridge and historical fresh-grid CuPy
  baseline.
- Any new claim that prepared RT beats pure CuPy must be checked against
  `partner_cupy_prepared_grid_components_3d`, not only against
  `partner_cupy_grid_components_3d`.
- If prepared pure CuPy wins on a dataset, the explicit plan must choose pure
  CuPy for that row and record the reason.
- This still does not authorize paper-level RT-DBSCAN reproduction or broad
  DBSCAN speedup claims.

## Required Pod Matrix

The next timing pass should compare these three modes:

```text
partner_cupy_grid_components_3d
partner_cupy_prepared_grid_components_3d
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

The minimum useful rows are:

```text
clustered3d: 32768, 65536, 131072, 262144
road3d:      32768, 65536, 131072, 262144
ngsim_dense: 32768, 65536, 131072
```

All rows must preserve signature parity. The report from that pod pass should
supersede any broad reading of the Goal2418/Goal2420 pure-CuPy comparisons.
