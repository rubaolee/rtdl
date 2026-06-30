# Goal3569 v2.9 Internal Performance Closeout

Date: 2026-06-06

## Purpose

Goal3569 closes v2.9 as an internal performance version. It consolidates the
late v2.9 evidence chain after the v2.8/v2.3 packet looked too weak for several
benchmark rows.

This is not a release packet and does not authorize public speedup claims.

## Evidence Chain

| Goal | Purpose | Result |
| --- | --- | --- |
| Goal3558 | Full A5000 v2.9/v2.3 packet after RTNN same-scalar cleanup | 11/11 rows target-compliant; RayDB sum still stale-negative at `0.944269x` |
| Goal3560 | Claude review of Goals3556-3559 | `accept-with-boundary`; required RTNN alternating probe; advisory RT-DBSCAN/RayDB/overlay cleanups |
| Goal3561 | Targeted near-parity rows probe | Barnes-Hut `0.997836x`, LibRTS `0.993581x`, robot collision `1.001180x`, RayJoin `1.044129x` |
| Goal3562 | RTNN 5-trial same-scalar probe | RTNN is near parity: `1.010948x`, not a stable `1.061x` headline |
| Goal3563 | RayDB 5-trial plus RT-DBSCAN/overlay advisory cleanup | RayDB count `1.002664x`; RT-DBSCAN seed probe `1.012725x`; RayDB sum identified as real next tuning target |
| Goal3564 | Generic grouped-i64 small-group sum fast path | App-agnostic native fast path for `sum`/`sum_count` with `group_capacity <= 1024` |
| Goal3565 | A5000 RayDB fast-path validation | RayDB sum repaired to `1.585627x`; count sanity `1.009085x` |
| Goal3566 | Claude review of Goals3563-3565 | `accept-with-boundary`; required stale packet refresh |
| Goal3567 | Composite v2.9 packet after RayDB fast path | 9 unchanged Goal3558 rows + 2 Goal3565 RayDB replacements; geomean `1.069163x`, median `1.009085x` |
| Goal3568 | Gemini review of Goal3567 | `accept-with-boundary`; composite method accepted with boundaries |
| Goal3570 | Claude review of Goal3569 closeout | `accept`; v2.9 internal closeout accepted |
| Goal3571 | Gemini review of Goal3569 closeout | `accept`; v2.9 internal closeout accepted |

## Final Internal Packet

The current v2.9 packet is:

`docs/reports/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_a5000/summary.json`

| Metric | Value |
| --- | ---: |
| row count | 11 |
| reused Goal3558 rows | 9 |
| Goal3565 replacement rows | 2 |
| geomean speedup | 1.069163x |
| median speedup | 1.009085x |
| min speedup | 0.987619x |
| max speedup | 1.585627x |

| Case | v2.9 speedup vs v2.3 | Closeout interpretation |
| --- | ---: | --- |
| `raydb_optix_partner_resident_sum` | 1.585627x | repaired by generic small-group grouped-i64 sum fast path |
| `contact_manifold_optix_aabb_broadphase_collect_k` | 1.219528x | positive packet row |
| `rtnn_optix_prepared_3d_ranked_summary` | 1.061225x in packet; 1.010948x targeted | treat as near parity-positive, not a stable headline |
| `triangle_counting_optix_rt_graph_2a1_partner` | 1.029580x | positive packet row |
| `hausdorff_optix_threshold` | 1.019555x | positive packet row |
| `raydb_optix_partner_resident_count` | 1.009085x | repaired to near parity-positive in Goal3565 targeted probe |
| `rt_dbscan_optix_grouped_stream` | 0.997206x in packet; 1.012725x seed probe | treat as near parity, no v2.9 code change |
| `barnes_hut_optix_node_coverage` | 0.993822x in packet; 0.997836x targeted | near parity, watch list only |
| `librts_optix_aabb_index` | 0.991776x in packet; 0.993581x targeted | smallest targeted residual, too small for v2.9 code change |
| `spatial_rayjoin_optix_prepared_full_route` | 0.988978x in packet; 1.044129x targeted | packet negative de-escalated by targeted probe |
| `robot_collision_optix_prepared_device_buffers` | 0.987619x in packet; 1.001180x targeted | packet negative de-escalated by targeted probe |

## Decision

v2.9 is closed as an internal performance version.

The reason is narrow and evidence-based:

- The only clear post-review weak row, RayDB `sum`, was repaired by a generic
  native fast path.
- RayDB `count` moved to near parity-positive under the same targeted evidence.
- The remaining packet negatives are all near-parity rows with targeted probes
  showing no strong source-change mandate.
- Claude and Gemini both accepted the late evidence chain with boundaries.
- Claude and Gemini both accepted this closeout report directly.

This closeout does not mean all future performance work is finished. It means
v2.9 has reached a consistent internal packet and should stop chasing sub-1%
or run-variance rows in this version.

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

## Next Version

Start the next performance version from larger architectural targets, not
minor v2.9 near-parity cleanup:

- stronger grouped-reduction and row-stream primitives for app continuations;
- repeated-packet robustness for rows near the parity threshold;
- larger-scale benchmark rows where v2.9 improvements should matter more;
- clearer separation between primitive-driven wins and partner-continuation wins.

Those belong in the next version lane rather than further v2.9 patching.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3570_3571_external_reviews_goal3569_v29_closeout_test tests.goal3569_v2_9_internal_performance_closeout_test tests.goal3568_gemini_review_goal3567_v29_composite_packet_test tests.goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_test tests.goal3566_claude_review_goal3563_3565_v29_raydb_sum_fastpath_test
```
