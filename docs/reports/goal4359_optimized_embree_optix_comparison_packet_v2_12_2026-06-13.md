# Goal4359: Optimized Embree vs OptiX Comparison Packet

Date: 2026-06-13

Status: internal comparison packet; not public speedup authorization.

## Verdict

This packet accepts one fully optimized LibRTS prepared-query comparison row, five fresh Embree scale rows from Goal4344, and the Goal4358 RayJoin LSI/PIP same-stream scalar-count rows. Three Goal4344 rows are clean internal query-ratio candidates; Robot Collision and RayDB-style remain boundary-limited because the current OptiX rows use stronger resident/device output paths.

The remaining serious comparison blockers are contract-choice apps: RT-DBSCAN, Barnes-Hut, and RTNN. Spatial RayJoin is now split into LSI/PIP scalar-count rows with internal-only ratios.

## Measured Pair

| App | Contract | Scale | Embree CPU Query Median Sec | OptiX RT Query Median Sec | OptiX Query Median Faster | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| librts_spatial_index | `generic_prepared_aabb_index_query_2d` | 1024 boxes x 1024 queries, `operation=all`, skip-counts | 0.011698941 | 0.000622335 | 18.8x | query-median only; elapsed totals not ratio-authorized |

The same Embree row improved from the pre-Goal4340 columnar fallback query median by about 3740.9x. That is evidence for the new generic Embree AABB primitive route, not a broad CPU-vs-GPU claim.

## Scale Rows

| App | Metric | Embree | OptiX | Embree / OptiX | Faster Backend | Authorization |
| --- | --- | ---: | ---: | ---: | --- | --- |
| hausdorff_xhd | `max_directed_query_fixed_radius_threshold_reached_count_sec` (sec) | 0.009892253 | 0.003847664 | 2.57x | `optix` | `internal_query_phase_ratio_only_not_public_claim` |
| robot_collision | `traversal_phase_median_sec` (sec) | 0.000995346 | 0.000040346 | 24.67x | `optix` | `boundary_limited_traversal_phase_only_no_end_to_end_ratio` |
| contact_manifold | `native_collect_elapsed_sec` (sec) | 0.000260988 | 0.000476252 | 0.55x | `embree` | `internal_query_phase_ratio_only_not_public_claim` |
| raydb_style | `native_rt_traversal_sec` (sec) | 0.012958745 | 0.000209417 | 61.88x | `optix` | `boundary_limited_traversal_phase_only_no_end_to_end_ratio` |
| triangle_counting | `query_median_ms` (ms) | 11.54467 | 0.158831477 | 72.69x | `optix` | `internal_query_phase_ratio_only_not_public_claim` |

## RayJoin Same-Stream Rows

| Workload | Embree ms | OptiX ms | Embree / OptiX | Count | Authorization |
| --- | ---: | ---: | ---: | ---: | --- |
| lsi | 14.538773001 | 0.335959005 | 43.28x | 8921 | `internal_same_stream_scalar_count_only_not_public_claim` |
| pip | 14.167796995 | 12.033906998 | 1.18x | 8686 | `internal_same_stream_scalar_count_only_not_public_claim` |

Boundary-limited rows are useful engineering evidence, but they are not clean end-to-end backend ratios.

## App Table

| App | OptiX Registry Row | Embree Registry Row | Goal4341 Status | Evidence Or Reason | Next Action |
| --- | --- | --- | --- | --- | --- |
| hausdorff_xhd | `hausdorff_xhd_scale_default_optix_threshold` | `hausdorff_xhd_embree_cpu_directed_summary` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree prepared threshold-decision row at the same copies, threshold, repeat, and warmup as the current OptiX scale row. | use query-phase ratio internally only; keep exact-distance and public speedup wording outside this packet |
| spatial_rayjoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | `same_stream_scalar_count_pairs_available` | Goal4358 supplies RayJoin-exported same-stream LSI and PIP scalar-count pairs for RTDL OptiX and RTDL Embree. The broad current registry row remains mixed, so these ratios are scoped to split scalar-count contracts. | use the same-stream LSI/PIP scalar-count rows internally; keep overlay active-count and whole-app wording separate |
| rt_dbscan | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | `rt_dbscan_embree_cpu_prepared_rows` | `contract_split_pair_required` | Current OptiX evidence is grouped-stream plus Numba continuation at 65K points; current Embree evidence is a tiny prepared-row route. | choose either fixed-radius neighbor rows or grouped signatures, then run that same contract on both backends |
| robot_collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | `robot_collision_embree_cpu_prepared_buffers` | `same_scale_boundary_limited` | Goal4344 supplies the Embree row at the same scene/query scale as OptiX, but the OptiX scale row uses the OptiX-only device-count path while Embree returns host compact flags. | show traversal-only internal phase comparison, or run an OptiX prepared-buffer flags row before reporting a clean output-contract ratio |
| contact_manifold | `contact_manifold_optix_scale_default_grid64` | `contact_manifold_embree_cpu_native_collect_k` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree native collect-k row at the same grid size, witness capacity, repeat count, and correctness policy as OptiX. | use native collect-k median internally only; keep public claims blocked |
| raydb_style | `raydb_style_optix_count_scale_default_262k` | `raydb_style_embree_cpu_count_primitive_first` | `same_scale_boundary_limited` | Goal4344 supplies the Embree generated 262144-row / 1024-group count row, but the current OptiX scale row is prepared/resident while the Embree row is a non-resident native grouped-reduction run. | show traversal/native-call phases as boundary-limited internal evidence; add prepared Embree residency before clean end-to-end ratios |
| barnes_hut | `barnes_hut_numba_scale_default_8192` | `barnes_hut_embree_cpu_node_coverage_prepared` | `contract_split_pair_required` | Current OptiX scale evidence is a Numba exact-force partner route; current Embree evidence is a prepared node-coverage route. | choose exact-force partner continuation or prepared node coverage as the comparison contract, then run that contract on both sides |
| librts_spatial_index | `librts_spatial_index_optix_scale_default_32768` | `librts_spatial_index_embree_cpu_aabb_index` | `measured_same_contract_optimized_pair` | Goal4340 supplies a fresh same-scale AABB_INDEX_QUERY_2D prepared-query row after replacing the old Embree columnar fallback with a native Embree collision route. | scale the same prepared-query row to larger box/query counts and report scene-prepare amortization separately from query median |
| rtnn | `rtnn_prepared_optix_scale_default_65536` | `rtnn_embree_cpu_ann_candidate_quality_reference` | `contract_split_pair_required` | Current OptiX evidence is a 3-D prepared ranked-summary route; current Embree evidence is a 2-D ANN candidate-quality route. | decide between 2-D ANN candidate quality and 3-D ranked-summary, then run the chosen contract on both backends |
| triangle_counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | `triangle_counting_embree_cpu_native_summary` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree RT-Graph 2A1 row at the same fixture, copy count, detail mode, repeat, and warmup as the OptiX scale row. | use query-median ratio internally only; keep public claims blocked |

## Claim Boundary

Goal4359 extends the Goal4341 optimized/same-scale Embree-vs-OptiX packet with the Goal4358 RayJoin same-stream LSI/PIP scalar-count rows. It separates clean same-contract query-ratio rows, RayJoin same-stream scalar-count rows, boundary-limited same-scale rows, and remaining contract-split/configured routes. This packet does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.
