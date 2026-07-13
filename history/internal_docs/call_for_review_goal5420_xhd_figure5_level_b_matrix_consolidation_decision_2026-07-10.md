# Call For Review - Goal5420 X-HD Figure 5 Level-B Matrix Consolidation Decision

Please strictly review Goal5420.

## Files To Review

```text
history/internal_docs/goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5420_figure5_level_b_matrix_consolidation_decision.py
tests/goal5420_figure5_level_b_matrix_consolidation_decision_test.py
```

Context:

```text
history/internal_docs/goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_result_2026-07-10.md
history/internal_docs/call_for_review_goal5419_xhd_figure5_level_b_same_pod_graphics_matrix_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5419_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
```

## Expected Verdict Labels

Choose one:

```text
approve_goal5420_figure5_level_b_matrix_consolidation_decision
approve_with_required_amendments
revise_goal5420_before_next_goal
block_goal5420_due_to_claim_boundary_or_next_step_error
```

## Review Questions

1. Does Goal5420 correctly consolidate the Goal5419 same-POD graphics matrix
   rather than claiming a new execution result?
2. Does it preserve the three graphics rows only (`dragon_happy`,
   `thai_happy_scaled`, `thai_asian_scaled`) and keep `dragon_asian_scaled`
   excluded?
3. Does it correctly preserve the required RTDL graphics preprocessing
   `translate_each_input_to_min_bound`?
4. Does it correctly state that all author reruns match paper-branch author-log
   scalar values and all RTDL routes match same-POD author rerun scalar values,
   while still remaining Level-B evidence?
5. Does it refuse Figure 5 reproduction, exact paper dataset reproduction,
   full paper reproduction, and author-vs-RTDL performance ratios?
6. Does the decision correctly stop route micro-optimization as the default next
   step?
7. Does it correctly keep the explicit `-lb` row-identity line stopped?
8. Is the decision to authorize a **bounded geo packet plan**, but not bounded
   geo execution yet, appropriate?
9. Are the two geo candidates (`county_zcta_bounded` and `water_bg_bounded`)
   correctly represented as bounded fixtures using a separate partner/Triton
   route family?
10. Does the builder avoid running POD commands or hidden subprocess execution?
11. Is Goal5421, as a bounded geo same-POD packet plan, the right next goal?

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
