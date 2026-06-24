# Goal4349: Human-Scale RT Core vs Embree CPU Comparison

Date: 2026-06-12

This packet reports hot prepared-query aggregates, not process wrapper time. Rows use the same repeat count when that can put both sides in the 1-10s band; otherwise they use duration-bounded throughput with identical work per iteration.

| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| barnes_hut | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.3912s | 3.6848s | 150/150 | 2.59x | 8 | `prepared_fixed_radius_node_coverage_threshold_decision` |
| contact_manifold | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 2.3219s | 2.9477s | 20/20 | 1.24x | 64 | `generic_aabb_broadphase_contact_candidates_2d_grid16384` |
| hausdorff_xhd | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.7003s | 4.1981s | 200/200 | 2.47x | 8 | `directed_threshold_prepared_fixed_radius_count` |
| librts_spatial_index | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.7266s | 4.4851s | 4800/48 | 173.81x | 8 | `generic_prepared_aabb_index_query_2d_all_ops` |
| raydb_style | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.9205s | 2.2429s | 5000/240 | 13.98x | 64 | `prepared_ray_triangle_grouped_i64_reduction_count` |
| robot_collision | `clean_backend_swap_traversal_phase_only` | `duration_bounded_throughput` | 6.2792s | 2.9005s | 49900/2450 | 9.58x | 8 | `prepared_triangle_scene_grouped_segment_any_hit_flags` |
| rt_dbscan | `mostly_clean_numba_continuation_same_native_handoff_differs` | `same_repeat_human_scale` | 1.2043s | 9.0184s | 90/90 | 8.55x | 64 | `fixed_radius_core_flags_plus_numba_column_signature` |
| rtnn | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.8934s | 1.4559s | 1500/120 | 6.56x | 64 | `prepared_3d_fixed_radius_ranked_summary_raw` |
| spatial_rayjoin_lsi | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 4.0336s | 3.024s | 5000/5 | 815.69x | 8 | `public_cdb_lsi_count` |
| spatial_rayjoin_pip | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.4435s | 1.2185s | 2000/2000 | 0.84x | 64 | `public_cdb_pip_count` |
| triangle_counting | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 2.91s | 3.3885s | 20000/500 | 43.61x | 8 | `rt_graph_2a1_generic_ray_triangle_any_hit` |

## Row Reasonability Review

| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |
| --- | --- | --- | --- | --- |
| barnes_hut | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 21.315 ms divided by OptiX median 8.2275 ms gives 2.59x. OptiX is faster by 2.59x on this per-iteration metric. Both sides run prepared node-coverage queries over the same body/tree workload; no app-level continuation changes the measured phase. | Safe as a prepared RT traversal comparison. |
| contact_manifold | `reasonable` | `yes_for_prepared_broadphase` | Embree median 143.07 ms divided by OptiX median 115.07 ms gives 1.24x. OptiX is faster by 1.24x on this per-iteration metric. Both sides run the same prepared AABB broadphase collect-k contract. A modest or reversed ratio is still plausible because this row is dominated by compact AABB candidate collection and witness bookkeeping rather than long coherent ray batches. | Safe, but word as a modest broadphase gain, not a dramatic whole-app claim. |
| hausdorff_xhd | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 20.991 ms divided by OptiX median 8.5015 ms gives 2.47x. OptiX is faster by 2.47x on this per-iteration metric. Both sides run the prepared directed-threshold nearest-query phase, so the ratio is attributable to RT traversal throughput plus each backend's native query overhead. | Safe as a prepared threshold-query traversal comparison. |
| librts_spatial_index | `reasonable` | `yes_for_prepared_aabb_index_ops` | Embree median 97.602 ms divided by OptiX median 0.5616 ms gives 173.81x. OptiX is faster by 173.81x on this per-iteration metric. Both sides run the prepared AABB-index all-ops contract with matching counts for point_contains, range_contains, and range_intersects. | Safe for the prepared AABB-index all-ops contract. |
| raydb_style | `reasonable` | `yes_for_prepared_grouped_reduction` | Embree median 8.1048 ms divided by OptiX median 0.5796 ms gives 13.98x. OptiX is faster by 13.98x on this per-iteration metric. Both sides use the prepared grouped i64 reduction surface over the same generated rows and groups, so the ratio follows the traversal/reduction backend path. | Safe as a prepared grouped-reduction comparison. |
| robot_collision | `reasonable` | `qualified_traversal_phase_only` | Embree median 1.1792 ms divided by OptiX median 0.1231 ms gives 9.58x. OptiX is faster by 9.58x on this per-iteration metric. This is intentionally traversal-phase only; full hot-loop timing can differ because tail/output work sits outside the RT traversal comparison. | Use only as traversal-phase speedup, not as whole hot-loop speedup. |
| rt_dbscan | `reasonable` | `qualified_native_handoff_differs` | Embree median 99.855 ms divided by OptiX median 11.677 ms gives 8.55x. OptiX is faster by 8.55x on this per-iteration metric. Both sides share the Numba continuation, while the native threshold/core-flag handoff is backend-specific; compare this as RT query acceleration plus fixed partner continuation. | Use as RT threshold plus shared Numba continuation; disclose the handoff difference. |
| rtnn | `reasonable` | `yes_for_prepared_ranked_summary_rows` | Embree median 12.131 ms divided by OptiX median 1.8501 ms gives 6.56x. OptiX is faster by 6.56x on this per-iteration metric. Both sides use prepared fixed-radius 3-D ranked-summary rows, so the old Embree neighbor-row materialization explanation no longer applies. | Safe as a prepared fixed-radius ranked-summary comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_lsi | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 602.68 ms divided by OptiX median 0.7389 ms gives 815.69x. OptiX is faster by 815.69x on this per-iteration metric. Both sides use a prepared native scalar-count contract for segment-pair intersection without materializing intersection rows. | Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_pip | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 0.6010 ms divided by OptiX median 0.7191 ms gives 0.84x. Embree is faster by 1.20x on this per-iteration metric. Both sides use a prepared native scalar-count contract for point-in-polygon positive hits without materializing hit rows. | Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard. |
| triangle_counting | `reasonable` | `yes_for_prepared_weighted_any_hit_summary` | Embree median 6.2325 ms divided by OptiX median 0.1429 ms gives 43.61x. OptiX is faster by 43.61x on this per-iteration metric. Both sides use the prepared weighted any-hit summary contract, so the row measures backend traversal plus scalar accumulation rather than hit-row output volume. | Safe as a prepared weighted any-hit summary comparison. |

## Interpretation

- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.
- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.
- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.
- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.
- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.

Validation status: `accept`.
