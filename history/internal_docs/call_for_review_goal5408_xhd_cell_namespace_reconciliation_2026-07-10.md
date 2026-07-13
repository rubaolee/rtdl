# Call For Review: Goal5408 X-HD Cell Namespace Reconciliation

Please strictly review:

```text
history/internal_docs/goal5408_xhd_cell_namespace_reconciliation_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5408_cell_namespace_reconciliation_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5408_cell_namespace_reconciliation.py
tests/goal5408_cell_namespace_reconciliation_test.py
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5407_2026-07-10.md
```

## Context

Goal5407 found that sampled author `(source, cell)` rows are absent from RTDL's
real full-cover surface:

```text
RTDL full-cover rows = 24,508,120 = 56 * 437,645
author raw rows      = 27,133,990 = 62 * 437,645
delta                = 2,625,870 = 6 * active_count
```

Goal5408 checks whether the absence is merely a compact-cell-id vs
original-grid-cell-id namespace mismatch.

## Requested Review Questions

1. Does the artifact correctly preserve Goal5407's row-count and hash context?
2. Does the script correctly build compact->original cell-id lookup from the
   generic RTDL grid cell columns?
3. Does the artifact correctly show that author sample cells are not RTDL
   original cell ids?
4. Does the artifact correctly show that author sample cells exist as global
   compact ids but are not present for the sampled author source ids?
5. Is the conclusion justified that simple compact/original namespace remapping
   does not recover the sampled author rows?
6. Does the report avoid claiming explicit `-lb` support, row/hash parity,
   Figure 7/11 reproduction, performance parity, exact dataset reproduction, or
   full paper reproduction?
7. Is the recommended Goal5409 direction correct: status-machine semantics or
   fail-closed decision rather than direct native fix?
8. Are the tests sufficient for this diagnostic stage?

## Expected Verdict Labels

Approve:

```text
approve_goal5408_cell_namespace_reconciliation__simple_remap_not_enough
```

Revise:

```text
revise_goal5408_before_using_as_status_machine_decision_input
```

Block:

```text
block_goal5408_due_to_invalid_cell_namespace_evidence
```

## Claim Boundary To Preserve

Allowed:

```text
The compact/original namespace check does not recover sampled author rows.
The remaining gap is not explained by simple RTDL compact/original id remapping.
Goal5409 should decide status-machine semantics vs fail-closed explicit -lb.
```

Forbidden:

```text
explicit -lb support;
author row/hash parity;
Figure 7 or Figure 11 reproduction;
author-vs-RTDL performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction;
hard-coding 6 or 62 rows per active.
```
