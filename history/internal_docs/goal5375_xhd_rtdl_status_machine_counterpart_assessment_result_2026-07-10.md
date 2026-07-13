# Goal5375 - X-HD RTDL Status-Machine Counterpart Assessment Result

Date: 2026-07-10

Status:

```text
rtdl_status_machine_counterpart_assessed__row_parity_not_established
```

Exit label:

```text
current_rtdl_surface_fails_author_lb_oracle__need_status_machine_implementation
```

## Purpose

Goal5375 compares the current RTDL `-lb` / heavy-offload telemetry surfaces
against the Goal5374 author status-machine oracle.

The purpose is deliberately strict:

```text
Do current RTDL surfaces already provide an author-compatible status-machine
counterpart for explicit -lb?
```

Answer:

```text
No.
```

This is still progress because it turns the failure into a machine-checked
artifact and narrows the next implementation target.

## Inputs

Primary author oracle:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
```

RTDL evidence compared:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_inline_global_bound_lb_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5373_rtdl_status_machine_telemetry_surface.json
```

New artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5375_rtdl_status_machine_counterpart_assessment.json
```

New builder / test:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5375_rtdl_status_machine_counterpart.py
tests/goal5375_rtdl_status_machine_counterpart_test.py
```

## Author Oracle Baseline

Goal5374 author oracle:

```text
OffloadingSize = 27133990
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
ActiveInQueueSize = 437645
StatusInitCount = 437645
StatusOffloadingAppendCount = 27133990
StatusCmax2MbrAbortCount = 0
StatusPointLoopEarlyBreakCount = 0
```

This is the denominator RTDL must match before explicit `-lb` can be accepted.

## RTDL Candidate Counterparts Assessed

Goal5375 evaluates four current RTDL surfaces:

| Candidate | RTDL rows | Delta author - RTDL | Ratio | Row parity |
|---|---:|---:|---:|---|
| `author_radius_inline_kind2_current_surface` | 21,006,960 | 6,127,030 | 0.7741935484 | false |
| `author_radius_inline_global_bound_kind2_current_surface` | 21,006,960 | 6,127,030 | 0.7741935484 | false |
| `author_radius_noinline_raw_kind2_current_surface` | 304,981,889 | -277,847,899 | 11.2398467384 | false |
| `goal5365_full_cover_lb256_behavior_gate_surface` | 24,508,120 | 2,625,870 | 0.9032258065 | false |

The closest existing surface is the old Goal5365 full-cover behavior gate, but
it still misses by:

```text
2,625,870 rows
```

Therefore no current RTDL surface establishes row-count parity.

## What This Rules Out

Goal5375 confirms and consolidates the previous no-go findings:

```text
inline current surface is too small;
inline + existing global-bound is unchanged;
no-inline raw kind2 is far too large;
old full-cover lb256 behavior gate is closest but still not equal;
current RTDL telemetry surface from Goal5373 is not ready.
```

This means the next work cannot be another scalar-radius probe, raw-kind2 probe,
or existing-global-bound probe.

## Remaining Missing / Unproven Semantics

The artifact records the remaining required semantic gaps:

```text
author cmin2/current-best restoration by in_q_idx
author cmax2 MBR abort status counter
author miss_queue append/count semantics
author loadBalanceProcessing sort/reduce feedback into later state
row-count parity against Goal5374 OffloadingSize
```

The current RTDL fields are field-shape analogs, not an author-compatible
status-machine implementation.

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5375_rtdl_status_machine_counterpart.py
py -m unittest tests.goal5375_rtdl_status_machine_counterpart_test tests.goal5374_author_lb_status_trace_oracle_test tests.goal5373_rtdl_status_machine_telemetry_surface_test tests.goal5371_inline_global_bound_lb_probe_test
```

Observed:

```text
Ran 14 tests OK
```

The known local Windows Python warning:

```text
Could not find platform independent libraries <prefix>
```

appeared and did not affect test success.

## Claim Boundary

Allowed:

```text
Current RTDL status-machine counterpart assessment is complete.
Current RTDL surfaces fail the Goal5374 author oracle row-count parity gate.
The next implementation must add a real status-machine mode or equivalent
queue/current-best/status accounting.
```

Not allowed:

```text
explicit -lb support
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core parity
performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Step

Recommended next goal:

```text
Goal5376 - implement or probe a real RTDL status-machine mode against the
Goal5374 author oracle
```

Minimum requirements:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Expected decision:

```text
Either establish row parity against Goal5374 or keep explicit -lb unsupported
with a precise denominator mismatch.
```
