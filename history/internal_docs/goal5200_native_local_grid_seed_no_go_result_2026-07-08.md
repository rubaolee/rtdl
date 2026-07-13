# Goal5200 Native CUDA Local-Grid Seed No-Go Result

Date: 2026-07-08

## Status

`implemented_experimental_native_cuda_seed__no_go_keep_default_numba`

Goal5200 tested whether the generic local-grid nearest-state seed could move
from the existing Numba parallel CPU implementation into a native CUDA helper
and lower the full-public X-HD Level-B route wall time.

It did not. The native CUDA seed is correct and callable through an explicit
experimental executor, but it is slower than the current default on the
full-public Dragon/HappyBuddha route. The default route remains:

```text
initial_state = local-grid-cell
local_grid_seed_executor = auto  # Numba parallel
grid_shape = 32,32,32
max_inline_points = 512
frontier_row_order = native
frontier_inline_nearest = true
frontier_row_capacity = 0
```

## What Changed

Implemented a generic optional native CUDA executor for the existing
`seed_nearest_witness_from_local_grid_cell_numpy_columns` contract:

- C ABI:
  `rtdl_optix_seed_nearest_witness_local_grid_3d`
- Python wrapper:
  `seed_nearest_witness_local_grid_cell_3d_cuda`
- public partner executor selection:
  `executor="native_cuda"` on the existing local-grid seed helper
- X-HD route flag:
  `--local-grid-seed-executor native_cuda`

The default remains `auto`, which resolves to the existing Numba parallel path.

The implementation is generic. It consumes only:

- query point columns;
- target point columns;
- compact grid-cell spans;
- a dense encoded-cell lookup table;
- grid shape and bounds.

It does not encode Hausdorff, X-HD, author binary, paper, or output semantics.

## Validation

Local validation:

```text
py -m unittest \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5196_local_grid_dense_lookup_test \
  tests.goal5189_local_grid_seed_test

Ran 12 tests in 1.579s
OK
```

POD validation:

```text
python3 -m unittest \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5196_local_grid_dense_lookup_test \
  tests.goal5189_local_grid_seed_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 20 tests in 17.534s
OK
```

POD native build:

```text
make build-optix
exit code: 0
```

POD small actual native call:

```text
native_ids [10, 30]
auto_ids   [10, 30]
native_dist [0.1, 0.1]
auto_dist   [0.1, 0.1]
executor native_cuda rtdl_optix_seed_nearest_witness_local_grid_3d
```

## Full-Public Same-POD Performance Comparison

Both runs use the same public Stanford Graphics Dragon/HappyBuddha Level-B
candidate pair, the same Goal5186 author HDResult comparator, the same route
settings, and the same POD session. The only changed flag is
`--local-grid-seed-executor`.

Control, current default:

```text
artifact:
Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_goal5200_auto_local_grid_seed_control_graphics_dragon_happy_buddha_2026-07-08.json

matched: true
author_abs_diff: 2.3848857610975216e-09
route_wall: 2.2580383121967316 s
initial_state_seed: 0.5628510117530823 s
initial_seed_executor: numba_parallel
initial_seed_executor_requested: auto
frontier_rows: 0
frontier_rows_phase: 0.9319010525941849 s
nearest_continuation: 0.01634712517261505 s
max_nearest_reduction: 0.07195407897233963 s
```

Experimental native CUDA seed:

```text
artifact:
Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_goal5200_native_local_grid_seed_final2_graphics_dragon_happy_buddha_2026-07-08.json

matched: true
author_abs_diff: 2.3848857610975216e-09
route_wall: 2.4362636134028435 s
initial_state_seed: 0.9580570980906487 s
initial_seed_executor: native_cuda
initial_seed_executor_requested: native_cuda
frontier_rows: 0
frontier_rows_phase: 0.7188352569937706 s
nearest_continuation: 0.016512170433998108 s
max_nearest_reduction: 0.07220050692558289 s
```

Observed delta:

```text
route_wall: +0.1782253012061119 s slower
seed_phase: +0.3952060863375664 s slower
```

The native seed made the frontier phase somewhat faster in this single run, but
not enough to offset its own seed overhead. End-to-end route wall worsened.

## Interpretation

The existing Numba parallel seed is already efficient for this host-resident
grid-cell lookup. The new native CUDA seed still uploads host arrays into a
fresh CUDA kernel invocation and downloads the nearest-state columns back to
host for the rest of the current route. That transfer/kernel setup overhead is
larger than the saved CPU loop work in this regime.

This result does not prove that device-resident seed construction can never be
useful. It proves only that this host-to-native CUDA seed wrapper is not a win
for the current full-public Level-B route.

## Claim Boundary

Allowed claim:

```text
Goal5200 implemented and validated an explicit experimental generic native CUDA
local-grid seed executor, but the same-POD full-public comparison shows it is
slower than the existing Numba default. Keep the default route unchanged.
```

Not authorized:

- no X-HD performance improvement claim;
- no author performance ratio;
- no exact paper dataset reproduction claim;
- no full paper reproduction claim;
- no claim that native CUDA seed is the default route;
- no claim that device-resident seeding is solved.

## Next Recommendation

Do not continue optimizing this host-to-native CUDA seed wrapper for v2.14.5
unless a new design removes the host upload/download boundary or reuses a
device-resident target/grid representation across multiple operators.

The next substantial performance work should attack a larger remaining floor,
such as native inline-nearest execution structure, stronger generic spatial
indexing, or true device-resident pipeline state, rather than another
host-to-device wrapper around a seed phase.
