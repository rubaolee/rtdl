# Goal5168 - Generic Parallel Nearest-Cell-MBR Seed Result

Date: 2026-07-08

## Objective

Optimize the generic `seed_nearest_witness_from_nearest_cell_mbr_numpy_columns`
helper by adding a Numba `prange` executor for the query-independent seed loop.

This attacks the largest measured full public res4 route phase after Goal5167:
nearest-cell-MBR seed construction. It remains an app-neutral RTDL helper
optimization, not an X-HD-specific primitive.

## Code Change

Updated:

```text
src/rtdsl/partner_continuations.py
```

Added:

```text
_seed_nearest_witness_parallel_loop_impl
```

The new implementation uses Numba `prange` over query rows. Each query writes
only its own output row, so the parallelization does not change tie-break
semantics. Explicit executor modes are now:

```text
numpy
numba
numba_parallel
auto
```

`auto` selects `numba_parallel` when Numba is available, otherwise it falls back
to the existing paths.

Added:

```text
tests/goal5168_parallel_nearest_cell_mbr_seed_test.py
```

The test verifies:

- `numba_parallel` matches NumPy and serial Numba seed outputs;
- `auto` may expose `numba_parallel`;
- the parallel seed implementation source window remains app-neutral;
- the POD artifact, when present, preserves no-ratio boundaries and records
  `numba_parallel_loop_min_distance_then_cell_id`.

Updated:

```text
tests/goal5161_numba_nearest_cell_mbr_seed_test.py
```

The older auto-executor test now accepts `numba_parallel` as a valid auto
selection while retaining explicit serial Numba coverage.

## Local Validation

```text
py -m unittest tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5167_grid_cell_mbr_reduceat_test \
  tests.goal5166_xhd_res4full_scaling_test

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
python3 -m unittest tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5167_grid_cell_mbr_reduceat_test \
  tests.goal5166_xhd_res4full_scaling_test

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
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5168_parallel_seed_matrix_pod.json
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5168_parallel_seed_matrix_pod.json
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

author Running.AvgTime = 4.576 ms
author process wall = 1.1826044917106628 s
RTDL route median = 0.0394270122051239 s
RTDL total median = 0.07910500466823578 s

ratios_authorized = false
```

Per-direction median phases after Goal5168:

```text
directed_a_to_b:
  direction_total = 0.018984682857990265 s
  grid_cell_mbrs = 0.002142861485481262 s
  initial_state_seed = 0.003177344799041748 s
  frontier_rows = 0.006241209805011749 s
  nearest_continuation = 0.004992879927158356 s
  max_nearest_reduction = 0.000725969672203064 s
  initial_cell_mbr_selection = numba_parallel_loop_min_distance_then_cell_id

directed_b_to_a:
  direction_total = 0.020141616463661194 s
  grid_cell_mbrs = 0.0015691965818405151 s
  initial_state_seed = 0.0032317936420440674 s
  frontier_rows = 0.0075620487332344055 s
  nearest_continuation = 0.004951462149620056 s
  max_nearest_reduction = 0.0010279342532157898 s
  initial_cell_mbr_selection = numba_parallel_loop_min_distance_then_cell_id
```

## Comparison To Goal5167

Goal5167 full-res4 route median:

```text
0.051644258201122284 s
```

Goal5168 full-res4 route median:

```text
0.0394270122051239 s
```

The route improves by about 12.2 ms on this POD run. The seed phase improves
more directly:

```text
Goal5167 combined seed median:
  0.009955748915672302 + 0.010062150657176971
  = 0.020017899572849274 s

Goal5168 combined seed median:
  0.003177344799041748 + 0.0032317936420440674
  = 0.0064091384410858154 s
```

So the measured seed phase falls by about 13.6 ms.

## Interpretation

This is a generic system optimization. The seed loop is independent per query,
so Numba `prange` is a natural executor-level improvement. The full-res4 route
now has no single dominant Python helper phase: native frontier rows and
nearest continuation are the next largest measured route components.

## What This Proves

- The parallel seed executor preserves NumPy and serial Numba seed semantics.
- The full public res4 Level B route still matches author HDResult.
- The measured seed phase improves on the POD run.

## What This Does Not Prove

- It does not prove exact paper dataset reproduction.
- It does not prove full X-HD paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Status

```text
goal5168_parallel_nearest_cell_mbr_seed_complete__review_pending
```
