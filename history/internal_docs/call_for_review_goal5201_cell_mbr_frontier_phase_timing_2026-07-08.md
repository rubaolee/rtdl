# Call For Review: Goal5201 Cell-MBR Frontier Native Phase Timing

Date: 2026-07-08

Please strictly review Goal5201.

## Files Under Review

Result report:

```text
history/internal_docs/goal5201_cell_mbr_frontier_phase_timing_result_2026-07-08.md
```

Implementation:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

Tests:

```text
tests/goal5201_cell_mbr_frontier_phase_timing_test.py
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5201_frontier_phase_timing_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5201_frontier_phase_timing_warm2_graphics_dragon_happy_buddha_2026-07-08.json
```

## Review Questions

1. Does Goal5201 correctly implement diagnostic-only native phase timing for
   the generic 3-D cell-MBR nearest-frontier collector without changing route
   semantics?
2. Is the instrumentation app-neutral, or did it introduce X-HD/paper-specific
   logic into RTDL core/native code?
3. Does the POD evidence show the full-public Dragon -> HappyBuddha Level-B
   route still matches the Goal5186 author HDResult?
4. Is the report correct that `accel_build ~= 0.0004s`, so prepared/reused
   cell-MBR accel build is not the next meaningful performance target?
5. Is the report correct that the remaining native frontier cost is dominated
   by native launch / inline nearest work (`optix_launch ~= 0.377s`) plus
   front-door/wrapper overhead between `native_total ~= 0.600s` and
   route-level `frontier_rows ~= 0.920s`?
6. Is it correct to treat the first run as cold/noisy because
   `initial_state_seed ~= 4.967s`, while using it only as repeat evidence for
   stable native frontier phase timings?
7. Does the report avoid claiming a performance improvement, author parity,
   exact paper dataset reproduction, or full X-HD paper reproduction?
8. Should Goal5201 close as
   `completed_cell_mbr_frontier_phase_timing__inline_launch_dominates__prepared_accel_not_next`?

## Expected Verdict Shape

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
```
