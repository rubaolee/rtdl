# Goal5242 X-HD Best Route Phase Decomposition + Inline Threshold Result

Date: 2026-07-09

## Verdict

`implemented__inline_threshold_1024_eliminates_continuation_rows__true_work_accounting_corrected__review_pending`

Goal5242 decomposes the Goal5241 best Dragon -> scaled AsianDragon route and
tests the generic native frontier inline-nearest threshold.

The strongest current route after Goal5242 is:

```text
source = Dragon, 437,645 points
target = scaled AsianDragon, 3,609,600 points
preprocessing = translate_each_input_to_min_bound
grid_shape = 96,60,72
initial_state = local-grid-cell
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
max_inline_points = 1024
global_bound_early_break = false
per_source_witness_exact = true
```

All three same-POD repeats matched the author rerun:

```text
RTDL route distance = 0.06536787240753439
author scaled HDResult = 0.06536787003278732
author_abs_diff = 2.3747470656587666e-09
matched = true
```

Median timing:

```text
direction_total = 2.8061167374253273s
route_wall = 3.059376485645771s
total_wall = 3.5552977472543716s
frontier_rows = 0
nearest_continuation = 0.0008386373519897461s
```

This improves the Goal5241 best route, but it does not prove author internal
performance parity, Figure reproduction, exact paper input byte identity, or
full X-HD paper reproduction.

## Evidence Artifacts

Native phase decomposition:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_native_phase_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_inline_stats_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_32grid_inline_stats_pod_2026-07-09.json
```

Inline threshold matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline128_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline256_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_inline_stats_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_rep2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_rep3_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline2048_pod_2026-07-09.json
```

Baseline/context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep3_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
```

## Fixed Correctness Contract

Goal5242 keeps the exact-value contract used by Goals5237-5241:

```text
translate_each_input_to_min_bound = true
global_bound_early_break = false
per_source_witness_exact = true
author HDResult = 0.06536787003278732
author_tolerance = 1e-6
full_pairwise_rows_materialized = false
```

Every all-source Goal5242 run in the matrix reports:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
distance/source/target = 0.06536787240753439 / 49577 / 1803033
```

## Native Frontier Phase Decomposition

The Goal5241 best route with `max_inline_points=512` was rerun with native phase
timings enabled.

Outer route phases:

```text
direction_total = 3.066827416419983s
grid_cell_mbrs = 0.6103946715593338s
initial_state_seed = 0.8482318073511124s
frontier_rows = 1.285792425274849s
nearest_continuation = 0.28843574970960617s
frontier_row_count = 180,821
```

Native frontier phases:

```text
total_native_sec = 1.26988834s
optix_launch_sec = 1.124687623s
device_alloc_upload_sec = 0.013301446s
query_pack_sec = 0.005191005s
host_sort_pack_sec = 0.005699s
row_download_sec = 0.000916057s
accel_build_sec = 0.00100355s
emitted_count = attempted_count = 180,821
```

Conclusion:

```text
The frontier phase is dominated by native OptiX launch work, not Python
row-download, host sort/pack, or host materialization.
```

## True Work Accounting Correction

Goal5241 reported:

```text
Goal5240 metadata/offload candidate evaluations:
  6,417,800,660 -> 145,373,825
  reduction = about 44x
```

That statement is valid only for the route metadata/offloaded candidate count.
It does not include point evaluations performed inside the native inline-nearest
frontier shader.

Goal5242 adds `inline_stats` and corrects the total point-evaluation accounting:

```text
true_point_evaluations =
  initial_candidate_distance_evaluations
  + inline_point_evaluation_count
  + continuation_candidate_distance_evaluations
```

Measured accounting:

```text
32x32x32, max_inline=512:
  initial = 328,347,700
  inline = 147,812,506
  continuation = 6,089,452,960
  true_point_evaluations = 6,565,613,166

96x60x72, max_inline=512:
  initial = 43,621,949
  inline = 1,135,725,446
  continuation = 101,751,876
  true_point_evaluations = 1,281,099,271

96x60x72, max_inline=1024:
  initial = 43,621,949
  inline = 1,229,829,134
  continuation = 0
  true_point_evaluations = 1,273,451,083
```

Corrected work reduction:

```text
32x32x32 -> 96x60x72/max_inline=1024:
  true point-evaluation reduction = 5.155763934436106x

96x60x72/max_inline=512 -> 96x60x72/max_inline=1024:
  true point-evaluation reduction = 1.0060058749818503x
```

Interpretation:

```text
Goal5241/5242 moved work from continuation rows into native inline traversal
and reduced true total point-evaluation work by about 5.16x versus the 32-grid
route. The earlier 44x figure must be read only as metadata/offload candidate
count reduction, not total point-evaluation reduction.
```

## Inline Threshold Matrix

All runs below use:

```text
grid_shape = 96,60,72
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
global_bound_early_break = false
```

All matched the author HDResult.

