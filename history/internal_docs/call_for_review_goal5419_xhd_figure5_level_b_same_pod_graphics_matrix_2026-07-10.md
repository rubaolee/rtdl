# Call For Review - Goal5419 X-HD Figure 5 Level-B Same-POD Graphics Matrix

Please strictly review Goal5419.

## Files To Review

```text
history/internal_docs/goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.py
tests/goal5419_figure5_level_b_same_pod_graphics_matrix_test.py
```

Context:

```text
history/internal_docs/goal5418_figure5_level_b_same_pod_matrix_readiness_2026-07-10.md
history/internal_docs/goal5417_figure5_level_b_same_pod_matrix_plan_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
```

## Expected Verdict Labels

Choose one:

```text
approve_goal5419_figure5_level_b_same_pod_graphics_matrix
approve_with_required_amendments
revise_goal5419_before_matrix_claims
block_goal5419_due_to_denominator_or_preprocessing_error
```

## Review Questions

1. Does Goal5419 genuinely execute the three primary graphics cases from
   Goal5418 on the same POD, rather than remaining a dry-run packet?
2. Does the result keep `dragon_asian_scaled` excluded and include exactly
   `dragon_happy`, `thai_happy_scaled`, and `thai_asian_scaled`?
3. Was the `--translate-each-input-to-min-bound` precondition correctly added
   before execution, and is it clear that omitting it changes the scalar result?
4. Do all author reruns match the paper-branch author-log scalar within
   tolerance, while still remaining Level-B same-source evidence rather than
   exact paper dataset reproduction?
5. Do all RTDL routes match the same-POD author rerun scalar within tolerance?
6. Does the report correctly keep author `Running.AvgTime`, author process
   wall, RTDL route wall, RTDL process wall, and RTDL input load as separate
   denominator columns?
7. Does the report refuse author-vs-RTDL ratios and avoid implying Figure 5
   reproduction?
8. Is the `per_source_witness_exact` distinction correct, especially the
   warning that `cell-mbr-fast-scalar` is scalar-only and not exact witness
   reproduction?
9. Does the runner avoid any speedup calculation or ratio publication?
10. Is the observation that `fast-scalar` is slower than `exact-witness` on
    `thai_asian_scaled` correctly reported rather than hidden?
11. Does this matrix justify a next consolidation/review decision rather than
    another route micro-optimization by default?

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
