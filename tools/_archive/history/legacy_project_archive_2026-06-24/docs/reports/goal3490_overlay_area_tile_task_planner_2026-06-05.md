# Goal3490 - Overlay-Area Component/Tile Task Planner

## Status

Implemented locally.

Goal3490 responds to Goal3489's workload-sizing result: the supported
public-CDB scalar overlay target contains `9,653,005` triangle pairs, with a
long-tail relation row containing `318,096` triangle pairs. A one-thread per
relation-row execution shape is therefore too imbalanced.

## What Changed

Updated module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

Added:

- `PreparedOverlayAreaTileTask`
- `plan_prepared_overlay_area_tile_tasks(...)`
- `summarize_prepared_overlay_area_tile_tasks(...)`

The planner splits prepared component-pair rows into bounded `component/tile tasks`.
Each task records:

- task ordinal;
- relation-row owner;
- component-pair row owner;
- pair offset/count inside the component-pair product;
- left/right triangle ranges.

This is the missing bridge between Goal3489's workload sizing and a balanced
GPU/native continuation: large relation rows can be decomposed into many tile
tasks, then the runtime can reduce by relation id.

## Boundary

This is task-planning metadata and CPU-side scaffolding. It does not execute a
runtime kernel and does not authorize release packaging, public speedup wording,
RT-core speedup wording, true-zero-copy wording, paper reproduction claims,
hidden dispatch, automatic partner selection, full overlay completion claims,
or app-specific native engine behavior.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3490_overlay_area_tile_task_planner_test`
