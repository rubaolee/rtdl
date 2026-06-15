# Goal4379 v2.14 Benchmark Cleanup Gap Matrix

Status: draft gate; not a release packet.

## Summary

- Validation: `accept_draft_gate`
- Promoted apps covered: `10`
- Release rows: `12`
- Fresh measurement required rows: `12`
- Public wording authorized rows now: `0`

## Rows

| Row | App | Contract | Partner policy | Primary blocker |
| --- | --- | --- | --- | --- |
| hausdorff_xhd_threshold | hausdorff_xhd | directed_threshold_prepared_fixed_radius_count | primitive-only for release row; partner baselines stay separated | fresh v2.14 same-contract measurement and phase explanation missing |
| spatial_rayjoin_lsi | spatial_rayjoin | public_cdb_lsi_count | no partner in the scalar-count comparison | fresh v2.14 measurement after Goal4376 source changes missing |
| spatial_rayjoin_pip | spatial_rayjoin | public_cdb_pip_count | no hidden partner difference; any Numba/CuPy path must be a separated row | PIP still needs fresh same-contract route choice and explanation under v2.14 wording |
| spatial_rayjoin_overlay | spatial_rayjoin | section57_overlay_lsi_vertex_pip_midpoint_pip_no_output | RTDL partner cache allowed only as an explicit cached/preprocessed application-wall protocol | author process-wall comparison must not be read as author hot-compute parity |
| rt_dbscan_core_flags_numba_signature | rt_dbscan | fixed_radius_core_flags_plus_numba_column_signature | Numba continuation fixed and named; not a pure backend-only swap | fresh current-head route and output-surface caveat required |
| robot_collision_grouped_segment_flags | robot_collision | prepared_triangle_scene_grouped_segment_any_hit_flags | primitive-only release row | must confirm whether v2.14 wording remains traversal-phase-only or can cover a wider hot loop |
| contact_manifold_aabb_collect_k | contact_manifold | generic_aabb_broadphase_contact_candidates_2d_grid16384 | primitive-only for broadphase row; exact manifold interpretation remains app logic | fresh v2.14 measurement and modest-speedup explanation required |
| raydb_style_grouped_i64_count | raydb_style | prepared_ray_triangle_grouped_i64_reduction_count | primitive-first native route; partner rows only for unfused continuations | fresh current-head measurement and primitive-first-vs-partner wording required |
| barnes_hut_node_coverage | barnes_hut | prepared_fixed_radius_node_coverage_threshold_decision | native node-coverage row separated from Numba exact-force reference | fresh v2.14 measurement and force-law boundary wording required |
| librts_spatial_index_aabb | librts_spatial_index | generic_prepared_aabb_index_query_2d_all_ops | primitive-only release row | fresh v2.14 measurement after native Embree/OptiX cleanup required |
| rtnn_ranked_summary | rtnn | prepared_3d_fixed_radius_ranked_summary_raw | primitive row only; ANN/paper and partner baselines remain separated | RTNN remains blocked for RT-core neighbor-search public wording without stronger end-to-end claim boundary |
| triangle_counting_any_hit | triangle_counting | rt_graph_2a1_generic_ray_triangle_any_hit | primitive-only release row | fresh v2.14 measurement and graph-scope boundary wording required |

## Claim Boundary

The v2.14 benchmark cleanup gap matrix is a draft planning and validation surface. It does not authorize release action, tag action, public speedup wording, whole-application speedup wording, broad RT-core wording, RTDL-beats-RayJoin wording, RayJoin paper-reproduction wording, author-hot-compute parity wording, automatic partner selection, Intel/AMD GPU performance wording, true-zero-copy wording, or app-specific native engine logic.

## Next Execution Order

1. Freeze the v2.14 app/row inventory.
2. Run fresh current-head OptiX and Embree rows for the primitive-only rows.
3. Run fixed-partner rows where the partner is part of the contract.
4. Re-run RayJoin LSI, PIP, and overlay with the author-code caveat table.
5. Fill the v2.14 public comparison and phase-explanation documents.
6. Ask external reviewers to reject any row without a phase explanation.
