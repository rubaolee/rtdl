# Call For Review: Goal5392 X-HD `-lb` Denominator Surface Reconciliation

Please strictly review Goal5392.

## Files Under Review

Result report:

```text
history/internal_docs/goal5392_xhd_lb_denominator_surface_reconciliation_result_2026-07-10.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5392_lb_denominator_surface_reconciliation.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5392_lb_denominator_surface_reconciliation.py
```

Tests:

```text
tests/goal5392_lb_denominator_surface_reconciliation_test.py
tests/goal5391_lb_fanout_semantics_test.py
tests/goal5390_full_trace_summary_gate_test.py
```

## Context

Goal5390 proved the current full-source RTDL bridge surface is not
author-compatible:

```text
active_query_count parity = true
RTDL bridge rows          = 2,188,225
author raw offload rows   = 27,133,990
row/hash parity           = false
```

Goal5391 converted that bridge mismatch into an aggregate fanout diagnostic:

```text
RTDL bridge rows / active = 5
author rows / active      = 62
```

Goal5392 adds a correction before native work continues: the bridge surface is
not the only denominator evidence. Earlier RTDL raw-kind2 / behavior-gate
surfaces are closer to the author raw denominator and must be reconciled before
choosing the next native status-stream target.

## Requested Review Questions

1. Does Goal5392 correctly preserve the Goal5390/5391 conclusion that the
   current bridge surface fails author row/hash parity?
2. Does the surface table correctly include the important denominator surfaces:
   bridge materialized rows, default raw kind2, inline+global-bound raw kind2,
   full-cover lb256 behavior gate, and no-inline/heavy-before overcount?
3. Are the numeric values and ratios correct?

```text
author rows      = 27,133,990
bridge rows      = 2,188,225
default kind2    = 21,006,960
full-cover       = 24,508,120
heavy-before     = 304,981,889
```

4. Is it correct to state that the bridge surface is not the sole or closest
   native implementation target?
5. Is it correct to mark `full_cover_lb256_behavior_gate_surface` as the closest
   prior surface while refusing to promote it to row parity, hash parity, or
   author status semantics?
6. Does Goal5392 avoid claiming explicit `-lb` support, Figure 7/11
   reproduction, same-denominator memory, author RT-core algorithm parity,
   performance ratio, exact input reproduction, or full X-HD reproduction?
7. Is the next-goal recommendation appropriate: a generic status-stream
   target-selection/design goal before native implementation?
8. Are the tests strong enough to prevent the old mistake of treating the
   bridge 5x surface as the only target or treating full-cover 56x as already
   correct?

## Expected Answer Shape

```text
Verdict:
  approve_goal5392_lb_denominator_surface_reconciliation
  OR approve_with_required_amendments
  OR reject

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to requested review questions:
  1. ...
  2. ...
  ...
```

## Requested Verdict Label If Approved

```text
approve_goal5392_lb_denominator_surfaces_reconciled__bridge_not_sole_target
```
