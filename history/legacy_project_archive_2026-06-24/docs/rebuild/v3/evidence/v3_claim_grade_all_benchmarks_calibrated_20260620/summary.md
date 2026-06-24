# V3 Claim-Grade All-Benchmark OptiX vs Embree Run

Status: serious V3 evidence candidate, not release authorization.

This artifact is the V3 rebuild answer to: can every promoted benchmark app
be evaluated with a non-toy OptiX-vs-Embree route that a user can inspect?

Rules for this run:

- all ten promoted benchmark apps are included;
- tiny sanity fixtures are excluded from headline speedup rows;
- every row records the exact command and raw JSON payload;
- `public_speedup_claim_authorized` stays false until external review;
- negative and mixed rows remain visible.
- scales are calibrated per app so one CPU-heavy baseline cannot block the all-app suite.

- Generated: `2026-06-20T12:17:58+0000`
- Artifact directory: `/root/rtdl_v3_rebuild_20260620/artifacts/v3_claim_grade_all_benchmarks_calibrated_20260620`
- Case repeat wrapper: `1`
- Timeout seconds: `1800`

## App Coverage

| App | Case count | Contract | Boundary |
| --- | ---: | --- | --- |
| `hausdorff_xhd` | 8 | same prepared fixed-radius threshold decision | Decision subproblem only; not full exact Hausdorff witness materialization. |
| `spatial_rayjoin` | 6 | authored non-tiny tiled PIP/LSI/overlay scalar-count routes | Derived tiled rows only; not full RayJoin paper reproduction or polygon overlay materialization. |
| `rt_dbscan` | 2 | cluster signature on clustered 3-D fixed-radius workload | Cluster-signature route, not a full paper reproduction claim. |
| `robot_collision` | 2 | prepared collision-flag query over scaled poses and obstacles | Collision flags only; not a full robot-planning system benchmark. |
| `raydb_style` | 4 | grouped count/sum query over repeated records | Partner-resident query route; requires Torch CUDA gate. |
| `barnes_hut` | 4 | node-coverage threshold decision | Node-coverage subproblem only; not full force aggregation. |
| `librts_spatial_index` | 2 | generic prepared AABB index count-only route | Generic RTDL AABB-index route, not LibRTS authors-code or paper-equivalent dataset timing. |
| `rtnn` | 6 | 3-D ranked nearest-neighbor summary | Distribution-sensitive; uniform rows may not favor OptiX. |
| `triangle_counting` | 4 | RT-Graph 2A1 triangle-summary backend-query subpath | Synthetic K4/clique ladder; not a full graph-database or paper-dataset reproduction. |
| `contact_manifold` | 2 | generic 2-D AABB broadphase collect-k | Broadphase collect-k only; not a full physics/contact solver. |

## Ratios

