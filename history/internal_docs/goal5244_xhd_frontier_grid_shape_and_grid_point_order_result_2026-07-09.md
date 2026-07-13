# Goal5244 - X-HD Frontier Grid Shape and Grid Point Order Result

Date: 2026-07-09

## Verdict

```text
completed_grid_shape_tuning_no_go__input_stable_order_small_generic_option
```

Goal5244 tested whether the best grid shape changed after Goal5243 removed the
runtime CUDA module compile/load cost from the generic native CUDA local-grid
seed path. It also added and tested an optional generic grid-cell point ordering
mode.

The result is bounded:

- Grid-shape tuning is a no-go for this workload. The existing `96x60x72` shape
  remains best among the tested shapes.
- Finer grids reduce inline point evaluations, but increase frontier OptiX
  launch cost enough to lose overall.
- `cell_point_order="input-stable"` is a valid generic option and preserves
  correctness. It was slightly faster in one same-POD comparison, but the delta
  is small and must not be presented as a major performance result.
- The remaining dominant cost is still the exact frontier / inline-nearest
  phase, especially the native OptiX frontier launch.

## Scope

```text
input1 = dragon.ply
input2 = asian_dragon_scaled_1e-3.ply
preprocessing = translate_each_input_to_min_bound
direction = directed-a-to-b
max_inline_points = 1024
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
frontier_inline_nearest = true
frontier_row_order = native
frontier_row_capacity = 5000000
author HDResult = 0.06536787003278732
tolerance = 1e-6
```

All Goal5244 runs reported:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = true
frontier_rows = 0
```

This remains a single Level-B same-source public workload checkpoint. It is not
full X-HD paper reproduction and it is not author internal `Running.AvgTime`
parity.

## Implementation Changes

Changed files:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5244_grid_cell_input_stable_order_test.py
```

New generic option:

```python
point_grid_cell_mbrs_numpy_columns(..., cell_point_order="point-id")
point_grid_cell_mbrs_numpy_columns(..., cell_point_order="input-stable")
```

Contracts:

```text
point-id      = cell_id_then_point_id
input-stable  = cell_id_then_input_order
```

The X-HD route runner now exposes:

```text
--grid-cell-point-order {point-id,input-stable}
```

This is app-neutral. It controls generic point ordering inside encoded grid
cells before cell-MBR reduction. It does not encode X-HD, paper, author, or
Hausdorff semantics.

## Local Verification

```text
py -m py_compile src/rtdsl/partner_continuations.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py

py -m unittest tests.goal5138_generic_grid_cell_candidate_api_test tests.goal5167_grid_cell_mbr_reduceat_test tests.goal5244_grid_cell_input_stable_order_test tests.goal5238_xhd_author_ply_loader_translation_contract_test
```

Observed:

```text
Ran 10 tests OK
```

## POD Grid-Shape Sweep

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_107x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x60x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x72x72_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x80x80_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_128x80x96_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_160x80x96_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_160x96x96_precompiled_inline1024_pod_2026-07-09.json
```

| Grid shape | Direction total (s) | Grid MBR (s) | Seed outer (s) | Seed native (s) | Frontier phase (s) | Frontier OptiX launch (s) | Inline evals | Seed total evals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 96x60x72 | 2.315611 | 0.622934 | 0.347830 | 0.203832 | 1.309741 | 1.164678 | 1,229,829,134 | 43,621,949 |
| 107x60x72 | 2.444478 | 0.612945 | 0.352125 | 0.209491 | 1.443721 | 1.297938 | 1,177,465,380 | 36,269,455 |
| 128x60x72 | 2.567792 | 0.622550 | 0.356844 | 0.218102 | 1.552577 | 1.406279 | 1,085,055,220 | 30,932,620 |
| 128x72x72 | 2.603874 | 0.631557 | 0.380843 | 0.239353 | 1.554834 | 1.409615 | 947,353,191 | 31,826,031 |
| 128x80x80 | 2.774917 | 0.634226 | 0.440119 | 0.287241 | 1.664743 | 1.516077 | 838,760,624 | 27,255,677 |
| 128x80x96 | 3.037783 | 0.624197 | 0.492357 | 0.348233 | 1.886263 | 1.737149 | 897,013,697 | 19,293,451 |
| 160x80x96 | 3.256009 | 0.635085 | 0.536188 | 0.383990 | 2.049488 | 1.903906 | 799,407,108 | 17,157,320 |
| 160x96x96 | 3.436825 | 0.639571 | 0.609663 | 0.449851 | 2.152712 | 2.005784 | 737,634,205 | 15,001,056 |

Interpretation:

- Finer grids reduce inline point evaluations from about 1.23B to about 0.74B.
- That reduction does not translate into lower route time because frontier
  OptiX launch time rises from about 1.16s to about 2.01s.
- The best measured shape remains `96x60x72`.
- Further manual grid-shape tuning is not a promising next step for this
  workload.

## POD Grid Point Order Comparison

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_input_stable_precompiled_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5244_grid_96x60x72_point_id_precompiled_inline1024_pod_2026-07-09.json
```

