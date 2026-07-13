# Goal5261 - X-HD hd_exec Entrypoint All-400 Performance Matrix Result

Date: 2026-07-09

## Objective

Build a denominator-separated performance matrix for the RTDL
`hd_exec`-compatible all-400 ModelNet40 entrypoint evidence.

This goal does not run a new algorithm and does not change the X-HD route. It
turns two already-existing all-400 evidence files into a reproducible timing
matrix:

```text
RTDL entrypoint evidence:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json

Author rerun baseline and older RTDL harness evidence:
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
```

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py
```

The builder matches cases by `case_name` and fails closed if the two evidence
files do not contain the same case set.

## Generated Matrix

Command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py \
  --hd-exec-batch Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json \
  --author-baseline Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json
```

Top-level result:

```text
schema = rtdl.paper_reproduction.xhd.hd_exec_entrypoint_performance_matrix.v1
case_count = 400
matched_case_count = 400
per_source_witness_exact_case_count = 400
all_cases_matched = true
all_cases_per_source_witness_exact = true
```

Correctness envelope:

```text
max_author_abs_diff    = 6.59728109919655e-08
median_author_abs_diff = 7.368051571643441e-09
sum_author_abs_diff    = 4.472201816704025e-06
```

## Timing Matrix

RTDL `hd_exec`-compatible entrypoint route wall time:

```text
sum    = 420310.53318828344 ms = 420.31053318828344 s
median = 675.8961826562881 ms
max    = 13892.487451434135 ms
```

RTDL `hd_exec`-compatible batch case wall time:

```text
sum    = 600.8750001639128 s
median = 0.9885044656693935 s
max    = 14.975484907627106 s
batch elapsed = 600.8786783665419 s
```

Author rerun process wall time:

```text
sum    = 255.03741998970509 s
median = 0.5205188095569611 s
max    = 3.2167051509022713 s
```

Author internal `Running.AvgTime`:

```text
sum    = 2794.7910000000006 ms
median = 5.8 ms
max    = 70.595 ms
```

Older Goal5253 RTDL batch harness, same exact-witness route:

```text
route_wall_sec sum = 424.56292333453894 s
total_sec sum      = 621.2066570222378 s
```

## Denominator-Separated Ratios

These ratios are labels, not speedup/parity claims.

```text
RTDL hd_exec route sum / author process wall sum
  = 1.648034759782505x

RTDL hd_exec case wall sum / author process wall sum
  = 2.356026814371663x

RTDL hd_exec route median / author process wall median
  = 1.2985048191276245x

RTDL hd_exec route sum / author internal Running.AvgTime sum
  = 150.3906850953375x

RTDL hd_exec route median / author internal Running.AvgTime median
  = 116.53382459591175x

RTDL hd_exec route sum / older Goal5253 RTDL route sum
  = 0.9899840755927131x

RTDL hd_exec case wall sum / older Goal5253 RTDL total sum
  = 0.967270703511477x
```

## Interpretation

The user-facing RTDL `hd_exec`-compatible entrypoint has all-400 functional
coverage and is nearly identical to the older Goal5253 batch harness for route
time:

```text
420.31 s vs 424.56 s route wall
```

Against the author rerun process-wall denominator, the RTDL route is slower:

```text
1.65x slower by route-wall sum
2.36x slower by batch case-wall sum
```

Against the author internal `Running.AvgTime`, the gap is much larger:

```text
150.39x slower by route-wall sum
```

That last number is a phase/algorithm gap indicator, not a fair user-facing
wall-time denominator. It must not be presented without the denominator label.

## Claim Boundary

Allowed:

```text
The RTDL hd_exec-compatible entrypoint matched author rerun HDResult for all
400 public ModelNet40 pair identities, with exact per-source witnesses, and its
route-wall sum is 420.31 s for this POD run.
```

Allowed with denominator label:

```text
RTDL route-wall sum / author process-wall sum = 1.65x slower.
RTDL route-wall sum / author internal Running.AvgTime sum = 150.39x slower.
```

Forbidden:

```text
RTDL is faster than author X-HD.
RTDL has author performance parity.
RTDL Running.AvgTime is author internal Running.AvgTime.
Full X-HD paper reproduction is complete.
Exact paper byte-input identity is proved.
All X-HD paper figures are reproduced.
```

## Validation

```text
py -m unittest tests.goal5261_xhd_hd_exec_entrypoint_performance_matrix_test
```

Result:

```text
Ran 3 tests in 0.085s
OK
```

Compile check:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_hd_exec_entrypoint_performance_matrix.py \
  tests/goal5261_xhd_hd_exec_entrypoint_performance_matrix_test.py
```

Result:

```text
OK
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goals5255-5261 for consolidated strict review.
2. If accepted, update X-HD user docs so `run_xhd_rtdl_hd_exec.py` and the
   summary batch bridge become the primary RTDL user entrypoint.
3. Keep performance messaging denominator-separated until a later phase-boundary
   review explicitly authorizes a stronger comparison.