```text
max_inline=128:
  direction_total = 6.215896539390087s
  seed = 0.8266885727643967s
  frontier = 1.2181786820292473s
  nearest = 3.5139518678188324s
  frontier_rows = 4,509,669
  inline_eval = 63,862,320
  continuation_eval = 1,584,784,578
  true_point_evaluations = 1,692,268,847

max_inline=256:
  direction_total = 5.19997500628233s
  seed = 0.8487479388713837s
  frontier = 1.1751765832304955s
  nearest = 2.516393907368183s
  frontier_rows = 3,133,163
  inline_eval = 240,893,401
  continuation_eval = 1,252,917,073
  true_point_evaluations = 1,537,432,423

max_inline=512:
  direction_total = 3.0710937827825546s
  seed = 0.820289634168148s
  frontier = 1.2901898175477982s
  nearest = 0.30977560579776764s
  frontier_rows = 180,821
  inline_eval = 1,135,725,446
  continuation_eval = 101,751,876
  true_point_evaluations = 1,281,099,271

max_inline=1024:
  direction_total = 2.76628365367651s
  seed = 0.8145695626735687s
  frontier = 1.3078664019703865s
  nearest = 0.0008367449045181274s
  frontier_rows = 0
  inline_eval = 1,229,829,134
  continuation_eval = 0
  true_point_evaluations = 1,273,451,083

max_inline=2048:
  direction_total = 2.816789224743843s
  seed = 0.8527098223567009s
  frontier = 1.31250761449337s
  nearest = 0.0008228868246078491s
  frontier_rows = 0
  inline_eval = 1,229,829,134
  continuation_eval = 0
  true_point_evaluations = 1,273,451,083
```

Conclusion:

```text
max_inline_points=1024 is the best current threshold for this workload.
It eliminates continuation rows and leaves almost no downstream nearest phase.
Increasing to 2048 does not reduce work further and is slightly slower.
```

## Three-Repeat Current Best Route

Three same-POD repeats for `max_inline_points=1024`:

```text
rep1:
  direction_total = 2.76628365367651s
  route_wall = 3.019617609679699s
  total_wall = 3.520039662718773s

rep2:
  direction_total = 2.806209795176983s
  route_wall = 3.059376485645771s
  total_wall = 3.5552977472543716s

rep3:
  direction_total = 2.8061167374253273s
  route_wall = 3.060816526412964s
  total_wall = 3.558831959962845s
```

Median:

```text
direction_total = 2.8061167374253273s
route_wall = 3.059376485645771s
total_wall = 3.5552977472543716s
```

Median major phases:

```text
grid_cell_mbrs = 0.6081122308969498s
initial_state_seed = 0.8466619104146957s
frontier_rows = 1.309279777109623s
nearest_continuation = 0.0008386373519897461s
frontier native optix_launch = 1.162741531s
frontier native total = 1.294948322s
```

## Performance Movement

Compared with Goal5241 best route (`max_inline_points=512`):

```text
direction_total:
  3.0695155784487724s -> 2.8061167374253273s
  improvement = 1.0938659598549414x

total_wall:
  3.8200959116220474s -> 3.5552977472543716s
  improvement = 1.0744798841593983x
```

Compared with Goal5239:

```text
direction_total:
  30.49027620255947s -> 2.8061167374253273s
  improvement = 10.865647817109332x

total_wall:
  31.252301812171936s -> 3.5552977472543716s
  improvement = 8.790347260312293x
```

Denominator-labelled author comparisons:

```text
author process wall = 2.6587867364287376s
author internal Running.AvgTime = 0.08349680000000001s

RTDL direction_total / author process wall = 1.0554124928404307x slower
RTDL route_wall / author process wall = 1.1506663711415615x slower
RTDL total_wall / author process wall = 1.3371880108104575x slower

RTDL direction_total / author internal Running.AvgTime = 33.607476423351876x slower
```

Interpretation:

```text
For this one Dragon -> scaled AsianDragon workload, RTDL route direction is now
near the author process wall denominator. It remains far from the author
internal AvgTime denominator.
```

## Current Bottleneck

The old continuation bottleneck has been removed:

```text
frontier_rows = 0
nearest_continuation ~= 0.00084s
```

The current major phases are:

```text
frontier native OptiX launch ~= 1.16s
native CUDA local-grid seed ~= 0.85s
grid_cell_mbr prep ~= 0.61s
```

Next targets must therefore be about generic seed/frontier traversal cost and
grid/cell preparation, not Python continuation.

## What This Does Not Prove

Goal5242 does not prove:

```text
full X-HD paper reproduction
Figure 6 reproduction
exact paper input byte identity
author internal AvgTime parity
universal grid shape or universal inline threshold
the author fused RT-core algorithm is reproduced
all X-HD workloads have this performance
```

## Next Recommended Goal

The next technical goal should attack the new dominant costs while preserving
the exact route contract:

```text
global_bound_early_break = false
per_source_witness_exact = true
no X-HD-specific RTDL core primitive
```

Candidate next goals:

1. Decompose and optimize `native_cuda` local-grid seed, especially the very
   large `initial_grid_cell_probes` count, with a generic seed policy or native
   phase breakdown.
2. Reduce the native frontier OptiX launch cost for the fully inline route,
   likely by reducing cell-query work or improving generic cell frontier
   pruning, not by app-specific X-HD shortcuts.
3. Decompose `grid_cell_mbrs` setup and test caching or native preparation if
   it is generic and workload-independent.
4. Run the current best route on a second Level-B workload only after the
   Dragon -> scaled AsianDragon bottleneck packet is reviewed.
