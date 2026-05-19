# Goal2423 Prepared OptiX+CuPy Radius Graph Components

Date: 2026-05-19

Status: implementation complete; pod smoke complete

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

## Pod Smoke

Artifacts:

```text
docs/reports/goal2423_prepared_optix_cupy_radius_graph_components_pod_smoke/
```

Environment:

```text
root@69.30.85.177 -p 22055
commit 88c51e87c9f2b58cbe1063077e38edcbe6a0125b
NVIDIA RTX A5000, driver 570.211.01
Python 3.12.3
CuPy 14.0.1
```

The pod focused tests passed:

```text
6 tests OK
```

The direct composite API smoke ran the prepared object twice and recorded:

```text
first run: prepared_composite_reused = false
second run: prepared_composite_reused = true
```

The repeat probe smoke for `clustered3d / 32768` reported:

| Mode | Warm-tail app sec |
| --- | ---: |
| `partner_cupy_grid_components_3d` | 0.184822 |
| `optix_rt_core_flags_cupy_prepared_grid_components_3d` | 0.181392 |

This smoke is not a new performance claim beyond Goals 2418 and 2420. It only
confirms that the public composite wrapper preserves the established prepared
path and reuse metadata.
