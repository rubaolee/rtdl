# Goal4349: Human-Scale RT Core vs Embree CPU Comparison

Date: 2026-06-12

This packet reports hot prepared-query aggregates, not process wrapper time. Rows use the same repeat count when that can put both sides in the 1-10s band; otherwise they use duration-bounded throughput with identical work per iteration.

| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| barnes_hut | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.478s | 3.7795s | 150/150 | 2.59x | 8 | `prepared_fixed_radius_node_coverage_threshold_decision` |
| contact_manifold | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 2.5023s | 3.112s | 20/20 | 1.23x | 8 | `generic_aabb_broadphase_contact_candidates_2d_grid16384` |
| hausdorff_xhd | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.8699s | 4.3761s | 200/200 | 2.34x | 8 | `directed_threshold_prepared_fixed_radius_count` |
| librts_spatial_index | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.7453s | 2.6763s | 4800/48 | 130.76x | 8 | `generic_prepared_aabb_index_query_2d_all_ops` |
| raydb_style | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 3.0017s | 3.988s | 5000/240 | 15.07x | 64 | `prepared_ray_triangle_grouped_i64_reduction_count` |
| robot_collision | `clean_backend_swap_traversal_phase_only` | `duration_bounded_throughput` | 5.9854s | 3.0705s | 49900/2450 | 10.66x | 8 | `prepared_triangle_scene_grouped_segment_any_hit_flags` |
| rt_dbscan | `mostly_clean_numba_continuation_same_native_handoff_differs` | `same_repeat_human_scale` | 1.2584s | 1.4738s | 90/90 | 1.36x | 8 | `fixed_radius_core_flags_plus_numba_column_signature` |
| rtnn | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 4.2816s | 9.2993s | 40/80 | 1.09x | 64 | `prepared_3d_fixed_radius_ranked_summary_raw` |
| spatial_rayjoin_lsi | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 1.6582s | 1.0127s | 20000/2000 | 6.01x | 8 | `public_cdb_lsi_count` |
| spatial_rayjoin_pip | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 0.1996s | 0.3678s | 2000/2000 | 1.71x | 64 | `public_cdb_pip_count` |
| triangle_counting | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.9748s | 3.3777s | 20000/500 | 42.48x | 8 | `rt_graph_2a1_generic_ray_triangle_any_hit` |

## Row Reasonability Review

| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |
| --- | --- | --- | --- | --- |
| barnes_hut | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 22.040 ms divided by OptiX median 8.4943 ms gives 2.59x. OptiX is faster by 2.59x on this per-iteration metric. Both sides run prepared node-coverage queries over the same body/tree workload; no app-level continuation changes the measured phase. | Safe as a prepared RT traversal comparison. |
| contact_manifold | `reasonable` | `yes_for_prepared_broadphase` | Embree median 152.28 ms divided by OptiX median 123.73 ms gives 1.23x. OptiX is faster by 1.23x on this per-iteration metric. Both sides run the same prepared AABB broadphase collect-k contract. A modest or reversed ratio is still plausible because this row is dominated by compact AABB candidate collection and witness bookkeeping rather than long coherent ray batches. | Safe, but word as a modest broadphase gain, not a dramatic whole-app claim. |
| hausdorff_xhd | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 21.880 ms divided by OptiX median 9.3495 ms gives 2.34x. OptiX is faster by 2.34x on this per-iteration metric. Both sides run the prepared directed-threshold nearest-query phase, so the ratio is attributable to RT traversal throughput plus each backend's native query overhead. | Safe as a prepared threshold-query traversal comparison. |
| librts_spatial_index | `reasonable` | `yes_for_prepared_aabb_index_ops` | Embree median 73.758 ms divided by OptiX median 0.5641 ms gives 130.76x. OptiX is faster by 130.76x on this per-iteration metric. Both sides run the prepared AABB-index all-ops contract with matching counts for point_contains, range_contains, and range_intersects. | Safe for the prepared AABB-index all-ops contract. |
| raydb_style | `reasonable` | `yes_for_prepared_grouped_reduction` | Embree median 8.9812 ms divided by OptiX median 0.5960 ms gives 15.07x. OptiX is faster by 15.07x on this per-iteration metric. Both sides use the prepared grouped i64 reduction surface over the same generated rows and groups, so the ratio follows the traversal/reduction backend path. | Safe as a prepared grouped-reduction comparison. |
| robot_collision | `reasonable` | `qualified_traversal_phase_only` | Embree median 1.2513 ms divided by OptiX median 0.1173 ms gives 10.66x. OptiX is faster by 10.66x on this per-iteration metric. This is intentionally traversal-phase only; full hot-loop timing can differ because tail/output work sits outside the RT traversal comparison. | Use only as traversal-phase speedup, not as whole hot-loop speedup. |
| rt_dbscan | `reasonable` | `qualified_native_handoff_differs` | Embree median 16.303 ms divided by OptiX median 12.027 ms gives 1.36x. OptiX is faster by 1.36x on this per-iteration metric. Both sides share the Numba continuation, while the native threshold/core-flag handoff is backend-specific; compare this as RT query acceleration plus fixed partner continuation. | Use as RT threshold plus shared Numba continuation; disclose the handoff difference. |
| rtnn | `reasonable` | `yes_for_prepared_ranked_summary_rows` | Embree median 115.68 ms divided by OptiX median 105.72 ms gives 1.09x. OptiX is faster by 1.09x on this per-iteration metric. Both sides use prepared fixed-radius 3-D ranked-summary rows, so the old Embree neighbor-row materialization explanation no longer applies. | Safe as a prepared fixed-radius ranked-summary comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_lsi | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 0.4806 ms divided by OptiX median 0.0800 ms gives 6.01x. OptiX is faster by 6.01x on this per-iteration metric. Both sides use a prepared native scalar-count contract for segment-pair intersection without materializing intersection rows. | Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_pip | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 0.1675 ms divided by OptiX median 0.0978 ms gives 1.71x. OptiX is faster by 1.71x on this per-iteration metric. Both sides use a prepared native scalar-count contract for point-in-polygon positive hits without materializing hit rows. | Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard. |
| triangle_counting | `reasonable` | `yes_for_prepared_weighted_any_hit_summary` | Embree median 6.1923 ms divided by OptiX median 0.1458 ms gives 42.48x. OptiX is faster by 42.48x on this per-iteration metric. Both sides use the prepared weighted any-hit summary contract, so the row measures backend traversal plus scalar accumulation rather than hit-row output volume. | Safe as a prepared weighted any-hit summary comparison. |

## Interpretation

- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.
- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.
- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.
- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.
- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.

Validation status: `reject`.
- spatial_rayjoin_pip: aggregate outside 1-10s band (optix=0.199635, embree=0.367846)
