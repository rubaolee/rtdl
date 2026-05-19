# Goal2400 RT-DBSCAN OptiX Summary To CuPy Component Bridge

Date: 2026-05-19

Status: implementation slice; pod timing pending

## Purpose

Goal2398 closed the immediate CuPy component-continuation pathology but left the
main RT-DBSCAN architecture gap: OptiX fixed-radius traversal still materialized
every neighbor row before the DBSCAN-style component continuation.

Goal2400 adds a smaller generic bridge:

```text
OptiX prepared fixed-radius summaries -> CuPy device-grid component continuation
```

This avoids O(edges) neighbor-row materialization. It still materializes
O(points) summary rows on the host and copies the resulting core flags/counts
into CuPy, so it is not the final paper-style device-output continuation.

## What Changed

- `radius_graph_components_3d_cupy_grid_partner_columns(...)` can now accept
  caller-supplied `core_flags` and `neighbor_counts` as partner columns.
- The benchmark app adds mode:
  `optix_core_flags_cupy_grid_components_3d`.
- The pod runner now records two OptiX+CuPy bridge rows after OptiX is built.

## Contract Boundary

This remains generic:

- OptiX emits fixed-radius ranked neighbor summaries.
- The partner continuation consumes generic core flags/counts and point columns.
- No DBSCAN-specific native ABI is added.

The bridge is exact for DBSCAN core classification when `min_neighbors <= 64`,
because the OptiX summary is requested with `k_max=min_neighbors`: counts are
threshold-capped, but the core flag is sufficient for component labeling.

## Claim Boundary

This is a bridge step, not final RT-DBSCAN parity with the IPDPS paper. It can
support a narrower claim if pod timing confirms it:

```text
RTDL can combine RT-core fixed-radius threshold summaries with a device-resident
partner component continuation without emitting all neighbor rows.
```

It cannot yet claim:

- full device-resident OptiX output handoff;
- paper reproduction;
- paper-level speedup;
- broad RT-core DBSCAN acceleration.
