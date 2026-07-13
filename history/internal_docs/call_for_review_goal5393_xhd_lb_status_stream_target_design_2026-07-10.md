# Call For Review: Goal5393 X-HD `-lb` Status-Stream Target Design

Please strictly review Goal5393.

## Files Under Review

Result report:

```text
history/internal_docs/goal5393_xhd_lb_status_stream_target_design_result_2026-07-10.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5393_lb_status_stream_target_design.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5393_lb_status_stream_target_design.py
```

Tests:

```text
tests/goal5393_lb_status_stream_target_design_test.py
tests/goal5392_lb_denominator_surface_reconciliation_test.py
tests/goal5391_lb_fanout_semantics_test.py
```

## Context

Goal5392 reconciled known RTDL denominator surfaces:

```text
author raw offload rows       = 27,133,990 = 62 * active_count
current bridge rows           =  2,188,225 =  5 * active_count
default / inline raw kind2    = 21,006,960 = 48 * active_count
full-cover lb256 surface      = 24,508,120 = 56 * active_count
```

Goal5393 selects the next target:

```text
selected_starting_surface = full_cover_lb256_behavior_gate_surface
missing rows to author = 2,625,870 = 6 * active_count
```

It does not promote full-cover to correctness. It only selects a generic design
target for the next probe.

## Requested Review Questions

1. Is it correct to choose the full-cover surface as the next starting target
   because it is the closest known RTDL row-count surface?
2. Does Goal5393 correctly refuse to promote full-cover to row-count parity,
   hash parity, explicit `-lb` support, or author RT-core semantics?
3. Are the key deltas correct?

```text
author rows = 27,133,990
full-cover rows = 24,508,120
missing rows = 2,625,870
missing rows per active = 6
```

4. Is it correct to reject the bridge 5x surface as the direct implementation
   target?
5. Are the semantic-gap hypotheses generic rather than X-HD-specific:
   multi-round feedback, current-best restore, terminal transitions, and
   loadBalanceProcessing feedback?
6. Is the selected next gate appropriate:
   `generic_full_cover_delta_status_probe`?
7. Does the report avoid claiming explicit `-lb`, Figure 7/11, same-denominator
   memory, author RT-core parity, performance ratio, exact input reproduction,
   or full X-HD reproduction?
8. Are the tests sufficient to prevent the two dangerous misreadings:
   "bridge is the only target" and "full-cover is already correct"?

## Expected Answer Shape

```text
Verdict:
  approve_goal5393_status_stream_target_design
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
approve_goal5393_lb_status_target_selected__full_cover_delta_probe_next
```
