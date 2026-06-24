# Phoenix V3 Release Completion Audit

Date: 2026-06-22
Status: `not_complete_redo_required`

## Purpose

This audit checks the active Phoenix V3 objective against current evidence. It
does not authorize release. It exists to prevent a false closeout from treating
the 13-row surface, the 507-test matrix, or polished tutorials as enough by
themselves.

## Bottom Line

Phoenix V3 has a coherent scoped technical surface:

- 13 exact M7-qualified row-scoped/supplemental rows;
- 9 / 9 planned generic capability families covered;
- green full V3 rebuild matrix, 106 modules / 509 tests OK;
- current wording gate passing with release and broad-speed claims blocked;
- short learner path restored for the current V3 rebuild.

Phoenix V3 is still not release-authorized and must be redone around the
runtime/language performance mandate:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
```

The remaining blocker is not another row promotion and not another scoped
review. It is proof that RTRDL V3, as a language/runtime, materially improves
on V2.x across serious benchmark-app stress tests.

## Requirement Audit

| Requirement | Current evidence | Completion state |
| --- | --- | --- |
| V3 must solve a real user problem better than V2.x. | `docs/rebuild/v3/README.md`, `docs/rebuild/v3/v3_design_intent_and_v2x_problem_statement_2026-06-20.md`, `docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md`. Current evidence supports a cleaner Python-hosted RTDL programming surface, better route health, clearer backend/partner choice, and row-scoped serious workloads. Same-row raw timing is not broadly better: the paired geomean is 1.012x. | Not satisfied for V3 major release. V3 must be redone around reusable runtime optimizations that materially beat V2.x. |
| Promote only reusable, evidence-backed engine capabilities into M7 rows. | `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`, `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`, `docs/reports/phoenix_v3_surface_integrity_gate_update_2026-06-22.md`. The gate records 13 rows, 9 capability families, path integrity, and blocked unsupported-claim flags. | Satisfied for the current scoped technical surface; not release authorization. |
| Start with RayDB/grouped_reduction and close it honestly. | Grouped-sum final packet and public-surface closure promote exactly three grouped sum rows: scalar-broadcast 262,144 and two CuPy device-column rows. Count rows and whole-app RayDB remain blocked. | Satisfied for exact row-scoped grouped sum; not satisfied for whole-app RayDB. |
| Close RTDBSCAN only where same-contract evidence supports it. | `component_union_clustered3d_65536_524288_repeat5_row_scoped` is promoted after optimized same-contract evidence and review. The old 1483x all-app reading is forbidden. | Satisfied for one exact component-union row; broader RTDBSCAN claims blocked. |
| Handle Spatial RayJoin without misleading users. | The full Spatial RayJoin speedup remains blocked. One bounded supplemental `point_location_topology_stream` row closes the capability-family breadth gap. Negative and near-miss rows are explained. | Satisfied for bounded capability coverage and negative-route honesty; not satisfied for public Spatial speedup or RTDL-beats-RayJoin wording. |
| Promote Triangle only as the exact prepared-graph chunk row. | `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` is M7-qualified with synthetic non-graph stream boundaries. | Satisfied for one exact row; graph/paper/full-app claims blocked. |
| Promote RTNN only where prepared-session evidence supports it. | `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` is M7-qualified as a narrow prepared repeat50 row. | Satisfied for one exact prepared-session row; whole-RTNN claims blocked. |
| Keep app-specific native engines out of V3 claims. | Release-surface breadth gate records generic capability families for all current rows; `phoenix_v3_next_generic_engine_work_queue_2026-06-21.json` records no active promotable app-specific queue item. | Satisfied locally; future rows must keep the same gate. |
| Keep V4/C ABI/embedding out of V3. | Current docs and wording gate block V4/C ABI/embedding wording. Old V3/V4 surface is quarantined under history. | Satisfied for current scanned docs. |
| Keep true zero-copy product claims out of V3. | Wording gate and current claim-boundary docs keep true zero-copy claims blocked. Same-stream/no-hidden-copy evidence remains internal accounting, not product wording. | Satisfied for current scanned docs. |
| Keep broad V2.x speedup claims out of V3. | Same-RT-hardware paired report records 1.012x same-metric timing geomean; readiness and wording gates keep `broad_v3_faster_than_v2_claim_authorized: false`. | Satisfied as a non-claim; broad speedup is not authorized. |
| Provide polished current docs and tutorials without old-info traps. | Old release/tutorial surface is quarantined. `docs/public_documentation_map.md` and `tutorials/current/README.md` now expose a short safe path. Wording gate scans current docs and tutorials. | Mostly satisfied locally; aggregate external release review is still missing. |
| Provide serious benchmark evidence for all benchmark apps. | `docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md` records calibrated all-app evidence; negative rows have explanations. | Not satisfied for V3 major release. The apps must be rerun as language/runtime stress tests, and promoted work must be reusable runtime capability rather than app-specific code. |
| Make release authorization explicit and externally reviewable. | The scoped Claude 13-row verdict exists, but scoped review does not prove the major-version performance mandate. | Not satisfied. External review must evaluate the broad V2.x runtime-performance case after serious reruns. |

## Exact Current Surface

The current surface is exactly these 13 row ids:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
aabb_candidate_stream_all_count_only_float32_32768
aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50
aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50
rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02
component_union_clustered3d_65536_524288_repeat5_row_scoped
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7
```

Rows outside this list are internal, blocked, no-go, historical, or future
work unless another focused packet and review promotes them.

## Current Non-Completion Reasons

Phoenix V3 must not be closed as complete while any of these remain true:

- `release_authorized: false`;
- `public_speedup_claim_authorized: false`;
- `broad_v3_faster_than_v2_claim_authorized: false`;
- current same-row V3-vs-V2.14 geomean is only `1.012x`;
- benchmark apps have not yet proven broad reusable RTRDL runtime improvement;
- the current full matrix is evidence of local health, not release
  authorization;
- the short learner path is evidence of user-surface cleanup, not release
  authorization;
- scoped source-tree/pod-gated install evidence is not package-install wording;
- single-RTX hardware waiver is not broad hardware portability;
- Spatial remains a bounded supplemental capability row, not public Spatial
  speedup.

## Next Valid Actions

1. Rerun serious same-RT-hardware V3-vs-V2.x benchmark apps as RTRDL
   language/runtime stress tests.
2. Identify reusable runtime optimizations that explain broad wins.
3. Reject app-specific patches as V3 release substance.
4. Request external review only after the major performance mandate has real
   evidence.

## Goal-Level Decision Audit

Decision: update the completion audit so Phoenix V3 is not close-to-release;
it is redo-required until runtime-level V2.x performance superiority is proven.

1. Was I foolish? Yes.
2. If yes, what actions made it foolish? The foolish action would be to treat
   13 rows, 503 tests, or a cleaner tutorial path as proof of V3 completion
   without proving broad runtime performance over V2.x.
3. Was there another path? Yes. I could have tried to update release wording
   directly, but that would repeat the old premature-approval failure.
4. Can I now try a different path? Yes. This audit keeps the current surface
   reviewable as internal evidence while making the exact redo reason visible.


