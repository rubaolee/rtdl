# Goal3492 - Public-CDB Overlay-Area Tile-Task Executor

## Status

Implemented locally. Pod execution is required for the full public-CDB evidence.

## Purpose

Goal3491 proved the CuPy tile-task executor on small fixtures. Goal3492 moves
that same execution shape onto the public-CDB active relation stream used by the
RayJoin benchmark lane.

The runner:

- discovers active relation row ordinals with the existing RTDL/OptiX relation
  producer;
- builds Shapely/GEOS oracle geometries for correctness comparison;
- lowers supported no-hole simple polygon and multipolygon inputs into prepared
  component payloads;
- expands each active relation row into component-pair rows plus relation-row
  owners;
- plans bounded tile tasks with `max_triangle_pairs_per_task`;
- runs `evaluate_prepared_overlay_area_tile_tasks_cupy(...)`;
- compares per-relation scalar areas against the Shapely/GEOS oracle.

## Added

- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `tests/goal3492_overlay_area_public_cdb_tile_task_executor_test.py`

## Boundary

This is still partner-backed public-CDB evidence, not a release authorization
and not the final native runtime path. It does not authorize public speedup
wording, broad RT-core speedup wording, true-zero-copy wording, automatic
partner selection, paper-reproduction claims, full overlay-geometry output
claims, or app-specific native engine behavior.

The goal is scalar exact overlay area over the supported prepared stream. Full
overlay geometry output remains a later streamed component/vertex contract.

## Expected Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py \
  --max-triangle-pairs-per-task 512 \
  --progress-every 500 \
  --output docs/reports/goal3492_overlay_area_public_cdb_tile_task_executor_pod_2026-06-05.json
```

The command prints phase progress for CDB loading, Shapely geometry building,
RTDL/OptiX relation discovery, oracle-area construction, task planning, and
CuPy execution.

## Local Validation

Local validation checks the script/report/gap scaffolding and Python syntax.
CUDA/CuPy public-CDB execution is intentionally left to the pod.
