# Goal5241 X-HD Grid Shape + Native Seed Performance Result

Date: 2026-07-09

## Verdict

`implemented__grid_shape_native_seed_cuts_candidate_work__route_near_author_process_wall__review_pending`

Goal5241 attacks the post-Goal5240 hard problem:

```text
candidate_distance_evaluations = 6,417,800,660
```

Goal5240 parallelized the same candidate work. Goal5241 reduces the candidate
work by changing the generic grid shape and using the existing generic native
CUDA local-grid seed executor.

Best current route:

```text
grid_shape = 96,60,72
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto  # resolves to numba_parallel
global_bound_early_break = false
translate_each_input_to_min_bound = true
```

Three same-POD repeats all matched the author HDResult:

```text
RTDL route distance = 0.06536787240753439
author scaled HDResult = 0.06536787003278732
author_abs_diff = 2.3747470656587666e-09
matched = true
```

Median timing for the best route:

```text
direction_total = 3.0695155784487724s
route_wall = 3.322203427553177s
total_wall = 3.8200959116220474s
```

This is a real route performance step. It still does not prove author internal
performance parity, Figure reproduction, exact paper input byte identity, or
full X-HD paper reproduction.

## Evidence Artifacts

### Seed strategy diagnostics, source limit 8192

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_local-grid-cell_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_nearest-cell-mbr_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid-cell-budget_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid-branch-bound_pod_2026-07-09.json
```

### Grid-shape diagnostics, source limit 8192

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_64x64x64_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_96x64x72_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_107x60x72_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_128x128x128_local_grid_pod_2026-07-09.json
```

### All-source grid/native-seed matrix

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_80x64x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep3_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x64x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x72x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_107x60x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_107x64x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_128x128x128_native_seed_auto_pod_2026-07-09.json
```

Context artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5240_dragon_asian_scaled_all_source_optix_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
```

## Fixed Correctness Contract

All all-source Goal5241 runs keep the exact contract:

```text
source = Dragon, 437,645 points
target = scaled AsianDragon, 3,609,600 points
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = false
per_source_witness_exact = true
author HDResult = 0.06536787003278732
author_tolerance = 1e-6
full_pairwise_rows_materialized = false
```

The winning route keeps:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
distance/source/target = 0.06536787240753439 / 49577 / 1803033
```

## Seed Strategy Diagnostic

At `source_limit=8192`, stronger seed strategies did reduce continuation work,
but their seed cost made them worse than local-grid-cell.

```text
local-grid-cell:
  direction_total = 1.398508220911026s
  seed = 0.20753031969070435s
  nearest = 0.23332529515028s
  total_candidate_distance_evaluations = 107,935,016

nearest-cell-mbr:
  direction_total = 2.386744685471058s
  seed = 1.2960334345698357s
  nearest = 0.1276012361049652s
  total_candidate_distance_evaluations = 69,741,645

grid-cell-budget:
  direction_total = 7.787977576255798s
  seed = 6.486178733408451s
  nearest = 0.33332086354494095s
  total_candidate_distance_evaluations = 186,861,929

grid-branch-bound:
  direction_total = 6.964956633746624s
  seed = 5.88697100430727s
  nearest = 0.11609915643930435s
  total_candidate_distance_evaluations = 189,382,007
```

Conclusion:

```text
Do not replace local-grid-cell with nearest-cell-mbr, grid-cell-budget, or
grid-branch-bound for this workload. They are correct but not faster.
```

## Grid Shape Diagnostic

With local-grid-cell and `frontier_nearest_executor=auto`, finer grids greatly
reduce continuation candidate work.

At `source_limit=8192`:

```text
32x32x32:
  frontier_rows = 55,331
  total_candidate_distance_evaluations = 107,935,016
  direction_total = 1.398508220911026s

64x64x64:
  frontier_rows = 37,445
  total_candidate_distance_evaluations = 25,665,253
  direction_total = 1.2797563821077347s

96x64x72:
  frontier_rows = 2,425
  total_candidate_distance_evaluations = 2,205,653
  direction_total = 1.3381715938448906s

