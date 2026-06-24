# Phoenix V3 M8 Remaining Blocker Queue

Status: `m8_remaining_blocker_queue_not_release_not_pod`

This is a planning queue, not a release scorecard update.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_pod_spend_authorized: false
focused_pod_spend_authorized: false
```

## Planning Projection

- Frozen all-row geomean: `1.011779x`
- Planning all-row geomean after covered fixes: `1.048703x`
- Planning Set-A geomean after covered fixes: `1.039066x`
- Planning Set-B geomean after covered fixes: `1.090163x`
- Planning Set-A app wins over 1.05x: `1 / 5`

## Covered Pending Full-Suite Validation

| row | frozen | planning | source |
| --- | ---: | ---: | --- |
| `goal2626_large|barnes_hut|node_coverage_prepared_threshold_decision|embree|barnes_hut_embree_node_coverage` | 1.016x | 1.032x | `barnes_hut_m7_focused_generic_symbol_cache` |
| `goal2626_large|barnes_hut|node_coverage_prepared_threshold_decision|optix|barnes_hut_optix_node_coverage` | 0.622x | 0.999x | `barnes_hut_m7_focused_generic_symbol_cache` |
| `goal2626_large|librts_spatial_index|aabb_index_all_count_only|embree|librts_embree_aabb_index` | 0.869x | 1.923x | `librts_repeat9_focused_generic_count_cache` |
| `goal2636_stress|barnes_hut|barnes_hut_node_coverage_bodies_131072|embree|barnes_hut_embree_node_coverage_bodies_131072` | 1.007x | 1.006x | `barnes_hut_m7_focused_generic_symbol_cache` |
| `goal2636_stress|barnes_hut|barnes_hut_node_coverage_bodies_131072|optix|barnes_hut_optix_node_coverage_bodies_131072` | 0.961x | 0.990x | `barnes_hut_m7_focused_generic_symbol_cache` |
| `goal2636_stress|barnes_hut|barnes_hut_node_coverage_bodies_32768|embree|barnes_hut_embree_node_coverage_bodies_32768` | 1.002x | 0.990x | `barnes_hut_m7_focused_generic_symbol_cache` |
| `goal2636_stress|barnes_hut|barnes_hut_node_coverage_bodies_32768|optix|barnes_hut_optix_node_coverage_bodies_32768` | 0.591x | 1.038x | `barnes_hut_m7_focused_generic_symbol_cache` |

## Active Row Losses

| row | speedup | next target |
| --- | ---: | --- |
| `goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048` | 0.888x | yes |
| `goal2636_stress|rtnn|rtnn_clustered_262144_ranked_summary|embree|rtnn_embree_clustered_262144_ranked_summary` | 0.946x |  |
| `goal2626_large|spatial_rayjoin|rayjoin_all_backend_query_summary|embree|spatial_rayjoin_embree_generic` | 0.964x |  |
| `goal2636_stress|rtnn|rtnn_shell_262144_ranked_summary|embree|rtnn_embree_shell_262144_ranked_summary` | 0.973x |  |
| `goal2626_large|rt_dbscan|dbscan_cluster_signature|optix|rt_dbscan_optix_grouped_stream` | 0.975x |  |

## Watch Rows

| row | frozen | focused repeat9 | status |
| --- | ---: | ---: | --- |
| `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index` | 1.010x | 0.913x | `unstable_watch_not_current_primary_target` |

## Next Target

- id: `spatial_rayjoin_lsi_optix_topology_stream`
- row: `goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048`
- reason: Largest uncovered Set-A row loss after Barnes-Hut and LibRTS Embree focused fixes; architecture-bearing Spatial/RayJoin LSI/topology route.
- initial action: non-POD local intake of Spatial/RayJoin LSI OptiX route mechanics and existing topology-stream evidence
- pod authorized now: `false`

## Goal-Level Decision Audit

Decision: Choose Spatial/RayJoin LSI OptiX as the next non-POD investigation target after M7.

1. Was I foolish? No for this decision.
2. If yes, what actions made it foolish? It would be foolish to keep burning effort on Barnes-Hut or LibRTS Embree after focused generic fixes already cover them for planning, or to run all-app POD before the remaining blockers move.
3. Was there another path? Attack RTNN clustered Embree first. That is plausible, but RTNN symbol-cache work already measured no material gain, while Spatial/RayJoin has the larger uncovered row loss.
4. Can I now try a different path that actually solves the problem? Do a local Spatial/RayJoin LSI OptiX mechanics intake and seek review before any implementation or POD spend.
