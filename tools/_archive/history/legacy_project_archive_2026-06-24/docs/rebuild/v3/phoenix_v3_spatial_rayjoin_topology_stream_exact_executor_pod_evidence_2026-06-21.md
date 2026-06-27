# Phoenix V3 Spatial RayJoin Topology-Stream Exact-Executor POD Evidence

Status: `spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7`.

This packet records fresh RTX 4000 Ada POD evidence for the reusable V3
`point_location_topology_stream` surface. Spatial RayJoin is only the evidence
harness here; the measured route is the generic OptiX prepared point/closed-shape
exact scalar-count executor with prepared point columns.

## Evidence Paths

- Main packet:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json`
- Smoke packet:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_smoke2_20260621/summary.json`
- Rejected device-filtered probe:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621/run.log`

## Main POD Result

- Dataset: public `br_county.cdb` on the RTX pod.
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- Count mode: `exact_prepared_points_executor`.
- Point order: `morton_xy`.
- Repeat protocol: `sample_repeat=5`, `query_repeat=50`, `warmup=5`.
- Stable exact row count: `47262`.
- Failed checks: `[]`.
- M7 rows added: `0`.

Median timing summary from the main packet:

| Field | Median seconds |
| --- | ---: |
| runner wall | 2.8939708545804024 |
| prepared query | 0.023217812180519104 |
| prepared query total for repeat=50 | 1.1688360273838043 |
| static scene prepare | 0.19943977892398834 |
| query stream prepare | 0.05608516186475754 |
| device transfer or residency | 0.0 |
| RT traversal / candidate emission | 0.000437483 |
| topology continuation / exact refine | 0.023139639 |
| host return / scalar materialization | 0.000076802 |

The prepared handle reports
`device_resident_prepared_point_probe_columns_with_reusable_exact_executor`.
This is a real V3 topology-stream/executor surface improvement, but it is not a
public speedup row: the hot path is still dominated by exact topology
continuation/refinement, and the packet has no author timing comparison or
external release review.

## Rejected Route

The same POD pass rejected `device_filtered_prepared_points_validated` on the
public county dataset:

```text
validated device-side closed-shape count did not match exact prepared count: 47570 != 47262
```

That route remains a correctness blocker, not a fast route. It must not be used
for V3 performance wording.

## Claim Boundary

- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `row_scoped_public_speedup_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `v4_embedding_claim_authorized: false`
- `m7_promotion_authorized: false`

## Goal-Level Decision Self-Audit

Decision: switch the Spatial topology-stream POD route from rejected
device-filtered counting to exact prepared-points executor evidence, while
keeping Spatial RayJoin unpromoted.

1. Was I foolish?
   No. The POD run first exposed that the device-filtered route is not exact on
   the public county dataset, then moved to the exact reusable executor route
   instead of hiding the mismatch.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would have been to tune around the
   mismatch, call the device-filtered count "close enough", or publish its
   timing.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. The older path was to keep using exact prepared-points without exposing
   executor capacity or M3 phase attribution. That was safer than
   device-filtered counting but left the reusable V3 executor surface
   under-documented.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is engine-level: reduce the remaining
   topology-continuation/exact-refine bottleneck or produce an author-basis
   comparison packet for external review. No M7 promotion is justified by this
   packet alone.
