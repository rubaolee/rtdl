# Call For Review: Goal5242 X-HD Best Route Phase Decomposition + Inline Threshold

Please strictly review Goal5242.

Goal5242 follows Goal5241. Goal5241 selected the best current route:

```text
grid_shape = 96,60,72
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
max_inline_points = 512
```

Goal5242 decomposes that route, corrects the candidate-work accounting by
including native inline point evaluations, and tests the generic native frontier
inline threshold. The strongest current route becomes:

```text
grid_shape = 96,60,72
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
max_inline_points = 1024
global_bound_early_break = false
per_source_witness_exact = true
```

## Files To Review

Result report:

```text
history/internal_docs/goal5242_xhd_best_route_phase_decomposition_inline_threshold_result_2026-07-09.md
```

Context:

```text
history/internal_docs/goal5239_dragon_asian_scaled_same_pod_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5240_xhd_nearest_continuation_executor_matrix_result_2026-07-09.md
history/internal_docs/goal5241_xhd_grid_shape_native_seed_performance_result_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_native_phase_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_inline_stats_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_32grid_inline_stats_pod_2026-07-09.json

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline128_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline256_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_best_route_inline_stats_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_rep2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline1024_rep3_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5242_dragon_asian_scaled_96grid_native_seed_auto_inline2048_pod_2026-07-09.json

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_dragon_asian_scaled_all_source_grid_96x60x72_native_seed_auto_rep3_pod_2026-07-09.json
```

## Claims To Review

1. Goal5242 preserves the exact-value contract:

   ```text
   translate_each_input_to_min_bound = true
   global_bound_early_break = false
   per_source_witness_exact = true
   author HDResult = 0.06536787003278732
   ```

2. Native phase timing shows the frontier phase is dominated by native OptiX
   launch work:

   ```text
   frontier outer = 1.285792425274849s
   native total = 1.26988834s
   optix_launch = 1.124687623s
   row_download = 0.000916057s
   host_sort_pack = 0.005699s
   ```

3. Goal5242 corrects the Goal5241 work accounting:

   ```text
   The earlier 44x reduction is only metadata/offload candidate-count reduction.
   Including native inline point evaluations, true point-evaluation reduction
   from the 32-grid route to the 96x60x72/max_inline=1024 route is about 5.16x.
   ```

4. `max_inline_points=1024` is the best threshold tested for this workload:

   ```text
   max_inline=512:
     direction_total = 3.0710937827825546s
     frontier_rows = 180,821
     nearest_continuation = 0.30977560579776764s

   max_inline=1024:
     direction_total = 2.76628365367651s single-run
     frontier_rows = 0
     nearest_continuation = 0.0008367449045181274s
   ```

5. Three-repeat median for the current best route:

   ```text
   direction_total = 2.8061167374253273s
   route_wall = 3.059376485645771s
   total_wall = 3.5552977472543716s
   matched = true
   author_abs_diff = 2.3747470656587666e-09
   ```

6. Performance movement is denominator-labelled:

   ```text
   vs Goal5241 direction_total: 3.0695155784487724s -> 2.8061167374253273s
   improvement = 1.0938659598549414x

   vs Goal5239 direction_total: 30.49027620255947s -> 2.8061167374253273s
   improvement = 10.865647817109332x

   RTDL direction_total / author process wall = 1.0554124928404307x slower
   RTDL total_wall / author process wall = 1.3371880108104575x slower
   RTDL direction_total / author internal Running.AvgTime = 33.607476423351876x slower
   ```

7. The new bottleneck is no longer Python/Numba continuation:

   ```text
   frontier_rows = 0
   nearest_continuation ~= 0.00084s
   dominant remaining phases are native frontier OptiX launch, native CUDA
   local-grid seed, and grid_cell_mbr prep.
   ```

8. This is still one workload, not full X-HD paper reproduction.

## Review Questions

1. Does Goal5242 preserve the Goal5237-5241 exact-value correctness contract?
2. Are all threshold and repeat runs actually matched against the same author
   HDResult?
3. Is the native phase decomposition supported, and does it really show OptiX
   launch domination rather than host row materialization?
4. Is the true point-evaluation accounting correction valid?
5. Is the report sufficiently explicit that Goal5241's 44x figure was not
   total point-evaluation reduction?
6. Is `max_inline_points=1024` correctly selected as the current best threshold
   based on the tested matrix and three-repeat median?
7. Are the performance ratios computed against the correct denominators?
8. Does the report avoid claiming author internal parity, Figure reproduction,
   exact paper input identity, or full paper reproduction?
9. Does this remain generic RTDL system work rather than X-HD app-specific core
   customization?
10. Is the next recommended work correct: attack generic seed/frontier/grid
    prep costs, not continuation rows?

## Expected Answer Shape

```text
Verdict:
  approve_goal5242_inline_threshold_1024_and_true_work_accounting
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```

## Forbidden Summaries

Please reject any summary that says:

```text
RTDL matches author internal performance.
RTDL reproduces Figure 6.
Full X-HD paper reproduction is complete.
Exact paper input byte identity is proved.
The 44x candidate reduction is total point-evaluation reduction.
96x60x72 or max_inline=1024 is universal.
The author fused RT-core algorithm is reproduced.
This result applies to all workloads.
```

## Allowed Summary Shape

The strongest allowed summary is:

```text
Goal5242 shows that for the Dragon -> scaled AsianDragon same-source all-source
route, raising the generic native frontier inline-nearest threshold to 1024
eliminates continuation rows while preserving the author HDResult match. The
current three-repeat median is about 2.81s direction time, 3.06s route wall, and
3.56s total wall. This is about 10.9x faster than the Goal5239 route direction
time and about 1.06x slower than the author process wall denominator, but still
about 33.6x slower than the author internal AvgTime denominator. Goal5242 also
corrects candidate-work accounting: the earlier 44x figure is metadata/offload
candidate-count reduction, while true point-evaluation reduction is about 5.16x
when native inline point evaluations are counted.
```
