# Codex 2-AI Consensus: Phoenix V3 Spatial RayJoin M7 Feasibility

Status: Claude/Codex consensus complete for a not-promoted Spatial RayJoin
feasibility packet.

## Sources

```text
docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md
docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.json
docs/reviews/claude_phoenix_v3_spatial_rayjoin_m7_feasibility_review_2026-06-21.md
docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
```

## Verdict

Codex agrees with Claude's `APPROVE_WITH_REQUIRED_FIXES` verdict after applying
the required packet fixes. Spatial RayJoin remains a strong internal
point-location/topology-stream capability family, but no Spatial RayJoin row is
promoted to M7 from this packet.

Keep false:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
```

## Fixes Applied

Claude P1 required a named 2-AI consensus gate so future work cannot treat this
packet as closed by accident. The packet now records:

```text
current_packet_external_review_status: claude_approved_with_required_fixes
current_packet_2ai_consensus_status: claude_codex_consensus_complete_no_m7_promotion
no_future_public_row_2ai_consensus_for_spatial_rayjoin_m7_promotion
```

Claude P2 notes were also applied:

```text
"strongest" -> "stronger" with M7 classification context
authored hot-route rows now cite the M7 classification packet as provenance
overlay active-count table now states OptiX/Embree repeats are 25 / 25
```

## Boundary

Allowed internal reading:

```text
Spatial RayJoin has useful V3 topology-stream evidence: RTDL OptiX and RTDL
Embree match on same-contract point-location and active-count rows, and RTDL
OptiX beats RTDL Embree on those exact internal contracts.
```

Forbidden:

```text
Do not claim RTDL beats RayJoin.
Do not claim RayJoin paper reproduction.
Do not claim full polygon overlay acceleration.
Do not cite the 0.034x tiny row or 30489x authored hot row as a public result.
Do not promote Spatial RayJoin to M7 without a new public-row packet and review.
```

## Goal-Level Decision Audit

Decision: close the Spatial RayJoin feasibility packet as reviewed but not
M7-promoted.

1. Was I foolish?

   No. The decision follows Claude's review, fixes the named gate issue, and
   refuses to turn a large hot-route number into a user-facing release claim.

2. If yes, what actions would make the decision foolish?

   It would be foolish to hide that RayJoin author RT is faster than RTDL
   OptiX on the M5 PIP row, or to treat same-contract topology evidence as
   RayJoin paper reproduction.

3. Was there another path?

   Yes. I could have tried to promote the 30489x authored row or tune RayJoin
   immediately. That would optimize the wrong claim before methodology is
   safe.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep Spatial RayJoin as internal V3 topology-stream evidence, require
   a future public-row packet for any promotion, and move Phoenix to the next
   candidate without misleading users.
