# Phoenix V3 Spatial RayJoin Exact-Executor Intake

Status: `spatial_rayjoin_exact_executor_intake_not_m7`.

This is a generic-engine intake packet for `point_location_topology_stream`.
Spatial RayJoin is the evidence harness, not the product boundary.

## Current POD Packet

- Source: `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json`
- Dataset: `/root/rtdl_v3_rebuild_20260620/current/data/rayjoin_public_cdb/br_county.cdb`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- Count mode: `exact_prepared_points_executor`
- Repeat protocol: sample_repeat=5, query_repeat=50, warmup=5
- Stable exact row count: `47262`
- Failed checks: `[]`
- Query stream residency: `device_resident_prepared_point_probe_columns_with_reusable_exact_executor`

## M3 Bottleneck Reading

| Phase | Median seconds |
| --- | ---: |
| static scene prepare | 0.19943977892398834 |
| query stream prepare | 0.05608516186475754 |
| device transfer/residency | 0.0 |
| RT traversal/candidate emission | 0.000437483 |
| topology continuation/exact refine | 0.023139639 |
| host return/scalar materialization | 7.6802e-05 |

Topology continuation / RT traversal: `52.89265868616609`.
Topology continuation fraction of prepared query: `0.9966330513869565`.

The reusable executor keeps query columns resident and removes device-transfer cost, but the hot path is dominated by exact topology continuation/refinement, not RT traversal.

## Rejected Probe

The device-filtered route remains rejected:

- Source: `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621/run.log`
- Device-filtered count: `47570`
- Exact count: `47262`

## Author Gap Boundary

- Scope: `prior_100k_same_stream_author_comparison_not_direct_public_county_packet`
- Prior RayJoin author / RTDL native traversal speedup: `3.860711740744286`
- Direct current-packet comparison authorized: `false`

This author gap is a carried-forward boundary from the prior M5 same-stream packet,
not a direct comparison against the public-county exact-executor packet.

## Claim Boundary

- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `m7_promotion_authorized: false`
- `m7_qualified_release_rows_added: 0`

## Next Engine Actions

- Move exact closed-shape membership/refinement work out of host GEOS/refine loops where a generic exact device continuation is possible.
- Keep the executor capacity policy explicit and fail-closed on overflow.
- Only compare to RayJoin author timing in a same-dataset packet with the timer basis printed beside RTDL wall and native/M3 phases.
- Seek external review before any Spatial RayJoin M7 wording.

## Forbidden Shortcuts

- Do not treat the public-county exact-executor packet as RayJoin-author comparison evidence.
- Do not publish the rejected device-filtered route.
- Do not call prepared point-column residency true zero-copy.
- Do not promote Spatial RayJoin to M7 without same-contract author-basis review.

## Goal-Level Decision Self-Audit

Decision: Convert the Spatial exact-executor POD result into a not-M7 intake packet that identifies the generic topology-continuation bottleneck.

1. Was I foolish?
   No. The packet prevents a fresh full-M3 POD result from being mistaken for an author comparison or public speedup row.
2. If yes, what actions made the decision foolish?
   The foolish action would be to quote the executor result as RTDL beating RayJoin, or to hide that exact refinement dominates the prepared query.
3. Was there another path that would have avoided getting stuck on one idea?
   Run more Spatial app timings immediately. That could add numbers, but it would not clarify the generic engine bottleneck or release boundary.
4. Can I now try a different path that actually solves the problem?
   Use the intake to drive generic exact topology-continuation work, then rerun a same-dataset author-basis packet before any M7 review.
