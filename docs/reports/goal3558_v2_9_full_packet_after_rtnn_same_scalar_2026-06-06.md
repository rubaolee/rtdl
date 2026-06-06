# Goal3558 v2.9 Full A5000 Packet After RTNN Same-Scalar Cleanup

Date: 2026-06-06

## Purpose

Goal3557 corrected the RTNN v2.3 overlay so both v2.3 and v2.8/v2.9 use the same `elapsed_median_sec` scalar. Goal3558 refreshes the full 11-row A5000 v2.9/v2.3 packet with that correction.

Artifact directory:

`docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_a5000_cap250k/`

## Packet Summary

| Metric | Value |
| --- | ---: |
| row count | 11 |
| target plan met pairs | 11 |
| target observed met pairs | 11 |
| observed target misses | 0 |
| geomean speedup | 1.016537x |
| median speedup | 0.993822x |
| min speedup | 0.944269x |
| max speedup | 1.219528x |

## Comparison Rows

| Case | v2.3 sec | v2.8/v2.9 sec | v2.8/v2.9 speedup |
| --- | ---: | ---: | ---: |
| `raydb_optix_partner_resident_sum` | 0.000748903 | 0.000793103 | 0.944269x |
| `raydb_optix_partner_resident_count` | 0.000571252 | 0.000587386 | 0.972533x |
| `robot_collision_optix_prepared_device_buffers` | 0.001890558 | 0.001914259 | 0.987619x |
| `spatial_rayjoin_optix_prepared_full_route` | 0.000179248 | 0.000181246 | 0.988978x |
| `librts_optix_aabb_index` | 0.000752487 | 0.000758727 | 0.991776x |
| `barnes_hut_optix_node_coverage` | 0.008123981 | 0.008174485 | 0.993822x |
| `rt_dbscan_optix_grouped_stream` | 0.012592142 | 0.012627419 | 0.997206x |
| `hausdorff_optix_threshold` | 0.031770580 | 0.031161210 | 1.019555x |
| `triangle_counting_optix_rt_graph_2a1_partner` | 0.000362574 | 0.000352157 | 1.029580x |
| `rtnn_optix_prepared_3d_ranked_summary` | 0.001532887 | 0.001444450 | 1.061225x |
| `contact_manifold_optix_aabb_broadphase_collect_k` | 0.028139902 | 0.023074425 | 1.219528x |

## Interpretation

The v2.9 performance picture is now much cleaner than the Goal3553 packet:

- RTNN is no longer a weak row after same-scalar cleanup: `0.956x` became `1.061x` in the full packet.
- Contact manifold is no longer a weak row after the collect-k microprobe correction: the full packet now shows `1.220x`.
- RT-DBSCAN remains essentially parity at `0.997x`.
- The worst remaining rows are RayDB sum (`0.944x`) and RayDB count (`0.973x`), followed by small near-parity negatives in robot collision, spatial RayJoin, LibRTS, and Barnes-Hut.

The packet is target-compliant and useful as internal v2.9 triage evidence. It is not a release or public speedup packet.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

## Validation

Pod validation:

```text
GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
Goal3536 full packet: 11/11 target plan met, 11/11 target observed met, 0 observed misses
```

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3558_v2_9_full_packet_after_rtnn_same_scalar_test tests.goal3557_rtnn_same_scalar_median_metric_a5000_test tests.goal3556_rtnn_median_repeat_metric_hardening_test
```

## Next Step

Start the next performance goal on RayDB partner-resident sum/count. The likely question is whether the v2.9 path added overhead in the generic grouped-i64 dispatch or in measurement/setup around the partner-resident query.
