# Goal3494 - Overlay-Area Resident CuPy Tile-Task Inputs

## Status

Implemented locally. Pod repeat timing is required.

## Purpose

Goals3492-3493 showed that the scalar exact-area tile-task executor is no
longer the main bottleneck. The remaining systems problem is repeated payload
packing and preparation:

- Goal3493 active-shape payload build: `7.8638s`
- Goal3493 one-shot CuPy tile-task executor: `0.2811s`

Goal3494 separates resident CuPy input preparation from executor replay.

## Added

Updated:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`

New API:

- `PreparedOverlayAreaCupyTileTaskInputs`
- `prepare_overlay_area_tile_task_cupy_inputs(...)`
- `evaluate_prepared_overlay_area_tile_task_cupy_inputs(...)`

The existing `evaluate_prepared_overlay_area_tile_tasks_cupy(...)` remains as a
one-shot compatibility wrapper.

Runner flags:

```bash
--resident-cupy-inputs
--executor-repeats N
```

These flags prepare CuPy payload/task columns once, then replay the tile-task
executor over the resident inputs. The artifact records both
`cupy_tile_task_input_prepare` and per-repeat executor times.

## Boundary

This is resident partner input reuse, not true zero-copy and not a public
speedup claim. Host-to-CuPy packing still occurs during input preparation. The
important engineering distinction is that repeated executor calls do not
rebuild those partner arrays.

No app-specific native engine logic is added.

## Expected Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py \
  --active-shapes-only \
  --resident-cupy-inputs \
  --executor-repeats 5 \
  --max-triangle-pairs-per-task 512 \
  --progress-every 1000 \
  --output docs/reports/goal3494_overlay_area_resident_cupy_tile_task_inputs_pod_2026-06-05.json
```

The expected correctness bars are unchanged: all task statuses zero, exact total
area within tolerance, positive row count match, and all claim-boundary flags
false.
