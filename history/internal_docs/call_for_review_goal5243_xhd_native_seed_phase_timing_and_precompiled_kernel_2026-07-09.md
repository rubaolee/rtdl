# Call For Review - Goal5243 X-HD Native Seed Phase Timing + Precompiled Kernel

Date: 2026-07-09

Please strictly review Goal5243.

## Files

Result:

```text
history/internal_docs/goal5243_xhd_native_seed_phase_timing_and_precompiled_kernel_result_2026-07-09.md
```

Midterm context:

```text
history/internal_docs/xhd_midterm_report_after_goal5243_2026-07-09.md
history/internal_docs/call_for_review_xhd_midterm_after_goal5243_2026-07-09.md
```

Implementation:

```text
Makefile
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_cuda_helpers.cu
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_seed_phase_inline1024_runtime_module_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run1_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run3_pod_2026-07-09.json
```

## Review Questions

1. Does the native phase timing correctly identify runtime CUDA module
   compile/load as the pre-Goal5243 local-grid seed bottleneck?

2. Does the precompiled helper preserve the prior runtime kernel's semantics,
   including nearest distance, item id, seed cell id, seed cell point count, and
   grid-cell probe count outputs?

3. Is the `Makefile` `OPTIX_CUDA_ARCH_DETECTED` change acceptable, or should it
   be opt-in only?

4. Are the POD results sufficient to claim:

```text
seed_module_ensure_sec = 0.0
seed_native_total median = 0.202945411s
direction_total median = 2.3074675127863884s
```

5. Does Goal5243 preserve exactness:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
per_source_witness_exact = true
frontier_rows = 0
```

6. Are the performance comparisons properly bounded to one Dragon -> scaled
   AsianDragon public workload?

7. Does the report avoid author internal AvgTime parity and full-paper claims?

8. Should Goal5243 be closed as a generic RTDL native packaging/performance
   improvement?

## Requested Verdict Label

If approved:

```text
approve_goal5243_xhd_generic_native_seed_precompiled_kernel
```
