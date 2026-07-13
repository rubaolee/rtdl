# Call For Review - Goal5300 X-HD Thai -> Asian RTDL Level-B Comparison

Please strictly review Goal5300.

## Files Under Review

```text
history/internal_docs/goal5300_xhd_thai_asian_rtdl_comparison_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_rtdl_fast_scalar_process_pod.json
tests/goal5300_xhd_thai_asian_rtdl_comparison_test.py
```

## Context

Goal5298 identified `ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3` as
an author-only Level-B graphics candidate:

```text
author HDResult    = 0.28763842582702637
paper-log HDResult = 0.28763845562934875
abs diff           = 2.98e-08
```

Goal5300 runs RTDL on the same public Stanford files on the current POD. It is
not exact paper dataset reproduction and not Figure 5 reproduction.

## Summary To Review

RTDL results:

```text
cell-mbr-exact-witness:
  HDResult = 0.2876384148709406
  route wall ~= 10.764s
  per_source_witness_exact = true

cell-mbr-fast-scalar:
  HDResult = 0.2876384148709406
  route wall ~= 12.505s
  per_source_witness_exact = false
  global_bound_early_break_count = 3,900,606
```

Both routes match the author rerun and paper-log scalar HDResult within `1e-6`.
On this pair, exact-witness is faster than fast-scalar because fast-scalar
produces millions of frontier rows and spends most time in nearest continuation.

## Review Questions

1. Does the Goal5298 author-only evidence support using this pair as a
   value-matched Level-B candidate?
2. Does the Goal5300 matrix correctly compare RTDL scalar HDResult to the
   author rerun and paper-log values?
3. Is it correct to classify exact-witness as exact per-source witness evidence?
4. Is it correct to classify fast-scalar as scalar-only evidence with approximate
   per-source witnesses?
5. Does the report correctly note that fast-scalar is slower than exact-witness
   on this pair, rather than treating the route label as a speed promise?
6. Is the refusal to report an author-vs-RTDL performance ratio correct?
7. Does Goal5300 avoid claiming exact paper dataset identity, Figure 5
   reproduction, full paper reproduction, or author RT-core equivalence?
8. Should Goal5300 be closed as Level-B same-source RTDL comparison evidence?

## Expected Answer Shape

```text
Verdict:
  approve_goal5300_thai_asian_level_b_rtdl_comparison__scalar_matched_no_ratio
  OR revise_goal5300_claim_boundary_or_witness_status
  OR block_goal5300_due_to_incorrect_value_or_route_evidence

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
```
