# Call For Review: V4 Goal4729 Barnes-Hut Deferred/Subprobe Row

Please review:

- `future/v4/v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.md`
- `future/v4/evidence/v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.json`
- `tests/v4_goal4729_barnes_hut_deferred_subprobe_row_test.py`

Context:

- `future/v4/evidence/v4_goal4676_serious_2026-06-25/summary.json`
- `future/v4/v4_goal4677_aggregate_frontier_promotion_2026-06-25.md`
- `src/rtdsl/aggregate_tree_reference.py::aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract`
- `future/v4/evidence/v4_goal4724_remaining_5_app_route_gap_audit_2026-06-26.json`

## Questions For Reviewer

1. Does this row correctly preserve aggregate-frontier as real bounded operator
   progress while blocking full Barnes-Hut app claims?
2. Is the V3.0.2 caveat visible enough: aggregate-frontier V4/V3 hot is about
   0.998x because V3 already had the same device-column family?
3. Does the row correctly block RT-core claims given `uses_optix_trace: false`
   in the fused weighted-vector contract?
4. Is the reopen condition strict enough: complete generic aggregate weighted
   workflow, parity, and app-level measurement before speed claims?

## Requested Verdict Labels

- `accept_goal4729_barnes_hut_deferred_subprobe_row`
- `accept_with_required_amendments`
- `reject_goal4729_row_overclaims_or_should_reopen`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims,
Barnes-Hut speedup wording, whole-app high-performance claims, all-benchmark
speedups, V4-over-V3 speed claims, RT-core speedup claims, POD spend, arbitrary
callback support, raw OptiX callbacks, app-specific native kernels, or hidden
V2/V3 fallbacks.

