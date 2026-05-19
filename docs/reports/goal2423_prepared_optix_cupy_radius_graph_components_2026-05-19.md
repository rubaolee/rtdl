# Goal2423 Prepared OptiX+CuPy Radius Graph Components

Date: 2026-05-19

Status: local implementation complete; pod smoke required

## Purpose

Goals 2418 and 2420 proved a useful RT-DBSCAN bridge:

```text
prepared OptiX RT count-threshold device columns
  -> prepared CuPy radius-grid component continuation
```

Before attempting a larger native edge-stream/union primitive, Goal2423 turns
that bridge into a reusable generic Python runtime contract:

```python
prepare_optix_cupy_radius_graph_components_3d(...)
radius_graph_components_3d_optix_cupy_prepared_partner_columns(...)
```

## Contract

The contract is:

```text
prepared_host_point_rows_self_radius_graph_3d
  -> generic_prepared_optix_cupy_radius_graph_component_labels_3d
```

It prepares:

- an OptiX fixed-radius count-threshold 3-D search scene;
- CuPy point columns;
- a CuPy radius-grid component continuation;
- reusable output columns for threshold flags and neighbor counts.

Each `run` returns the same component-column schema as the lower-level partner
continuations:

```text
point_ids
component_labels
is_core
neighbor_counts
```

## Boundary

This is a generic fixed-radius graph-components composition. It does not add a native DBSCAN ABI, does not hide dispatch, and does not authorize broad DBSCAN or paper-reproduction claims.

The deeper next primitive remains:

```text
device-resident radius-graph edge stream or grouped union continuation
```

Goal2423 is the cleaner baseline users and future benchmarks should call while
that larger primitive is designed.