107x60x72:
  frontier_rows = 1,014
  total_candidate_distance_evaluations = 1,228,373
  direction_total = 1.3595731928944588s

128x128x128:
  frontier_rows = 0
  total_candidate_distance_evaluations = 230,681
  direction_total = 2.225139908492565s
```

Interpretation:

```text
Finer grids reduce continuation work dramatically, but overly fine grids
increase seed/frontier overhead. The optimum is a balance, not simply the
smallest candidate count.
```

## All-Source Grid + Native Seed Matrix

All all-source runs below matched the author HDResult with:

```text
author_abs_diff = 2.3747470656587666e-09
```

Sorted by `direction_total`:

```text
96x60x72:
  direction_total = 3.0628106743097305s
  seed = 0.8459959700703621s
  frontier = 1.2888829335570335s
  nearest = 0.2795383110642433s
  frontier_rows = 180,821
  total_candidate_distance_evaluations = 145,373,825

96x64x72:
  direction_total = 3.1644412502646446s
  seed = 0.8192519620060921s
  frontier = 1.4301046952605247s
  nearest = 0.27189093828201294s
  frontier_rows = 119,838
  total_candidate_distance_evaluations = 112,659,026

107x60x72:
  direction_total = 3.1934417337179184s
  seed = 0.8448984324932098s
  frontier = 1.4475979432463646s
  nearest = 0.24508855491876602s
  frontier_rows = 45,746
  total_candidate_distance_evaluations = 61,326,336

96x72x72:
  direction_total = 3.2014861032366753s
  seed = 0.8361783549189568s
  frontier = 1.461994469165802s
  nearest = 0.24780870229005814s
  frontier_rows = 53,796
  total_candidate_distance_evaluations = 69,902,081

107x64x72:
  direction_total = 3.290824554860592s
  seed = 0.9248110353946686s
  frontier = 1.4644709527492523s
  nearest = 0.24940918385982513s
  frontier_rows = 63,909
  total_candidate_distance_evaluations = 72,236,940

80x64x72:
  direction_total = 3.672826051712036s
  seed = 0.831386037170887s
  frontier = 1.403795063495636s
  nearest = 0.7868180423974991s
  frontier_rows = 662,306
  total_candidate_distance_evaluations = 420,324,644

128x128x128:
  direction_total = 4.790914997458458s
  seed = 1.368628941476345s
  frontier = 2.750627875328064s
  nearest = 0.0008369758725166321s
  frontier_rows = 0
  total_candidate_distance_evaluations = 12,134,614
```

## Best Route Stability

The best route, `96x60x72 + native_cuda seed + auto continuation`, was repeated
three times on the same POD.

```text
rep1:
  direction_total = 3.0628106743097305s
  route_wall = 3.3162371069192886s
  total = 3.811066411435604s

rep2:
  direction_total = 3.082673095166683s
  route_wall = 3.335612513124943s
  total = 3.835918143391609s

rep3:
  direction_total = 3.0695155784487724s
  route_wall = 3.322203427553177s
  total = 3.8200959116220474s
```

Median:

```text
direction_total = 3.0695155784487724s
route_wall = 3.322203427553177s
total = 3.8200959116220474s
seed = 0.8296843618154526s
frontier = 1.2888829335570335s
nearest = 0.3105670288205147s
```

Work counters:

```text
frontier_rows = 180,821
total_candidate_distance_evaluations = 145,373,825
initial_grid_cell_probes = 2,422,467,460
```

## Improvement

Compared with Goal5239:

```text
route direction:
  30.49027620255947s -> 3.0695155784487724s
  improvement = 9.93325344775354x

full app / total wall:
  31.252301812171936s -> 3.8200959116220474s
  improvement = 8.181025433704864x
```

Compared with Goal5240 `32x32x32 + auto`:

```text
direction_total:
  9.171282961964607s -> 3.0695155784487724s

total_candidate_distance_evaluations:
  6,417,800,660 -> 145,373,825
  reduction = 44.14687898595225x

