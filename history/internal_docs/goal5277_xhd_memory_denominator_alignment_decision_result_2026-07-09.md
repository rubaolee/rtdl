# Goal5277 - X-HD Figure 11 Memory Denominator Alignment Decision

Status:

```text
implemented_review_pending
```

## Purpose

Goal5276 made RTDL memory evidence reviewable as a bounded/status-bearing
matrix, but review still needed one sharper answer:

```text
Are RTDL's current WL / WL Heavy Peak fields actually comparable to the
author Figure 11 denominator?
```

Goal5277 answers that by auditing the author source and updating the RTDL
memory-accounting semantics.  The result is a formal **not same denominator**
decision, not another reshaping of the same memory rows.

## Author Source Audit

POD:

```text
45c502cfccb5
NVIDIA RTX 4000 Ada Generation
```

Author source:

```text
/tmp/xhd-goal5112/author/src/hd_impl/hausdorff_distance_rt.h
```

Relevant lines observed through the POD wrapper:

```text
140: uint32_t wl_bytes = 0, wl_heavy_peak_bytes = 0;
143: wl_bytes = 2 * n_points_a * sizeof(uint32_t);  // in+miss queues
222: Queue<uint32_t> in_queue(n_points_a, stream);
223: Queue<uint32_t> miss_queue(n_points_a, stream);
348: auto offloading_size = offloading_point_ids_.size(stream);
349-351: wl_heavy_peak_bytes = max(wl_heavy_peak_bytes,
         offloading_size * 2 * sizeof(uint32_t));
445: mem["WL"] = wl_bytes;
446: mem["WL Heavy Peak"] = wl_heavy_peak_bytes;
```

Therefore:

```text
Author WL = in_queue + miss_queue = 2 * n_points_a * sizeof(uint32_t)
Author WL Heavy Peak = peak heavy-cell offload queues
                       (offloading_point_ids_ + offloading_cell_ids_)
```

## RTDL Current Denominator

Current RTDL route memory accounting has:

```text
BVH:
  measured OptiX GAS output buffer bytes for the generic cell-MBR frontier
  route when native telemetry is available.

WL:
  estimated generic frontier row-table capacity:
  frontier_row_capacity * 8 generic 64-bit frontier row columns.

WL Heavy Peak:
  unavailable; the current route has no author-like heavy-cell offload queue.
```

The WL names are similar, but the denominators are different.  RTDL's WL is a
frontier row-table capacity estimate; author WL is an in/miss queue pair.

## Code Changes

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_rtdl_memory_matrix.py
```

The RTDL WL status is now:

```text
estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue
```

The method text explicitly says:

```text
This is RTDL route capacity accounting, not the author's Figure 11 WL
denominator; author WL is in_queue + miss_queue, computed in
hausdorff_distance_rt.h as 2 * n_points_a * sizeof(uint32_t).
```

The memory matrix builder now recomputes memory accounting through the current
helper instead of trusting possibly stale `RTDL.memory_accounting` already
embedded inside older hd_exec-compatible JSON artifacts.

## Result Artifacts

Decision artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5277_memory_denominator_alignment_decision_2026-07-09.json
```

Updated bounded matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json
```

Key decision:

```text
status: figure11_denominator_alignment_not_met__heavy_worklist_api_required
same_denominator_author_figure11: false
figure11_reproduced: false
```

Claim boundary remains false for:

```text
figure11_reproduced
author_memory_parity_claimed
same_denominator_author_figure11_claimed
wl_same_denominator_author_claimed
wl_heavy_peak_measured_by_rtdl
performance_ratio_claimed
```

## Validation

Focused tests:

```text
py -m unittest \
  tests.goal5277_xhd_memory_denominator_alignment_decision_test \
  tests.goal5276_xhd_rtdl_bounded_memory_matrix_test \
  tests.goal5273_xhd_rtdl_memory_accounting_test
```

Result:

```text
Ran 9 tests in 0.017s
OK
```

## What This Does Not Prove

This does not prove:

```text
Figure 11 reproduction
author memory parity
author-vs-RTDL memory ratio
same-denominator WL comparison
WL Heavy Peak measurement
exact GPU allocator peak accounting
```

## Decision

Figure 11 cannot be honestly closed from the current RTDL route and telemetry.
The route has useful RTDL memory evidence, including measured native OptiX GAS
output bytes, but it does not implement or expose author-like in/miss queues or
heavy-cell offload peak queues.

To reproduce Figure 11 later, RTDL needs one of the following:

```text
1. a generic heavy-cell/offload worklist API tied to RT traversal output, plus
   matching peak queue telemetry; or
2. an external review decision explicitly accepting a different memory question
   as non-Figure-11 evidence.
```

Until then:

```text
Figure 11 remains not_reproduced.
same_denominator_author_figure11 remains false.
```
