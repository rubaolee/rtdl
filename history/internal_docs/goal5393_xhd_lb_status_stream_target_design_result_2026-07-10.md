# Goal5393 X-HD `-lb` Status-Stream Target Design

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5393 selects the next explicit `-lb` status-stream target after Goal5392
reconciled all known denominator surfaces.

Goal5392 showed:

```text
author raw offload rows       = 27,133,990 = 62 * active_count
current bridge rows           =  2,188,225 =  5 * active_count
default / inline raw kind2    = 21,006,960 = 48 * active_count
full-cover lb256 surface      = 24,508,120 = 56 * active_count
```

Goal5393 chooses the full-cover surface as the starting target because it is the
closest known RTDL row-count surface. It does not promote that surface to
correctness.

Primary exit label:

```text
lb_status_stream_target_selected__implement_generic_full_cover_delta_probe_next
```

## Artifacts

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
```

## Inputs

```text
Goal5392 denominator reconciliation:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5392_lb_denominator_surface_reconciliation.json

Goal5387 author trace v2:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json

Goal5384 generic multi-round status reference:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5384_multiround_status_requirements.json

Goal5365 full-cover behavior gate:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
```

## Selected Target

Selected starting surface:

```text
full_cover_lb256_behavior_gate_surface
```

Why:

```text
It is the closest known RTDL row-count surface to the author raw offload
denominator while staying inside generic RTDL row semantics.
```

Numbers:

```text
author rows                         = 27,133,990
full-cover rows                     = 24,508,120
missing rows to author              = 2,625,870
active query count                  = 437,645
missing rows per active, aggregate  = 6
```

The current bridge surface is rejected as the direct implementation target:

```text
bridge rows                         = 2,188,225
bridge missing rows to author        = 24,945,765
```

The default raw kind2 surface is also less close than full-cover:

```text
default raw kind2 rows               = 21,006,960
default missing rows to author       = 6,127,030
```

## What Goal5393 Does Not Claim

Goal5393 does not claim:

```text
explicit -lb support;
row-count parity;
hash/sample parity;
native backend completion;
author RT-core parity;
Figure 7 reproduction;
Figure 11 reproduction;
same-denominator memory;
performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

It only selects a generic target for the next design-to-implementation step.

## Gap Hypotheses To Test Next

The remaining full-cover-to-author delta is:

```text
2,625,870 rows = 6 * active_count
```

Goal5393 identifies four generic hypotheses that can explain that delta without
hard-coding X-HD constants:

```text
1. multi-round feedback or reactivation delta;
2. author current-best / cmin2 restore delta;
3. miss / completed / aborted transition delta;
4. loadBalanceProcessing feedback delta.
```

These are generic status-stream concepts, not paper-specific primitive names.

## Selected Next Gate

Next gate:

```text
generic_full_cover_delta_status_probe
```

Suggested next goal:

```text
Goal5394
```

Goal5394 should add a generic status-stream probe that starts from the closest
full-cover-like raw surface and measures whether generic multi-round feedback,
current-best, and terminal transitions can explain the remaining delta to the
author trace v2 oracle.

Required comparisons:

```text
row_count against author 27,133,990;
raw offload row hash or deterministic samples;
status_count_offloading;
feedback update count or explicit not-applicable evidence;
miss/completed/aborted counters or explicit not-applicable evidence.
```

Exit labels:

```text
generic_status_stream_moves_denominator_toward_author
generic_status_stream_target_not_author_compatible__lb_fail_closed_candidate
```

## Verification

Built artifact:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5393_lb_status_stream_target_design.py
```

Focused tests:

```text
py -m unittest \
  tests.goal5393_lb_status_stream_target_design_test \
  tests.goal5392_lb_denominator_surface_reconciliation_test \
  tests.goal5391_lb_fanout_semantics_test
```

Observed:

```text
Ran 12 tests in 0.027s
OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is the known Windows Python environment noise and did not indicate test
failure.

## Decision

Goal5393 chooses:

```text
selected_direction = implement_generic_full_cover_delta_status_probe_next
```

Native code is not authorized by this goal alone:

```text
native_code_authorized_by_this_goal = false
```

The next implementation may proceed only as a generic full-cover-delta status
probe. If the missing rows require X-HD-specific constants or author-only logic,
explicit `-lb` should be fail-closed rather than forced into RTDL core.
