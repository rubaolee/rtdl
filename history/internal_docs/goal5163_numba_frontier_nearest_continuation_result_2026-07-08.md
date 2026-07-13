# Goal5163 - Numba Frontier Nearest Continuation Result

## Verdict

`completed_numba_frontier_nearest_continuation_executor`

## What Changed

Goal5163 adds a generic executor option to:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns(...)
```

The helper now accepts:

```text
executor: "auto" | "numpy" | "numba" = "auto"
```

Behavior:

- `executor="numpy"` preserves the Goal5157 vectorized expand + lexsort path.
- `executor="numba"` scans active frontier row spans in a compiled loop and
  updates each query's current best witness directly.
- `executor="auto"` uses Numba when available and falls back to NumPy otherwise.

This is a generic nearest-witness continuation over generic cell-MBR frontier
rows. It is not an X-HD-specific primitive.

## Why This Was The Next Target

Goal5162 showed the sample2048 post-Goal5161 profile was dominated by nearest
continuation:

```text
sample2048 route median ~= 0.0586s
nearest continuation combined ~= 0.0339s
```

So the next measured target was the generic nearest continuation over active
frontier rows.

## Semantics

The Numba executor preserves:

- pruned rows are ignored;
- inline/offload rows are scanned;
- existing seeded current-best distances/items remain valid;
- a candidate updates a query if it is closer;
- if the distance ties, the lower target item id wins.

The implementation keeps an internal squared-distance best state so exact
tie-breaks are not disturbed by `sqrt` round-trip comparisons.

## Files Changed

```text
src/rtdsl/partner_continuations.py
tests/goal5157_vectorized_frontier_nearest_continuation_test.py
tests/goal5163_numba_frontier_nearest_continuation_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_numba_continuation_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample2048 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_numba_continuation_profile_pod.json
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_numba_continuation_profile_pod.json
```

## Results

```text
case = sample2048
point_count_a = 2048
point_count_b = 2048
matched = true
author Running.AvgTime = 4.245 ms
RTDL route median = 0.025455787777900696 s
RTDL total median = 0.03902154415845871 s
validation_mode = author-only
ratios_authorized = false
```

Directional median phase profile:

```text
A->B:
  grid_cell_mbrs = 0.004754737019538879 s
  seed = 0.003442130982875824 s
  frontier_rows = 0.00321853905916214 s
  nearest_continuation = 0.0011857599020004272 s
  max_nearest_reduction = 0.000264681875705719 s
  frontier_row_count = 5852
  total_candidate_distance_evaluations = 85761

B->A:
  grid_cell_mbrs = 0.0043215155601501465 s
  seed = 0.0028838664293289185 s
  frontier_rows = 0.002722024917602539 s
  nearest_continuation = 0.0011366084218025208 s
  max_nearest_reduction = 0.00027139484882354736 s
  frontier_row_count = 5594
  total_candidate_distance_evaluations = 80737
```

## Before / After Against Goal5162

The comparable Goal5162 sample2048 production matrix reported:

```text
RTDL route median = 0.05855253338813782 s
nearest continuation combined ~= 0.0339 s
```

Goal5163 reports:

```text
RTDL route median = 0.025455787777900696 s
nearest continuation combined ~= 0.00232 s
```

So, for the RTDL route itself:

```text
sample2048 route improvement ~= 2.30x vs Goal5162
```

## Interpretation

Goal5163 removes the sample2048 continuation bottleneck. The route is now more
balanced: grid construction, seed, and frontier rows are all in the low
milliseconds per direction, while continuation is no longer dominant.

This still does not authorize an author-vs-RTDL ratio. Author `Running.AvgTime`,
author process wall, RTDL route time, and RTDL total time are different phase
boundaries.

## Validation

Local:

```text
py -m unittest tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5162_xhd_sample2048_post_numba_seed_profile_test
Ran 14 tests OK (skipped=1 before artifact existed)
```

POD:

```text
python3 -m unittest tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5162_xhd_sample2048_post_numba_seed_profile_test
Ran 14 tests OK (skipped=1)
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a generic Numba executor for nearest-witness continuation over
cell-MBR frontier rows and measured RTDL-route phase reduction on a
representative same-source sample2048 fixture.
