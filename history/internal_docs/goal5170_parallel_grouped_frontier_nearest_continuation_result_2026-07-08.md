# Goal5170 - Parallel Grouped Frontier Nearest Continuation Result

Date: 2026-07-08

## Objective

Reduce the remaining nearest-continuation cost in the generic cell-MBR frontier
route without introducing any X-HD-specific primitive.

After Goal5169, the full public Stanford res4 route showed native frontier rows
and nearest continuation as the largest measured route phases. The existing
`nearest_witness_from_cell_mbr_frontier_numpy_columns(..., executor="numba")`
scanned frontier rows serially. A naive row-parallel implementation would be
incorrect because multiple frontier rows may update the same query row. Goal5170
therefore implements a grouped-by-query parallel executor.

## Code Change

Updated:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
```

New executor:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns(..., executor="numba_parallel")
```

Implementation strategy:

```text
1. filter out pruned frontier rows;
2. stable-sort remaining frontier rows by query_row_id;
3. build group_start/group_end arrays per query;
4. run one Numba prange task per query group;
5. scan rows within each query group serially and apply the existing
   min-distance then lower-item-id tie-break.
```

This avoids cross-thread races because each parallel task writes exactly one
query row's best distance and item id.

The existing executors remain:

```text
executor="numpy"
executor="numba"
executor="auto"
```

`auto` now selects `numba_parallel` when Numba is available; otherwise it falls
back to the existing NumPy route. The route and matrix scripts now expose and
record:

```text
--frontier-nearest-executor auto|numpy|numba|numba_parallel
nearest_executor
nearest_executor_requested
nearest_reduction_strategy
```

## Tests

Added:

```text
tests/goal5170_parallel_grouped_frontier_nearest_continuation_test.py
```

The new test intentionally uses non-contiguous rows for the same query and a
pruned row, so a parallel implementation that assumes pre-contiguous rows or
updates per frontier row would be unsafe. It verifies:

- `numba_parallel` matches NumPy and serial Numba;
- the seeded current-best tie-break is preserved;
- candidate and used-frontier row counts remain correct;
- `auto` exposes the parallel executor when available;
- the source window remains app-neutral;
- the POD artifact, when present, keeps no-ratio boundaries.

Updated:

```text
tests/goal5163_numba_frontier_nearest_continuation_test.py
```

so the existing `auto` contract accepts `numba_parallel`.

## Local Validation

```text
py -m unittest tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 20 tests OK (skipped=1)
```

After downloading POD artifacts:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_serial_frontier_continuation_matrix_pod.json
py -m unittest tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5166_xhd_res4full_scaling_test

Ran 21 tests OK
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
python3 -m unittest tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5154_xhd_seeded_performance_matrix_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 19 tests OK (skipped=1)
```

POD matrix commands:

```text
cd /root/rtdl_goal5093

python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full \
  --backend optix \
  --validation-mode author-only \
  --rtdl-repeat-count 5 \
  --frontier-nearest-executor numba \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_serial_frontier_continuation_matrix_pod.json

python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full \
  --backend optix \
  --validation-mode author-only \
  --rtdl-repeat-count 5 \
  --frontier-nearest-executor numba_parallel \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_serial_frontier_continuation_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Result

Same POD, same full public Stanford res4 inputs:

```text
case = res4full
point_count_a = 5205
point_count_b = 7108
validation_mode = author-only
matched = true
author_abs_diff = 4.440050771492565e-09
```

Serial Numba control:

```text
author Running.AvgTime = 4.769 ms
RTDL route median = 0.03571823984384537 s
RTDL total median = 0.077659472823143 s

directed_a_to_b nearest_continuation = 0.005077570676803589 s
directed_b_to_a nearest_continuation = 0.004911020398139954 s
combined nearest_continuation = 0.009988591074943543 s
nearest_reduction_strategy = numba_loop_min_distance_then_item_id
```

Parallel grouped Numba:

```text
author Running.AvgTime = 4.798 ms
RTDL route median = 0.03398209810256958 s
RTDL total median = 0.07456588745117188 s

directed_a_to_b nearest_continuation = 0.0033083483576774597 s
directed_b_to_a nearest_continuation = 0.003439776599407196 s
combined nearest_continuation = 0.006748124957084656 s
nearest_reduction_strategy = numba_parallel_grouped_query_loop_min_distance_then_item_id
```

Observed delta in this same-POD control:

```text
nearest continuation: 0.00999s -> 0.00675s  (~32% lower)
route median:          0.03572s -> 0.03398s  (~4.9% lower)
total median:          0.07766s -> 0.07457s  (~4.0% lower)
```

Compared with the previous Goal5169 artifact:

```text
Goal5169 route median = 0.03561349958181381 s
Goal5170 route median = 0.03398209810256958 s
```

The improvement is small but real on this route. It is not a step-change and
does not close the author denominator gap.

## Interpretation

Goal5170 removes a real continuation cost without changing the public route
semantics. The largest remaining measured phases on the parallel artifact are
now native frontier rows and seed/grid setup rather than frontier continuation:

```text
directed_a_to_b:
  frontier_rows = 0.005183562636375427 s
  nearest_continuation = 0.0033083483576774597 s
  initial_state_seed = 0.003218613564968109 s
  grid_cell_mbrs = 0.002403341233730316 s

directed_b_to_a:
  frontier_rows = 0.005936071276664734 s
  nearest_continuation = 0.003439776599407196 s
  initial_state_seed = 0.003131955862045288 s
  grid_cell_mbrs = 0.0017878636717796326 s
```

So the next target should be selected from fresh phase evidence, likely native
frontier row production and remaining seed/grid overheads.

## What This Proves

- A race-free grouped Numba parallel continuation can consume generic
  cell-MBR frontier rows.
- It preserves seeded current-best semantics and lower-item-id tie-breaks.
- The full public res4 Level B route still matches author HDResult.
- In the same-POD control, the continuation subphase and overall route improve
  modestly.

## What This Does Not Prove

- It does not prove exact paper dataset reproduction.
- It does not prove full X-HD paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Status

```text
goal5170_parallel_grouped_frontier_nearest_continuation_complete__review_pending
```
