# RTDL Backend Maturity

Status: V3 Phoenix rebuild backend map, not release authorization.

Backends and partners are not globally mature or immature. In Phoenix V3, every
backend statement is row-scoped and artifact-scoped.

Global truth:

```text
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 13
```

Primary sources:

```text
docs/rebuild/v3/v3_gpu_environment_gate_2026-06-20.md
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
```

## Backend And Partner Map

| Backend or partner | Current V3 role | Evidence status | User rule |
| --- | --- | --- | --- |
| CPU Python reference | Semantics and small-row correctness anchor. | Used by tutorials and selected benchmark validation paths. | Start here when learning a kernel or debugging output. |
| Embree | CPU RT backend and same-contract baseline. | Built and measured on the RTX 4000 Ada pod; sometimes the best route for small/setup-dominated rows. | Treat Embree as the baseline, not as a fallback of lesser importance. |
| OptiX | NVIDIA RT backend. | Built and measured on the RTX 4000 Ada pod; many row-scoped hot wins, plus important wall-time losses and negative rows. | Use OptiX only when the exact row classification supports it. |
| CuPy | Explicit GPU partner for selected continuation/refinement work. | GPU environment gate passes. | Require the gate before teaching or claiming CuPy-dependent rows. |
| PyTorch CUDA | Explicit partner dependency for RayDB-style rows. | CUDA tensor gate passes; grouped-reduction evidence depends on this path. | Treat CPU-only Torch environments as unsupported for those rows. |
| Numba CUDA | Explicit partner/JIT continuation path. | CUDA JIT gate passes with the documented compiler path. | Use only when the environment exposes the required CUDA compiler/runtime. |
| Vulkan, HIPRT, Apple RT | Historical or non-Phoenix-focus surfaces. | Not part of the current Phoenix V3 release evidence. | Do not use for Phoenix V3 performance claims. |

## Maturity Labels

Use these labels in current docs:

| Label | Meaning |
| --- | --- |
| `available` | The backend or partner can be present or built. |
| `correctness-ready row` | Correctness checks pass for a named row. |
| `performance-candidate row` | Timing is meaningful for a named row, but not release-authorized. |
| `boundary lesson` | A row is useful for teaching the contract and non-claims. |
| `internal evidence` | Evidence is real but should not be used in public performance wording. |
| `M7-qualified release row` | Current count is thirteen exact row-scoped/supplemental rows. The base packet records twelve rows, and the release-surface breadth gate adds one bounded Spatial supplemental row. This label still does not authorize release or broad speedup wording. |
| `no speed claim` | Route may run, but current timing does not support speedup wording. |

Do not use release-like candidate labels as public maturity labels during
Phoenix V3 rebuild. They are too easy to confuse with release authorization.

## Current Row Examples

| Row | Backend/partner reading | Maturity |
| --- | --- | --- |
| `raydb_style / grouped_sum` | Exactly three grouped_reduction rows are row-scoped M7-qualified: `grouped_reduction_sum_scalar_broadcast_repeat100_262144`, `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`, and `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`. Release, external zero-copy interop, whole-RayDB, pure backend-only, and broad claims remain false. | M7-qualified release row |
| `librts_spatial_index / AABB candidate stream` | Exactly three rows are row-scoped M7-qualified: `aabb_candidate_stream_all_count_only_float32_32768`, `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`, and `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`; release, paper, authors-code, full spatial-index, float64 exact-geometry, and V3-over-V2 claims remain false. | M7-qualified release row |
| `spatial_rayjoin / point_location_topology_stream` | Exactly `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7` is a bounded supplemental release-surface row; RayJoin author RT remains faster on PIP, so RTDL-beats-RayJoin and full spatial-join claims remain false. | M7-qualified release row |
| `rt_dbscan / component_union` | Exactly `component_union_clustered3d_65536_524288_repeat5_row_scoped` is row-scoped M7-qualified; full DBSCAN, noisy datasets, automatic continuation selection, and V3-over-V2 claims remain false. | M7-qualified release row |
| `triangle_counting / prepared_graph_chunk` | Exactly `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` passed Claude external refresh review and Codex consensus; release, paper, graph database, M113 graph capture, automatic partner selection, full app, and V3-over-V2 claims remain false. | M7-qualified release row |
| `rtnn / ranked_summary` | Exactly `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` is row-scoped M7-qualified for prepared repeat50 amortization; one-shot RTNN, cold-start RTNN, paper reproduction, and V3-over-V2 claims remain false. | M7-qualified release row |
| `hausdorff_xhd / threshold_summary` | Exactly `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` is row-scoped M7-qualified; full exact Hausdorff, witness materialization, X-HD paper reproduction, and V3-over-V2 claims remain false. | M7-qualified release row |
| `robot_collision / collision_flag_stream` | Exactly `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped` is row-scoped M7-qualified after separate CPU probe-reference validation and no-probe paired timing; full robot planning, exact solid collision, continuous collision, zero-copy, and V3-over-V2 claims remain false. | M7-qualified release row |
| `contact_manifold / broadphase collect-k` | CPU reference passes; query/collect-k win; wall loses. | boundary lesson |
| `barnes_hut / aggregate_frontier` | Exactly `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` is row-scoped M7-qualified for fused partner weighted-vector aggregation; full force calculation, prepared OptiX superiority, automatic partner selection, and V3-over-V2 claims remain false. | M7-qualified release row |

## User Rule

Do not infer maturity from a backend name. The valid question is never
"Is OptiX mature?" The valid question is:

```text
For this exact row, on this hardware, with this partner and this baseline, what
does the saved artifact prove?
```

## Goal-Level Decision Audit

Decision: replace broad backend maturity wording with row-scoped Phoenix V3
maturity labels.

1. Was I foolish?

   No. Backend names alone were hiding the real maturity boundary.

2. If yes, what actions made the decision foolish?

   It would be foolish to say OptiX is mature globally when RTNN, robot
   collision, and contact manifold all have wall-time blockers.

3. Was there another path?

   Yes: keep one backend table and rely on per-app docs. That is weaker because
   users start from backend choice.

4. Can I now try a different path that actually solves the problem?

   Yes. Make backend maturity a row-scoped decision table and reserve
   `M7-qualified release row` for rows that actually pass.
