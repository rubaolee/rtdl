# Goal5231 ModelNet40 Denominator-Explicit Performance Matrix Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_denominator_explicit_performance_matrix__no_ratio_claim
```

Goal5231 builds a performance matrix for the Goal5229 ModelNet40 all-400
unique-pair run and links it to the Goal5230 all-2000 record coverage result.
The matrix is deliberately denominator-explicit: author internal timing,
author process wall timing, RTDL route timing, and RTDL full app timing are
reported as separate scopes. Ratios are computed only as diagnostics and are
explicitly not authorized as speedup, parity, or paper-performance claims.

## Input Evidence

```text
unique-pair evidence:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json

record-coverage evidence:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5230_modelnet40_all2000_record_coverage_summary_2026-07-09.json

output matrix:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5231_modelnet40_performance_matrix_2026-07-09.json
```

The unique-pair evidence contains 400 matched ModelNet40 pairs after
author-float32 normalization. The record-coverage evidence maps the paper-log
2000 records to those 400 unique pairs with five duplicate algorithm records
per pair.

## Matrix Summary

```text
case_count: 400
record_count: 2000
covered_record_count: 2000
all_records_covered: true
algorithm_distribution:
  Early Break: 400
  Hybrid:      1200
  Ray Tracing: 400
```

Timing scope totals:

```text
author_internal_avg_time_sec sum: 2.7705300000000013
author_process_wall_sec sum:     256.336787045002
rtdl_route_wall_sec sum:         396.20282135903835
rtdl_full_total_sec sum:         593.3385793119669
```

Median timings:

```text
author_internal_avg_time_sec median: 0.0058525
author_process_wall_sec median:     0.5232663489878178
rtdl_route_wall_sec median:         0.10844340547919273
rtdl_full_total_sec median:         0.4081716984510422
```

Largest observed RTDL case:

```text
rtdl_route_wall_sec max: 123.61829536408186
rtdl_full_total_sec max: 124.26449476927519
```

The max outlier is preserved in the matrix rather than hidden. The matrix does
not reinterpret it or remove it as noise.

Value agreement envelope:

```text
rtdl_author_abs_diff median: 7.368051571643441e-09
rtdl_author_abs_diff max:    6.59728109919655e-08
```

This remains comfortably inside the Goal5229 `1e-6` value gate.

## Diagnostic Ratios

The output JSON includes these diagnostic ratios:

```text
rtdl_route_sum_over_author_internal_sum:      143.00614732886436
rtdl_full_total_sum_over_author_internal_sum: 214.16067658966594
rtdl_route_sum_over_author_process_wall_sum:  1.5456338745850073
rtdl_full_total_sum_over_author_process_wall_sum: 2.314683686847497
```

These ratios are **not authorized performance claims**. The matrix labels them
with:

```json
"ratios_are_authorized_performance_claims": false
```

Reason: author internal `Running.AvgTime`, author process wall, RTDL route wall,
and RTDL full app total are different denominators. They expose the envelope;
they do not prove speedup, parity, or paper-performance reproduction.

## Why This Goal Matters

Earlier X-HD work correctly avoided performance ratios when denominators did
not align. Goal5231 makes that discipline concrete for the large ModelNet40
value-coverage run:

1. It keeps author internal time and author process wall separate.
2. It keeps RTDL route time and RTDL full app time separate.
3. It links performance evidence to the exact 400 matched unique pairs and the
   2000-record coverage map.
4. It prevents future summaries from picking one convenient denominator without
   showing the others.

## What This Does Not Prove

Goal5231 does **not** prove:

```text
author-vs-RTDL speedup
author-vs-RTDL parity
paper-performance reproduction
full X-HD paper reproduction
algorithm-specific Early Break / Hybrid / Ray Tracing performance reproduction
exact paper input byte identity
```

It is a performance accounting artifact for the value-covered ModelNet40
packet, not a parity claim.

## Validation

Local validation:

```text
py -m unittest \
  tests.goal5231_modelnet40_performance_matrix_test \
  tests.goal5230_modelnet40_record_coverage_test \
  tests.goal5223_modelnet40_algorithm_aware_comparator_test

Ran 18 tests in 1.377s
OK
```

Compile validation:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_modelnet40_performance_matrix.py \
  tests/goal5231_modelnet40_performance_matrix_test.py
```

Generated matrix command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_modelnet40_performance_matrix.py \
  --unique-summary Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json \
  --record-coverage Paper-reproduction-apps/x-hd-paper/results/xhd_goal5230_modelnet40_all2000_record_coverage_summary_2026-07-09.json \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_goal5231_modelnet40_performance_matrix_2026-07-09.json \
  --goal-label Goal5231
```

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_modelnet40_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5231_modelnet40_performance_matrix_2026-07-09.json
tests/goal5231_modelnet40_performance_matrix_test.py
history/internal_docs/goal5231_modelnet40_denominator_explicit_performance_matrix_result_2026-07-09.md
```

## Next Step

Send Goal5231 for strict review. If accepted, the ModelNet40 packet has:

```text
Goal5229: all 400 unique pairs match at 1e-6 after author-float32 normalization
Goal5230: all 2000 paper-log records are value-covered by the 400 unique pairs
Goal5231: denominator-explicit performance matrix for those same 400 pairs
```

The next technical frontier is not another accounting pass; it is either
additional paper workload-family coverage or a stricter, denominator-aligned
performance protocol.
