# Goal4369 Embree CPU Fairness Hardening Packet

Status: internal v2.13 CPU-side fairness evidence; not public speedup wording.

## Summary

| Field | Value |
| --- | --- |
| Validation | `accept` |
| Rows | 11 |
| Promoted apps | 10 |
| Fresh threads=8 CPU reference all-pass | True |
| Fresh CPU platform | `Linux-6.8.0-40-generic-x86_64-with-glibc2.39` |
| Numba partner rows | 1 |
| Fallback rows accepted | 0 |
| Embree rows marked RT-core accelerated | 0 |

## Thread Protocol

| Env var | Value |
| --- | ---: |
| `MKL_NUM_THREADS` | 8 |
| `NUMEXPR_NUM_THREADS` | 8 |
| `OMP_NUM_THREADS` | 8 |
| `OPENBLAS_NUM_THREADS` | 8 |
| `RTDL_EMBREE_THREADS` | 8 |
| `TBB_NUM_THREADS` | 8 |

## Row Audit

| Row | Embree route | Partner | Metric | Embree/OptiX | Repeat/Warmup | Threaded CPU ref | Fallback |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| barnes_hut | `embree_prepared_fixed_radius_threshold_count_2d` | `python_barnes_hut_opening_force_logic_outside_timed_row` | 3.949 sec | 1.938x | 3/1 | pass (barnes_hut_embree_cpu_node_coverage_prepared) | none |
| contact_manifold | `rtdl_embree_collect_k_bounded_i64` | `none` | 0.000261 sec | 0.548004x | 3/0 | pass (contact_manifold_embree_cpu_native_collect_k) | none |
| hausdorff_xhd | `embree_threshold_count` | `none` | 0.009892 sec | 2.571x | 5/1 | pass (hausdorff_xhd_embree_cpu_directed_summary) | none |
| LibRTS prepared AABB query | `embree_native_aabb_collision_index` | `none` | 0.011699 sec | 18.798x | 2/1 | pass (librts_spatial_index_embree_cpu_aabb_index) | none |
| raydb_style | `embree_prepared_ray_triangle_grouped_i64_reduction` | `none` | 0.021955 sec | 22.147x | 9/1 | pass (raydb_style_embree_cpu_count_primitive_first) | none |
| robot_collision | `embree_prepared_grouped_segment_any_hit_flags` | `none` | 0.002454 sec | 1.595x | 50000/100 | pass (robot_collision_embree_cpu_prepared_buffers) | none |
| rt_dbscan | `embree_point_query_fixed_radius_3d_threshold_capped_rows` | `numba_fixed_on_both_sides` | 17.314 sec | 54.955x | 3/1 | pass (rt_dbscan_embree_cpu_prepared_rows) | none |
| rtnn | `embree_prepared_fixed_radius_ranked_summary_raw_rows_3d` | `python_ranked_summary_contract_not_rt_core_neighbor_search` | 0.122745 sec | 1.183x | 3/0 | pass (rtnn_embree_cpu_ann_candidate_quality_reference) | none |
| Spatial RayJoin LSI same-stream scalar count | `prepared_embree_native_scalar_count_lsi` | `none` | 14.539 ms | 43.275x | 5/1 | pass (spatial_rayjoin_pip_count_embree_cpu_generic_kernel) | none |
| Spatial RayJoin PIP same-stream scalar count | `prepared_embree_native_scalar_count_pip` | `none` | 19.428 ms | 3.216x | 7/1 | pass (spatial_rayjoin_pip_count_embree_cpu_generic_kernel) | none |
| triangle_counting | `embree_ray_triangle_weighted_any_hit_sum_3d` | `python_graph_fixture_preprocessing_outside_timed_row` | 11.545 ms | 72.685x | 3/1 | pass (triangle_counting_embree_cpu_native_summary) | none |

## Interpretation

- The CPU side is not NVIDIA RT-core accelerated: every Embree row records `embree_rt_core_accelerated = false`.
- The fresh pod reference run proves all ten promoted benchmark apps still have passing Embree CPU front doors under `RTDL_EMBREE_THREADS=8` and matching OMP/TBB/MKL/OpenBLAS/NumExpr thread caps.
- RT-DBSCAN is the only Numba-partner row in this packet, and the policy is fixed on both sides rather than auto-selected.
- The PIP row uses the clean Goal4368 exact prepared-points executor evidence, so the current same-contract PIP CPU-vs-RT comparison is about 3.22x in favor of OptiX while RayJoin RT still remains faster than RTDL PIP.

## Boundary

Goal4369 hardens the Embree CPU side of the v2.13 comparison matrix. It records route, partner, thread, repeat/warmup, and fallback status for the internal row-scoped comparison. It does not authorize public speedup, whole-application speedup, paper-reproduction, Intel GPU, AMD GPU, automatic partner selection, or broad RT-core wording.

Validation status: `accept`.
