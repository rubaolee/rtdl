# Phoenix V3 Spatial RayJoin Relation-Status Corrected Executor No-Go

Status: `spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch`.

This packet records a rejected generic point-location topology-stream candidate.
It is not a release packet, not M7, and not public speedup evidence.

## Evidence

- Source log: `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_relation_status_corrected_rejected_smoke_20260621/run.log`
- Dataset: `/root/rtdl_v3_rebuild_20260620/current/data/rayjoin_public_cdb/br_county.cdb`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- Candidate route: `relation_status_corrected_executor_validated`
- Exact authority count: `47262`
- Candidate count: `47259`
- Candidate minus exact: `-3`
- Failure class: `validated_candidate_exactness_mismatch`

## Interpretation

The relation-status corrected executor is a reusable generic device-side scalar-count candidate, but it is not exact on the public county packet. The fail-closed validation worked and no Spatial RayJoin M7 or public speedup claim is authorized.

## Claim Boundary

- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `m7_promotion_authorized: false`
- `m7_qualified_release_rows_added: 0`

## Next Engine Action

Keep the route diagnostic-only until relation-status boundary semantics match exact prepared closed-shape membership on public county plus adverse subset evidence.

## Goal-Level Decision Self-Audit

Decision: Reject the relation-status corrected Spatial executor for Phoenix M7 after exact-count validation failed on public county.

1. Was I foolish?
   No. I tried a plausible existing generic continuation route but required exact parity before allowing evidence promotion.
2. If yes, what actions made the decision foolish?
   The foolish action would be to keep the faster-looking route, hide the 47259 != 47262 mismatch, or call it an acceptable approximation for V3.
3. Was there another path that would have avoided getting stuck on one idea?
   I could have skipped this route because old history had mixed correctness. Testing it with a fail-closed gate was better because it produced current evidence.
4. Can I now try a different path that actually solves the problem?
   Do not promote relation-status corrected Spatial. Continue with exact topology-continuation correctness repair or another generic engine target.
