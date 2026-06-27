# Phoenix V3 Serious V2.x Paired Benchmark

Status: `serious_paired_evidence_not_release`

This packet compares V2.14 and current Phoenix V3 on the same RT hardware
using serious all-benchmark-app suites. It does not authorize release by itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
same_metric_comparison_count: 51
V3 faster by >5%: 16
Within +/-5%: 31
V3 slower by >5%: 4
Geomean V3 speedup vs V2.14: 1.049x
release_consideration_eligible: false
```

## Preregistered Bar

```text
overall_geomean_v3_speedup_vs_v2 >= 1.20x
at least 8 of 10 app geomeans > 1.05x
no app geomean < 0.95x without accepted explanation
all required suites must finish with rc=0
```

## Suite Status

| Suite | V2.14 | Current V3 |
| --- | --- | --- |
| `goal2626_large` | `{'rows': 22, 'ok': 20, 'failed': 2}` | `{'rows': 22, 'ok': 22, 'failed': 0}` |
| `goal2636_stress` | `{'rows': 34, 'ok': 32, 'failed': 2}` | `{'rows': 34, 'ok': 33, 'failed': 1}` |
| `goal3828_full` | `{'rows': 10, 'pass': 10, 'failed': 0, 'all_pass': True, 'json_pass_count': 10}` | `{'rows': 10, 'pass': 10, 'failed': 0, 'all_pass': True, 'json_pass_count': 10}` |

## App Geomean

| App | V3 speedup vs V2.14 |
| --- | ---: |
| `barnes_hut` | 0.831x |
| `contact_manifold` | 1.421x |
| `hausdorff_xhd` | 1.134x |
| `librts_spatial_index` | 1.827x |
| `raydb_style` | 0.986x |
| `robot_collision` | 1.027x |
| `rt_dbscan` | 1.002x |
| `rtnn` | 1.003x |
| `spatial_rayjoin` | 1.068x |
| `triangle_counting` | 0.987x |

## App Coverage

```text
expected_promoted_app_count: 10
actual_promoted_app_count: 10
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
```

## Strongest V3 Wins

| Suite | App | Case | Backend | Speedup |
| --- | --- | --- | --- | ---: |
| `goal2626_large` | `librts_spatial_index` | `librts_embree_aabb_index` | `embree` | 4.156x |
| `goal2626_large` | `contact_manifold` | `contact_manifold_optix_aabb_broadphase_collect_k` | `optix` | 1.776x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_131072` | `optix` | 1.299x |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_embree_pip_tiled_x2048` | `embree` | 1.265x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_32768` | `optix` | 1.221x |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_optix_threshold` | `optix` | 1.209x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_16384` | `embree` | 1.190x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_16384` | `optix` | 1.187x |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_embree_threshold` | `embree` | 1.146x |
| `goal2626_large` | `contact_manifold` | `contact_manifold_embree_aabb_broadphase_collect_k` | `embree` | 1.137x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_262144` | `optix` | 1.117x |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_optix_promoted_lsi_tiled_x2048` | `optix` | 1.102x |

## Strongest V3 Losses

| Suite | App | Case | Backend | Speedup |
| --- | --- | --- | --- | ---: |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_32768` | `optix` | 0.577x |
| `goal2626_large` | `barnes_hut` | `barnes_hut_optix_node_coverage` | `optix` | 0.598x |
| `goal2626_large` | `librts_spatial_index` | `librts_optix_aabb_index` | `optix` | 0.803x |
| `goal2626_large` | `raydb_style` | `raydb_embree_sum` | `embree` | 0.922x |
| `goal2626_large` | `raydb_style` | `raydb_optix_partner_resident_count` | `optix` | 0.956x |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_embree_node_coverage_bodies_131072` | `embree` | 0.967x |
| `goal2636_stress` | `rtnn` | `rtnn_embree_shell_262144_ranked_summary` | `embree` | 0.968x |
| `goal2636_stress` | `triangle_counting` | `triangle_counting_embree_rt_graph_2a1_cliques_20000` | `embree` | 0.971x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_65536` | `embree` | 0.976x |
| `goal2626_large` | `barnes_hut` | `barnes_hut_embree_node_coverage` | `embree` | 0.981x |
| `goal2626_large` | `spatial_rayjoin` | `spatial_rayjoin_embree_generic` | `embree` | 0.981x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_65536` | `optix` | 0.983x |

## OptiX vs Embree Explanation Rows

| Suite | App | Group | V2.14 OptiX/Embree | V3 OptiX/Embree | Change | Interpretation |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `goal2626_large` | `barnes_hut` | `node_coverage_prepared_threshold_decision` | 3.069x | 1.871x | 0.610x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2626_large` | `contact_manifold` | `generic_aabb_broadphase_collect_k` | 1.373x | 2.146x | 1.562x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_threshold_decision` | 1.920x | 2.027x | 1.055x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2626_large` | `librts_spatial_index` | `aabb_index_all_count_only` | 0.398x | 0.077x | 0.193x | OptiX slower than Embree in both V2.14 and V3; investigate workload/route fit before blaming the V3 delta. |
| `goal2626_large` | `raydb_style` | `raydb_grouped_count` | 401.680x | 357.576x | 0.890x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2626_large` | `raydb_style` | `raydb_grouped_sum` | 381.044x | 412.316x | 1.082x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2626_large` | `robot_collision` | `prepared_collision_flags` | 7.997x | 8.091x | 1.012x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `rt_dbscan` | `dbscan_cluster_signature` | 2938.995x | 2934.284x | 0.998x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `rtnn` | `prepared_3d_ranked_summary` | 1.123x | 1.100x | 0.980x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_node_coverage_bodies_131072` | 1.874x | 1.952x | 1.041x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_node_coverage_bodies_32768` | 3.215x | 1.855x | 0.577x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_16384` | 2.039x | 2.033x | 0.997x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_262144` | 1.721x | 1.818x | 1.056x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_65536` | 1.570x | 1.581x | 1.007x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_clustered_262144_ranked_summary` | 9.512x | 9.517x | 1.001x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_clustered_65536_ranked_summary` | 4.320x | 4.102x | 0.950x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2636_stress` | `rtnn` | `rtnn_shell_262144_ranked_summary` | 2.896x | 2.986x | 1.031x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_shell_65536_ranked_summary` | 1.169x | 1.180x | 1.009x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_uniform_262144_ranked_summary` | 1.102x | 1.096x | 0.995x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_uniform_65536_ranked_summary` | 1.100x | 1.100x | 1.000x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_lsi_authored_tiled_x2048` | 411.114x | 418.998x | 1.019x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_pip_authored_tiled_x2048` | 12.249x | 9.679x | 0.790x | OptiX remains faster than Embree but lost relative margin in V3. |

## Boundary

This is serious evidence, not a release claim. If the geomean and app-level
results do not show broad material V3 superiority, Phoenix V3 remains
`redo_required` and the losing rows define the next generic runtime work.
