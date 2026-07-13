# Call For Review: Goal5241 X-HD Grid Shape + Native Seed Performance

Please strictly review Goal5241.

Goal5241 follows Goal5240. Goal5240 reduced the Dragon -> scaled AsianDragon
all-source exact route from ~31s to ~9s by using the existing generic
`auto`/`numba_parallel` nearest-continuation executor. Goal5241 then attacks the
remaining candidate work by tuning generic grid shape and using the existing
generic native CUDA local-grid seed executor.

## Files To Review

Result report:

```text
history/internal_docs/goal5241_xhd_grid_shape_native_seed_performance_result_2026-07-09.md
```

Context:

```text
history/internal_docs/goal5239_dragon_asian_scaled_same_pod_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5240_xhd_nearest_continuation_executor_matrix_result_2026-07-09.md
history/internal_docs/xhd_midterm_report_after_goal5239_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_local-grid-cell_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_nearest-cell-mbr_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid-cell-budget_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid-branch-bound_pod_2026-07-09.json

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_64x64x64_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_96x64x72_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_107x60x72_local_grid_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5241_diag8192_grid_128x128x128_local_grid_pod_2026-07-09.json

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

## Claims To Review

1. Goal5241 preserves the exact-value contract:

   ```text
   translate_each_input_to_min_bound = true
   global_bound_early_break = false
   per_source_witness_exact = true
   author HDResult = 0.06536787003278732
   ```

2. Stronger seed strategies are not the answer for this workload:

   ```text
   nearest-cell-mbr / grid-cell-budget / grid-branch-bound reduce some
   continuation work but are dominated by seed cost.
   ```

3. Finer generic grid shapes reduce candidate work dramatically.

4. `128x128x128` removes frontier continuation but is slower because seed and
   frontier/native traversal overhead become too high.

5. Best current route is:

   ```text
   grid_shape = 96,60,72
   local_grid_seed_executor = native_cuda
   frontier_nearest_executor = auto
   ```

6. The best route was repeated three times and remained matched:

   ```text
   median direction_total = 3.0695155784487724s
   median route_wall = 3.322203427553177s
   median total = 3.8200959116220474s
   author_abs_diff = 2.3747470656587666e-09
   ```

7. Compared with Goal5239:

   ```text
   route direction: 30.49027620255947s -> 3.0695155784487724s
   improvement = 9.93325344775354x
   ```

8. Compared with Goal5240:

   ```text
   candidate_distance_evaluations:
     6,417,800,660 -> 145,373,825
     reduction = 44.14687898595225x
   ```

9. Denominator-labelled author comparison:

   ```text
   RTDL direction_total / author process wall = 1.1544797995237943x slower
   RTDL total wall / author process wall = 1.4367816189549567x slower
   RTDL direction_total / author internal Running.AvgTime = 36.76207445613212x slower
   RTDL total wall / author internal Running.AvgTime = 45.751404983449035x slower
   ```

10. This is a generic route tuning/system win, not an X-HD-specific native
    primitive and not author internal parity.

## Review Questions

1. Does Goal5241 preserve the Goal5237/5240 exact-value correctness contract?
2. Are all all-source tuned runs actually matched against the same author
   HDResult?
3. Is the seed-strategy no-go conclusion supported by the 8192 diagnostics?
4. Is the grid-shape conclusion supported by the 8192 and all-source matrices?
5. Is `96x60x72 + native_cuda seed + auto continuation` correctly selected as
   the current best route based on median evidence?
6. Are the performance improvements reported with the right baseline:
   Goal5239 for overall route improvement, Goal5240 for candidate-work
   reduction?
7. Are the author comparisons denominator-explicit and not overstated?
8. Does the report avoid claiming author internal parity, Figure reproduction,
   exact paper input identity, or full paper reproduction?
9. Does this remain generic RTDL system work rather than X-HD app-specific core
   customization?
10. Is the next recommended work correct: review this packet, then either
    decompose the new `frontier_rows` / native seed bottlenecks or broaden to
    another workload?

## Expected Answer Shape

```text
Verdict:
  approve_goal5241_grid_shape_native_seed_route_win
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
96x60x72 is a universal X-HD grid.
The author fused RT-core algorithm is reproduced.
This result applies to all workloads.
```

## Allowed Summary Shape

The strongest allowed summary is:

```text
Goal5241 shows that for the Dragon -> scaled AsianDragon same-source all-source
route, generic grid-shape tuning plus the existing native CUDA local-grid seed
executor preserves the author HDResult match and reduces median route direction
time to about 3.07s, roughly 9.9x faster than the Goal5239 route. It also
reduces candidate distance evaluations by about 44x compared with Goal5240.
This brings RTDL near author process-wall scale for this one workload, but it
is still far from author internal AvgTime and is not Figure reproduction or
full paper reproduction.
```
