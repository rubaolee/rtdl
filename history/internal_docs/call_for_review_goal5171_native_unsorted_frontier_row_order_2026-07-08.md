# Call For Review: Goal5171 Native Unsorted Frontier Row Order

Please strictly review Goal5171:

```text
history/internal_docs/goal5171_native_unsorted_frontier_row_order_result_2026-07-08.md
```

Primary code/evidence:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5171_unsorted_native_frontier_rows_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5171_sorted_frontier_rows_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5171_native_unsorted_frontier_rows_matrix_pod.json
```

## Expected Answer Shape

Please answer:

1. Does Goal5171 preserve legacy sorted+unique behavior by default?
2. Is the new `sort_rows` / row-order option app-neutral and appropriate for
   the generic 3-D cell-MBR nearest-frontier collector?
3. Does the Python runtime fail closed when `sort_rows=False` but the backend
   does not export `rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2`?
4. Do the local/POD tests adequately verify Python policy plumbing and the
   no-regression path?
5. Does the POD evidence show the native v2 symbol was used for both sorted and
   native-unsorted runs?
6. Did the native-unsorted route preserve correctness on the full public res4
   representative case?
7. Is the performance interpretation correctly bounded as a small route win
   (~0.03376s -> ~0.03309s) with part of the native frontier saving moved into
   continuation grouping cost?
8. Does the report avoid author-performance parity, speedup-ratio, full-paper,
   and exact-paper-dataset claims?
9. Should Goal5171 be closed as
   `completed_native_unsorted_frontier_row_order__small_route_win`, or should it
   be revised/no-go?

## Requested Verdict Label

One of:

```text
approve_goal5171_native_unsorted_frontier_row_order_small_win
revise_goal5171_native_unsorted_frontier_row_order
block_goal5171_native_unsorted_frontier_row_order
```
