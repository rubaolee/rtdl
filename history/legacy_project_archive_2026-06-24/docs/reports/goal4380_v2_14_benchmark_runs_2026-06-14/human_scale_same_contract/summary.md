# Goal4349: Human-Scale RT Core vs Embree CPU Comparison

Date: 2026-06-12

This packet reports hot prepared-query aggregates, not process wrapper time. Rows use the same repeat count when that can put both sides in the 1-10s band; otherwise they use duration-bounded throughput with identical work per iteration.

| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| barnes_hut | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.3808s | 3.6835s | 150/150 | 2.63x | 8 | `prepared_fixed_radius_node_coverage_threshold_decision` |
| contact_manifold | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 2.4028s | 2.9361s | 20/20 | 1.21x | 8 | `generic_aabb_broadphase_contact_candidates_2d_grid16384` |
| hausdorff_xhd | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.6804s | 4.1891s | 200/200 | 2.49x | 8 | `directed_threshold_prepared_fixed_radius_count` |
| librts_spatial_index | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.7401s | 3.8976s | 4800/48 | 163.90x | 64 | `generic_prepared_aabb_index_query_2d_all_ops` |
| raydb_style | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.9131s | 2.7419s | 5000/240 | 14.05x | 64 | `prepared_ray_triangle_grouped_i64_reduction_count` |
| robot_collision | `clean_backend_swap_traversal_phase_only` | `duration_bounded_throughput` | 6.1445s | 2.8996s | 49900/2450 | 9.72x | 8 | `prepared_triangle_scene_grouped_segment_any_hit_flags` |
| rt_dbscan | `mostly_clean_numba_continuation_same_native_handoff_differs` | `same_repeat_human_scale` | 1.2153s | 9.0751s | 90/90 | 8.55x | 64 | `fixed_radius_core_flags_plus_numba_column_signature` |
| rtnn | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 4.0488s | 8.8275s | 40/80 | 1.09x | 64 | `prepared_3d_fixed_radius_ranked_summary_raw` |
| spatial_rayjoin_lsi | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 1.7566s | 5.1047s | 20000/2000 | 29.93x | 8 | `public_cdb_lsi_count` |
| spatial_rayjoin_pip | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.4465s | 1.6034s | 2000/2000 | 1.10x | 8 | `public_cdb_pip_count` |
| triangle_counting | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.9107s | 3.3402s | 20000/500 | 42.60x | 8 | `rt_graph_2a1_generic_ray_triangle_any_hit` |

## Row Reasonability Review

| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |
| --- | --- | --- | --- | --- |
| barnes_hut | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 21.405 ms divided by OptiX median 8.1422 ms gives 2.63x. OptiX is faster by 2.63x on this per-iteration metric. Both sides run prepared node-coverage queries over the same body/tree workload; no app-level continuation changes the measured phase. | Safe as a prepared RT traversal comparison. |
| contact_manifold | `reasonable` | `yes_for_prepared_broadphase` | Embree median 143.03 ms divided by OptiX median 118.31 ms gives 1.21x. OptiX is faster by 1.21x on this per-iteration metric. Both sides run the same prepared AABB broadphase collect-k contract. A modest or reversed ratio is still plausible because this row is dominated by compact AABB candidate collection and witness bookkeeping rather than long coherent ray batches. | Safe, but word as a modest broadphase gain, not a dramatic whole-app claim. |
| hausdorff_xhd | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 20.945 ms divided by OptiX median 8.4018 ms gives 2.49x. OptiX is faster by 2.49x on this per-iteration metric. Both sides run the prepared directed-threshold nearest-query phase, so the ratio is attributable to RT traversal throughput plus each backend's native query overhead. | Safe as a prepared threshold-query traversal comparison. |
| librts_spatial_index | `reasonable` | `yes_for_prepared_aabb_index_ops` | Embree median 92.475 ms divided by OptiX median 0.5642 ms gives 163.90x. OptiX is faster by 163.90x on this per-iteration metric. Both sides run the prepared AABB-index all-ops contract with matching counts for point_contains, range_contains, and range_intersects. | Safe for the prepared AABB-index all-ops contract. |
| raydb_style | `reasonable` | `yes_for_prepared_grouped_reduction` | Embree median 8.1238 ms divided by OptiX median 0.5783 ms gives 14.05x. OptiX is faster by 14.05x on this per-iteration metric. Both sides use the prepared grouped i64 reduction surface over the same generated rows and groups, so the ratio follows the traversal/reduction backend path. | Safe as a prepared grouped-reduction comparison. |
| robot_collision | `reasonable` | `qualified_traversal_phase_only` | Embree median 1.1806 ms divided by OptiX median 0.1214 ms gives 9.72x. OptiX is faster by 9.72x on this per-iteration metric. This is intentionally traversal-phase only; full hot-loop timing can differ because tail/output work sits outside the RT traversal comparison. | Use only as traversal-phase speedup, not as whole hot-loop speedup. |
| rt_dbscan | `reasonable` | `qualified_native_handoff_differs` | Embree median 100.29 ms divided by OptiX median 11.728 ms gives 8.55x. OptiX is faster by 8.55x on this per-iteration metric. Both sides share the Numba continuation, while the native threshold/core-flag handoff is backend-specific; compare this as RT query acceleration plus fixed partner continuation. | Use as RT threshold plus shared Numba continuation; disclose the handoff difference. |
| rtnn | `reasonable` | `yes_for_prepared_ranked_summary_rows` | Embree median 109.89 ms divided by OptiX median 100.65 ms gives 1.09x. OptiX is faster by 1.09x on this per-iteration metric. Both sides use prepared fixed-radius 3-D ranked-summary rows, so the old Embree neighbor-row materialization explanation no longer applies. | Safe as a prepared fixed-radius ranked-summary comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_lsi | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 2.5716 ms divided by OptiX median 0.0859 ms gives 29.93x. OptiX is faster by 29.93x on this per-iteration metric. Both sides use a prepared native scalar-count contract for segment-pair intersection without materializing intersection rows. | Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_pip | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 0.7937 ms divided by OptiX median 0.7221 ms gives 1.10x. OptiX is faster by 1.10x on this per-iteration metric. Both sides use a prepared native scalar-count contract for point-in-polygon positive hits without materializing hit rows. | Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard. |
| triangle_counting | `reasonable` | `yes_for_prepared_weighted_any_hit_summary` | Embree median 6.1402 ms divided by OptiX median 0.1441 ms gives 42.60x. OptiX is faster by 42.60x on this per-iteration metric. Both sides use the prepared weighted any-hit summary contract, so the row measures backend traversal plus scalar accumulation rather than hit-row output volume. | Safe as a prepared weighted any-hit summary comparison. |

## Interpretation

- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.
- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.
- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.
- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.
- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.

Validation status: `accept`.
