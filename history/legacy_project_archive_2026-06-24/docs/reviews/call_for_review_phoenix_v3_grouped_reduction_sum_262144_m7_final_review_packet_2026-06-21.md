# Call For Review: Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet

Please critically review this packet as a possible first Phoenix V3
M7-qualified row.

Files under review:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md
tutorials/current/07_grouped_sum_prepared_query.md
```

Question:

Can `grouped_reduction_sum_scalar_broadcast_repeat100_262144` become the first
M7-qualified Phoenix V3 release row if the public wording remains exactly
row-scoped?

Critical facts:

```text
generic_capability: grouped_reduction
operation: group_sum_i64
rows: 262,144
groups: 1,024
hardware: NVIDIA RTX 4000 Ada Generation
warmup: 3
repeat: actual repeat=100
partner continuation required: false
same contract: true
CPU reference matched: true
app-specific native engine logic: false
hot prepared-query OptiX/Embree: 203.022x
actual repeat100 loop OptiX/Embree: 200.353x
actual cold plus repeat100 loop OptiX/Embree: 27.917x
```

Rows intentionally excluded:

```text
524,288 grouped_sum: excluded because cold plus loop is only 2.983x and OptiX
cold plus loop is 98.960s.

count rows: excluded because break-even requires double-digit repeats.
```

Please answer:

1. Approve this exact 262,144 grouped_sum row as M7-qualified?
2. Approve only as final-review candidate, not M7?
3. Reject as public-row evidence?

Also identify any P0 wording or evidence fixes needed before promotion.
