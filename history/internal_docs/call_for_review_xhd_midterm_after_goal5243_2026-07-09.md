# Call For Review - X-HD Midterm After Goal5243

Date: 2026-07-09

Please strictly review the X-HD midterm packet after Goal5243. Be harsh about
claim boundaries, denominators, and whether single-workload evidence is being
overstated.

## Files Under Review

Primary midterm report:

```text
history/internal_docs/xhd_midterm_report_after_goal5243_2026-07-09.md
```

Goal5243 result report:

```text
history/internal_docs/goal5243_xhd_native_seed_phase_timing_and_precompiled_kernel_result_2026-07-09.md
```

Supporting prior reports:

```text
history/internal_docs/goal5242_xhd_best_route_phase_decomposition_inline_threshold_result_2026-07-09.md
history/internal_docs/goal5241_xhd_grid_shape_native_seed_performance_result_2026-07-09.md
history/internal_docs/goal5240_xhd_nearest_continuation_executor_matrix_result_2026-07-09.md
history/internal_docs/goal5239_xhd_author_vs_rtdl_same_input_performance_matrix_result_2026-07-09.md
history/internal_docs/goal5237_xhd_dragon_asian_scaled_full_source_route_gate_result_2026-07-09.md
```

Key evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_seed_phase_inline1024_runtime_module_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run1_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run3_pod_2026-07-09.json
```

Implementation files changed by Goal5243:

```text
Makefile
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_cuda_helpers.cu
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

## Claims To Verify

1. Goal5243 removed runtime CUDA module compile/load from the generic native
   local-grid seed path:

```text
seed_module_ensure_sec: 0.496675326 -> 0.0
seed_native_total:      0.698966517 -> median 0.202945411
seed_outer:             0.851726666 -> median 0.349251054
```

2. Correctness is preserved:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = true
frontier_rows = 0
```

3. The same-workload route improved:

```text
Goal5239 direction_total = 30.49027620255947s
Goal5243 direction_total median = 2.3074675127863884s
improvement = about 13.21x
```

4. The result remains a limited Level-B single-workload result:

```text
not full paper reproduction
not exact paper byte-input identity
not paper-log exact match
not Figure reproduction
not author internal AvgTime parity
not a multi-workload Level-B matrix
```

5. The denominator-explicit author comparison is correctly framed:

```text
RTDL Goal5243 route_wall / author process wall = 0.868x
RTDL Goal5243 total_wall / author process wall = 1.150x
RTDL Goal5243 direction_total / author internal Running.AvgTime = 27.64x slower
```

The review should reject any summary that converts `route_wall < author process
wall` into author internal parity.

## Questions For Review

1. Do the Goal5243 artifacts actually prove that runtime module compile/load was
   removed from the local-grid seed path?

2. Is the Makefile architecture-detection change acceptable as a generic native
   packaging fix, or does it introduce a portability risk that must be amended?

3. Does the precompiled CUDA helper preserve the exact same seed semantics,
   output columns, and tie-breaking as the prior runtime-compiled kernel?

4. Are the three precompiled POD repeats enough to claim the median
   `2.3074675127863884s` route number for this checkpoint?

5. Is the `13.21x` improvement from Goal5239 to Goal5243 a fair same-workload
   comparison, or does any denominator/regime mismatch invalidate it?

6. Does the midterm report correctly carry forward the prior strict-review
   caveats:

```text
exact-value-only
author rerun, not paper log
single workload, not broad Level-B completion
```

7. Is the author comparison correctly denominator-labelled, especially the
   distinction between author process wall and author internal Running.AvgTime?

8. Does the latest work preserve the principle that RTDL is a generic system and
   X-HD is an app?

9. Are the next goals correct:

```text
frontier/inline nearest decomposition
generic prepared target-grid workspace
second Level-B workload
author denominator/phase-boundary audit
```

10. Should this midterm be approved as a Level-B single-workload checkpoint, or
    are there required amendments before it can be used as the current project
    status?

## Expected Answer Shape

Please respond with:

```text
Verdict:
  approve
  approve_with_required_amendments
  block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  ...

Allowed final summary:
  ...

Forbidden summaries:
  ...
```

## Requested Verdict Label

If approved:

```text
approve_xhd_midterm_after_goal5243_single_workload_level_b_checkpoint
```
