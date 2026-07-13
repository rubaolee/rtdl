# Goal5373 - RTDL Status-Machine Telemetry Surface Audit

Date: 2026-07-09

Status: `completed_rtdl_status_machine_telemetry_surface_audit__lb_trace_fields_missing`

Exit label:

```text
current_surface_insufficient__native_status_probe_or_author_instrumentation_required
```

## Purpose

Goal5372 pinned the author X-HD `-lb` / heavy-cell offload denominator as a
shader payload/status-machine problem. Goal5373 asks a narrower question:

```text
Does the current generic RTDL cell-MBR frontier telemetry surface already expose
the minimum fields needed for the next author_shader_status_machine_lb_trace
gate?
```

Answer:

```text
No.
```

The current surface is useful and real, but it is not sufficient for explicit
`-lb` support or author OffloadingSize denominator parity.

## Artifact

Generated:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5373_rtdl_status_machine_telemetry_surface.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5373_rtdl_status_machine_telemetry_surface.py
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5373.rtdl_status_machine_telemetry_surface.v1
```

## What The Current RTDL Surface Has

The audit verifies that the existing generic cell-MBR frontier path exposes:

```text
raw_frontier_kind_counts
raw_frontier_kind2_rows
inline_cell_hit_count
inline_point_evaluation_count
global_bound_early_break_count
global_bound_distance
native_phase_timings
native_memory_telemetry
```

This is not nothing. It is enough for raw kind-count diagnostics like Goals5368
and 5371, and it proves that RTDL already has a generic native telemetry surface
around cell-MBR frontier collection.

## What Is Missing For Author `-lb`

Goal5372's next gate requires these fields:

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

Goal5373 classifies the current coverage as:

```text
missing_count = 8
partial_count = 3
available_count = 0
```

Partial:

```text
raw_offload_rows_before_sort_reduce
point_loop_early_break_count
current_best_state_source
```

Missing:

```text
active_in_queue_size
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
row_count_parity_against_author_offloading_size
```

## Interpretation

The current `raw_frontier_kind2_rows` field is only a partial proxy for author
heavy-cell offload rows. It counts generic RTDL offload-kind rows before Python
materialization, but it is not counted in the author's active `in_q_idx`
namespace and it does not include the author shader's prune / abort / status
semantics.

The current `global_bound_early_break_count` field is also only a partial proxy.
It belongs to RTDL's generic max-nearest global-bound experiment. It is not the
author's `max_dist2 <= cmax2` MBR abort count, and Goal5371 already showed it
does not fire in the Dragon -> AsianDragon `lb=256` probe.

Therefore:

```text
ready_for_author_shader_status_machine_lb_trace = false
```

## Decision

Explicit `-lb` support remains unauthorized.

The next useful work is one of:

```text
1. Add a generic experimental native status-machine probe that emits the missing fields.
2. Instrument the author code to dump raw queue/status/cmin2 oracle rows.
```

Recommended next goal:

```text
Goal5374 author_shader_status_machine_lb_trace implementation_or_author_instrumentation
```

## Claim Boundary

Allowed:

```text
Goal5373 audits the current RTDL telemetry surface against Goal5372's minimum
author-status-machine fields and proves the current surface is insufficient for
explicit -lb support.
```

Not allowed:

```text
explicit -lb support is complete
row-count parity is proven
same-denominator Figure 11 memory is proven
Figure 7 or Figure 11 is reproduced
author RT-core algorithm parity is proven
RTDL/author performance ratio is fair or final
exact paper dataset reproduction is complete
full X-HD paper reproduction is complete
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5373_rtdl_status_machine_telemetry_surface.py
py -m unittest tests.goal5373_rtdl_status_machine_telemetry_surface_test tests.goal5372_author_shader_status_machine_gap_test tests.goal5371_inline_global_bound_lb_probe_test
```

Result:

```text
Ran 12 tests in 0.051s
OK
```

The local Windows warning:

```text
Could not find platform independent libraries <prefix>
```

appeared before the test run. This is the known local environment warning and
does not indicate failure when the tests pass.
