# Goal2417 RT-DBSCAN Prepared CuPy Grid Continuation

Date: 2026-05-19

Status: local implementation in progress; pod steady-state evidence is still required

## Purpose

Goal2415 showed that the corrected clique-safe microcell path was
performance-negative. This goal pivots to the stronger base path that already
won locally and on the pod:

```text
OptiX RT count-threshold device columns
  -> CuPy device-grid radius-graph component continuation
```

The improvement here is preparation and reuse. Instead of rebuilding the CuPy
grid, sorted order, unique-cell ranges, parent workspace, label workspace, and
count/flag buffers for every repeat, RTDL now exposes a prepared generic CuPy
grid continuation object.
In short: this is the prepared CuPy grid continuation pivot after the microcell path was performance-negative.

## New Generic Contract

Added Python-side partner helpers:

```text
PreparedCupyRadiusGraphComponents3DGrid
prepare_radius_graph_components_3d_cupy_grid_partner_columns(...)
radius_graph_components_3d_cupy_prepared_grid_partner_columns(...)
```

The contract is generic:

```text
prepared_partner_device_point_columns_3d
  -> generic_prepared_cupy_grid_radius_graph_component_labels_3d
```

It is not a DBSCAN-specific native entry point. No native RTDL engine ABI was added.

## Benchmark Wiring

The RT-DBSCAN benchmark app gained:

```text
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

The one-shot app mode prepares the grid inside a normal app call, so it is
mainly a functional path. The repeat probe is the important measurement path:

```text
scripts/goal2403_rt_dbscan_repeat_probe.py
```

For the prepared mode, the repeat probe prepares the OptiX scene, CuPy point
columns, CuPy grid index, sorted order, unique-cell ranges, and output
workspaces once. It then repeats only:

```text
prepared OptiX RT count-threshold pass
prepared CuPy component continuation
signature materialization for evidence
```

This makes the measurement closer to a steady-state server/workflow setting.

## Claim Boundary

- This is a generic radius-graph component continuation.
- This is not a DBSCAN native ABI.
- This is not a release claim yet.
- This is not broad RT-core acceleration evidence yet.
- Pod timing must decide whether the prepared reuse actually improves
  RT-DBSCAN steady-state performance.

## Expected Evidence

The next pod run should compare, at large sizes and with repeat-tail medians:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
optix_rt_core_flags_cupy_prepared_grid_components_3d
```

Datasets should include at least:

```text
clustered3d
road3d
```

The desired result is not merely that the prepared mode runs. It should show
whether removing repeated grid/index/workspace setup closes the gap found in
Goal2415, especially for road-shaped data where the microcell path was clearly
wrong.
