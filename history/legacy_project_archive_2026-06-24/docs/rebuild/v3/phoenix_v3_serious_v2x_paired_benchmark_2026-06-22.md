# Phoenix V3 Serious V2.x Paired Benchmark

Status: `serious_paired_evidence_not_release`

This packet compares V2.14 and current Phoenix V3 on the same RT hardware
using serious all-benchmark-app suites. It does not authorize release by itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
same_metric_comparison_count: 52
V3 faster by >5%: 12
Within +/-5%: 35
V3 slower by >5%: 5
Geomean V3 speedup vs V2.14: 1.012x
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
| `goal2636_stress` | `{'rows': 34, 'ok': 32, 'failed': 2}` | `{'rows': 34, 'ok': 34, 'failed': 0}` |
| `goal3828_full` | `{'rows': 0, 'ok': 0, 'failed': 0, 'missing': True}` | `{'rows': 10, 'pass': 10, 'failed': 0, 'all_pass': True, 'json_pass_count': 10}` |

## App Geomean

| App | V3 speedup vs V2.14 |
| --- | ---: |
| `barnes_hut` | 0.844x |
| `contact_manifold` | 1.017x |
| `hausdorff_xhd` | 1.149x |
| `librts_spatial_index` | 0.937x |
| `raydb_style` | 1.046x |
| `robot_collision` | 0.993x |
| `rt_dbscan` | 0.988x |
| `rtnn` | 1.003x |
| `spatial_rayjoin` | 1.027x |
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
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_embree_pip_tiled_x2048` | `embree` | 1.336x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_32768` | `optix` | 1.278x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_16384` | `embree` | 1.242x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_16384` | `optix` | 1.238x |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_embree_threshold` | `embree` | 1.220x |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_optix_threshold` | `optix` | 1.197x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_131072` | `optix` | 1.191x |
| `goal2636_stress` | `rtnn` | `rtnn_embree_clustered_65536_ranked_summary` | `embree` | 1.149x |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_262144` | `optix` | 1.123x |
| `goal2626_large` | `raydb_style` | `raydb_embree_count` | `embree` | 1.079x |
| `goal2626_large` | `raydb_style` | `raydb_embree_sum` | `embree` | 1.066x |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_optix_promoted_pip_tiled_x2048` | `optix` | 1.059x |

## Strongest V3 Losses

| Suite | App | Case | Backend | Speedup |
| --- | --- | --- | --- | ---: |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_32768` | `optix` | 0.591x |
| `goal2626_large` | `barnes_hut` | `barnes_hut_optix_node_coverage` | `optix` | 0.622x |
| `goal2626_large` | `librts_spatial_index` | `librts_embree_aabb_index` | `embree` | 0.869x |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_optix_promoted_lsi_tiled_x2048` | `optix` | 0.888x |
| `goal2636_stress` | `rtnn` | `rtnn_embree_clustered_262144_ranked_summary` | `embree` | 0.946x |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_131072` | `optix` | 0.961x |
| `goal2626_large` | `spatial_rayjoin` | `spatial_rayjoin_embree_generic` | `embree` | 0.964x |
| `goal2636_stress` | `rtnn` | `rtnn_embree_shell_262144_ranked_summary` | `embree` | 0.973x |
| `goal2626_large` | `rt_dbscan` | `rt_dbscan_optix_grouped_stream` | `optix` | 0.975x |
| `goal2636_stress` | `rtnn` | `rtnn_embree_shell_65536_ranked_summary` | `embree` | 0.981x |
| `goal2626_large` | `triangle_counting` | `triangle_counting_embree_rt_graph_2a1` | `embree` | 0.985x |
| `goal2626_large` | `contact_manifold` | `contact_manifold_optix_aabb_broadphase_collect_k` | `optix` | 0.985x |

## OptiX vs Embree Explanation Rows

| Suite | App | Group | V2.14 OptiX/Embree | V3 OptiX/Embree | Change | Interpretation |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `goal2626_large` | `barnes_hut` | `node_coverage_prepared_threshold_decision` | 3.167x | 1.938x | 0.612x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2626_large` | `contact_manifold` | `generic_aabb_broadphase_collect_k` | 1.458x | 1.368x | 0.939x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2626_large` | `hausdorff_xhd` | `hausdorff_threshold_decision` | 2.062x | 2.023x | 0.981x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `librts_spatial_index` | `aabb_index_all_count_only` | 0.110x | 0.128x | 1.162x | OptiX slower than Embree in both V2.14 and V3; investigate workload/route fit before blaming the V3 delta. |
| `goal2626_large` | `raydb_style` | `raydb_grouped_count` | 407.804x | 375.921x | 0.922x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2626_large` | `raydb_style` | `raydb_grouped_sum` | 369.364x | 362.085x | 0.980x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `robot_collision` | `prepared_collision_flags` | 8.482x | 8.526x | 1.005x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `rt_dbscan` | `dbscan_cluster_signature` | 2985.451x | 2907.313x | 0.974x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2626_large` | `rtnn` | `prepared_3d_ranked_summary` | 1.097x | 1.090x | 0.994x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_node_coverage_bodies_131072` | 1.910x | 1.824x | 0.955x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `barnes_hut` | `barnes_hut_node_coverage_bodies_32768` | 3.001x | 1.770x | 0.590x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_16384` | 2.013x | 2.006x | 0.997x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_262144` | 1.647x | 1.848x | 1.122x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2636_stress` | `hausdorff_xhd` | `hausdorff_threshold_copies_65536` | 1.645x | 1.674x | 1.018x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_clustered_262144_ranked_summary` | 8.582x | 9.054x | 1.055x | OptiX remains faster than Embree and improved its relative margin in V3. |
| `goal2636_stress` | `rtnn` | `rtnn_clustered_65536_ranked_summary` | 3.997x | 3.550x | 0.888x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2636_stress` | `rtnn` | `rtnn_shell_262144_ranked_summary` | 2.893x | 2.953x | 1.021x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_shell_65536_ranked_summary` | 1.144x | 1.156x | 1.011x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_uniform_262144_ranked_summary` | 1.105x | 1.075x | 0.973x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `rtnn` | `rtnn_uniform_65536_ranked_summary` | 1.099x | 1.092x | 0.994x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_lsi_authored_tiled_x2048` | 434.956x | 387.483x | 0.891x | OptiX remains faster than Embree but lost relative margin in V3. |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_overlay_seed_authored_tiled_x2048` | 32685.713x | 32471.428x | 0.993x | OptiX-vs-Embree relative margin is broadly unchanged. |
| `goal2636_stress` | `spatial_rayjoin` | `rayjoin_pip_authored_tiled_x2048` | 11.168x | 8.853x | 0.793x | OptiX remains faster than Embree but lost relative margin in V3. |

## Boundary

This is serious evidence, not a release claim. If the geomean and app-level
results do not show broad material V3 superiority, Phoenix V3 remains
`redo_required` and the losing rows define the next generic runtime work.
