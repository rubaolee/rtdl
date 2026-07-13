# Call For Review - Goal5299 X-HD Thai -> Happy RTDL Level-B Comparison

Please strictly review Goal5299.

## Files

```text
history/internal_docs/goal5299_xhd_thai_happy_rtdl_comparison_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_exact_witness_process_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_rtdl_fast_scalar_process_pod.json
tests/goal5299_xhd_thai_happy_rtdl_comparison_test.py
```

Related author evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_happy_scaled_author.json
```

## Context

Goal5298 found three current-POD author-rerun graphics cases that match
paper-branch author-log HDResult values. Goal5299 selects one:

```text
ThaiStatuette scaled 1e-3 -> HappyBuddha
```

This goal runs RTDL on that same Level-B public Stanford case.

## Result Summary

Author rerun:

```text
HDResult = 0.21912431716918945
paper-log HDResult = 0.21912434697151184
paper-log abs diff = 2.9802322387695312e-08
author Running.AvgTime = 26.57 ms
author process wall = 2.3395375460386276 s
```

RTDL:

```text
route                  HDResult              abs diff vs author   route wall   total sec   process wall   witness exact
cell-mbr-exact-witness 0.2191243235042005    6.335e-9            5.0015s     5.9969s     6.9526s       true
cell-mbr-fast-scalar   0.2191243235042005    6.335e-9            1.0029s     2.0014s     2.9271s       false
```

The fast route uses global-bound early break and reports:

```text
global_bound_early_break = true
global_bound_early_break_count = 4,982,182
per_source_witness_exact = false
```

## Review Questions

1. Does the matrix correctly show that both RTDL routes match the current POD
   author rerun and paper-branch author-log HDResult within `1e-6`?
2. Is the distinction between `cell-mbr-exact-witness` and
   `cell-mbr-fast-scalar` correctly stated?
3. Is it correct to allow the fast route as exact scalar HDResult evidence but
   forbid exact per-source witness claims for that route?
4. Is the denial of exact paper dataset identity and full paper/figure
   reproduction still correct?
5. Is it correct to refuse an author-vs-RTDL performance ratio, given that
   author `Running.AvgTime`, author process wall, RTDL route wall, RTDL total,
   and RTDL process wall remain different denominators?
6. Are the tests sufficient for this stage: two routes present, both scalar
   matched, exact route witness exact, fast route witness not exact, and ratio
   claim disabled?
7. Should the next step continue to another Goal5298 value-matched case, or
   consolidate these graphics Level-B cases into a review packet first?

## Expected Verdict Labels

```text
approve_goal5299_thai_happy_level_b_rtdl_comparison__scalar_matched_no_ratio
revise_goal5299_witness_or_denominator_claim_boundary
block_goal5299_due_to_incorrect_value_or_route_evidence
```
