# Goal4359: Optimized Embree vs OptiX Comparison Packet

Date: 2026-06-13

Status: internal comparison packet; not public speedup authorization.

## Verdict

This packet accepts one fully optimized LibRTS prepared-query comparison row, five fresh Embree scale rows from Goal4344, and the Goal4358 RayJoin LSI/PIP same-stream scalar-count rows, the Goal4360 RTNN prepared ranked-summary raw-row same-contract backend pair, and the Goal4361 RT-DBSCAN same-contract RTDL+Numba configured-route pair, and the Goal4362 Barnes-Hut same-contract native node-coverage pair. Three Goal4344 rows are clean internal query-ratio candidates; Robot Collision and RayDB-style remain boundary-limited because the current OptiX rows use stronger resident/device output paths.

No promoted benchmark app remains in the contract-choice blocker bucket. Spatial RayJoin is now split into LSI/PIP scalar-count rows with internal-only ratios; RTNN has a same-contract raw-row backend ratio that still does not authorize RT-core wording; RT-DBSCAN has a same-contract configured-route ratio with the Numba continuation held fixed; Barnes-Hut has a native node-coverage ratio scoped away from force-vector and paper-reproduction wording.

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

## Same-Contract Backend Rows

| App | Contract | Embree Sec | OptiX Sec | Embree / OptiX | Correctness | RT-Core Claim | Authorization |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| rtnn | `prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows` | 0.122744617 | 0.103778298 | 1.18x | `True` | `False` | `internal_same_contract_raw_row_query_only_not_public_rt_core_claim` |
| rt_dbscan | `rt_dbscan_clustered3d_count_threshold_flags_plus_numba_prepared_grid_column_signature` | 17.313535127 | 0.315049268 | 54.96x | `True` | `True` | `internal_same_contract_configured_numba_route_only_not_public_claim` |
| barnes_hut | `prepared_fixed_radius_node_coverage_threshold_decision` | 3.948736324 | 2.037808402 | 1.94x | `True` | `True` | `internal_same_contract_native_node_coverage_only_not_public_claim` |

Boundary-limited rows are useful engineering evidence, but they are not clean end-to-end backend ratios.

## App Table

| App | OptiX Registry Row | Embree Registry Row | Goal4341 Status | Evidence Or Reason | Next Action |
| --- | --- | --- | --- | --- | --- |
| hausdorff_xhd | `hausdorff_xhd_scale_default_optix_threshold` | `hausdorff_xhd_embree_cpu_directed_summary` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree prepared threshold-decision row at the same copies, threshold, repeat, and warmup as the current OptiX scale row. | use query-phase ratio internally only; keep exact-distance and public speedup wording outside this packet |
| spatial_rayjoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | `same_stream_scalar_count_pairs_available` | Goal4358 supplies RayJoin-exported same-stream LSI and PIP scalar-count pairs for RTDL OptiX and RTDL Embree. The broad current registry row remains mixed, so these ratios are scoped to split scalar-count contracts. | use the same-stream LSI/PIP scalar-count rows internally; keep overlay active-count and whole-app wording separate |
| rt_dbscan | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | `rt_dbscan_embree_cpu_prepared_rows` | `same_contract_configured_numba_route_available` | Goal4361 supplies a same-scale/same-seed clustered3d 65,536-point configured-route pair: OptiX RT-core count-threshold flags plus Numba prepared-grid column signature versus Embree threshold-capped rows plus the same Numba continuation. | use this configured-route ratio internally only; keep public whole-app and paper-speedup wording blocked |
| robot_collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | `robot_collision_embree_cpu_prepared_buffers` | `same_scale_boundary_limited` | Goal4344 supplies the Embree row at the same scene/query scale as OptiX, but the OptiX scale row uses the OptiX-only device-count path while Embree returns host compact flags. | show traversal-only internal phase comparison, or run an OptiX prepared-buffer flags row before reporting a clean output-contract ratio |
| contact_manifold | `contact_manifold_optix_scale_default_grid64` | `contact_manifold_embree_cpu_native_collect_k` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree native collect-k row at the same grid size, witness capacity, repeat count, and correctness policy as OptiX. | use native collect-k median internally only; keep public claims blocked |
| raydb_style | `raydb_style_optix_count_scale_default_262k` | `raydb_style_embree_cpu_count_primitive_first` | `same_scale_boundary_limited` | Goal4344 supplies the Embree generated 262144-row / 1024-group count row, but the current OptiX scale row is prepared/resident while the Embree row is a non-resident native grouped-reduction run. | show traversal/native-call phases as boundary-limited internal evidence; add prepared Embree residency before clean end-to-end ratios |
| barnes_hut | `barnes_hut_numba_scale_default_8192` | `barnes_hut_embree_cpu_node_coverage_prepared` | `same_contract_native_node_coverage_available` | Goal4362 supplies a same-scale 1,000,000-body prepared node-coverage scalar-threshold pair for OptiX and Embree. The broad registry row still points at the Numba exact-force partner route, so the ratio is scoped to the native node-coverage contract. | use this native node-coverage ratio internally only; keep force-vector, paper-reproduction, whole-app, and public speedup wording blocked |
| librts_spatial_index | `librts_spatial_index_optix_scale_default_32768` | `librts_spatial_index_embree_cpu_aabb_index` | `measured_same_contract_optimized_pair` | Goal4340 supplies a fresh same-scale AABB_INDEX_QUERY_2D prepared-query row after replacing the old Embree columnar fallback with a native Embree collision route. | scale the same prepared-query row to larger box/query counts and report scene-prepare amortization separately from query median |
| rtnn | `rtnn_prepared_optix_scale_default_65536` | `rtnn_embree_cpu_ann_candidate_quality_reference` | `same_contract_raw_rows_available_not_rt_core_proof` | Goal4360 supplies a same-scale/same-seed prepared 3-D fixed-radius bounded ranked-summary raw-row pair for OptiX and Embree, with matching aggregate row signatures. | use this as an internal backend row only; keep RT-core wording blocked because the current OptiX RTNN phase is the prepared uniform-cell ranked-summary implementation |
| triangle_counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | `triangle_counting_embree_cpu_native_summary` | `internal_query_ratio_candidate_ready` | Goal4344 supplies the Embree RT-Graph 2A1 row at the same fixture, copy count, detail mode, repeat, and warmup as the OptiX scale row. | use query-median ratio internally only; keep public claims blocked |

## Claim Boundary

Goal4362 extends the Goal4361 optimized/same-scale Embree-vs-OptiX packet with the Barnes-Hut prepared node-coverage same-contract pair. It separates clean same-contract query-ratio rows, RayJoin same-stream scalar-count rows, RTNN raw-row backend rows, RT-DBSCAN configured-route rows, Barnes-Hut native node-coverage rows, and boundary-limited same-scale rows. This packet does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic.

Validation status: `accept`.
