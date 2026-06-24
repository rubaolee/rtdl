# Goal3498 Overlay Area Device Tile-Task Planner

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

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

## Pod Evidence

Artifact:
`docs/reports/goal3498_overlay_area_device_tile_task_planner_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `7d69a9f9204f4788adfe961e0149e597fa45e97d`

Command shape:

```text
--active-shapes-only --device-active-shape-ordinals --bounds-positive-filter --device-tile-task-planner --device-planner-repeats 5 --resident-cupy-inputs --executor-repeats 5
```

Measured result:

- Relation rows: 4,543
- Bounds-positive candidate rows: 2,274
- Supported candidate rows: 2,271
- Component-pair rows: 24,389
- Tile tasks: 36,414
- Planned/processed triangle pairs: 7,655,567
- Exact total area: 26.08321766231046
- Observed total area: 26.083217671827335
- Total absolute error: 9.516874399650987e-09
- Max relation absolute error: 1.0414238360567651e-09
- Positive row count match: true

Timing:

- Device tile-task planning repeats:
  `[0.1280s, 0.0506s, 0.0440s, 0.0523s, 0.0415s]`
- Device tile-task planning best repeat: 0.0415s
- Previous Goal3497 host planning: about 0.2113s
- CuPy tile-task input preparation: 0.0s, because the planner returns resident
  inputs directly
- CuPy tile-task executor best repeat: 0.0251s

The result is a steady-state planning win after CuPy RawKernel warmup. It is
not a first-use latency win; cold planner launch/JIT is visible in the first
repeat. The dominant total-path cost remains CPU-owned payload construction
at about 6.89s.

## Boundary

This is still not native prepared-payload construction and not full
device-resident overlay planning from raw relation columns. The runner copies relation ordinals into CuPy-owned arrays
before the native relation-column owner is released. This goal does not authorize release, public speedup claims,
RT-core speedup claims, true-zero-copy wording, full overlay completion claims,
or app-specific native-engine behavior.
