# Goal3491 - Overlay-Area CuPy Tile-Task Executor

## Status

Implemented with pod validation on an NVIDIA RTX A5000.

## Purpose

Goal3490 split prepared simple-polygon overlay-area work into bounded
relation-owner tile tasks. Goal3491 executes that task plan with CuPy:

- one GPU thread per tile task;
- one tile task owns a bounded slice of a component-pair triangle product;
- each task writes a partial area and status;
- CuPy then performs `cupy_add_at_by_relation_row_ordinal` to reduce by relation id.

This is the first executable shape for the public-CDB scalar exact-area path
that does not require one thread to own an entire long-tail relation row.

## What Changed

Updated module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

Added public exports:

- `PreparedOverlayAreaCupyTileTaskResult`
- `evaluate_prepared_overlay_area_tile_tasks_cupy(...)`

The executor consumes `PreparedOverlayAreaTileTask` rows from
`plan_prepared_overlay_area_tile_tasks(...)`. It validates relation ids, task
pair ranges, and triangle ranges before importing CuPy or launching the kernel,
so malformed metadata fails closed on non-CUDA development hosts too.

## Boundary

This is still a partner-backed prototype, not the final native runtime path. It
does not authorize release packaging, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, automatic partner selection,
paper-reproduction claims, full overlay completion claims, or app-specific
native engine behavior.

The executor proves the task-stream execution shape on small fixtures. It does
not yet prove the full public-CDB stream, accepted performance, or integration
with the device-resident relation producer.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3491_overlay_area_tile_task_cupy_executor_test tests.goal3490_overlay_area_tile_task_planner_test tests.goal3486_overlay_area_cupy_tiled_prototype_test`
- Result: `18` tests passed, `3` CUDA/CuPy tests skipped on Windows.

Pod validation:

- Source commit: `fee479b5`
- GPU: NVIDIA RTX A5000
- CuPy: `14.1.1`
- Command: `PYTHONPATH=src:. python3 -m unittest tests.goal3491_overlay_area_tile_task_cupy_executor_test tests.goal3490_overlay_area_tile_task_planner_test tests.goal3486_overlay_area_cupy_tiled_prototype_test`
- Result: `18` tests passed.

Pod artifact:

- `docs/reports/goal3491_overlay_area_tile_task_cupy_executor_pod_2026-06-05.json`

The artifact records:

- a concave/simple fixture whose relation total is `1.75`;
- a two-component-pair fixture where two component rows reduce into one
  relation total of `2.0`;
- zero absolute area error for both fixtures;
- task status counts of `{"0": 3}` and `{"0": 4}`;
- host-side fail-closed validation for bad relation counts and malformed task
  ranges;
- gap-matrix wording and non-authorizing claim flags.

## Next Work

Run this executor on the pod and capture a pod artifact for the small fixtures.
After that, the next substantive step is a public-CDB run over the supported
prepared stream from Goal3488/Goal3489.
