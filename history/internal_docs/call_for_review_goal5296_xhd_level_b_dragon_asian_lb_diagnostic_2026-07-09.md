# Call For Review - Goal5296 X-HD Level-B Dragon -> AsianDragon LB Diagnostic

Date: 2026-07-09

Please strictly review Goal5296.

## Review Scope

Goal5296 runs the author `hd_exec` binary on the currently available temporary
Dragon -> AsianDragon input with `lb=0` and `lb=256`.

This is a **separately named Level-B author-only diagnostic**. It is not Figure
7 reproduction, not RTDL execution, not an author-vs-RTDL ratio, and not an
exact paper input claim.

## Files Under Review

```text
history/internal_docs/goal5296_xhd_level_b_dragon_asian_lb_diagnostic_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
tests/goal5296_xhd_level_b_lb_diagnostic_test.py
```

Supporting context:

```text
history/internal_docs/goal5292_xhd_figure7_load_balance_audit_result_2026-07-09.md
history/internal_docs/goal5295_xhd_figures7_8_10_pod_dataset_availability_result_2026-07-09.md
```

## Evidence Summary

Input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
```

These are temporary POD inputs, not proven exact paper inputs and not enough to
reconstruct the full Figure 7 matrix.

Author run results:

```text
lb=0:
  HDResult = 52.453487396240234
  Running.AvgTime = 107.254 ms
  wall = 16.25388788431883 s
  LargeCells = 0
  WL Heavy Peak = 0
  Iteration 3 ComparedPoints = 7,969,408,615
  Iteration 3 RTTime = 96.854 ms
  Iteration 3 CUDATime = 0.054 ms

lb=256:
  HDResult = 52.453487396240234
  Running.AvgTime = 131.841 ms
  wall = 17.09253077954054 s
  LargeCells = 5060
  WL Heavy Peak = 217,071,920
  Iteration 3 ComparedPoints = 1,242,037,623
  Iteration 3 RTTime = 45.519 ms
  Iteration 3 CUDATime = 75.923 ms
  Iteration 3 OffloadingSize = 27,133,990
```

Interpretation under review:

```text
The two author runs return equal HDResult. On this temporary input, lb=256
reduces iteration-3 compared points and RTTime but adds heavy offload work and
is slower by single-run author Running.AvgTime and process wall. This is useful
as Level-B author-side load-balance evidence, but it is not Figure 7
reproduction and not an RTDL comparison.
```

## Review Questions

1. Is this correctly framed as a separately named Level-B author-only diagnostic
   rather than Figure 7 reproduction?
2. Are the input paths correctly treated as temporary POD inputs, not exact
   paper inputs?
3. Does the evidence correctly show that `lb=0` and `lb=256` return the same
   author HDResult?
4. Does the evidence correctly show that `lb=256` reduces iteration-3 compared
   points / RTTime but increases heavy offload work and CUDATime?
5. Is it correct not to claim a load-balance speedup from this diagnostic,
   since `lb=256` is slower by author `Running.AvgTime` and process wall?
6. Does the result avoid RTDL claims, author-vs-RTDL ratios, exact dataset
   claims, or Figure 7 reproduction?
7. Is the recommended next step correct: either recover exact HDDatasets and
   regenerate the real author matrix, or authorize a separate Level-B RTDL
   diagnostic?
8. Can Goal5296 be marked externally reviewed and approved, or are amendments
   required?

## Expected Answer Shape

Please answer with:

```text
verdict_label: ...
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  Q1: ...
  Q2: ...
  ...
  Q8: ...
recommended_next_action:
```

Acceptable verdict examples:

```text
approve_goal5296_level_b_dragon_asian_author_lb_diagnostic_not_figure7
revise_goal5296_lb_diagnostic_claim_boundary_or_input_status
block_goal5296_due_to_incorrect_author_lb_evidence
```
