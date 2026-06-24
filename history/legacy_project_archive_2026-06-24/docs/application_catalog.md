# RTDL Application Catalog

Status: V3 Phoenix rebuild catalog, not release authorization.

This catalog is the current user-facing map of V3 benchmark applications after
the Phoenix evidence run and boundary packets. It answers one question:

```text
What can a user study today, and what must they not infer from it?
```

Current global truth:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 13
```

Primary sources:

```text
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
tutorials/current/README.md
```

## Catalog

| App | User problem | Current V3 status | What to tell users |
| --- | --- | --- | --- |
| `raydb_style` | Grouped count/sum over candidate rows. | Three exact `grouped_reduction` rows are M7-qualified; V3 release is still blocked. | Only `grouped_reduction_sum_scalar_broadcast_repeat100_262144`, `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`, and `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups` have row-scoped public wording after review. Do not generalize them to whole RayDB, count rows, true zero-copy, pure backend-only ratios, whole-app speedup, or broad V3-over-V2 speedup. |
| `spatial_rayjoin` | PIP, LSI, and overlay-style spatial join routes. | One bounded supplemental `point_location_topology_stream` row is in the current release surface; V3 release is still blocked. | Only `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7` has bounded release-surface wording. M5 recovered RayJoin author timing and RTDL same-contract rows, but RayJoin author RT is still faster than RTDL OptiX on the PIP row. Do not claim RTDL beats RayJoin, full spatial join speedup, or broad V3-over-V2 speedup. |
| `rt_dbscan` | Fixed-radius/core-summary discovery plus explicit continuation. | One exact `component_union` row is M7-qualified; V3 release is still blocked. | Only `component_union_clustered3d_65536_524288_repeat5_row_scoped` has row-scoped wording. It is clustered 3D component-union evidence, not full DBSCAN acceleration, not noisy-dataset evidence, not automatic continuation selection, and not broad V3-over-V2 speedup. |
| `triangle_counting` | RT-Graph-shaped prepared graph chunks. | One exact `prepared_graph_chunk` row is M7-qualified; V3 release is still blocked. | Only `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` has row-scoped public wording after Claude external refresh review and Codex consensus. It is synthetic non-graph stream evidence with 347.232x hot-query and 6.342x wall-time speedup; not RT-Graph paper reproduction, graph-database acceleration, M113 graph-capture readiness, full Triangle app speedup, automatic partner selection, or V3-over-V2 speedup. |
| `rtnn` | Ranked nearest-neighbor summaries. | One exact `ranked_summary` row is M7-qualified; V3 release is still blocked. | Only `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` has row-scoped wording. It is prepared repeat50 ranked-summary amortization evidence, not one-shot nearest-neighbor search, cold-start RTNN, whole RTNN, RTNN paper reproduction, automatic partner selection, or broad V3-over-V2 speedup. |
| `librts_spatial_index` | Generic AABB/spatial-index count-only queries. | Three exact `aabb_candidate_stream` rows are M7-qualified; V3 release is still blocked. | Only `aabb_candidate_stream_all_count_only_float32_32768`, `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`, and `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50` have row-scoped wording after review. They are native float32-inclusive AABB candidate-stream rows, not LibRTS paper/authors-code timing, not full spatial-index acceleration, not float64 exact geometry, and not V3-over-V2 speedup. |
| `hausdorff_xhd` | Threshold decisions over point sets. | One exact `threshold_summary` row is M7-qualified; V3 release is still blocked. | Only `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` has row-scoped wording. It is threshold-summary evidence, not full exact Hausdorff witness materialization, not X-HD paper reproduction, and not broad V3-over-V2 speedup. |
| `robot_collision` | Prepared collision flags for sampled robot/link probes. | One exact `collision_flag_stream` row is M7-qualified; V3 release is still blocked. | Only `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped` has row-scoped wording. Prepared-phase mean is 5.086x and conservative no-probe wrapper mean is 1.171x after separating CPU probe-reference validation; this is sampled flag-stream evidence, not full robot planning, exact solid collision, continuous collision, or broad V3-over-V2 speedup. |
| `contact_manifold` | Generic broadphase candidate rows for contact-style workloads. | Broadphase boundary lesson, not M7. | Query timing is 1.235x and collect-k is 2.759x with `matches_cpu_reference: true`, but wall timing is 0.803x and the full contact solver remains app-owned. |
| `barnes_hut` | Node coverage and aggregate-frontier/vector route parity. | One exact `aggregate_frontier` row is M7-qualified; V3 release is still blocked. | Only `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` has row-scoped wording. It is fused partner weighted-vector aggregation evidence, not full Barnes-Hut force calculation, not prepared OptiX superiority, not automatic partner selection, and not broad V3-over-V2 speedup. |

## Reading Rule

An app is not public or release-authorized just because it appears in this
catalog.
Every performance sentence must name:

- the app and exact row;
- backend and partner, if any;
- hardware;
- baseline;
- output contract;
- artifact path;
- claim boundary.

If those fields are missing, the sentence is not a valid V3 performance claim.

## Current Tutorial Path

The rebuild tutorial path is:

```text
tutorials/current/README.md
```

The serious row-scoped lessons start at lesson 7 and currently cover:

```text
grouped_reduction
point_location_topology_stream
component_union
prepared_graph_chunk
ranked_summary
aabb_candidate_stream
aggregate_frontier
threshold_summary
collision_flag_stream
contact broadphase candidate rows
```

These lessons are for learning the current V3 truth. They are not a release
tutorial track until the release blockers close.

## Non-Speedup And Mixed Rows

These rows must remain visible because they prevent broad claims:

| Row | Current meaning |
| --- | --- |
| `spatial_rayjoin / rayjoin_all_backend_query_summary` | Tiny route-health row, 0.034x OptiX/Embree. Do not use as RayJoin performance evidence. |
| `librts_spatial_index / aabb_index_all_count_only` | Small synthetic route-health row, 0.065x OptiX/Embree. Do not use as LibRTS paper evidence. |
| `rt_dbscan / same-contract serious rows` | Corrected serious rows are only modestly faster and continuation-dominated. |
| `rtnn / ranked_summary` | Hot metrics win, wall timing loses for all three distributions. |
| `robot_collision / prepared_collision_flags` | Hot metrics win, wall timing is parity/slightly slower. |
| `contact_manifold / generic_aabb_broadphase_collect_k` | Query and collect-k win, wall timing loses. |

## Current Non-Claims

- Do not claim V3 is released.
- Do not claim V3 broadly beats V2.x.
- Do not claim any row beyond the thirteen exact current Phoenix release-surface rows
  in `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
  plus `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
  is M7-qualified.
- Do not claim RTDL automatically chooses the fastest backend.
- Do not claim OptiX being available means a speedup is authorized.
- Do not claim these rows reproduce RayJoin, LibRTS, RT-Graph, RTNN, Barnes-Hut, or other
  paper results;
- Do not claim app-specific examples are full production replacements for specialized
  engines.

## Goal-Level Decision Audit

Decision: rebuild the public application catalog from Phoenix row
classification, not from earlier old candidate wording.

1. Was I foolish?

   No. The old catalog language risked making candidate evidence sound like
   release evidence.

2. If yes, what actions made the decision foolish?

   It would be foolish to keep old candidate labels after the updated final
   review packets promote exactly two rows and keep every broader release flag
   false.

3. Was there another path?

   Yes: leave the catalog alone and rely on deeper rebuild docs. That would
   make users fall into old wording again.

4. Can I now try a different path that actually solves the problem?

   Yes. Make the catalog a boundary map: useful apps, exact status, and explicit
   non-claims.
