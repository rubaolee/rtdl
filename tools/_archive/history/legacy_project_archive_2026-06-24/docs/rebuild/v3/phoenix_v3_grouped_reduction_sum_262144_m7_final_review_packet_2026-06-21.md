# Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet

Status: M7-qualified row-scoped packet, not V3 release authorization.

## Verdict

This packet advances exactly one `grouped_reduction` row to final external M7
review:

```text
row_id: grouped_reduction_sum_scalar_broadcast_repeat100_262144
status: grouped_reduction_sum_262144_m7_qualified_row_scoped
local_evidence_sufficient_for_external_public_row_review: true
current_packet_external_review_status: claude_approved
current_packet_2ai_consensus_status: claude_codex_consensus_complete
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
m7_promotion_authorized: true
Phoenix M7-qualified release rows: 1
```

This packet promotes exactly one row-scoped M7-qualified result. It does not
authorize a V3 release, a whole-app/database speedup claim, or a broad
V3-over-V2 claim.

## External Review Status

Claude approved this exact row as M7-qualified, subject to documenting the
source-provenance gap and recording second-AI consensus:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_review_2026-06-21.md
```

Codex agrees and records the 2-AI closure at:

```text
docs/reviews/codex_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2ai_consensus_2026-06-21.md
```

The earlier blocked attempts remain preserved at:

```text
docs/reviews/external_review_blocked_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md
```

## Source Evidence

Source packets:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md
```

Source artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620/grouped_sum_scalar_broadcast_repeat100_262144.json
```

## Source Provenance

The pod artifact does not contain a usable git HEAD:

```text
fatal: not a git repository (or any of the parent directories): .git
```

For this row, source traceability is therefore the saved SHA-256 manifest:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620/source_manifest.sha256
```

It covers:

```text
VERSION
src/rtdsl/optix_runtime.py
examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
scripts/v3_gpu_python_env_gate.py
scripts/v3_optix_hardware_gate.py
```

Saved source version:

```text
v3-rebuild-2026-06-20
```

## Candidate Row

| Field | Value |
| --- | --- |
| Generic capability | `grouped_reduction` |
| Operation | `group_sum_i64` |
| Rows | 262,144 |
| Groups | 1,024 |
| Hardware | NVIDIA RTX 4000 Ada Generation |
| Backend pair | Embree baseline versus OptiX candidate |
| Warmup | 3 |
| Repeat | actual repeat=100 |
| Partner continuation required | false |
| Same contract | true |
| CPU reference matched | true |
| App-specific native engine logic | false |

Timing:

| Metric | Value |
| --- | ---: |
| Hot prepared-query OptiX over Embree | 203.022x |
| Actual repeat100 prepared loop OptiX over Embree | 200.353x |
| Actual cold plus repeat100 loop OptiX over Embree | 27.917x |
| Embree cold plus loop | 102.219s |
| OptiX cold plus loop | 3.662s |
| Embree workload build | 1.620s |
| OptiX workload build | 1.644s |
| Embree hit events before dedup | 1,853 |
| OptiX hit events before dedup | 3,693 |

This is measured actual repeat100 evidence, not the older modeled repeat100
projection.

The pre-dedup hit-event counts differ between Embree and OptiX because backend
traversal/order details differ before reduction. Both rows match the CPU
reference after grouped reduction, so this is not treated as a correctness
blocker.

## Excluded Rows

| Row | Reason |
| --- | --- |
| `grouped_reduction_sum_scalar_broadcast_repeat100_524288` | Excluded from first M7 promotion because cold plus loop is only 2.983x and OptiX cold plus loop is 98.960s. |
| `grouped_reduction_count_repeat100_262144` | Count row remains internal because break-even requires double-digit repeats. |
| `grouped_reduction_count_repeat100_524288` | Count row remains internal because break-even requires double-digit repeats. |

## Approved Row-Scoped Public Wording

This wording is authorized only for this exact row-scoped result:

```text
For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada
Generation pod, 262,144 rows / 1,024 groups, warmup=3 and actual repeat=100,
RTDL's OptiX route was 200.353x faster than the Embree route for the measured
100-query prepared loop. Counting cold prepare once plus that measured loop,
OptiX was 27.917x faster. This is a row-scoped grouped_reduction
prepared-query result, not a whole-app, whole-database, or broad V3-over-V2
speedup claim.
```

## Promotion Blockers

Closed for this exact row:

- fresh external public-row review closed by Claude;
- 2-AI consensus closed by Claude/Codex;
- source provenance gap documented;
- final wording approved for the exact row;
- whole-app and broad V3-over-V2 claims remain false.

Still not authorized:

- V3 release;
- broad V3-over-V2 speedup;
- whole-app or whole-database speedup;
- `grouped_reduction_sum_scalar_broadcast_repeat100_524288`;
- count rows.

## Forbidden Public Wording

- Do not claim V3 is 200x faster.
- Do not claim RTDL is 200x faster end to end.
- Do not claim RTDL is a database engine.
- Do not claim RayDB is accelerated end to end.
- Do not claim grouped_reduction proves broad V3-over-V2 speedup.
- Do not claim 524,288 grouped_sum is the public row.
- Do not claim count rows are public grouped_reduction speedup rows.

## Goal-Level Decision Audit

Decision: promote only the 262,144-row grouped_sum actual repeat100 row to
M7-qualified row-scoped status after Claude/Codex consensus.

1. Was I foolish?

   No. Claude approved the exact row subject to documenting source provenance
   and recording second-AI consensus; both conditions are now recorded.

2. If yes, what actions made the decision foolish?

   It would be foolish to treat this as a V3 release, hide the missing git_head
   provenance gap, include the 524,288-row/count rows, or claim broad
   V3-over-V2 speedup.

3. Was there another path?

   Leave the row in blocked candidate status even after external approval. That
   would under-use the strongest reusable V3 capability evidence.

4. Can I now try a different path that actually solves the problem?

   Promote one exact row, keep release and broad claims false, and continue
   Phoenix V3 with the next reusable capability.
