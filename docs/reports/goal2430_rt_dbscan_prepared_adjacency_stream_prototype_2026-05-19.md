# Goal2430 RT-DBSCAN Prepared Adjacency Stream Prototype

Date: 2026-05-19

Status: local wiring complete; pod performance evidence pending

## Purpose

Goal2428 scoped the remaining RT-DBSCAN weakness as a generic continuation
problem: counts and core flags alone cannot label connected components without
connectivity information.

Goal2430 adds the first partner-side prototype for that missing contract:

```text
prepared fixed-radius directed adjacency stream
  -> grouped union/find component continuation
```

This is deliberately partner-side CuPy work first. It lets RTDL test the stream
shape, metadata, app boundary, and correctness before adding any native OptiX
edge-stream writer.

## New Public Prototype

The new functions are:

```python
rt.prepare_radius_graph_adjacency_3d_cupy_partner_columns(...)
rt.radius_graph_components_3d_cupy_prepared_adjacency_partner_columns(...)
```

The RT-DBSCAN benchmark app exposes:

```text
partner_cupy_prepared_adjacency_components_3d
```

The prototype builds:

- `edge_offsets`: one offset per point plus a final end offset;
- `neighbor_indices`: a directed neighbor-index stream;
- exact `neighbor_counts`;
- component labels from a device-side union/find continuation over that stream.

## Boundary

This does not claim RT-core acceleration. It does not add native DBSCAN ABI.
It is a generic fixed-radius graph adjacency contract used by a DBSCAN-style
benchmark.

The next evidence step is pod validation against:

- `partner_cupy_prepared_grid_components_3d`;
- `optix_rt_core_flags_cupy_prepared_grid_components_3d`;
- the negative microcell continuation.

If the adjacency stream proves useful, the native follow-up should be a generic
prepared fixed-radius adjacency writer, not a DBSCAN-specific engine path.
