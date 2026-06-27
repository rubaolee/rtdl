# V2.14 vs Current V3 Same RT Hardware Paired Benchmark

Status: serious paired evidence, not release authorization.

Artifact: `/root/rtdl_v3_rebuild_20260620/artifacts/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120`

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB

## Suite Status

| Suite | Rows | Passed/OK | Failed | all_pass |
| --- | ---: | ---: | ---: | --- |
| `v2_14_goal2626_standard` | 22 | 20 | 2 |  |
| `v3_current_goal2626_standard` | 22 | 22 | 0 |  |
| `v2_14_goal2636_standard` | 28 | 26 | 2 |  |
| `v3_current_goal2636_standard` | 28 | 28 | 0 |  |
| `v2_14_goal3828_full` | 10 | 9 | 1 | False |
| `v3_current_goal3828_full` | 10 | 10 | 0 | True |

## Same-Metric Timing Result

Compared rows with numeric `primary_metric_sec`: 46
V3 faster by >5%: 10
Within +/-5%: 32
V3 slower by >5%: 4
Geomean V3 speedup vs V2.14 across compared rows: 1.012x

| App | Geomean V3 speedup vs V2.14 |
| --- | ---: |
| `barnes_hut` | 0.917x |
| `contact_manifold` | 0.996x |
| `hausdorff_xhd` | 1.062x |
| `librts_spatial_index` | 1.163x |
| `raydb_style` | 1.017x |
| `robot_collision` | 1.016x |
| `rt_dbscan` | 0.992x |
| `rtnn` | 1.019x |
| `spatial_rayjoin` | 1.000x |
| `triangle_counting` | 0.984x |

## Fastest V3 Rows

| Suite | App | Case | Backend | V2 sec | V3 sec | V3/V2 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_optix_promoted_overlay_seed_tiled_x512` | `optix` | 8.03843e-05 | 6.16089e-05 | 1.305x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_16384` | `optix` | 0.292265 | 0.241796 | 1.209x |
| `goal2626_standard` | `librts_spatial_index` | `librts_embree_aabb_index` | `embree` | 0.0136378 | 0.0113064 | 1.206x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_16384` | `embree` | 0.572254 | 0.474909 | 1.205x |
| `goal2636_standard` | `rtnn` | `rtnn_embree_clustered_65536_ranked_summary` | `embree` | 0.724214 | 0.605986 | 1.195x |
| `goal2626_standard` | `raydb_style` | `raydb_optix_partner_resident_sum` | `optix` | 0.000764076 | 0.000661816 | 1.155x |
| `goal2626_standard` | `librts_spatial_index` | `librts_optix_aabb_index` | `optix` | 0.199243 | 0.177699 | 1.121x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_optix_threshold_copies_4096` | `optix` | 0.0413196 | 0.0390443 | 1.058x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_embree_threshold_copies_65536` | `embree` | 2.60026 | 2.47127 | 1.052x |
| `goal2636_standard` | `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_32768` | `optix` | 3.13881 | 2.98451 | 1.052x |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_optix_promoted_lsi_tiled_x512` | `optix` | 0.000132933 | 0.000127807 | 1.040x |
| `goal2626_standard` | `hausdorff_xhd` | `hausdorff_optix_threshold` | `optix` | 0.0404937 | 0.0391708 | 1.034x |

## Slowest V3 Rows

| Suite | App | Case | Backend | V2 sec | V3 sec | V3/V2 |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `goal2636_standard` | `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_32768` | `optix` | 0.0434271 | 0.0679492 | 0.639x |
| `goal2626_standard` | `spatial_rayjoin` | `spatial_rayjoin_embree_generic` | `embree` | 0.0292882 | 0.0342377 | 0.855x |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_embree_lsi_tiled_x512` | `embree` | 0.0381491 | 0.0416118 | 0.917x |
| `goal2636_standard` | `spatial_rayjoin` | `rayjoin_embree_pip_tiled_x512` | `embree` | 0.0392522 | 0.0416808 | 0.942x |
| `goal2636_standard` | `barnes_hut` | `barnes_hut_embree_node_coverage_bodies_32768` | `embree` | 0.130133 | 0.136848 | 0.951x |
| `goal2636_standard` | `barnes_hut` | `barnes_hut_embree_node_coverage_bodies_8192` | `embree` | 0.0285224 | 0.029919 | 0.953x |
| `goal2626_standard` | `raydb_style` | `raydb_optix_partner_resident_count` | `optix` | 0.000633989 | 0.00065995 | 0.961x |
| `goal2626_standard` | `raydb_style` | `raydb_embree_count` | `embree` | 0.237497 | 0.247182 | 0.961x |
| `goal2636_standard` | `rtnn` | `rtnn_optix_clustered_65536_ranked_summary` | `optix` | 0.167981 | 0.173157 | 0.970x |
| `goal2636_standard` | `triangle_counting` | `triangle_counting_embree_rt_graph_2a1_cliques_20000` | `embree` | 0.137845 | 0.14069 | 0.980x |
| `goal2626_standard` | `triangle_counting` | `triangle_counting_embree_rt_graph_2a1` | `embree` | 0.0240627 | 0.0245235 | 0.981x |
| `goal2626_standard` | `rt_dbscan` | `rt_dbscan_optix_grouped_stream` | `optix` | 0.0137046 | 0.0139415 | 0.983x |

## Runability Difference

`goal3828_full` is the clearest V3 improvement in this run: V2.14 returned rc=1 while current V3 returned rc=0.

V2.14 failed rows:

- `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` (`spatial_rayjoin`), status `fail`, returncode `1`

Current V3 failed rows:

- none

## Claim Boundary

This evidence does not authorize a broad public claim that V3 is faster than V2.x. It supports a narrower claim: current V3 is more runnable on the full scale-profile gate and has row-specific same-metric wins, but same-row timing is mixed.

`release_authorized: false`
`broad_v3_faster_than_v2_claim_authorized: false`
