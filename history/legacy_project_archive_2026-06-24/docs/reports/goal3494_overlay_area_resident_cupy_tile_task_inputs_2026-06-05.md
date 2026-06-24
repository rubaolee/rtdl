# Goal3494 - Overlay-Area Resident CuPy Tile-Task Inputs

## Status

Implemented with pod repeat timing on an NVIDIA RTX A5000.

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

## Pod Result

Artifact:

- `docs/reports/goal3494_overlay_area_resident_cupy_tile_task_inputs_pod_2026-06-05.json`

Source commit:

- `15ed0780`

Public-CDB active-shape workload:

- relation rows: `4,543`
- component-pair rows: `39,947`
- tile tasks: `54,232`
- triangle pairs processed per repeat: `9,653,005`
- executor repeats: `5`
- task status counts: `{"0": 54232}`

Correctness:

- observed total area: `26.083217672086707`
- exact Shapely/GEOS total area: `26.08321766231046`
- total absolute error: `9.776247367199176e-09`
- max relation absolute error: about `1.0414236140121602e-09`
- positive row count match: true

Resident-input timing:

- CuPy input preparation: `0.10114209912717342` seconds
- repeat times: `0.1847483618184924`, `0.029110463336110115`,
  `0.02901996672153473`, `0.02896842733025551`,
  `0.028768520802259445` seconds
- best repeat: `0.028768520802259445` seconds

Interpretation: after payload/task arrays are resident in CuPy, repeated scalar
exact-area executor calls are about `30ms` for the `9,653,005` triangle-pair
public-CDB workload. This is still partner residency/reuse, not true zero-copy.