| App | Row group | Embree sec | OptiX sec | OptiX speedup vs Embree | Verdict | Metric source |
| --- | --- | ---: | ---: | ---: | --- | --- |
| barnes_hut | barnes_hut_node_coverage_bodies_131072 | 0.567762 | 0.303666 | 1.870x | row_scoped_speedup_candidate | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| barnes_hut | barnes_hut_node_coverage_bodies_32768 | 0.128889 | 0.0679021 | 1.898x | row_scoped_speedup_candidate | `{"embree": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.0300649 | 0.024347 | 1.235x | row_scoped_speedup_candidate | `{"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_16384 | 0.468228 | 0.234063 | 2.000x | row_scoped_speedup_candidate | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_262144 | 10.3906 | 5.57315 | 1.864x | row_scoped_speedup_candidate | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| hausdorff_xhd | hausdorff_threshold_copies_65536 | 2.55152 | 1.5994 | 1.595x | row_scoped_speedup_candidate | `{"embree": "run_phases.query_fixed_radius_threshold_reached_count_sec", "optix": "run_phases.query_fixed_radius_threshold_reached_count_sec"}` |
| librts_spatial_index | aabb_index_all_count_only_large_32768 | 36.0938 | 0.0443228 | 814.339x | row_scoped_speedup_candidate | `{"embree": "run_phases.query_median_sec", "optix": "run_phases.query_median_sec"}` |
| raydb_style | raydb_grouped_count | 0.249614 | 0.000651188 | 383.321x | partner_gated_route_speedup_candidate | `{"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"}` |
| raydb_style | raydb_grouped_sum | 0.23892 | 0.000650093 | 367.516x | partner_gated_route_speedup_candidate | `{"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"}` |
| robot_collision | prepared_collision_flags | 0.011322 | 0.0021916 | 5.166x | row_scoped_speedup_candidate | `{"embree": "tail_medians.total_run_seconds", "optix": "tail_medians.total_run_seconds"}` |
| rt_dbscan | dbscan_cluster_signature | 25.9604 | 0.0174982 | 1483.603x | partner_gated_route_speedup_candidate | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_clustered_65536_ranked_summary | 0.584627 | 0.175412 | 3.333x | row_scoped_speedup_candidate | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_shell_65536_ranked_summary | 0.124816 | 0.10563 | 1.182x | row_scoped_speedup_candidate | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| rtnn | rtnn_uniform_65536_ranked_summary | 0.11501 | 0.106142 | 1.084x | row_scoped_speedup_candidate | `{"embree": "elapsed_sec", "optix": "elapsed_sec"}` |
| spatial_rayjoin | rayjoin_lsi_authored_tiled_x2048 | 0.0458621 | 8.87439e-05 | 516.792x | qualified_hot_route_not_whole_app_claim | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_overlay_seed_authored_tiled_x2048 | 5.11213 | 0.000167668 | 30489.613x | qualified_hot_route_not_whole_app_claim | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| spatial_rayjoin | rayjoin_pip_authored_tiled_x2048 | 0.0557547 | 0.00520915 | 10.703x | qualified_hot_route_not_whole_app_claim | `{"embree": "elapsed_sec", "optix": "phases_sec.prepared_query_sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_20000 | 0.141561 | 0.00121972 | 116.060x | row_scoped_speedup_candidate | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |
| triangle_counting | triangle_count_rt_graph_2a1_cliques_80000 | 0.547887 | 0.00157787 | 347.232x | row_scoped_speedup_candidate | `{"embree": "timing_ms.query_median_ms converted-ms-to-sec", "optix": "timing_ms.query_median_ms converted-ms-to-sec"}` |

## Case Results

| App | Case | Backend | Status | Primary sec | Metric source |
| --- | --- | --- | --- | ---: | --- |
| `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_131072` | `optix` | ok | 2.82995 | `primary.elapsed_sec` |
| `hausdorff_xhd` | `hausdorff_optix_exact_grouped_seeded_pruned_points_32768` | `optix` | ok | 2.87784 | `primary.elapsed_sec` |
| `hausdorff_xhd` | `hausdorff_embree_threshold_copies_16384` | `embree` | ok | 0.468228 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `hausdorff_xhd` | `hausdorff_optix_threshold_copies_16384` | `optix` | ok | 0.234063 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `hausdorff_xhd` | `hausdorff_embree_threshold_copies_262144` | `embree` | ok | 10.3906 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `hausdorff_xhd` | `hausdorff_optix_threshold_copies_262144` | `optix` | ok | 5.57315 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `hausdorff_xhd` | `hausdorff_embree_threshold_copies_65536` | `embree` | ok | 2.55152 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `hausdorff_xhd` | `hausdorff_optix_threshold_copies_65536` | `optix` | ok | 1.5994 | `run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `spatial_rayjoin` | `rayjoin_embree_lsi_tiled_x2048` | `embree` | ok | 0.0458621 | `elapsed_sec` |
| `spatial_rayjoin` | `rayjoin_optix_promoted_lsi_tiled_x2048` | `optix` | ok | 8.87439e-05 | `phases_sec.prepared_query_sec` |
| `spatial_rayjoin` | `rayjoin_embree_overlay_seed_tiled_x2048` | `embree` | ok | 5.11213 | `elapsed_sec` |
| `spatial_rayjoin` | `rayjoin_optix_promoted_overlay_seed_tiled_x2048` | `optix` | ok | 0.000167668 | `phases_sec.prepared_query_sec` |
| `spatial_rayjoin` | `rayjoin_embree_pip_tiled_x2048` | `embree` | ok | 0.0557547 | `elapsed_sec` |
| `spatial_rayjoin` | `rayjoin_optix_promoted_pip_tiled_x2048` | `optix` | ok | 0.00520915 | `phases_sec.prepared_query_sec` |
| `rt_dbscan` | `rt_dbscan_embree_fixed_radius_rows` | `embree` | ok | 25.9604 | `elapsed_sec` |
| `rt_dbscan` | `rt_dbscan_optix_grouped_stream` | `optix` | ok | 0.0174982 | `elapsed_sec` |
| `robot_collision` | `robot_collision_embree_prepared_buffers` | `embree` | ok | 0.011322 | `tail_medians.total_run_seconds` |
| `robot_collision` | `robot_collision_optix_prepared_device_buffers` | `optix` | ok | 0.0021916 | `tail_medians.total_run_seconds` |
| `raydb_style` | `raydb_embree_count` | `embree` | ok | 0.249614 | `metadata.timings.query_sec` |
| `raydb_style` | `raydb_optix_partner_resident_count` | `optix` | ok | 0.000651188 | `metadata.timings.query_median_sec` |
| `raydb_style` | `raydb_embree_sum` | `embree` | ok | 0.23892 | `metadata.timings.query_sec` |
| `raydb_style` | `raydb_optix_partner_resident_sum` | `optix` | ok | 0.000650093 | `metadata.timings.query_median_sec` |
| `barnes_hut` | `barnes_hut_embree_node_coverage_bodies_131072` | `embree` | ok | 0.567762 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_131072` | `optix` | ok | 0.303666 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `barnes_hut` | `barnes_hut_embree_node_coverage_bodies_32768` | `embree` | ok | 0.128889 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `barnes_hut` | `barnes_hut_optix_node_coverage_bodies_32768` | `optix` | ok | 0.0679021 | `node_coverage.run_phases.query_fixed_radius_threshold_reached_count_sec` |
| `librts_spatial_index` | `librts_embree_aabb_index_large_32768` | `embree` | ok | 36.0938 | `run_phases.query_median_sec` |
| `librts_spatial_index` | `librts_optix_aabb_index_large_32768` | `optix` | ok | 0.0443228 | `run_phases.query_median_sec` |
| `rtnn` | `rtnn_embree_clustered_65536_ranked_summary` | `embree` | ok | 0.584627 | `elapsed_sec` |
| `rtnn` | `rtnn_optix_clustered_65536_ranked_summary` | `optix` | ok | 0.175412 | `elapsed_sec` |
| `rtnn` | `rtnn_embree_shell_65536_ranked_summary` | `embree` | ok | 0.124816 | `elapsed_sec` |
| `rtnn` | `rtnn_optix_shell_65536_ranked_summary` | `optix` | ok | 0.10563 | `elapsed_sec` |
| `rtnn` | `rtnn_embree_uniform_65536_ranked_summary` | `embree` | ok | 0.11501 | `elapsed_sec` |
| `rtnn` | `rtnn_optix_uniform_65536_ranked_summary` | `optix` | ok | 0.106142 | `elapsed_sec` |
| `triangle_counting` | `triangle_counting_embree_rt_graph_2a1_cliques_20000` | `embree` | ok | 0.141561 | `timing_ms.query_median_ms converted-ms-to-sec` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_cliques_20000` | `optix` | ok | 0.00121972 | `timing_ms.query_median_ms converted-ms-to-sec` |
| `triangle_counting` | `triangle_counting_embree_rt_graph_2a1_cliques_80000` | `embree` | ok | 0.547887 | `timing_ms.query_median_ms converted-ms-to-sec` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_cliques_80000` | `optix` | ok | 0.00157787 | `timing_ms.query_median_ms converted-ms-to-sec` |
| `contact_manifold` | `contact_manifold_embree_aabb_broadphase_collect_k` | `embree` | ok | 0.0300649 | `run_phases.emit_aabb_intersection_pair_rows_2d_median_sec` |
| `contact_manifold` | `contact_manifold_optix_aabb_broadphase_collect_k` | `optix` | ok | 0.024347 | `run_phases.emit_aabb_intersection_pair_rows_2d_median_sec` |

## Failures

No failed rows in this run.

## Release Boundary

This run may support row-scoped candidate wording after review. It does not
authorize broad V3 speedup wording, paper reproduction wording, automatic
backend choice, or release publication.

