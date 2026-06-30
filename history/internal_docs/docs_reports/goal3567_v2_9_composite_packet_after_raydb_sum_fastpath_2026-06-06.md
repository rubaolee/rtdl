# Goal3567 v2.9 Composite Packet After RayDB Sum Fast Path

Date: 2026-06-06

## Purpose

Goal3565 repaired the stale RayDB `sum` weak row by adding and validating a
generic small dense grouped-i64 sum fast path. Goal3567 refreshes the v2.9
all-app performance table so the packet no longer carries the pre-fast-path
RayDB numbers from Goal3558.

Artifact directory:

`docs/reports/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_a5000/`

## Method

This is an explicit composite packet, not a raw all-row rerun:

- 9 unchanged rows are reused from the Goal3558 A5000 full 10-second packet.
- 2 RayDB rows are replaced with Goal3565 targeted A5000 evidence.

A raw all-row rerun was attempted on the A5000 pod, but it spent several
minutes in an unchanged CPU-heavy v2.3 robot-collision row before reaching the
RayDB rows. Because the native/code change only affects the grouped-i64
`sum`/`sum_count` path, the cleaner evidence path is to preserve the existing
10-second rows for unchanged apps and splice in the fresh targeted RayDB
evidence with row-level provenance.

## Packet Summary

| Metric | Value |
| --- | ---: |
| row count | 11 |
| reused Goal3558 rows | 9 |
| Goal3565 replacement rows | 2 |
| geomean speedup | 1.069163x |
| median speedup | 1.009085x |
| min speedup | 0.987619x |
| max speedup | 1.585627x |

## Comparison Rows

| Case | v2.3 sec | v2.9 sec | v2.9 speedup | Evidence source |
| --- | ---: | ---: | ---: | --- |
| `robot_collision_optix_prepared_device_buffers` | 0.001890558 | 0.001914259 | 0.987619x | Goal3558 full 10-second packet |
| `spatial_rayjoin_optix_prepared_full_route` | 0.000179248 | 0.000181246 | 0.988978x | Goal3558 full 10-second packet |
| `librts_optix_aabb_index` | 0.000752487 | 0.000758727 | 0.991776x | Goal3558 full 10-second packet |
| `barnes_hut_optix_node_coverage` | 0.008123981 | 0.008174485 | 0.993822x | Goal3558 full 10-second packet |
| `rt_dbscan_optix_grouped_stream` | 0.012592142 | 0.012627419 | 0.997206x | Goal3558 full 10-second packet |
| `raydb_optix_partner_resident_count` | 0.000588950 | 0.000583647 | 1.009085x | Goal3565 targeted RayDB fast-path packet |
| `hausdorff_optix_threshold` | 0.031770580 | 0.031161210 | 1.019555x | Goal3558 full 10-second packet |
| `triangle_counting_optix_rt_graph_2a1_partner` | 0.000362574 | 0.000352157 | 1.029580x | Goal3558 full 10-second packet |
| `rtnn_optix_prepared_3d_ranked_summary` | 0.001532887 | 0.001444450 | 1.061225x | Goal3558 full 10-second packet |
| `contact_manifold_optix_aabb_broadphase_collect_k` | 0.028139902 | 0.023074425 | 1.219528x | Goal3558 full 10-second packet |
| `raydb_optix_partner_resident_sum` | 0.000751490 | 0.000473938 | 1.585627x | Goal3565 targeted RayDB fast-path packet |

## Interpretation

The RayDB weak row identified after Goal3558 is repaired in the v2.9 packet:

- RayDB `sum`: `0.944269x` became `1.585627x`.
- RayDB `count`: `0.972533x` became `1.009085x`.

The improvement comes from generic runtime behavior, not app-specific engine
logic: for small dense grouped-i64 `sum`/`sum_count`, the native path
accumulates counts and sums in shared memory per block and emits far fewer
global atomics.

The remaining negative rows are near-parity unchanged rows from Goal3558. This
packet therefore closes the stale-RayDB-table problem, but it does not imply
that v2.9 has no remaining performance tuning opportunities.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_test tests.goal3566_claude_review_goal3563_3565_v29_raydb_sum_fastpath_test tests.goal3565_raydb_sum_fastpath_a5000_test tests.goal3564_grouped_i64_small_group_sum_fastpath_test
```

Pod evidence:

```text
GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
Goal3565 targeted RayDB sum: 1.585627x
Goal3565 targeted RayDB count: 1.009085x
```

## Next Step

Close the v2.9 internal performance packet with external review of this
composite provenance, then decide whether the remaining near-parity negatives
belong in v2.9 cleanup or are deferred to the next performance version.
