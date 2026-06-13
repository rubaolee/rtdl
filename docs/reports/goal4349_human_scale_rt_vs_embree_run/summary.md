# Goal4349: Human-Scale RT Core vs Embree CPU Comparison

Date: 2026-06-12

This packet reports hot prepared-query aggregates, not process wrapper time. Rows use the same repeat count when that can put both sides in the 1-10s band; otherwise they use duration-bounded throughput with identical work per iteration.

| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| barnes_hut | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.3666s | 3.8118s | 150/150 | 2.71x | 8 | `prepared_fixed_radius_node_coverage_threshold_decision` |
| contact_manifold | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 2.3399s | 2.9644s | 20/20 | 1.24x | 8 | `generic_aabb_broadphase_contact_candidates_2d_grid16384` |
| hausdorff_xhd | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.6866s | 4.2634s | 200/200 | 2.53x | 8 | `directed_threshold_prepared_fixed_radius_count` |
| librts_spatial_index | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 1.7381s | 3.8993s | 4800/48 | 259.89x | 8 | `generic_prepared_aabb_index_query_2d_all_ops` |
| raydb_style | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 3.3335s | 2.2283s | 5000/240 | 12.13x | 64 | `prepared_ray_triangle_grouped_i64_reduction_count` |
| robot_collision | `clean_backend_swap_traversal_phase_only` | `duration_bounded_throughput` | 6.4765s | 2.896s | 49900/2450 | 9.29x | 64 | `prepared_triangle_scene_grouped_segment_any_hit_flags` |
| rt_dbscan | `mostly_clean_numba_continuation_same_native_handoff_differs` | `same_repeat_human_scale` | 1.3078s | 9.3734s | 90/90 | 8.00x | 64 | `fixed_radius_core_flags_plus_numba_column_signature` |
| rtnn | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 4.1669s | 8.9706s | 40/80 | 1.09x | 64 | `prepared_3d_fixed_radius_ranked_summary_raw` |
| spatial_rayjoin_lsi | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 4.0311s | 1.0817s | 5000/500 | 3.51x | 8 | `public_cdb_lsi_count` |
| spatial_rayjoin_pip | `clean_backend_swap_prepared_phase` | `same_repeat_human_scale` | 1.6324s | 1.5559s | 2000/2000 | 0.95x | 8 | `public_cdb_pip_count` |
| triangle_counting | `clean_backend_swap_prepared_phase` | `duration_bounded_throughput` | 3.154s | 3.3534s | 20000/500 | 39.54x | 8 | `rt_graph_2a1_generic_ray_triangle_any_hit` |

## Row Reasonability Review

| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |
| --- | --- | --- | --- | --- |
| barnes_hut | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 21.898 ms divided by OptiX median 8.0949 ms gives 2.71x. OptiX is faster by 2.71x on this per-iteration metric. Both sides run prepared node-coverage queries over the same body/tree workload; no app-level continuation changes the measured phase. | Safe as a prepared RT traversal comparison. |
| contact_manifold | `reasonable` | `yes_for_prepared_broadphase` | Embree median 143.69 ms divided by OptiX median 115.76 ms gives 1.24x. OptiX is faster by 1.24x on this per-iteration metric. Both sides run the same prepared AABB broadphase collect-k contract. A modest or reversed ratio is still plausible because this row is dominated by compact AABB candidate collection and witness bookkeeping rather than long coherent ray batches. | Safe, but word as a modest broadphase gain, not a dramatic whole-app claim. |
| hausdorff_xhd | `reasonable` | `yes_for_prepared_hot_phase` | Embree median 21.317 ms divided by OptiX median 8.4328 ms gives 2.53x. OptiX is faster by 2.53x on this per-iteration metric. Both sides run the prepared directed-threshold nearest-query phase, so the ratio is attributable to RT traversal throughput plus each backend's native query overhead. | Safe as a prepared threshold-query traversal comparison. |
| librts_spatial_index | `reasonable` | `yes_for_prepared_aabb_index_ops` | Embree median 91.516 ms divided by OptiX median 0.3521 ms gives 259.89x. OptiX is faster by 259.89x on this per-iteration metric. Both sides run the prepared AABB-index all-ops contract with matching counts for point_contains, range_contains, and range_intersects. | Safe for the prepared AABB-index all-ops contract. |
| raydb_style | `reasonable` | `yes_for_prepared_grouped_reduction` | Embree median 8.0217 ms divided by OptiX median 0.6615 ms gives 12.13x. OptiX is faster by 12.13x on this per-iteration metric. Both sides use the prepared grouped i64 reduction surface over the same generated rows and groups, so the ratio follows the traversal/reduction backend path. | Safe as a prepared grouped-reduction comparison. |
| robot_collision | `reasonable` | `qualified_traversal_phase_only` | Embree median 1.1784 ms divided by OptiX median 0.1268 ms gives 9.29x. OptiX is faster by 9.29x on this per-iteration metric. This is intentionally traversal-phase only; full hot-loop timing can differ because tail/output work sits outside the RT traversal comparison. | Use only as traversal-phase speedup, not as whole hot-loop speedup. |
| rt_dbscan | `reasonable` | `qualified_native_handoff_differs` | Embree median 103.26 ms divided by OptiX median 12.912 ms gives 8.00x. OptiX is faster by 8.00x on this per-iteration metric. Both sides share the Numba continuation, while the native threshold/core-flag handoff is backend-specific; compare this as RT query acceleration plus fixed partner continuation. | Use as RT threshold plus shared Numba continuation; disclose the handoff difference. |
| rtnn | `reasonable` | `yes_for_prepared_ranked_summary_rows` | Embree median 112.05 ms divided by OptiX median 103.11 ms gives 1.09x. OptiX is faster by 1.09x on this per-iteration metric. Both sides use prepared fixed-radius 3-D ranked-summary rows, so the old Embree neighbor-row materialization explanation no longer applies. | Safe as a prepared fixed-radius ranked-summary comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_lsi | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 2.1938 ms divided by OptiX median 0.6258 ms gives 3.51x. OptiX is faster by 3.51x on this per-iteration metric. Both sides use a prepared native scalar-count contract for segment-pair intersection without materializing intersection rows. | Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard. |
| spatial_rayjoin_pip | `reasonable` | `yes_for_prepared_scalar_count` | Embree median 0.7699 ms divided by OptiX median 0.8130 ms gives 0.95x. Embree is faster by 1.06x on this per-iteration metric. Both sides use a prepared native scalar-count contract for point-in-polygon positive hits without materializing hit rows. | Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard. |
| triangle_counting | `reasonable` | `yes_for_prepared_weighted_any_hit_summary` | Embree median 6.1493 ms divided by OptiX median 0.1555 ms gives 39.54x. OptiX is faster by 39.54x on this per-iteration metric. Both sides use the prepared weighted any-hit summary contract, so the row measures backend traversal plus scalar accumulation rather than hit-row output volume. | Safe as a prepared weighted any-hit summary comparison. |

## Interpretation

- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.
- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.
- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.
- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.
- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.

Validation status: `accept`.
