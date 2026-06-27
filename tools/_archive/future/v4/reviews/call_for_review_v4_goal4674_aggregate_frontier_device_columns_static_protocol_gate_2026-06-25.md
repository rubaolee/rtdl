# Call For Review: V4 Goal4674 Aggregate-Frontier Device Columns Static/Protocol Gate

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4674_static_protocol_gate_continue_goal4675`
- `accept_with_required_amendments`
- `reject_goal4674_target_or_protocol`

## Files To Review

- `future/v4/v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.md`
- `future/v4/evidence/v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.json`
- `tests/v4_goal4674_aggregate_frontier_device_columns_gate_test.py`
- `src/rtdsl/aggregate_tree_reference.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`

## Review Questions

1. Does Goal4674 correctly classify `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` as a
   valid local V4 target while keeping POD and release claims blocked?
2. Does the static source audit prove enough for Goal4675 local runner work:
   app-generic surface, no old host-row collector wrapping, and forbidden host
   frontier materialization before partner continuation?
3. Is the V2.14 denominator correctly frozen as aggregate-frontier row
   collection plus explicit CuPy/Numba weighted-vector continuation?
4. Is the V3.0.2 caveat correct: the device-column primitive already exists
   there, so V4/V3 parity cannot be sold as a clean new V4 speed win?
5. Are the correctness contract, frozen later POD bars, and kill conditions
   strong enough to prevent another weak or post-hoc performance claim?
6. Does Goal4674 preserve the boundary that the old aggregate-tree fused
   weighted-vector sum cannot be promoted as-is?
7. Does this review authorize only Goal4675 local runner productization, not POD
   benchmarking, release, public speedup wording, or whole-app high-performance
   wording?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, POD spend, RT-core speedup wording,
true-zero-copy wording, C ABI, embedding, non-Python hosts, arbitrary callback
claims, or app-identity native kernels.
