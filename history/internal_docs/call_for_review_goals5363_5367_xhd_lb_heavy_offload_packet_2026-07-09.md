# Consolidated Call For Review - Goals5363-5367 X-HD lb / Heavy-Offload Packet

Please strictly review the X-HD `-lb` / heavy-cell offload packet from
Goal5363 through Goal5367.

This supersedes the Goals5363-5366 packet by adding the explicit author-radius
RTDL probe from Goal5367.

## Packet Files

```text
history/internal_docs/goal5363_xhd_lb_heavy_offload_semantics_audit_result_2026-07-09.md
history/internal_docs/goal5364_xhd_lb_trace_gate_author_pair_contract_result_2026-07-09.md
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
history/internal_docs/goal5366_xhd_lb_denominator_reconciliation_result_2026-07-09.md
history/internal_docs/goal5367_xhd_lb_author_radius_probe_result_2026-07-09.md
```

## Short Progression

```text
Goal5363:
  author -lb semantics audited from source.

Goal5364:
  author Dragon->Asian lb=0/lb=256 pair promoted to contract.

Goal5365:
  RTDL lb0/lb256 behavior gate passed, but row denominator differed.

Goal5366:
  byte formula shape aligned, row-count parity still not established.

Goal5367:
  explicit author-radius RTDL probe preserves value but still fails row-count
  parity; radius alignment alone is not enough.
```

## Key Numbers

```text
Author lb256:
  HDResult = 52.453487396240234
  OffloadingSize = 27,133,990
  radius = 79.2156982421875

RTDL lb256 full-cover:
  HDResult = 52.453491321261296
  heavy_offload_peak_rows = 24,508,120
  radius = 266.9466183641096

RTDL lb256 author-radius:
  HDResult = 52.453491321261296
  heavy_offload_peak_rows = 21,006,960
  radius = 79.2156982421875
```

## Packet Question

Is this packet ready to close as:

```text
lb_behavior_gate_passed__radius_alignment_not_sufficient__queue_denominator_unresolved
```

with explicit `-lb` support still unauthorized?

## Required Review Points

1. Does the packet correctly separate threshold-rule shape alignment,
   behavior-level value/offload evidence, byte-formula alignment, and actual
   row-count parity?

2. Does Goal5367 correctly rule out scalar radius mismatch as the full
   explanation for row-count denominator mismatch?

3. Does the packet correctly identify the next real gate as author
   queue/in_queue/cmin2/raw-offload denominator alignment?

4. Does the packet avoid Figure 7, Figure 11, memory parity, performance ratio,
   and full paper reproduction claims?

5. Does the packet preserve RTDL generic-system boundaries?

## Expected Verdict

```text
approve_goals5363_5367_lb_heavy_offload_packet
```

or list required amendments / blocking findings.
