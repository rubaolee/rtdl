# Call For Review: Goal5200 Native CUDA Local-Grid Seed No-Go

Please strictly review Goal5200.

## Files Under Review

```text
history/internal_docs/goal5200_native_local_grid_seed_no_go_result_2026-07-08.md

src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py

Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py

tests/goal5200_native_local_grid_seed_test.py

Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_goal5200_auto_local_grid_seed_control_graphics_dragon_happy_buddha_2026-07-08.json
  xhd_full_public_all_source_goal5200_native_local_grid_seed_final2_graphics_dragon_happy_buddha_2026-07-08.json
```

## Question

Does Goal5200 correctly implement an explicit generic native CUDA executor for
the local-grid nearest-state seed, validate that it is correct, and honestly
classify it as a no-go because it is slower than the existing Numba default on
the full-public Level-B X-HD route?

## Expected Review Points

1. Is the new native symbol generic?
   - It should operate on point columns, compact grid-cell spans, dense lookup,
     and grid bounds only.
   - It must not encode X-HD, Hausdorff, author binary, paper, or output
     semantics.

2. Is the default route unchanged?
   - `seed_nearest_witness_from_local_grid_cell_numpy_columns` default executor
     must remain `auto`, resolving to the existing Numba path.
   - The native path must require explicit `executor="native_cuda"` /
     `--local-grid-seed-executor native_cuda`.

3. Is fail-closed behavior preserved?
   - Native CUDA seed should require dense lookup rather than silently falling
     back.
   - Existing local-grid dense lookup tests should still pass.

4. Is the same-POD comparison fair?
   - Compare:
     - auto/Numba artifact:
       `xhd_full_public_all_source_goal5200_auto_local_grid_seed_control_graphics_dragon_happy_buddha_2026-07-08.json`
     - native CUDA artifact:
       `xhd_full_public_all_source_goal5200_native_local_grid_seed_final2_graphics_dragon_happy_buddha_2026-07-08.json`
   - Confirm both match Goal5186 author HDResult and use the same route
     settings except local-grid seed executor.

5. Is the no-go conclusion correct?
   - Auto/Numba route wall: `2.2580383121967316s`; seed phase:
     `0.5628510117530823s`.
   - Native CUDA route wall: `2.4362636134028435s`; seed phase:
     `0.9580570980906487s`.
   - Native CUDA is slower end-to-end, so it must not become the default.

6. Are claims bounded?
   - No X-HD performance improvement.
   - No author performance ratio.
   - No exact paper dataset reproduction.
   - No full paper reproduction.
   - No claim that device-resident seeding is solved.

## Requested Verdict Label

If approved:

```text
approve_goal5200_native_local_grid_seed_no_go_keep_numba_default
```

If blocked, please identify whether the issue is:

```text
block_due_to_app_specific_native_seed_leak
block_due_to_default_route_changed_without_win
block_due_to_unfair_same_pod_comparison
block_due_to_missing_correctness_validation
```
