# Call For Review: Phoenix V3 Spatial RayJoin M7 Feasibility

Date: 2026-06-20

Scope: V3-only. Review the new Spatial RayJoin M7 feasibility packet and decide
whether its classification is honest:

```text
status: spatial_rayjoin_m7_feasibility_not_promoted
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

## Artifacts To Review

- Feasibility packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md`
- Machine-readable packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json`
- Current M5 evidence:
  `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`
- M5 artifact:
  `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620`
- Existing external M5 review:
  `docs/reviews/claude_phoenix_v3_m5_author_recovery_review_2026-06-20.md`
- Existing Codex M5 closure:
  `docs/reviews/codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md`
- Current M7 row classification:
  `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`

## Facts Claimed By The New Packet

- The standard all-workload row remains a tiny negative non-claim:
  `rayjoin_all_backend_query_summary`, `0.03414924661592695x`.
- The M5 PIP point-location row uses 100,000 backend-parity-filtered points,
  rejects 1 exact-row tie candidate, has 0 exact mismatches, and avoids row
  materialization in the timed path.
- RTDL OptiX beats RTDL Embree on the M5 PIP same-contract row:
  `1.920x` wall and `2.834x` native traversal.
- RayJoin author RT is faster than RTDL OptiX on that PIP row:
  `5.728x` versus RTDL OptiX wall and `3.861x` versus RTDL OptiX native
  traversal.
- Overlay active-count is same-contract internal evidence with active count
  `174`, not full polygon overlay.
- Authored hot-route rows are strong internal OptiX-over-Embree signals, but
  they are not M7 public rows.

## Review Questions

1. Is `spatial_rayjoin_m7_feasibility_not_promoted` the correct classification?
2. Does the packet correctly separate tiny route-health evidence, same-contract
   topology evidence, authored hot-route evidence, and RayJoin author-code
   comparison?
3. Are any statements still too strong for current evidence?
4. Are the listed M7 blockers complete enough before any future public row
   promotion?
5. Does this packet introduce any V4/C ABI/embedding leakage or broad V3-over-V2
   speedup claim?

## Requested Verdict Format

Return one of:

```text
APPROVE
APPROVE_WITH_REQUIRED_FIXES
REJECT
```

Include P0/P1/P2 findings. Treat missing claim boundaries, paper-reproduction
leakage, or hiding that RayJoin author RT is faster as P0.
