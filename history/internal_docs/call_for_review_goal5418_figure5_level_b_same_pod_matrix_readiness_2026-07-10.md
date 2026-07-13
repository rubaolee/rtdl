# Call For Review - Goal5418 Figure 5 Level-B Same-POD Matrix Readiness

Please strictly review Goal5418.

## Files To Review

```text
history/internal_docs/goal5418_figure5_level_b_same_pod_matrix_readiness_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.py
tests/goal5418_figure5_level_b_same_pod_matrix_readiness_test.py
```

Context:

```text
history/internal_docs/goal5417_figure5_level_b_same_pod_matrix_plan_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
```

## Expected Verdict Labels

Choose one:

```text
approve_goal5418_figure5_level_b_same_pod_matrix_readiness
revise_goal5418_before_pod_execution
block_goal5418_execution_packet
```

## Review Questions

1. Does Goal5418 correctly remain a dry-run/readiness packet, with
   `same_pod_execution_claimed=false` and `matrix_rows_executed=0`?
2. Are the three primary graphics cases exactly the Goal5417 included cases
   (`dragon_happy`, `thai_happy_scaled`, `thai_asian_scaled`)?
3. Is `dragon_asian_scaled` correctly excluded because the author rerun does
   not match the paper-branch author-log value?
4. Do the generated author commands and RTDL commands preserve the intended
   input paths, route labels, grid shape, inline threshold, and output JSON
   paths?
   Do all RTDL graphics commands also carry
   `--translate-each-input-to-min-bound`, matching the established
   public-graphics preprocessing contract?
5. Is the `cell-mbr-exact-witness_if_operational` route correctly normalized
   to `cell-mbr-exact-witness` while keeping its conditional execution label?
6. Are the two bounded geo rows correctly deferred rather than mixed into the
   graphics hd_exec-compatible execution packet?
7. Does the packet preserve the no-ratio denominator discipline from Goal5417?
8. Does the script avoid actually running POD/SSH/author/RTDL commands?
9. Is the POD wrapper rule clear enough for Goal5419, and does it forbid naked
   SSH?
10. Does the report avoid Figure 5 reproduction, exact paper dataset, full
    paper reproduction, and performance ratio claims?

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
10. ...
```
