# Goal3498 Overlay Area Device Tile-Task Planner

Date: 2026-06-05

## Verdict

`pending-pod-evidence`.

Goal3498 adds an opt-in CuPy planner for prepared simple-polygon overlay-area
tile tasks:

`prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(...)`

The planner consumes generic relation row ordinals, left/right shape ordinals,
and prepared component tables. It performs component-pair and tile-task expansion on device,
then returns the same
`PreparedOverlayAreaCupyTileTaskInputs` object consumed by the existing
resident CuPy tile-task executor.

## Why This Exists

Goals3495 and 3497 made the front of the overlay-area continuation more
device-first, but still left Python host code expanding component pairs and
tile tasks. Goal3498 moves that expansion step to a generic CuPy continuation
once CPU-owned prepared payloads already exist.

This does not solve Shapely geometry construction or triangulation. It targets
the smaller but important planning bridge between prepared payloads and the
resident tile-task executor.

## Boundary

This is still not native prepared-payload construction and not full
device-resident overlay planning from raw relation columns. The runner copies relation ordinals into CuPy-owned arrays
before the native relation-column owner is released. This goal does not authorize release, public speedup claims,
RT-core speedup claims, true-zero-copy wording, full overlay completion claims,
or app-specific native-engine behavior.
