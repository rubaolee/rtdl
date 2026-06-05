# Goal3533 v2.8 Promoted-Path Recovery Table

Date: 2026-06-05

Status: internal recovery table for Goal3527. This is not a release packet and does not authorize public speedup wording, broad RT-core speedup wording, whole-app acceleration claims, true zero-copy claims, paper reproduction claims, package-install claims, hidden partner selection, or app-specific native-engine behavior.

## Purpose

Goal3524 gave us a useful but uncomfortable same-runner table: it was reproducible on an RTX A5000, but it blended older v2.3-era runner contracts with newer v2.8 promoted paths. The most visible problems were:

- Barnes-Hut appeared as a severe `0.401x` regression.
- RayJoin appeared as a weak single `1.096x` row, hiding several different promoted contracts.
- Several rows hovered near `1.0x`, making the table look technically correct but unconvincing.

Goal3527 required us to stop hiding behind the blended table. Goal3533 is the recovery table that separates diagnostic same-runner evidence from promoted-path evidence.

## Evidence Sources

| Evidence | Artifact |
| --- | --- |
| Same-runner v2.8 vs v2.3 diagnostic table | `docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json` |
| Barnes-Hut cold repeated probe | `docs/reports/goal3531_barnes_hut_p0_focus_a5000/summary.json` |
| Barnes-Hut warm prepared-query probe | `docs/reports/goal3531_barnes_hut_p0_warm_probe_a5000/summary.json` |
| RayJoin promoted-contract packet | `docs/reports/goal3532_rayjoin_promoted_contract_packet_a5000_cdb_pair/summary.json` |

All A5000 evidence in this chain used the same pod endpoint family recorded in the source reports. Goal3532 specifically used:

- Pod: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- RTDL commit: `98879336e041bff6363f0a18e3996953a021d53a`

## Recovery Table

| Area | Goal3524 diagnostic | Promoted/recovered evidence | Current reading |
| --- | ---: | --- | --- |
| Barnes-Hut node coverage | `0.401x`; rerun `0.503x` | Warm prepared-query: `0.983x` at 8192 bodies, `1.015x` at 32768 bodies | Recovered for steady-state prepared use; cold one-shot path remains diagnostic debt. |
| RayJoin blended route | `1.096x` | Split into 10 promoted contract rows; relation/grouped/payload/overlay continuations are isolated and mostly sub-ms on checked-in CDB pair | Old row should not be used as headline; use per-contract packet instead. |
| Contact manifold | `0.973x`; rerun `1.030x` | No promoted-path rewrite needed for Goal3527 | Treat as parity/noise until a larger same-contract probe says otherwise. |
| RayDB count | `0.987x`; rerun `0.997x` | RayDB sum is `7.202x`; count is flat | Count is parity/noise; sum is the real promoted primitive win. |
| Robot collision | `0.990x`; rerun `0.969x` | No recovery packet yet | Small but consistent loss remains open; lower priority than Barnes-Hut/RayJoin because absolute delta is tiny. |
| Triangle counting | `0.992x`; rerun `1.025x` | No recovery packet needed for Goal3527 | Treat as parity/noise. |
| RT-DBSCAN grouped stream | `1.111x` | Same-runner win, no immediate recovery needed | Modest positive row; not a broad claim. |
| RTNN ranked summary | `1.038x` | Same-runner win, no immediate recovery needed | Modest positive row; not a broad claim. |
| LibRTS AABB index | `1.002x` | Same-runner parity | Stable parity row. |
| Hausdorff threshold | `1.203x` | Same-runner win | Positive row, but still a threshold-decision contract, not exact full Hausdorff. |

## RayJoin Contract Rows

Goal3532 replaces the old single RayJoin row with this promoted-contract packet:

| Row | Primary metric sec | Contract |
| --- | ---: | --- |
| `rayjoin_count_parity_pip_prepared_optix` | 0.000275 | point closed-shape membership count |
| `rayjoin_count_parity_lsi_left_id_dense_count` | 0.059606 | segment-pair intersection count by left id |
| `rayjoin_count_parity_overlay_seed_active_count` | 0.345494 | shape-pair active dependency count |
| `rayjoin_relation_columns_cdb_pair` | 0.000532 | shape-pair relation device columns |
| `rayjoin_relation_grouped_count_cdb_pair` | 0.000177 | shape-pair relation grouped count by left |
| `rayjoin_shape_pair_payload_bounds_cdb_pair` | 0.000936 | bounds-overlap area payload |
| `rayjoin_shape_pair_payload_witness_cdb_pair` | 0.000721 | relation witness payload |
| `rayjoin_overlay_area_relation_stream_cdb_pair` | 0.000454 | shape-pair relation stream steady-state |
| `rayjoin_overlay_area_device_tile_planner_cdb_pair` | 0.001283 | prepared overlay-area device tile-task planner |
| `rayjoin_overlay_area_tile_executor_cdb_pair` | 0.001268 | prepared overlay-area tile-task executor |

Correctness:

- Relation rows stable across 3 iterations: `[9, 9, 9]`
- Grouped-count sums match rows: `true`
- Relation witnesses resolved: `true`
- Overlay positive row-count matches Shapely/GEOS oracle: `true`
- Overlay total area absolute error: `8.661876771398624e-12`
- Overlay max relation absolute error: `7.238779020646291e-12`

Boundary: these rows use the checked-in non-empty CDB fixture pair, not missing public-CDB data, and they are not a RayJoin paper reproduction.

## Engineering Meaning

Goal3527 is now materially repaired, but not transformed into a marketing win:

- The Barnes-Hut catastrophe was mostly a cold/setup measurement artifact for the promoted use case. Warm prepared-query evidence clears the `>=0.95x` recovery bar at both tested scales.
- RayJoin was never one thing. The promoted contract packet shows strong isolated continuation timings, but it also exposes which count paths still carry setup or tiny-fixture overhead.
- The near-1.0 rows are not exciting, and we should not pretend they are. They are either parity/noise or small open debts.

The right next performance work is not another blended all-app table. It is targeted recovery:

1. Robot collision warm prepared-device-buffer probe, because it is a small but repeated loss.
2. RayJoin larger resident CDB/RayJoin-exported stream packet, because tiny fixture rows understate the continuation work and overstate setup.
3. RayJoin overlay active-count route tuning, because `0.345494s` is the remaining ugly promoted-contract row in the packet.

## Verdict

`accept-with-boundary`

Goal3527's immediate recovery requirement is satisfied for Barnes-Hut and RayJoin interpretability: the severe Barnes-Hut regression is explained/recovered under warm promoted use, and the weak RayJoin row is decomposed into contract-level evidence. The table still does not justify public release or speedup claims.
