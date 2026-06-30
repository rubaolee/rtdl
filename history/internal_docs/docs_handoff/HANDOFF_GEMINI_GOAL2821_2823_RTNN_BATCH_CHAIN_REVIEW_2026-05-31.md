# Handoff: Goal2821-Goal2823 RTNN Batch Chain Review

Please independently review the Goal2821-Goal2823 RTNN v2.5 batch-optimization
chain as a distinct external AI reviewer.

## Scope

- Goal2821: heterogeneous prepared-aggregate batch requests.
- Goal2822: fused 2D-grid block-partial batch kernel.
- Goal2823: device-side partial-reduce negative probe, reverted as default.

## Files To Inspect

- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_2026-05-31.md`
- `docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_2026-05-31.md`
- `docs/reports/goal2823_device_side_partial_reduce_negative_probe_2026-05-31.md`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/goal2821_summary.json`
- `docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_pod/goal2822_summary.json`
- `docs/reports/goal2823_rtnn_device_side_batch_partial_reduce_pod/goal2823_summary.json`
- `tests/goal2821_rtnn_heterogeneous_batched_aggregate_requests_test.py`
- `tests/goal2822_rtnn_fused_batch_block_partial_kernel_test.py`
- `tests/goal2823_device_side_partial_reduce_negative_probe_test.py`

## Facts To Verify

- Goal2821 adds generic heterogeneous request-list support and records clean pod
  evidence: 1.16x at 32K and 2.50x at 65K versus four sequential single
  aggregate calls over the same prepared handles.
- Goal2822 replaces per-request block-partial launches with one fused 2D-grid
  request/query kernel and records clean pod evidence: 1.105x at 32K and 1.085x
  at 65K versus Goal2821 batch.
- Goal2823 tested device-side final reduction of block partials, found mixed
  evidence (0.990x at 32K, 1.020x at 65K versus Goal2822), and reverted that
  implementation as the default while preserving the artifacts/report.
- Current main keeps the Goal2822 fused batch path, not the Goal2823
  device-side partial reducer.
- All reports keep public/release/paper/single-request speedup claims closed.
- The native code remains app-agnostic: fixed-radius neighbors,
  ranked-summary aggregates, request-indexed block partials, no RTNN ABI.

## Review Questions

1. Is the accepted Goal2821/Goal2822 chain a valid generic v2.5 runtime
   hardening step?
2. Is the Goal2823 reject-as-default decision correct given the mixed evidence?
3. Are the performance comparisons narrowly and fairly stated?
4. Are any claim boundaries too loose?
5. Should the next RTNN direction be CUDA graph replay, event-ordered aggregate
   chaining, or a different generic runtime change?

## Required Output

Write the review to:

`docs/reviews/goal2824_gemini_review_rtnn_batch_chain_2821_2823_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
