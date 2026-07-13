# Call For Review: Goal5231 ModelNet40 Denominator-Explicit Performance Matrix

Please strictly review Goal5231.

## Files To Review

```text
history/internal_docs/goal5231_modelnet40_denominator_explicit_performance_matrix_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_modelnet40_performance_matrix.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5231_modelnet40_performance_matrix_2026-07-09.json
tests/goal5231_modelnet40_performance_matrix_test.py
```

Context files:

```text
history/internal_docs/goal5229_modelnet40_author_float32_normalization_result_2026-07-09.md
history/internal_docs/goal5230_modelnet40_all2000_record_coverage_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5230_modelnet40_all2000_record_coverage_summary_2026-07-09.json
```

## Requested Review Questions

1. Does Goal5231 correctly use the Goal5229 all-400 matched unique-pair summary
   as its case source?
2. Does it correctly link the Goal5230 all-2000 record coverage result without
   pretending that all 2000 records were individually rerun?
3. Are the four timing denominators correctly separated?

```text
author_internal_avg_time_sec
author_process_wall_sec
rtdl_route_wall_sec
rtdl_full_total_sec
```

4. Does the matrix correctly mark diagnostic ratios as **not authorized
   performance claims**?
5. Are the reported totals and medians consistent with the JSON evidence?
6. Does the result avoid author speedup, parity, full paper reproduction, or
   algorithm-specific performance claims?
7. Does the test suite adequately guard the denominator boundaries and reject
   unmatched unique cases?
8. Does the script remain app-owned accounting infrastructure rather than a new
   RTDL core or native primitive?
9. Is it acceptable that the matrix preserves the large RTDL max outlier rather
   than filtering it?
10. Should Goal5231 be closed as
   `completed_modelnet40_denominator_explicit_performance_matrix__no_ratio_claim`?

## Expected Answer Shape

```text
Verdict:
  approve_goal5231_modelnet40_denominator_explicit_performance_matrix
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  ...
```

## Claim Boundary To Enforce

Allowed:

```text
Goal5231 reports a denominator-explicit performance matrix for the same 400
ModelNet40 unique pairs that matched in Goal5229 and the 2000 record coverage
map from Goal5230.
```

Forbidden:

```text
RTDL is faster than author.
RTDL has author parity.
The ratios are paper-performance claims.
All 2000 records were individually rerun.
Algorithm-specific Early Break / Hybrid / Ray Tracing performance is reproduced.
Full X-HD paper reproduction is complete.
```
