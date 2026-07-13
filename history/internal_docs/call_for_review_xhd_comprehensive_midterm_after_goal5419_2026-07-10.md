# Call For Review - X-HD Comprehensive Midterm After Goal5419

Please strictly review the current X-HD comprehensive midterm packet after the
same-POD graphics matrix.

## Files To Review

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5419_2026-07-10.md
history/internal_docs/goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_result_2026-07-10.md
history/internal_docs/call_for_review_goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.py
tests/goal5419_figure5_level_b_same_pod_graphics_matrix_test.py
```

Context:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5418_2026-07-10.md
history/internal_docs/goal5418_figure5_level_b_same_pod_matrix_readiness_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json
```

## Expected Verdict Labels

Choose one:

```text
approve_xhd_midterm_after_goal5419
approve_with_required_amendments
revise_xhd_midterm_after_goal5419_before_goal5420
block_goal5420_until_midterm_fixed
```

## Review Questions

1. Does the midterm correctly state that full X-HD paper reproduction is still
   incomplete?
2. Does it keep Level-B same-source public graphics evidence separate from
   exact paper dataset reproduction?
3. Does it accurately report the Goal5419 same-POD matrix and all three
   graphics cases?
4. Does it correctly state that the min-bound translation preprocessing is
   required, and that omitting it changes the scalar HDResult?
5. Does it keep author `Running.AvgTime`, author process wall, RTDL route wall,
   RTDL process wall, input load, and witness exactness as separate denominator
   columns?
6. Does it refuse author-vs-RTDL ratios and Figure 5 reproduction claims?
7. Does it clearly distinguish `cell-mbr-fast-scalar` scalar correctness from
   exact per-source witness reproduction?
8. Does it report the unfavorable case where fast-scalar is slower than
   exact-witness on `thai_asian_scaled`?
9. Does it correctly fail-close / stop the explicit `-lb` line and avoid
   drifting back into row-identity reverse engineering?
10. Is the recommended Goal5420 decision point appropriate, or should bounded
    geo / exact-data work be ordered differently?
11. Are any implemented/review-pending goals incorrectly promoted to externally
    reviewed status?

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
11. ...
```
