# Call For Review - Goal5277 X-HD Memory Denominator Alignment Decision

Please strictly review Goal5277.

## Files Under Review

```text
history/internal_docs/goal5277_xhd_memory_denominator_alignment_decision_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5277_memory_denominator_alignment_decision_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
tests/goal5277_xhd_memory_denominator_alignment_decision_test.py
tests/goal5276_xhd_rtdl_bounded_memory_matrix_test.py
tests/goal5273_xhd_rtdl_memory_accounting_test.py
```

## Context

Goal5272 extracted the author Figure 11 memory log matrix.  Goal5273 defined a
status-bearing RTDL memory-accounting boundary.  Goal5275 added native OptiX
GAS memory telemetry.  Goal5276 built a bounded RTDL memory matrix.

Goal5277 does not try to force a memory ratio.  It audits the author source for
the `WL` and `WL Heavy Peak` definitions and decides whether RTDL's current
bounded memory matrix has the same Figure 11 denominator.

## Evidence To Verify

Author source on POD:

```text
/tmp/xhd-goal5112/author/src/hd_impl/hausdorff_distance_rt.h
```

Observed source lines:

```text
140: wl_bytes / wl_heavy_peak_bytes declarations
143: wl_bytes = 2 * n_points_a * sizeof(uint32_t)
222-223: in_queue / miss_queue allocation
348-351: wl_heavy_peak_bytes from offloading_size * 2 * sizeof(uint32_t)
445-446: mem["WL"] and mem["WL Heavy Peak"]
```

RTDL updated status:

```text
estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue
```

Decision artifact status:

```text
figure11_denominator_alignment_not_met__heavy_worklist_api_required
```

## Review Questions

1. Does the author source evidence correctly establish that author Figure 11
   `WL` is in/miss queues, not RTDL frontier rows?
2. Does the author source evidence correctly establish that author `WL Heavy
   Peak` is the peak heavy-cell offload queue?
3. Does the updated RTDL memory accounting avoid implying same-denominator
   comparability for `WL`?
4. Is it correct that current RTDL has no author-like heavy-cell offload peak
   denominator and therefore leaves `WL Heavy Peak` unavailable?
5. Does the regenerated bounded matrix correctly recompute memory accounting
   through the current helper rather than trusting stale embedded JSON fields?
6. Does the decision artifact correctly keep Figure 11 reproduction,
   same-denominator author memory, memory parity, and performance ratio claims
   false?
7. Is the next required work correctly identified as a generic heavy-cell /
   offload worklist API plus native peak queue telemetry, if Figure 11 is still
   pursued?
8. Are there any remaining phrases that could be read as author memory parity,
   Figure 11 reproduction, or same-denominator memory ratio?

## Expected Answer Shape

```text
Verdict: approve_goal5277_memory_denominator_alignment_decision |
         approve_with_required_amendments |
         reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Review question answers:
1. ...
2. ...
...
8. ...
```

Requested approval label:

```text
approve_goal5277_memory_denominator_alignment_decision__figure11_not_reproduced
```
