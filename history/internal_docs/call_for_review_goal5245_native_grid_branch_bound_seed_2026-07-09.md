# Call For Review: Goal5245 Native Grid-Branch-Bound Seed

Please strictly review Goal5245.

## Files Under Review

Result report:

```text
history/internal_docs/goal5245_native_grid_branch_bound_seed_result_2026-07-09.md
```

Evidence JSON:

```text
history/internal_docs/goal5245_probe_grid_branch_bound_numba_current_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_skip_frontier_pod_2026-07-09.json
history/internal_docs/goal5245_native_grid_branch_bound_seed_skip_frontier_input_stable_pod_2026-07-09.json
```

Implementation:

```text
src/native/optix/rtdl_optix_cuda_helpers.cu
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5245_native_grid_branch_bound_seed_test.py
```

## Review Questions

1. Does the new native CUDA grid-branch-bound seed remain app-neutral and avoid
   X-HD / Hausdorff / paper-specific core semantics?
2. Is the exact-seed frontier skip semantically valid only when the seed
   declares `exact_nearest_witness_under_grid_cell_branch_bound`?
3. Do the POD results prove a real capability improvement over the previous
   Numba grid-branch-bound seed?
4. Do the POD results also prove the important negative conclusion: this route
   is still slower than the Goal5244 current best route and should not become
   the default X-HD route?
5. Are the performance numbers reported under the correct boundary:
   representative single Dragon -> scaled AsianDragon workload only, not full
   X-HD paper reproduction?
6. Does the report avoid author parity / paper-log exact / Figure reproduction
   claims?
7. Is the next recommendation correct: stop this exact seed as a performance
   route and move to a stronger generic prepared spatial index / nearest
   traversal design?
8. Are there any lifecycle, ABI, or native timing risks in the new symbol or
   Python binding that should block closing Goal5245?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 8 review questions:
```

Suggested verdict if approved:

```text
approve_goal5245_native_grid_branch_bound_seed_capability__performance_no_go
```
