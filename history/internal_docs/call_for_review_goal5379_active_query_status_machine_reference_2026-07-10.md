# Call For Review - Goal5379 Generic Active-Query Status-Machine Reference

Date: 2026-07-10

Please strictly review Goal5379.  This is a CPU/NumPy generic reference
implementation for active-query/status-machine semantics.  It is **not**
explicit X-HD `-lb` support and not a native backend claim.

## Files To Review

Result report:

```text
history/internal_docs/goal5379_active_query_status_machine_reference_result_2026-07-10.md
```

Result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5379_active_query_status_machine_reference.json
```

Implementation:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
```

Tests:

```text
tests/goal5379_active_query_status_machine_reference_test.py
tests/goal5279_generic_heavy_offload_worklist_test.py
tests/goal5280_heavy_offload_non_xhd_consumer_gate_test.py
```

Preceding decision:

```text
history/internal_docs/goal5378_xhd_lb_status_machine_direction_decision_2026-07-10.md
```

## Review Questions

1. Does Goal5379 implement a genuinely app-neutral active-query/status-machine
   reference, rather than an X-HD-specific shortcut?

2. Is it correct that the new API belongs in RTDL system space, given that it
   models generic active query state, offload rows, miss rows, completed rows,
   and continuation feedback?

3. Does the implementation avoid paper/app vocabulary in core code?

4. Do the tests adequately cover completed, offload, miss, and aborted rows?

5. Do the tests adequately cover continuation feedback into current-best state
   by `active_queue_index`?

6. Does the overflow behavior correctly fail closed with no partial output
   rows?

7. Does this reference layer correctly build on, rather than replace, the
   existing Goal5279/5280 generic heavy-offload worklist assets?

8. Is the report's claim boundary strict enough: no explicit `-lb`, no row
   parity, no Figure 7/11, no native backend, no performance claim, no full
   paper reproduction?

9. Is Goal5380 correctly identified as the next native/POD step only after this
   reference contract?

10. Should Goal5379 be approved, amended, or blocked?

## Expected Answer Shape

Please answer in this form:

```text
Verdict:
  approve_goal5379_generic_active_query_status_machine_reference
  or approve_with_required_amendments
  or revise_goal5379_reference_contract
  or block_goal5379_due_to_genericity_or_semantic_gap

Blocking findings:
  - ...

Required amendments:
  - ...

Non-blocking notes:
  - ...

Answers to the 10 review questions:
  1. ...
  ...
  10. ...
```

## Claim Boundary To Enforce

Goal5379 may claim:

```text
RTDL has a generic CPU/NumPy active-query/status-machine reference contract.
The contract can be used as the semantic baseline for a future native
author-oracle probe.
```

Goal5379 must not claim:

```text
explicit X-HD -lb support;
row-count parity with author OffloadingSize;
same-denominator Figure 11 memory parity;
Figure 7 or Figure 11 reproduction;
author RT-core algorithm parity;
performance improvement;
native backend completion;
exact paper dataset reproduction;
full X-HD paper reproduction.
```
