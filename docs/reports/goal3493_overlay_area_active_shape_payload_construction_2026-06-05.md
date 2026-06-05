# Goal3493 - Overlay-Area Active-Shape Payload Construction

## Status

Implemented locally. Pod timing is required to quantify the improvement.

## Purpose

Goal3492 showed that the CuPy tile-task executor processed the full supported
public-CDB scalar overlay-area stream quickly, but payload construction was the
dominant cost:

- CuPy tile-task executor: `0.48830951377749443` seconds
- payload construction/triangulation: `22.716640373691916` seconds

The problem was not the generic tile-task executor. The runner prepared every
left/right CDB shape before relation discovery told us which shapes were
actually active. The active stream used only `1,261` of `15,700` left shapes and
all `949` right shapes.

Goal3493 adds an active-shape-only mode:

- first discover active relation ordinals with RTDL/OptiX;
- build Shapely/GEOS oracle geometries only for active shape ordinals;
- prepare simple-polygon component payloads only for those active shapes;
- keep the same component-pair rows, tile-task planner, CuPy executor, and
  Shapely/GEOS correctness comparison.

## Changed

Updated:

- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`

Added CLI:

```bash
--active-shapes-only
```

The output now records:

- `active_shapes_only`
- `prepared_left_shape_count`
- `prepared_right_shape_count`

## Boundary

This is a payload-construction optimization for the same app-agnostic prepared
component payload contract. It does not add app-specific native engine logic and
does not authorize release, speedup, RT-core, true-zero-copy, RayJoin-paper, or
full-overlay claims.

## Expected Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py \
  --active-shapes-only \
  --max-triangle-pairs-per-task 512 \
  --progress-every 500 \
  --output docs/reports/goal3493_overlay_area_active_shape_payload_construction_pod_2026-06-05.json
```

The expected success criteria are unchanged from Goal3492: all tile tasks status
zero, `9,653,005` triangle pairs processed, scalar total area within tolerance
of the Shapely/GEOS oracle, and all claim-boundary flags false.
