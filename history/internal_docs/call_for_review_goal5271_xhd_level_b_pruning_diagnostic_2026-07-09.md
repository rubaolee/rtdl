# Call For Review - Goal5271 X-HD Level-B Pruning Diagnostic

Please strictly review:

```text
history/internal_docs/goal5271_xhd_level_b_pruning_diagnostic_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5271_level_b_pruning_diagnostic_2026-07-09.json
tests/goal5271_xhd_level_b_pruning_diagnostic_test.py
```

## Context

Goal5270 confirmed exact Figure 6 graphics inputs are unavailable on the current
POD. Goal5271 therefore creates only a separately named Level-B pruning
diagnostic from the current public/same-source scaled Dragon -> AsianDragon
candidate.

## Review Questions

1. Is it correct to include only correctness-clean `noopt`, `eb`, and
   `eb_prune` rows in the primary diagnostic?
2. Are the derived speedup/reduction factors computed from the source rows
   correctly?
3. Is `lb=256` correctly marked invalid on this candidate?
4. Is `lb=2048` correctly marked as a candidate-only control, not a Figure 6
   substitute?
5. Does the report avoid claiming Figure 6 reproduction, full paper
   reproduction, exact paper byte-input identity, author RT-core equivalence,
   and author/RTDL performance ratio?
6. Is this diagnostic useful as a bounded Level-B fallback while exact inputs
   remain unavailable?

## Expected Verdict Labels

Use one:

```text
approve_goal5271_level_b_pruning_diagnostic_not_figure6
revise_goal5271_diagnostic_claim_boundary_or_math
block_goal5271_due_to_figure6_overclaim
```
