# Goal4349: Human-Scale RT Core vs Embree CPU Comparison

Date: 2026-06-12

This packet reports hot prepared-query aggregates, not process wrapper time. Rows use the same repeat count when that can put both sides in the 1-10s band; otherwise they use duration-bounded throughput with identical work per iteration.

| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| barnes_hut | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.5052s | 3.9999s | 150/150 | 2.76x | 8 | `prepared_fixed_radius_node_coverage_threshold_decision` |
| contact_manifold | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 2.5342s | 3.1909s | 20/20 | 1.27x | 8 | `generic_aabb_broadphase_contact_candidates_2d_grid16384` |
| hausdorff_xhd | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.8315s | 4.5526s | 200/200 | 2.49x | 8 | `directed_threshold_prepared_fixed_radius_count` |
| librts_spatial_index | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.8225s | 2.2736s | 4800/48 | 69.32x | 64 | `generic_prepared_aabb_index_query_2d_all_ops` |
| raydb_style | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 3.0905s | 1.7445s | 5000/240 | 11.38x | 64 | `prepared_ray_triangle_grouped_i64_reduction_count` |
| robot_collision | `clean_backend_swap_traversal_phase_only` | `duration_bounded_throughput` | 6.4055s | 3.0502s | 49900/2450 | 9.87x | 8 | `prepared_triangle_scene_grouped_segment_any_hit_flags` |
| rt_dbscan | `mostly_clean_numba_continuation_same_native_handoff_differs` | `same_repeat_human_scale` | 1.2443s | 9.423s | 90/90 | 9.00x | 64 | `fixed_radius_core_flags_plus_numba_column_signature` |
| rtnn | `mixed_native_summary_vs_embree_row_materialization` | `duration_bounded_throughput` | 3.0224s | 3.3809s | 1500/9 | 201.31x | 64 | `prepared_3d_fixed_radius_ranked_summary_raw` |
| spatial_rayjoin_lsi | `mostly_clean_scalar_count_contract_native_output_form_differs` | `duration_bounded_throughput` | 4.1127s | 2.3012s | 5000/5 | 640.93x | 64 | `public_cdb_lsi_count` |
| spatial_rayjoin_pip | `mostly_clean_scalar_count_contract_native_output_form_differs` | `same_repeat_human_scale` | 1.18s | 6.6305s | 1500/1500 | 5.57x | 8 | `public_cdb_pip_count` |
| triangle_counting | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 3.1271s | 3.5776s | 20000/500 | 42.16x | 8 | `rt_graph_2a1_generic_ray_triangle_any_hit` |

## Row Reasonability Review

| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |
| --- | --- | --- | --- | --- |
| barnes_hut | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 22.79 ms divided by OptiX median 8.27 ms gives 2.76x. The row is traversal-heavy, emits only a threshold decision, and keeps the prepared node-coverage contract fixed. | Safe as a prepared RT traversal comparison. |
| contact_manifold | `reasonable` | `yes_for_prepared_broadphase` | Embree median 157.46 ms divided by OptiX median 124.28 ms gives 1.27x. The modest gain matches the row-output-heavy AABB broadphase: both sides emit the same 16,384 candidate rows and then share the exact refinement. | Safe, but word as a modest broadphase gain, not a dramatic whole-app claim. |
| hausdorff_xhd | `reasonable` | `yes_for_prepared_hot_phase` | Embree combined per-iteration threshold work 22.76 ms divided by OptiX 9.16 ms gives 2.49x. Two directed fixed-radius threshold queries use the same prepared contract. | Safe as a prepared threshold-query traversal comparison. |
| librts_spatial_index | `reasonable` | `yes_for_prepared_aabb_index_ops` | Embree all-ops median 39.00 ms divided by OptiX median 0.563 ms gives 69.32x. Counts match for point_contains, range_contains, and range_intersects over the same prepared AABB workload. | Safe for the prepared AABB-index all-ops contract. |
| raydb_style | `reasonable` | `yes_for_prepared_grouped_reduction` | Embree native grouped-reduction median 6.60 ms divided by OptiX median 0.580 ms gives 11.38x. Both sides now use the prepared grouped i64 reduction surface over the same generated rows/groups. | Safe as a prepared grouped-reduction comparison. |
| robot_collision | `reasonable` | `qualified_traversal_phase_only` | Embree traversal median 1.195 ms divided by OptiX traversal median 0.121 ms gives 9.87x. The full hot run is smaller because tail/output work dominates outside the traversal phase. | Use only as traversal-phase speedup, not as whole hot-loop speedup. |
| rt_dbscan | `reasonable` | `qualified_native_handoff_differs` | Embree median 102.91 ms divided by OptiX median 11.43 ms gives 9.00x. The native threshold/core-flag portion has a matching 9.47x ratio, while the Numba continuation is nearly equal across backends. | Use as RT threshold plus shared Numba continuation; disclose the handoff difference. |
| rtnn | `reasonable_but_not_pure_backend_swap` | `no_output_surface_differs` | Embree median 376.46 ms divided by OptiX median 1.87 ms gives 201.31x. The magnitude is explained by OptiX producing a native ranked summary while Embree materializes neighbor rows before building the summary. | Do not word as only RT cores versus CPU cores until Embree has the same native summary surface. |
| spatial_rayjoin_lsi | `reasonable_but_not_pure_backend_swap` | `no_output_surface_differs` | Embree median 480.62 ms divided by OptiX median 0.750 ms gives 640.93x. The scalar count agrees, but OptiX uses a prepared native count path while Embree goes through the generic row-count/materialization path. | Report only with the native-output-form caveat. |
| spatial_rayjoin_pip | `reasonable` | `qualified_output_surface_differs` | Embree median 4.065 ms divided by OptiX median 0.729 ms gives 5.57x. The count matches, and the size of the speedup is consistent with an exact prepared count path versus a generic Embree row-count path. | Usable with the scalar-count/output-form caveat. |
| triangle_counting | `reasonable` | `yes_for_prepared_weighted_any_hit_summary` | Embree prepared weighted any-hit median 6.07 ms divided by OptiX median 0.144 ms gives 42.16x. Both sides now use the same scalar weighted any-hit summary contract without materializing hit rows. | Safe as a prepared weighted any-hit summary comparison. |

## Interpretation

- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.
- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.
- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.
- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.
- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.

Validation status: `accept`.