| Point order | Direction total (s) | Route wall (s) | Total wall (s) | Grid MBR (s) | Seed outer (s) | Seed native (s) | Frontier phase (s) | Frontier OptiX launch (s) | Matched |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| input-stable | 2.304212 | 2.304286 | 3.048796 | 0.604916 | 0.343141 | 0.204393 | 1.319580 | 1.174186 | true |
| point-id | 2.312657 | 2.312731 | 3.060299 | 0.609525 | 0.351496 | 0.206008 | 1.315612 | 1.169706 | true |

The `input-stable` run was slightly faster in this one same-POD comparison:

```text
direction_total delta ~= 0.00845s
route_wall delta ~= 0.00844s
total_wall delta ~= 0.01150s
```

This is too small and too single-run to promote as a major performance win. It
is best treated as a valid generic option, not as a new headline route.

## Current Best Label

After Goal5244, the conservative current best remains:

```text
grid_shape = 96,60,72
max_inline_points = 1024
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
frontier_inline_nearest = true
grid_cell_point_order = point-id by default, input-stable optional
matched = true
per_source_witness_exact = true
frontier_rows = 0
```

The best single Goal5244 timing came from optional `input-stable`:

```text
direction_total = 2.3042124956846237s
route_wall = 2.304285980761051s
total_wall = 3.048795871436596s
```

Stable public summary should remain approximate:

```text
RTDL direction_total ~= 2.30s
RTDL route_wall ~= 2.30s
RTDL total_wall ~= 3.05s
```

with the same denominator cautions from Goal5243:

```text
author process wall ~= 2.66s
author internal Running.AvgTime ~= 83.5ms
```

No author internal parity claim is authorized.

## What This Proves

- The current grid shape is near the practical optimum for this route on the
  tested workload.
- The remaining frontier cost is not simply too many point evaluations; it is
  heavily tied to native frontier launch and traversal structure.
- The grid-cell point ordering is now a generic configurable system behavior.

## What This Does Not Prove

This does not prove:

- full X-HD paper reproduction;
- exact paper byte-input identity;
- Figure 5-11 reproduction;
- author internal `Running.AvgTime` parity;
- a universal grid shape for all datasets;
- a major speedup from `input-stable` ordering;
- that further app-level grid tuning can close the remaining gap.

## Next Recommended Work

The next real technical mountain is not more grid-shape tuning. It is the
frontier/inline-nearest phase:

```text
frontier phase ~= 1.31s
frontier OptiX launch ~= 1.17s
```

Two plausible next system-level directions:

1. Build a generic native CUDA exact grid-nearest / branch-bound kernel that
   bypasses the current OptiX cell-MBR frontier path for dense grid workloads.
2. Build a generic prepared target-grid workspace so repeated route calls can
   reuse target coordinate/grid state where the regime permits.

Either direction must remain a generic RTDL system feature, not an X-HD-only
primitive.
