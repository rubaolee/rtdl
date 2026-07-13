# Call For Review - Goal5270 X-HD Figure 6 Exact-Input Availability Decision

Please strictly review:

```text
history/internal_docs/goal5270_xhd_figure6_exact_input_availability_decision_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5270_figure6_exact_input_availability_decision_2026-07-09.json
tests/goal5270_xhd_figure6_exact_input_decision_test.py
```

## Review Context

Goal5268 mapped the author Figure 6 pruning-effectiveness script and found that
the LB=256/full-XHD variant fails `check=true` on the current Level-B
public/same-source Dragon -> AsianDragon scaled candidate.

Goal5269 scanned LB thresholds and found that `lb=2048` is correctness-clean on
the current candidate, but `lb=256` is not. Goal5270 decides whether this can
still be called Figure 6 reproduction.

## Questions

1. Does the POD availability evidence support that the author exact
   `/local/storage/shared/HDDatasets/graphics` inputs are unavailable?
2. Is it correct to treat `/tmp/xhd_goal5234/data/*` as candidate Level-B inputs
   rather than exact paper inputs?
3. Does the report correctly preserve the author Figure 6 contract
   (`eb/prune/lb` variants, especially `lb=256` for XHD)?
4. Does it correctly carry forward Goal5269's finding that `lb=2048` passes but
   is not authorized as a Figure 6 substitute?
5. Is the decision to keep Figure 6 in `not_reproduced` status correct?
6. Is authorizing only a separately named Level-B pruning diagnostic the right
   next step if exact files remain unavailable?
7. Does the packet avoid claims of full paper reproduction, exact paper dataset
   identity, author RT-core equivalence, and performance ratio?
8. Are the tests sufficient for this decision-boundary goal?

## Expected Verdict Labels

Use one:

```text
approve_goal5270_exact_inputs_unavailable_level_b_diagnostic_only
revise_goal5270_figure6_decision_boundary
block_goal5270_due_to_unproven_input_availability_or_overclaim
```
