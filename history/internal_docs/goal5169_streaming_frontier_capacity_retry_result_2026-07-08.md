# Goal5169 - Streaming Native Frontier Capacity Retry Result

Date: 2026-07-08

## Objective

Reduce avoidable allocation overhead in the generic native 3-D cell-MBR frontier
helper for streaming consumers.

After Goal5168, full public res4 showed native frontier rows as one of the
largest remaining phases. Inspection found that
`cell_mbr_nearest_frontier_native_3d_optix_columns` inferred default
`row_capacity = query_count * cell_count`, even when `emit_pruned_rows=False`
and the X-HD streaming route only consumes active frontier rows. For full res4,
that means allocating for millions of rows while emitting about 18k/22k rows.

## Code Change

Updated:

```text
src/rtdsl/partner_continuations.py
```

When all of the following are true:

```text
row_capacity is None
emit_pruned_rows is False
```

the helper now uses a smaller inferred initial capacity:

```text
min(query_count * cell_count, max(query_count * 8, 1024))
```

If the native backend reports fail-closed overflow, the wrapper doubles capacity
and retries until the original `query_count * cell_count` full capacity. If the
caller supplies an explicit `row_capacity`, the old fail-closed behavior remains:
no silent retry and no partial result.

New metadata:

```text
full_row_capacity
row_capacity_policy
row_capacity_attempts
```

Added:

```text
tests/goal5169_streaming_frontier_capacity_retry_test.py
```

The test verifies:

- inferred streaming capacity is smaller than full capacity;
- fail-closed overflow retries safely;
- explicit capacity still fails without retry;
- the POD artifact, when present, preserves no-ratio boundaries.

## Local Validation

```text
py -m unittest tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5160_active_frontier_rows_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 14 tests OK
```

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

POD tests:

```text
python3 -m unittest tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5160_active_frontier_rows_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 13 tests OK
```

POD matrix command:

```text
cd /root/rtdl_goal5093 &&
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5169_frontier_capacity_matrix_pod.json
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5169_frontier_capacity_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Result

```text
case = res4full
matched = true
point_count_a = 5205
point_count_b = 7108
validation_mode = author-only

author HDResult = 0.1241602823138237
RTDL author_comparison_distance = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09

author Running.AvgTime = 4.548 ms
author process wall = 1.1420316100120544 s
RTDL route median = 0.03561349958181381 s
RTDL total median = 0.07466382533311844 s

ratios_authorized = false
```

Per-direction median phases after Goal5169:

```text
directed_a_to_b:
  direction_total = 0.017731785774230957 s
  grid_cell_mbrs = 0.0020945072174072266 s
  initial_state_seed = 0.003166764974594116 s
  frontier_rows = 0.0050322189927101135 s
  nearest_continuation = 0.00507529079914093 s
  max_nearest_reduction = 0.0007164850831031799 s

directed_b_to_a:
  direction_total = 0.017489701509475708 s
  grid_cell_mbrs = 0.0015735328197479248 s
  initial_state_seed = 0.0030209720134735107 s
  frontier_rows = 0.005178585648536682 s
  nearest_continuation = 0.004898935556411743 s
  max_nearest_reduction = 0.0010363459587097168 s
```

## Comparison To Goal5168

Goal5168 full-res4 route median:

```text
0.0394270122051239 s
```

Goal5169 full-res4 route median:

```text
0.03561349958181381 s
```

The route improves by about 3.8 ms on this POD run. The measured native frontier
phase improves more directly:

```text
Goal5168 combined frontier median:
  0.006241209805011749 + 0.0075620487332344055
  = 0.013803258538246155 s

Goal5169 combined frontier median:
  0.0050322189927101135 + 0.005178585648536682
  = 0.010210804641246796 s
```

So the measured frontier phase falls by about 3.6 ms.

## Interpretation

This is a modest but real generic system improvement. It removes over-allocation
for streaming consumers without relaxing fail-closed overflow behavior.

The result also shows that frontier cost is not only output allocation: native
traversal, launch, BVH/build, atomic append, host/device transfer, and final row
sort still contribute. After Goal5169, native frontier rows and nearest
continuation are roughly tied as the largest measured phases.

## What This Proves

- Streaming native frontier consumers can avoid default full-capacity output
  allocation.
- Explicit caller-supplied capacity still fails closed without retry.
- The full public res4 Level B route still matches author HDResult.
- The measured native frontier phase improves on the POD run.

## What This Does Not Prove

- It does not prove exact paper dataset reproduction.
- It does not prove full X-HD paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Status

```text
goal5169_streaming_frontier_capacity_retry_complete__review_pending
```
