# Phoenix V3 Spatial RayJoin Topology-Stream Contract

Status: `spatial_rayjoin_topology_stream_contract_candidate_not_m7`.

This packet advances the Spatial RayJoin queue item by making the
`point_location_topology_stream` phase-accounting contract explicit.
It does not promote a new M7 row.

```text
release_authorized: false
public_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

Current local prepared OptiX payload interface:

- M3 table contract: `topology_stream_m3_phase_table_v1`
- Prepared handle contract: `topology_stream_prepared_handle_v1`
- Interface status: `local_payload_interface_added_not_pod_performance_closed`
- This is not POD performance closure and not a public Spatial RayJoin win.

## PIP Point-Location Accounting

- Contract: `rayjoin_cdb_point_location_positive_face_count`
- Query points: `100000`
- Exact mismatches: `0`
- RTDL OptiX / RTDL Embree wall speedup: `1.920x`
- RTDL OptiX visible non-traversal overhead fraction: `0.326`
- RayJoin author / RTDL OptiX wall speedup: `5.728x`
- RayJoin author / RTDL OptiX native traversal speedup: `3.861x`

RTDL OptiX beats RTDL Embree on the same point-location topology contract, but RayJoin author RT remains faster and RTDL OptiX still has material visible non-traversal overhead.

## Overlay Active-Count Accounting

- Contract: `overlay_active_pair_dependency_count`
- Left/right shapes: `478` / `501`
- Active count: `174`
- RTDL OptiX / RTDL Embree wall speedup: `499.112x`

Overlay active-count is strong internal same-contract topology evidence, but it is not full polygon overlay and has no author-paper comparison.

## Preserved M7 Blockers

- `rayjoin_author_rt_faster_than_rtdl_optix`
- `mixed_timing_basis_requires_public_methodology_review`
- `m3_phase_table_gap_for_pip_before_public_row`
- `not_full_rayjoin_paper_reproduction`
- `not_full_polygon_overlay_or_materialization`
- `no_future_public_row_2ai_consensus_for_spatial_rayjoin_m7_promotion`

## Future Public-Row Requirements

- Choose one named user contract, not the whole Spatial RayJoin app.
- Use one exact dataset path plus a saved query stream with parity-filter provenance.
- Report RTDL OptiX and RTDL Embree same-contract wall and native traversal timing.
- Use the topology_stream_prepared_handle_v1 payload metadata and topology_stream_m3_phase_table_v1 table emitted by the prepared OptiX route.
- When RayJoin author timing is cited, report the author timer basis beside RTDL wall and native traversal basis.
- Replace the current partial wall/native accounting with a full M3 phase table: static scene prepare, query stream prepare, device transfer or residency, RT traversal, topology continuation, and host return or scalar materialization.
- Keep paper, full overlay, RTDL-beats-RayJoin, and broad V3-over-V2 wording false unless separately proven.
- Obtain fresh external public-row review plus Codex consensus before any Spatial RayJoin M7 promotion.

## Forbidden Shortcuts

- Do not promote the 1.920x RTDL OptiX/Embree wall ratio without author and M3 phase context.
- Do not invert the 5.728x RayJoin-author-over-RTDL-OptiX gap into an RTDL win.
- Do not publish the 499x overlay active-count row as full polygon overlay.
- Do not mix the tiny 0.034x route-health row with authored hot-route rows without contract labels.

## Goal-Level Decision Audit

Decision: Add topology-stream phase accounting for Spatial RayJoin without promoting a row.

1. Was I foolish?
   No. This exposes the RTDL overhead and author timing gap instead of hiding them behind a same-contract OptiX/Embree win.
2. If yes, what actions made the decision foolish?
   It would be foolish to quote the 1.920x PIP wall win or 499x overlay active-count win without also showing that RayJoin author RT is faster and that PIP lacks a full M3 phase table.
3. Was there another path that would have avoided getting stuck on that idea?
   Tune RayJoin-specific code immediately. That might improve one benchmark, but it would not give Phoenix a reusable topology-stream accounting contract.
4. Can I now try a different path that actually solves the problem?
   Use this contract to drive the next public-row runner: reduce visible non-traversal overhead, collect full M3 phases, and keep author/paper wording blocked until reviewed.
