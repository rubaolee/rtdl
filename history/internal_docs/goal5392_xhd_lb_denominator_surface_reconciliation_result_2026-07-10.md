# Goal5392 X-HD `-lb` Denominator Surface Reconciliation

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5392 reconciles the known RTDL `-lb` row-denominator surfaces before any new
native status-stream implementation is written.

Goal5391 correctly showed that the current full-source bridge surface emits:

```text
RTDL bridge rows = 2,188,225 = 5 * active_count
author rows      = 27,133,990 = 62 * active_count
```

However, that bridge surface is not the only RTDL denominator evidence in the
history. Earlier raw-kind2 / behavior-gate surfaces are much closer to the
author raw offload stream. Goal5392 gathers those surfaces into one decision
artifact and prevents the next implementation from chasing the wrong `5x`
post-bridge target.

Primary exit label:

```text
lb_denominator_surfaces_reconciled__select_raw_status_target_before_native_work
```

## Artifact

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
```

## Inputs

Goal5392 uses existing evidence only; no new POD run is required.

```text
Goal5387 author trace v2:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json

Goal5391 bridge fanout:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5391_lb_fanout_semantics.json

Goal5375 RTDL surface assessment:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5375_rtdl_status_machine_counterpart_assessment.json

Goal5377 default and heavy-before status probes:
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_default_status_probe_pod.json
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_heavy_before_inline_prune_probe_pod.json
```

## Surface Table

Author oracle:

```text
active_count = 437,645
author raw offload rows = 27,133,990
author rows / active = 62
author raw offload row hash = 4333109858711462591
```

RTDL surfaces:

| Surface | Rows | Rows / Active | Ratio vs Author | Status |
|---|---:|---:|---:|---|
| current bridge materialized offload rows | 2,188,225 | 5 | 0.0806451613 | fails, post-bridge surface only |
| default / inline raw kind2 count | 21,006,960 | 48 | 0.7741935484 | under-counts |
| inline + existing global-bound raw kind2 count | 21,006,960 | 48 | 0.7741935484 | unchanged by existing global bound |
| full-cover lb256 behavior-gate surface | 24,508,120 | 56 | 0.9032258065 | closest prior surface, still not parity |
| no-inline / heavy-before raw kind2 overcount | 304,981,889 | ~696.87 | 11.2398467384 | over-counts |

Key result:

```text
closest_surface_by_absolute_row_delta = full_cover_lb256_behavior_gate_surface
closest_raw_candidate_absolute_row_delta = 2,625,870
bridge_absolute_row_delta = 24,945,765
bridge_surface_is_sole_target = false
any_surface_has_row_count_parity = false
any_surface_has_hash_parity = false
```

## Interpretation

Goal5390 and Goal5391 remain correct:

```text
The current bridge output is a full-source failure and is not source-limited.
Bridge runtime optimization is not the next main path.
```

Goal5392 adds the missing denominator context:

```text
The current bridge output is not the closest raw-denominator surface.
RTDL already has raw-kind2 / full-cover surfaces that are closer to the author
raw offload count, though still wrong.
```

Therefore the next native work should not optimize or hard-code the bridge row
count. It should target author-compatible raw status semantics and explain the
gap between the closest prior surface and the author trace.

## Decision

Goal5392 selects:

```text
native_implementation_should_start_from =
  author_compatible_raw_status_semantics_not_post_bridge_row_count
```

Next gate:

```text
generic_status_stream_target_selection_or_fail_closed_closeout
```

Meaning:

```text
Before writing a new native multi-round status stream, the next design must
state which raw surface it is trying to reproduce and why.
```

The full-cover surface is allowed to inform the design because it is closest by
row count. It is not promoted to correctness, row parity, hash parity, or
author status semantics.

## Verification

Built artifact:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5392_lb_denominator_surface_reconciliation.py
```

Focused tests:

```text
py -m unittest \
  tests.goal5392_lb_denominator_surface_reconciliation_test \
  tests.goal5391_lb_fanout_semantics_test \
  tests.goal5390_full_trace_summary_gate_test
```

Observed:

```text
Ran 10 tests in 0.025s
OK
```

The local Python warning:

```text
Could not find platform independent libraries <prefix>
```

is the known Windows Python environment noise and did not indicate test
failure.

## Claim Boundary

Allowed:

```text
Goal5392 reconciles known RTDL denominator surfaces.
The current bridge surface is not the sole or closest target.
The full-cover surface is the closest prior row-count surface but is not
author-semantic parity.
The next native work must select an author-compatible raw status target before
implementation.
```

Forbidden:

```text
Do not claim explicit -lb support.
Do not claim row-count parity.
Do not claim hash/sample parity.
Do not claim full-cover surface correctness.
Do not claim bridge surface as the only target.
Do not claim Figure 7 or Figure 11 reproduction.
Do not claim same-denominator memory.
Do not claim author RT-core algorithm parity.
Do not claim author-vs-RTDL performance ratio.
Do not claim exact paper dataset reproduction.
Do not claim full X-HD paper reproduction.
```

## Next Work

Recommended immediate next goal:

```text
Goal5393: generic status-stream target-selection / design.
```

Goal5393 should choose one of:

```text
1. target the full-cover-like raw behavior and explain the remaining 2,625,870
   row gap through generic status transitions;
2. target another raw-kind2/status surface if review rejects full-cover as the
   right starting point;
3. fail-close explicit -lb if an author-compatible raw denominator requires
   X-HD-specific logic.
```

POD is not required for Goal5392. POD is expected for any later native build and
full Dragon -> AsianDragon row/hash parity probe.
