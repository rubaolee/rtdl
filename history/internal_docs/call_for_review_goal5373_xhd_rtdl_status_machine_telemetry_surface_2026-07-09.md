# Call For Review - Goal5373 RTDL Status-Machine Telemetry Surface Audit

Please strictly review Goal5373.

## Files Under Review

```text
history/internal_docs/goal5373_xhd_rtdl_status_machine_telemetry_surface_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5373_rtdl_status_machine_telemetry_surface.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5373_rtdl_status_machine_telemetry_surface.json
tests/goal5373_rtdl_status_machine_telemetry_surface_test.py
```

Context files:

```text
history/internal_docs/goal5372_xhd_author_shader_status_machine_gap_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5372_author_shader_status_machine_gap.json
```

## Review Questions

1. Does Goal5373 correctly treat Goal5372's `author_shader_status_machine_lb_trace`
   fields as the next required gate for X-HD explicit `-lb` work?
2. Does the artifact honestly distinguish existing generic RTDL telemetry
   (`raw_frontier_kind_counts`, `global_bound_early_break_count`, inline stats,
   native memory telemetry) from the missing author status-machine fields?
3. Is the classification fair that
   `raw_offload_rows_before_sort_reduce`, `point_loop_early_break_count`, and
   `current_best_state_source` are only partial coverage, not complete author
   `-lb` support?
4. Is it correct that `active_in_queue_size`, status counts, miss count,
   `cmax2_mbr_abort_count`, author-width raw row bytes, and row-count parity are
   missing from the current RTDL surface?
5. Does the builder avoid adding app-specific semantics to RTDL core and merely
   audit existing generic surfaces?
6. Do the tests meaningfully guard against silently promoting generic kind-count
   telemetry into author `-lb` status-machine parity?
7. Does the result properly keep explicit `-lb`, Figure 7, Figure 11,
   author RT-core parity, fair performance ratio, exact paper reproduction, and
   full X-HD reproduction unclaimed?
8. Is the recommended next gate valid:
   `Goal5374 author_shader_status_machine_lb_trace implementation_or_author_instrumentation`?
9. Should Goal5373 close with:

```text
current_surface_insufficient__native_status_probe_or_author_instrumentation_required
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 9 review questions:
```

Requested verdict label if approved:

```text
approve_goal5373_rtdl_status_machine_telemetry_surface_audit__lb_trace_fields_missing
```
