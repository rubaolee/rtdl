# Goal5239 Dragon -> AsianDragon Scaled Same-POD Performance Matrix Result

Date: 2026-07-09

## Verdict

`implemented__same_pod_same_input_performance_matrix__rtdl_correct_but_slower__review_pending`

Goal5239 builds a denominator-explicit performance matrix for the
Dragon -> scaled AsianDragon all-source route.

This is the first performance matrix for the same scaled-public all-source
input after Goal5237 established RTDL route correctness.

## Input / Correctness Contract

```text
source = dragon.ply
target = asian_dragon_scaled_1e-3.ply
source_count = 437,645
target_count = 3,609,600
same POD = true
author preprocessing = PLY loader per-input min-bound translation
RTDL preprocessing = translate_each_input_to_min_bound
```

Correctness:

```text
author scaled HDResult = 0.06536787003278732
RTDL route distance    = 0.06536787240753439
author_abs_diff        = 2.3747470656587666e-09
matched                = true

paper-log HDResult     = 0.06536811590194702
RTDL-vs-paper diff     = 2.4349441263282756e-07
```

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_goal5239_author_dragon_asian_scaled_perf_summary_2026-07-09.json
  xhd_goal5239_author_dragon_asian_scaled_rt_gpu_rerun_2026-07-09.json
  xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
  xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
```

## Author Measurement

Author command path:

```text
/tmp/xhd-goal5222_build_paper/bin/hd_exec
variant = rt
execution = gpu
input_type = ply
n_dims = 3
```

Author summary:

```text
process_wall_sec = 2.6587867364287376
internal Running.AvgTime = 83.49680000000001 ms
repeat_count = 5
first_repeat_sum_RTTime = 81.019 ms
first_repeat_BVHBuildTime = 0.656 ms
first_repeat_grid_BuildTime = 1.51 ms
```

Author grid metadata:

```text
GridSize = [107, 60, 72]
TotalCells = 462,240
MedianPointsPerCell = 228
MaxPoints = 813
GiniIndex = 0.38537219166755676
```

## RTDL Measurement

RTDL artifact:

```text
xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
```

RTDL exact-value mode:

```text
global_bound_early_break = false
per_source_witness_exact = true
full_pairwise_rows_materialized = false
full_all_source_route_run = true
```

RTDL timing:

```text
full_app_wall_sec = 31.252301812171936
route_direction_total_sec = 30.49027620255947
load_full_inputs_sec = 0.5014200136065483

grid_cell_mbrs = 0.5977412909269333
initial_state_seed = 0.9031352773308754
frontier_rows = 0.8221020475029945
nearest_continuation = 28.124958105385303
max_nearest_reduction = 0.0007915198802947998
```

Work counters:

```text
frontier_row_count = 3,306,122
candidate_distance_evaluations = 6,417,800,660
```

## Denominator-Explicit Ratios

These are diagnostic ratios with labels. They are not a claim of
author-performance parity or paper Figure reproduction.

```text
RTDL full app wall / author process wall
  = 31.252301812171936 / 2.6587867364287376
  = 11.75434696735015x slower

RTDL route_direction_total / author internal Running.AvgTime
  = 30.49027620255947 / 0.0834968
  = 365.1670028379467x slower

RTDL nearest_continuation / author internal Running.AvgTime
  = 28.124958105385303 / 0.0834968
  = 336.83875436406305x
```

## Interpretation

The correctness gap for this one Level-B graphics workload is closed at the
all-source scalar level.

The performance gap is not closed.

The dominant RTDL cost is:

```text
nearest_continuation = 28.124958105385303s
```

This means the current RTDL route still behaves like:

```text
generic cell-MBR frontier production
-> generic NumPy/Numba nearest continuation over frontier rows
-> max-nearest reduction
```

The author route behaves like:

```text
fused RT radius-growth / pruning / payload-state iterations
```

Goal5239 therefore points to the next real performance mountain:

```text
the generic continuation is correct, but it is not fused enough to compete
with the author's RT iteration pipeline.
```

## Claim Boundary

Allowed:

```text
On the same POD and same scaled-public all-source Dragon -> AsianDragon input,
RTDL matches the author scaled HDResult but is substantially slower under both
process-wall and internal-route denominators.
```

Forbidden:

```text
RTDL matches author performance.
RTDL reproduces Figure 6 performance.
RTDL proves exact paper input byte identity.
The diagnostic ratios are paper speedup/parity claims.
Full X-HD paper reproduction is complete.
```

## Next Recommended Work

1. External review of Goals5233-5239 as the Dragon -> AsianDragon correctness
   and performance packet.
2. Decide whether to attack the 28s nearest-continuation bottleneck via a
   generic fused nearest-continuation primitive, or move to the next paper
   workload first.
3. Do not spend effort on PLY loading, frontier row production, or max
   reduction before the nearest-continuation bottleneck is addressed.
