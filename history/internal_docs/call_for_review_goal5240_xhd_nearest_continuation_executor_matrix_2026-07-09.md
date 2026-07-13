# Call For Review: Goal5240 X-HD Nearest Continuation Executor Matrix

Please strictly review Goal5240.

This goal responds to the Goal5239 performance diagnosis that the dominant
RTDL cost on Dragon -> scaled AsianDragon was:

```text
nearest_continuation = 28.124958105385303s
```

Goal5240 does not introduce a new native primitive. It tests whether the
existing generic nearest-continuation executor choices already contain a safe
win.

## Files To Review

Result report:

```text
history/internal_docs/goal5240_xhd_nearest_continuation_executor_matrix_result_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5240_dragon_asian_scaled_all_source_optix_numba_baseline_rerun_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5240_dragon_asian_scaled_all_source_optix_numba_parallel_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5240_dragon_asian_scaled_all_source_optix_auto_pod_2026-07-09.json
```

Context reports:

```text
history/internal_docs/goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_result_2026-07-09.md
history/internal_docs/goal5238_xhd_author_ply_loader_translation_contract_result_2026-07-09.md
history/internal_docs/goal5239_dragon_asian_scaled_same_pod_performance_matrix_result_2026-07-09.md
history/internal_docs/xhd_midterm_report_after_goal5239_2026-07-09.md
```

Relevant implementation:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

## Claims To Review

1. The executor matrix keeps the exact mode fixed:

   ```text
   translate_each_input_to_min_bound = true
   global_bound_early_break = false
   author HDResult = 0.06536787003278732
   source_count = 437,645
   target_count = 3,609,600
   ```

2. Both `numba`, `numba_parallel`, and `auto` runs match the same author
   HDResult:

   ```text
   author_abs_diff = 2.3747470656587666e-09
   matched = true
   ```

3. `auto` resolves to `numba_parallel`.

4. Same-POD baseline rerun:

   ```text
   frontier_nearest_executor = numba
   direction_total = 31.01092080026865s
   nearest_continuation = 28.445445612072945s
   ```

5. Explicit parallel run:

   ```text
   frontier_nearest_executor = numba_parallel
   direction_total = 10.097781844437122s
   nearest_continuation = 7.6326252073049545s
   ```

6. Recommended/default route:

   ```text
   frontier_nearest_executor = auto
   actual executor = numba_parallel
   direction_total = 9.171282961964607s
   nearest_continuation = 6.6945535987615585s
   ```

7. The work count is unchanged:

   ```text
   frontier_row_count = 3,306,122
   candidate_distance_evaluations = 6,417,800,660
   ```

8. Therefore this is an executor parallelization win, not an algorithmic
   pruning win.

9. The next performance mountain is reducing candidate work / fusing the
   continuation, not loading, max reduction, or frontier row production.

## Review Questions

1. Does Goal5240 preserve the exact-value reproduction contract from Goal5237?
2. Do all three executor runs match the same author HDResult with the same
   distance/source/target?
3. Is the comparison fair enough as a same-POD executor matrix, or does it need
   repeated medians before being used in a summary?
4. Does `auto` genuinely resolve to `numba_parallel` in the artifact?
5. Is the reported speedup correctly framed as RTDL route improvement, not
   author parity or Figure reproduction?
6. Does the unchanged `candidate_distance_evaluations` count correctly support
   the interpretation that this is not an algorithmic pruning win?
7. Is `nearest_continuation_executor_win_promote_generic` the right exit label?
8. Is the proposed next goal correct: reduce candidate work via a generic fused
   continuation / pruning primitive, rather than continue optimizing small
   phases?
9. Does the report keep RTDL genericity: no X-HD-specific native primitive,
   no Dragon/AsianDragon hard-coded core semantics?
10. Are any performance ratios or denominator comparisons overstated?

## Expected Answer Shape

```text
Verdict:
  approve_goal5240_nearest_continuation_executor_win
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
RTDL matches author performance.
Figure 6 performance is reproduced.
Full X-HD paper reproduction is complete.
The author fused RT-core algorithm is reproduced.
Candidate work has been reduced.
The result proves all X-HD workloads will speed up.
global_bound_early_break is exact.
```

## Allowed Summary Shape

The strongest allowed summary is:

```text
Goal5240 shows that the Dragon -> scaled AsianDragon exact all-source route
was using a slow serial nearest-continuation executor. Switching to the existing
generic `auto` / `numba_parallel` executor preserves the author HDResult match
and reduces RTDL route direction time from about 31s to about 9-10s on the same
POD. This is a real RTDL route improvement, but it does not reduce the 6.4B
candidate evaluations and does not close the author performance gap.
```
