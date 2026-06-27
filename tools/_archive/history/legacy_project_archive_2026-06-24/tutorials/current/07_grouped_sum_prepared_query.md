# Grouped Sum Prepared Query

Status: V3 rebuild tutorial, not a release claim.

This lesson connects a tiny runnable grouped-sum example to the serious Phoenix
grouped-reduction evidence. The tiny example teaches the RTDL shape. The pod
evidence is the only source for performance wording.

## Run The Tiny Example

From the repository root:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\current\features\database\rtdl_db_grouped_sum.py --backend cpu_python_reference
```

Expected rows:

```json
[
  {
    "region": "east",
    "sum": 6
  },
  {
    "region": "west",
    "sum": 20
  }
]
```

The RTDL shape is:

```python
candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
groups = rt.refine(
    candidates,
    predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
)
return rt.emit(groups, fields=["region", "sum"])
```

This example is deliberately small. It proves syntax and correctness, not
performance.

## Serious Evidence

The Phoenix grouped-reduction candidate is a fixed-schema prepared grouped-sum workload.
It is not SQL, not a DBMS, not RayDB end to end, and not broad V3 speedup over
V2.x.

Current candidate rows:

| Row | Rows | Groups | Hot OptiX/Embree | Actual repeat100 loop | Actual cold plus loop | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `grouped_reduction_sum_scalar_broadcast_repeat100_262144` | 262,144 | 1,024 | 203.022x | 200.353x | 27.917x | M7-qualified row-scoped; V3 release still false |
| `grouped_reduction_sum_scalar_broadcast_repeat100_524288` | 524,288 | 2,048 | 158.970x | 157.642x | 2.983x | not M7; large cold prepare cost |

These repeat100 values are measured with `repeat=100` on both Embree and OptiX.
The cold-plus-loop column counts cold prepare once plus the measured 100-query
loop. The current numbers use the scalar-broadcast repeat100 rerun, which
removed full-length constant ray direction/tmax arrays from the typed-buffer
packing path. The older modeled 32x/33x repeat100 values and the pre-optimization
actual repeat100 values are superseded.

## What To Learn

- Use `grouped_sum` when the user has a fixed group key and integer value
  column.
- Separate the tiny teaching example from serious pod evidence.
- Separate hot prepared-query timing from repeat end-to-end timing.
- Name the repeat count and cold cost whenever an actual repeat result is
  discussed.
- Treat scalar-broadcast packing as a generic V3 optimization, not a special
  app-native engine.
- Treat the 262,144-row result as
  `m7_qualified_row_scoped_after_claude_codex_consensus`: usable only as that
  exact grouped-sum row, not as V3 release or broad speedup wording.
- Keep count rows internal for now because their break-even repeat count is much
  higher.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md`

## Claim Boundary

Allowed:

```text
V3 has a reviewed grouped-sum prepared-query candidate with strong hot-query
and actual repeat100 evidence. The 262,144-row final-review packet is
Claude/Codex M7-qualified for row-scoped public wording, but V3 release,
whole-app speedup, and broad V3-over-V2 speedup remain unauthorized.
```

Forbidden:

```text
Do not claim V3 is 224x faster.
Do not claim RayDB is 224x faster.
Do not claim RTDL is a database system.
Do not claim RTDL is 33x faster end to end from the older modeled packet.
Do not hide cold prepare cost.
Do not claim any grouped-sum row beyond
`grouped_reduction_sum_scalar_broadcast_repeat100_262144` is M7-qualified.
Do not publish the 524,288-row sum or any count row as an M7 result.
```

Read next:

- [Claim Boundaries](06_claim_boundaries.md)
