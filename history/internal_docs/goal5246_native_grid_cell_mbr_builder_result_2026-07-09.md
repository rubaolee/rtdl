# Goal5246 Native Grid-Cell MBR Builder Result

Date: 2026-07-09

## Verdict

```text
completed_native_grid_cell_mbr_builder__new_best_single_workload_route
```

Goal5246 adds a generic native CUDA/Thrust backend for 3-D point-grid cell MBR
construction. Unlike Goal5245's exact branch-bound seed, this route **does**
improve the current Dragon -> scaled AsianDragon Level-B workload.

## What Changed

Generic system additions:

- Native CUDA/Thrust symbol:

```text
rtdl_cuda_point_grid_cell_mbrs_3d
```

- Python native binding:

```text
point_grid_cell_mbrs_3d_cuda(...)
```

- RTDL partner helper:

```text
point_grid_cell_mbrs_native_3d_cuda_columns(...)
```

- X-HD route CLI selector:

```text
--grid-cell-builder {numpy,native_cuda}
```

The helper preserves the same generic cell-column contract as
`point_grid_cell_mbrs_numpy_columns`:

```text
cell_ids
original_cell_ids
point_begin_offsets
point_counts
point_ids
point_row_indices
grid_shape
grid_lower_bounds
grid_upper_bounds
min_x/min_y/min_z
max_x/max_y/max_z
```

No X-HD, Hausdorff, paper, or author-specific semantics are encoded in the
native layer.

## POD Workload

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
direction = directed-a-to-b
preprocessing = translate_each_input_to_min_bound
grid_shape = 96x60x72
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
frontier_inline_nearest = true
frontier_row_order = native
tolerance = 1e-6
```

Evidence files:

```text
history/internal_docs/goal5246_numpy_repeat1_2026-07-09.json
history/internal_docs/goal5246_numpy_repeat2_2026-07-09.json
history/internal_docs/goal5246_numpy_repeat3_2026-07-09.json
history/internal_docs/goal5246_native_cuda_repeat1_2026-07-09.json
history/internal_docs/goal5246_native_cuda_repeat2_2026-07-09.json
history/internal_docs/goal5246_native_cuda_repeat3_2026-07-09.json
```

All six runs:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
```

## Performance Matrix

Same POD, three repeats each:

| Grid builder | direction_total values | median direction_total | median total_sec |
|---|---:|---:|---:|
| numpy | 2.3126s, 2.3229s, 2.3201s | 2.3201s | 3.0756s |
| native_cuda | 2.0793s, 2.0865s, 2.0756s | 2.0793s | 2.8358s |

Median improvement:

```text
direction_total: 2.3201s -> 2.0793s  (~10.4% faster)
total_sec:       3.0756s -> 2.8358s  (~7.8% faster)
```

## Phase Movement

| Phase | numpy median | native_cuda median | Interpretation |
|---|---:|---:|---|
| grid_cell_mbrs | 0.6170s | 0.4450s | native builder wins |
| initial_state_seed | 0.3465s | 0.2565s | downstream native seed also benefits from layout/cache effects |
| frontier_rows | 1.3140s | 1.3354s | still dominant and slightly higher |
| direction_total | 2.3201s | 2.0793s | new best route |

The remaining largest phase is still:

```text
frontier_rows ~= 1.33s
```

## Comparison To Recent Routes

```text
Goal5244 best route                         ~= 2.3042s
Goal5245 native exact seed + frontier skip  ~= 2.4508s
Goal5246 native grid builder route median   ~= 2.0793s
```

Goal5246 is therefore the new best same-source Dragon -> scaled AsianDragon
Level-B route.

## What This Proves

- The generic native CUDA/Thrust grid-cell MBR builder compiles and runs on POD.
- It preserves the generic point-grid cell-column contract.
- It improves the current representative X-HD route on the same POD and same
  workload.
- It remains a system feature: generic point-grid grouping and per-cell MBR
  reduction, not an X-HD-specific primitive.

## What This Does Not Prove

- It does not complete full X-HD paper reproduction.
- It does not prove exact paper byte-input identity.
- It does not reproduce Figures 5-11.
- It does not prove author internal `Running.AvgTime` parity.
- It does not establish a universal grid-builder speedup across all workloads.

## Recommendation

Adopt `--grid-cell-builder native_cuda` as the current best **experimental X-HD
Level-B route setting** for Dragon -> scaled AsianDragon, while keeping the
default API explicit until reviewed.

Next technical mountain:

```text
frontier_rows ~= 1.33s
```

The correct next attack is a stronger generic nearest traversal / prepared
spatial index strategy that reduces the OptiX frontier launch or moves more of
the nearest computation into a reusable prepared target-side structure.

## Verification

Local:

```text
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py src/rtdsl/__init__.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py tests/goal5246_native_grid_cell_mbr_builder_test.py
py -m unittest tests.goal5246_native_grid_cell_mbr_builder_test
```

POD:

```text
make build-optix
python3 -m unittest tests.goal5246_native_grid_cell_mbr_builder_test
```

POD test result:

```text
Ran 3 tests in 1.483s
OK
```

Additional POD native-vs-NumPy smoke:

```text
matched = true
contract = generic_point_grid_cell_mbr_columns
native_generic_symbol = rtdl_cuda_point_grid_cell_mbrs_3d
```
