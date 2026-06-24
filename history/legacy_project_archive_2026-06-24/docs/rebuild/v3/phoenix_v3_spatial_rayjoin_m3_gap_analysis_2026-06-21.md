# Phoenix V3 Spatial RayJoin M3 Gap Analysis

Status: `spatial_rayjoin_m3_gap_analysis_not_m7`.

This is an optimization-target packet, not a release row. It answers why
Spatial RayJoin remains useful for V3: it exposes a reusable
`point_location_topology_stream` host-staging and phase-accounting problem.

```text
release_authorized: false
public_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
true_zero_copy_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Same-Stream PIP 100k

- Query count: `100000`
- RTDL OptiX / RTDL Embree wall speedup: `10.129x`
- RayJoin author / RTDL OptiX wall speedup: `11.541x`
- Backend exact counts match: `true`

RTDL OptiX is much faster than RTDL Embree on this exact scalar-count same-stream contract, but RayJoin author RT is still faster than RTDL OptiX.

## Large PIP Device-Resident Delta

- Query points: `5288684`
- Counts match: `true`
- Default host-points wall: `0.273922s`
- Device-resident points wall: `0.120060s`
- Device-resident wall speedup vs default: `2.282x`
- Default visible residual after native transfer: `0.140988s`
- Device-resident visible residual after native transfer: `0.001373s`

The old large-PIP evidence shows the useful V3 direction: keep the query point stream resident inside RTDL's prepared route and the hot wall time moves close to native traversal. This is internal V3 topology-stream residency evidence, not a true zero-copy product claim.

## M3 Public-Row Gap

Required phases:

- `static_scene_prepare_sec`
- `query_stream_prepare_sec`
- `device_transfer_or_residency_sec`
- `rt_traversal_sec`
- `topology_continuation_sec`
- `host_return_or_scalar_materialization_sec`

Available now:

- same-contract RTDL OptiX/Embree wall timing
- same-stream RayJoin author timer basis
- native traversal and point-upload medians for large PIP route
- device-resident internal route delta

Missing or not public-row ready:

- single fresh runner that emits all M3 phases together
- static scene prepare for the large device-resident route in the same packet
- query-stream prepare separated from device transfer/residency
- topology continuation separated from RT traversal
- host scalar return separated from Python dispatch
- fresh external public-row review plus Codex consensus

Next engine target:

Build or repair a reusable topology-stream prepared handle/runner that keeps query columns resident, emits the full M3 phase table, and proves the same contract against Embree and RayJoin author timing without RayJoin-specific native logic.

## Forbidden Shortcuts

- Do not call the device-resident internal delta true zero-copy.
- Do not claim RTDL beats RayJoin from the same-stream PIP evidence.
- Do not publish Spatial RayJoin M7 wording until a fresh full-M3 public row passes review.
- Do not implement a RayJoin-only native shortcut; the target is a reusable topology-stream prepared route.

## Goal-Level Decision Audit

Decision: Use old and current RayJoin evidence to define a V3 topology-stream M3 gap and optimization target, not to promote Spatial RayJoin.

1. Was I foolish?
   No. This converts the confusing RayJoin evidence into a reusable V3 engine target and keeps every release/public flag false.
2. If yes, what actions made the decision foolish?
   The foolish action would be to quote either the 1.920x OptiX/Embree row or the 2x device-resident delta as a public Spatial RayJoin win while hiding the RayJoin-author gap and incomplete M3 table.
3. Was there another path that would have avoided getting stuck on that idea?
   Keep rerunning author comparisons. That may produce more tables, but it does not itself reduce RTDL host/query staging or make V3 user-responsible.
4. Can I now try a different path that actually solves the problem?
   Treat resident topology-stream columns and full phase accounting as the next generic V3 engine task.
