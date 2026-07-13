# Consolidated Call For Review - Goals5363-5368 X-HD `-lb` / Heavy Offload Packet

Please strictly review the X-HD `-lb` / heavy-offload semantic packet covering
Goals5363-5368.

This packet does **not** claim explicit `-lb` support, Figure 7 reproduction,
Figure 11 memory parity, author RT-core parity, performance parity, exact paper
dataset identity, or full X-HD paper reproduction.

## Documents

```text
history/internal_docs/goal5363_xhd_lb_heavy_offload_semantics_audit_result_2026-07-09.md
history/internal_docs/goal5364_xhd_lb_trace_gate_author_pair_contract_result_2026-07-09.md
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
history/internal_docs/goal5366_xhd_lb_denominator_reconciliation_result_2026-07-09.md
history/internal_docs/goal5367_xhd_lb_author_radius_probe_result_2026-07-09.md
history/internal_docs/goal5368_xhd_cell_mbr_raw_kind_count_telemetry_result_2026-07-09.md
```

Individual call-for-review docs:

```text
history/internal_docs/call_for_review_goal5363_xhd_lb_heavy_offload_semantics_audit_2026-07-09.md
history/internal_docs/call_for_review_goal5364_xhd_lb_trace_gate_author_pair_contract_2026-07-09.md
history/internal_docs/call_for_review_goal5365_xhd_rtdl_lb_counterpart_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5366_xhd_lb_denominator_reconciliation_2026-07-09.md
history/internal_docs/call_for_review_goal5367_xhd_lb_author_radius_probe_2026-07-09.md
history/internal_docs/call_for_review_goal5368_xhd_cell_mbr_raw_kind_count_telemetry_2026-07-09.md
```

## Packet Arc

### Goal5363 - Author `-lb` Semantics Audit

Author source semantics:

```text
lb=0   -> processing_threshold = UINT32_MAX, offload disabled
lb=N   -> cell point_count > N appends (in_queue_idx, cell_id) to offload queue
memory -> WL Heavy Peak = OffloadingSize * 2 * sizeof(uint32_t)
```

### Goal5364 - Author Dragon -> AsianDragon Pair

Temporary Level-B input:

```text
dragon.ply -> asian_dragon.ply
exact_paper_dataset_identity_proven = false
```

Author:

```text
lb0:
  HDResult       = 52.453487396240234
  OffloadingSize = 0

lb256:
  HDResult       = 52.453487396240234
  OffloadingSize = 27133990
  Radius         = 79.2156982421875
  WL Heavy Peak  = 217071920
```

### Goal5365 - RTDL Counterpart Behavior Gate

RTDL:

```text
lb0 disabled:
  HDResult                = 52.453491321261296
  heavy_offload_peak_rows = 0

lb256 full-cover:
  HDResult                = 52.453491321261296
  heavy_offload_peak_rows = 24508120
```

Behavior-level gate passed; row-count parity did not.

### Goal5366 - Denominator Reconciliation

Byte formula shape aligns:

```text
author: OffloadingSize * 2 * sizeof(uint32_t)
RTDL:   heavy_offload_peak_rows * 2 * sizeof(uint32_t)  [author-width candidate]
```

But row parity fails:

```text
author OffloadingSize = 27133990
RTDL heavy rows       = 24508120
RTDL / author         = 0.9032258064516129
```

The gap is not explained by RTDL host duplicate collapse in the Goal5365
artifact.

### Goal5367 - Author Radius Probe

RTDL with author radius:

```text
radius                  = 79.2156982421875
HDResult                = 52.453491321261296
heavy_offload_peak_rows = 21006960
RTDL / author           = 0.7741935483870968
```

Radius alignment preserves the value but worsens denominator alignment.  The
gap is not simply scalar radius mismatch.

### Goal5368 - Raw Kind-Count Telemetry

Added generic native raw frontier kind-count telemetry and count-only overflow
diagnostics.

No-inline/count-only RTDL probe with author radius:

```text
attempted all kinds       = 589961522
raw_frontier_kind1_rows   = 284979633
raw_frontier_kind2_rows   = 304981889
raw_frontier_kind3_rows   = 0
raw kind2 / author        = 11.239846738352892
```

This proves that author `OffloadingSize` is not simply all raw RTDL cells above
the `lb` threshold under the same scalar radius.

## Main Question For Review

Does the packet correctly conclude that explicit `-lb` support remains
unauthorized because the author offload denominator depends on iterative author
queue state (`in_queue_idx`, `cmin2/current best`, radius schedule, raw offload
emission semantics), not merely on the scalar radius or generic kind2 row shape?

## Review Questions

1. Is the author `-lb` semantics audit faithful to the source?
2. Is the author pair a valid temporary Level-B diagnostic input while not
   being an exact paper dataset?
3. Does RTDL correctly preserve HD value for `lb0` and `lb256` counterparts?
4. Does Goal5366 correctly align byte formula shape while refusing row-count
   parity?
5. Does Goal5367 correctly reject the scalar-radius-only hypothesis?
6. Does Goal5368 correctly add generic raw kind-count telemetry and use it to
   show no-inline raw kind2 is about `11.24x` author `OffloadingSize`?
7. Does the packet avoid author RT-core parity, Figure 7/11 reproduction,
   same-denominator memory parity, and performance ratio overclaims?
8. Is the proposed next target correct: author-queue-aligned `lb` trace with
   `in_queue_idx`, `cmin2/current best`, iteration radius, and raw offload queue
   semantics?

Expected verdict labels:

```text
approve_goals5363_5368_xhd_lb_packet__next_author_queue_alignment
revise_goals5363_5368_xhd_lb_packet
block_goals5363_5368_xhd_lb_packet
```
