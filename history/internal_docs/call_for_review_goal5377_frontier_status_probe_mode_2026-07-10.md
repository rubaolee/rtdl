# Call For Review: Goal5377 Frontier Status Probe Mode

Please strictly review Goal5377.

## Files Under Review

- `history/internal_docs/goal5377_frontier_status_probe_mode_result_2026-07-10.md`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_frontier_status_probe_mode_comparison.json`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_default_status_probe_pod.json`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_heavy_before_inline_prune_probe_pod.json`
- `tests/goal5377_frontier_status_probe_mode_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_continuations.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py`

## Review Context

Goal5374 established the author `-lb` status trace oracle for Dragon ->
AsianDragon:

```text
active_in_queue_size: 437,645
raw_offload_rows_before_sort_reduce: 27,133,990
raw_offload_rows_author_width_bytes: 217,071,920
```

Goal5375 showed current RTDL surfaces do not match the oracle:

```text
inline author-radius current surface: 21,006,960 rows
no-inline raw surface:                304,981,889 rows
```

Goal5377 tested one narrow hypothesis: maybe author `-lb` counts heavy/offload
status before RTDL's inline-current-best prune suppresses the cell. The new
generic `frontier_status_probe_mode="heavy-before-inline-prune"` implements
only that branch-order probe.

## Expected Reviewer Questions

Please answer:

1. Does Goal5377 add a genuinely generic probe mode rather than X-HD-specific
   core behavior?
2. Does the v6 native ABI preserve old behavior by default?
3. Does `heavy-before-inline-prune` do exactly what the report says: classify
   heavy/offload cells before inline-current-best pruning?
4. Are the Python and partner front doors correctly forwarding and reporting
   `frontier_status_probe_mode`?
5. Do the local and POD validations support the implementation claims?
6. Does the POD comparison correctly show that the new mode is a no-go for
   author OffloadingSize parity?
7. Are the no-go conclusions and claim boundaries stated strongly enough?
8. Should the v6 probe remain experimental/non-default?
9. Is any wording accidentally implying explicit `-lb` support, author parity,
   same-denominator memory parity, or performance progress?
10. What should the next goal be: stronger generic status-machine modeling, or
    keeping author `-lb` fail-closed?

## Requested Verdict Labels

Use one:

```text
approve_goal5377_frontier_status_probe_mode_no_go
revise_goal5377_claim_boundary
block_goal5377_due_to_genericity_or_abi_issue
```