frontier_rows:
  3,306,122 -> 180,821
  reduction = 18.283949320045792x
```

## Denominator-Explicit Author Comparison

Author numbers from Goal5239:

```text
author process wall = 2.6587867364287376s
author internal Running.AvgTime = 83.49680000000001ms
```

Best RTDL route:

```text
direction_total median = 3.0695155784487724s
total wall median = 3.8200959116220474s
```

Diagnostic ratios:

```text
RTDL direction_total / author process wall
  = 3.0695155784487724 / 2.6587867364287376
  = 1.1544797995237943x slower

RTDL total wall / author process wall
  = 3.8200959116220474 / 2.6587867364287376
  = 1.4367816189549567x slower

RTDL direction_total / author internal Running.AvgTime
  = 3.0695155784487724 / 0.0834968
  = 36.76207445613212x slower

RTDL total wall / author internal Running.AvgTime
  = 3.8200959116220474 / 0.0834968
  = 45.751404983449035x slower
```

These are diagnostic denominator-labelled ratios only. The process-wall ratio
is now close, but author internal timing is still far ahead. Do not convert
this into a Figure 6 or author-parity claim.

## Interpretation

Goal5241 changes the bottleneck.

Before:

```text
Goal5239:
  nearest_continuation = 28.124958105385303s

Goal5240:
  nearest_continuation = 6.6945535987615585s
  candidate_distance_evaluations = 6,417,800,660
```

After:

```text
Goal5241 best route:
  nearest_continuation median ~= 0.31s
  candidate_distance_evaluations = 145,373,825
  direction_total median ~= 3.07s
```

The current dominant phases are now:

```text
frontier_rows ~= 1.29s
local-grid native CUDA seed ~= 0.83s
grid cell MBR construction ~= 0.61s
nearest continuation ~= 0.31s
```

The original continuation mountain is no longer the dominant cost for this
workload under the best route.

## Genericity Boundary

This work uses existing generic RTDL mechanisms:

```text
generic point-grid cell MBRs
generic local-grid-cell nearest-state seed
generic native CUDA local-grid seed executor
generic native OptiX cell-MBR frontier rows
generic nearest-continuation executor
generic max-nearest reduction
```

It does not add:

```text
X-HD-specific native primitive
Dragon/AsianDragon-specific core logic
paper-log shortcut
author-output hard-code
```

The grid shape is a route parameter. The particular `96x60x72` setting is
workload-tuned for this public candidate and must not be generalized without
more workload evidence.

## Claim Boundary

Allowed:

```text
For Dragon -> scaled AsianDragon, under the same Level-B same-source exact
route contract, RTDL now matches the author rerun HDResult with median route
direction time about 3.07s and median total wall about 3.82s using a generic
96x60x72 grid, native CUDA local-grid seed, and auto/numba_parallel nearest
continuation.
```

Not allowed:

```text
RTDL matches author internal performance.
RTDL reproduces Figure 6 performance.
Exact paper input byte identity is proved.
Full X-HD paper reproduction is complete.
96x60x72 is a universal X-HD grid.
The author fused RT-core algorithm is reproduced.
This result applies to all paper workloads.
```

## Next Recommended Work

Goal5241 exits as:

```text
grid_shape_native_seed_route_win__next_bottleneck_frontier_and_seed
```

Next technical targets:

1. Review Goals5240-5241 together, because together they move the Dragon ->
   scaled AsianDragon route from about 31s to about 3.07s.
2. Decide whether to:
   - attack the new dominant phase `frontier_rows ~= 1.29s`;
   - attack native CUDA seed grid probes;
   - broaden to another paper workload to test whether the tuned route holds.
3. Do not claim full X-HD paper reproduction or author internal parity.

Recommended Goal5242:

```text
Run the best current route on at least one additional Level-B paper-relevant
workload, or, if staying on Dragon -> AsianDragon, decompose the native OptiX
frontier phase and native CUDA seed phase to see which generic primitive is the
next real bottleneck.
```
