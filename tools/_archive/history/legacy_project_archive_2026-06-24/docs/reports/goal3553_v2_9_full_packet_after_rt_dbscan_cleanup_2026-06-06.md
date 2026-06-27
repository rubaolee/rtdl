# Goal3553 v2.9 Full A5000 Packet After RT-DBSCAN Cleanup

Date: 2026-06-06

## Summary

Goal3553 refreshes the full 11-row v2.8/v2.3 same-contract packet after the Goal3551/Goal3552 RT-DBSCAN internal-repeat cleanup. It also raises `--max-internal-repeat` to `250000`, because RayJoin's prepared-route hot loop is very fast and otherwise hits the old `50000` repeat cap before reaching the 10-second evidence target. The final packet embeds the per-lane plans used for every row.

Final artifact:

- `docs/reports/goal3553_v2_9_full_packet_after_rt_dbscan_a5000_cap250k/summary.json`
- `docs/reports/goal3553_v2_9_full_packet_after_rt_dbscan_a5000_cap250k/summary.md`

Seed artifact:

- `docs/reports/goal3553_v2_9_full_packet_seed_after_rt_dbscan.json`

Hardware:

- NVIDIA RTX A5000
- Driver 580.126.09
- 24564 MiB memory

## Packet Result

All rows are target-compliant:

- row count: `11`
- ratio count: `11`
- target met by plan: `11/11`
- target met by observed measured time: `11/11`
- observed target misses: `0`

Aggregate:

- geomean speedup: `1.000293x`
- median speedup: `0.998649x`
- min speedup: `0.845813x`
- max speedup: `1.094800x`

## Row Table

| App | Case | v2.3 primary sec | v2.8 primary sec | v2.8/v2.3 | Observed sec v2.3/v2.8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Barnes-Hut | `barnes_hut_optix_node_coverage` | `0.00829550` | `0.00808242` | `1.026x` | `12.825 / 12.180` |
| Contact manifold | `contact_manifold_optix_aabb_broadphase_collect_k` | `0.0232914` | `0.0275373` | `0.846x` | `10.574 / 12.474` |
| Hausdorff X-HD | `hausdorff_optix_threshold` | `0.0336996` | `0.0307815` | `1.095x` | `13.278 / 12.097` |
| LibRTS spatial index | `librts_optix_aabb_index` | `0.000750912` | `0.000750632` | `1.000x` | `12.347 / 12.502` |
| RayDB count | `raydb_optix_partner_resident_count` | `0.000586916` | `0.000537366` | `1.092x` | `12.403 / 11.367` |
| RayDB sum | `raydb_optix_partner_resident_sum` | `0.000750821` | `0.000751837` | `0.999x` | `11.883 / 11.903` |
| Robot collision | `robot_collision_optix_prepared_device_buffers` | `0.00187188` | `0.00191219` | `0.979x` | `12.388 / 13.039` |
| RT-DBSCAN | `rt_dbscan_optix_grouped_stream` | `0.0126433` | `0.0126609` | `0.999x` | `12.517 / 12.433` |
| RTNN | `rtnn_optix_prepared_3d_ranked_summary` | `0.00131119` | `0.00137186` | `0.956x` | `11.621 / 12.943` |
| Spatial RayJoin | `spatial_rayjoin_optix_prepared_full_route` | `0.000191489` | `0.000181905` | `1.053x` | `13.343 / 12.764` |
| Triangle counting | `triangle_counting_optix_rt_graph_2a1_partner` | `0.000349659` | `0.000355497` | `0.984x` | `12.456 / 12.401` |

## Interpretation

This packet is a better v2.9 baseline than Goal3548 because every row now satisfies both the plan target and the observed 10-second measured-time target. The old RT-DBSCAN weak row is no longer the main problem; it moved from `0.955x` in Goal3548 to `0.999x` here under the calibrated internal-repeat protocol.

The result is not a performance victory yet. It is a clean parity baseline:

- Several rows are positive: Hausdorff, RayDB count, Spatial RayJoin, Barnes-Hut.
- Several rows are near parity: LibRTS, RayDB sum, RT-DBSCAN, triangle counting, robot collision.
- The main negative rows are now:
  - Contact manifold: `0.846x`
  - RTNN ranked summary: `0.956x`
  - Robot collision: `0.979x`

The next v2.9 work should target real runtime/kernel improvements, not measurement cleanup. Contact manifold is the top priority because it is the only large regression left in the all-target packet.

## Boundary

This is internal benchmark evidence only. It does not authorize:

- release;
- public speedup claims;
- whole-app speedup claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.

## Next Step

Goal3554 should focus on the contact-manifold row. The likely question is whether v2.8's AABB broadphase collect-k path has extra bounded-witness overhead versus the v2.3 overlay, or whether the difference is measurement noise exposed by a large repeat count. The first step should be a targeted contact-manifold packet with phase-level inspection before changing code.
