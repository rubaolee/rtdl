# RTDL Performance Model

Status: V3 Phoenix capability/quality performance model, not release authorization.

This page explains how to read V3 performance evidence without turning internal
progress into public overclaims.

Global truth:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 13
phase_a_high_performance_path: no_go_enter_phase_h
```

## Rule 1: Performance Is Row-Scoped

Every V3 performance statement must name:

- app and exact row;
- backend and partner, if any;
- hardware;
- baseline;
- metric scope;
- output contract;
- artifact path;
- claim boundary.

Without those fields, the sentence is not a valid performance claim.

## Rule 2: V3-over-V2.x Is Mostly Parity, And Phase A Did Not Prove A Speed Release

The same-RT-hardware paired V2.14-vs-current-V3 run found:

```text
same_metric_comparison_count: 46
same-row geomean V3 speedup vs V2.14: 1.012x
10 rows faster by more than 5%
32 rows within +/-5%
4 rows slower by more than 5%
broad_v3_faster_than_v2_claim_authorized: false
```

The current honest V3 story is runability, a productized prepared-execution
runtime trunk, route health, clearer contracts, and exact row-scoped evidence.
It is not a broad raw timing victory over V2.14.

The Phase A trunk-first attempt is complete. Barnes-Hut proved trunk execution
but stayed backend-bound; RTNN executed with parity but moved the frozen
scorecard row only to `1.03622547722238x`, below the `>=1.20x` Set-A
performance-source bar. Claude and Antigravity both accepted the No-Go and
directed V3 into the Phase H capability/quality branch.

Source:

```text
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md
```

## Rule 3: Hot, Query, Wall, And End-To-End Are Different Claims

Many rows have a fast hot metric and a weaker wall metric. Do not turn one into
the other.

| Row | Strong metric | Blocking metric or scope |
| --- | ---: | --- |
| `raydb_style / grouped_sum` | Scalar-broadcast 262,144 row: 200.353x actual repeat100 hot loop and 27.917x cold-plus-loop. Device-column rows: 3.599x and 73.586x host-packed OptiX/device-column OptiX cold-plus-loop. | Three exact grouped_sum rows are row-scoped M7-qualified. The Embree/device-column ratios are same-contract context where Embree remains host-packed and OptiX uses `cupy_device_columns`; they are not pure backend-only ratios. V3 release, whole-app, external zero-copy interop, and broad V2 speedup claims remain false. |
| `triangle_counting / prepared_graph_chunk` | 116.060x and 347.232x hot-query wins. | The 80,000-clique row is row-scoped M7-qualified only as `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`: 347.232x hot-query and 6.342x wall-time speedup on a synthetic non-graph stream row; not graph DB, paper reproduction, M113 graph capture, automatic partner selection, full Triangle app speedup, or V3-over-V2. |
| `rt_dbscan / component_union` | `component_union_clustered3d_65536_524288_repeat5_row_scoped` is row-scoped M7-qualified. | Clustered 3D component union only; not full DBSCAN, not noisy datasets, and not V2 comparison wording. |
| `rtnn / ranked_summary` | `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` is row-scoped M7-qualified for prepared repeat50 amortization. | One-shot ranked-summary rows still show wall losses; do not claim cold-start RTNN, whole RTNN, paper reproduction, or V2 comparison wording. |
| `hausdorff_xhd / threshold_summary` | `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` is row-scoped M7-qualified. | Threshold-summary decision only; not full exact Hausdorff witness materialization, not X-HD paper reproduction, and not V2 comparison wording. |
| `robot_collision / collision_flag_stream` | `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped` is row-scoped M7-qualified: 5.086x tail prepared phase, 5.075x total-run window, 1.171x conservative no-probe wrapper. | Sampled flag stream only; CPU probe-reference validation is separate; not full robot planning, exact solid collision, continuous collision, or V2 comparison wording. |
| `contact_manifold / broadphase collect-k` | 1.235x query and 2.759x collect-k wins. | Wall ratio is 0.803x; full contact solver remains app-owned. |
| `spatial_rayjoin / point_location_topology_stream` | `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7` is a bounded supplemental release-surface row. | RayJoin author RT remains faster on PIP; not RTDL-beats-RayJoin, full spatial join, true zero-copy, or V2 comparison wording. |
| `barnes_hut / aggregate_frontier` | `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` is row-scoped M7-qualified for fused partner weighted-vector aggregation. | Full force calculation, prepared OptiX superiority, automatic partner selection, and V2 comparison wording remain false. |

Values above 1.0 mean OptiX was faster than Embree for that measured scope.
Wall ratios below 1.0 mean OptiX was slower for the wall path.

## Rule 4: Strong Ratios Still Need A Claim Boundary

Representative strong current-side OptiX-over-Embree ratios:

| Row | Signal | Current claim boundary |
| --- | ---: | --- |
| `spatial_rayjoin / rayjoin_overlay_seed_authored_tiled_x2048` | 30489.613x | RayJoin author RT is still faster than RTDL OptiX on PIP; route-scoped only. |
| `librts_spatial_index / aabb_index_all_count_only_large_32768` | 814.339x query, 132.753x wall | M7-qualified only as `aabb_candidate_stream_all_count_only_float32_32768`: native float32-inclusive generic AABB count-only, not LibRTS paper/authors-code, not full spatial-index acceleration, not float64 exact geometry, and not V3-over-V2. |
| `raydb_style / grouped_sum scalar broadcast` | 200.353x actual repeat100 loop and 27.917x cold-plus-loop at 262,144 rows | This scalar-broadcast grouped_sum row is row-scoped M7-qualified public wording. It is not RayDB whole-app wording, not the old scalar-broadcast 524,288-row result, and not broad V3-over-V2 wording. |
| `raydb_style / grouped_sum device columns` | 3.599x and 73.586x host-packed OptiX/device-column OptiX cold-plus-loop | M7-qualified only as the two exact `cupy_device_columns` prepared grouped_sum rows. The 218.248x cold-prepare phase ratio is not headline wording; it includes workload-build/input-path collapse, ray-batch preparation, native prepare, and other cold setup. |
| `triangle_counting / triangle_count_rt_graph_2a1_cliques_80000` | 347.232x hot, 6.342x wall | M7-qualified only as `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`: synthetic non-graph stream, not RT-Graph paper, graph DB, M113 graph capture, automatic partner selection, full app, or V3-over-V2. |

Strong internal evidence is useful. It becomes public wording only after the
exact row passes the M7 qualification path and external review; today that is
true only for thirteen exact row-scoped/supplemental release-surface rows:
`grouped_reduction_sum_scalar_broadcast_repeat100_262144`,
`grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`,
`grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`,
`aabb_candidate_stream_all_count_only_float32_32768`,
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`,
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`,
`rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`,
`aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`,
`component_union_clustered3d_65536_524288_repeat5_row_scoped`,
`prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`,
`hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`, and
`collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`,
plus the bounded Spatial supplemental row
`point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`.

The thirteenth-row installer/reproducibility scope extension is still awaiting
external review; this list is not release authorization.

## Rule 5: Negative Rows Stay In The Story

The following rows explain why broad OptiX or broad V3 wording is forbidden:

| Row | Signal | Meaning |
| --- | ---: | --- |
| `spatial_rayjoin / rayjoin_all_backend_query_summary` | 0.034x | Tiny route-health fixture, not RayJoin performance evidence. |
| `librts_spatial_index / aabb_index_all_count_only` | 0.065x | Small synthetic route-health fixture, not LibRTS paper evidence. |
| `rt_dbscan / same-contract serious rows` | 1.150x, 1.079x, 1.071x | Corrected rows are modest and continuation-dominated. |
| `barnes_hut / aggregate_frontier` | Prepared OptiX is 7.328x, 5.120x, and 13.912x slower than fastest fused Numba CUDA route. | Current Barnes-Hut performance path is fused partner code, not prepared OptiX. |

Source:

```text
docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md
```

Barnes-Hut RT-core wording remains blocked. The historical
`generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1` marker must
still be read with the `specified_not_implemented` claim-boundary label for
RT-core traversal claims; current CUDA/Numba/native leaf-DFS evidence is useful
runtime evidence, not a public Barnes-Hut RT-core speedup.

## Rule 6: Environment Is Part Of The Evidence

Partner-dependent rows require the GPU environment gate:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

CuPy, Torch CUDA, and Numba CUDA evidence is invalid for a user's machine until
the relevant environment gate passes there.

## Current Evidence Index

Use these files before making any performance statement:

```text
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
tutorials/current/README.md
```

## Current Non-Claims

- Do not claim V3 is released.
- Do not claim V3 broadly beats V2.x.
- Do not claim OptiX automatically means faster.
- Do not claim a hot-query ratio is an end-to-end app speedup.
- Do not claim a benchmark row reproduces a paper unless the packet explicitly
  proves that.
- Do not claim any row beyond the thirteen exact current Phoenix release-surface rows is M7-qualified today.

## Goal-Level Decision Audit

Decision: make the performance model a claim-boundary guide, not a ratio
showcase.

1. Was I foolish?

   No. The old ratio table was useful but too easy to read as headline release
   wording.

2. If yes, what actions made the decision foolish?

   It would be foolish to keep superseded representative numbers after newer
   calibrated and focused packets superseded them.

3. Was there another path?

   Yes: only update the numbers. That would still leave users unsure about hot
   versus wall versus end-to-end scope.

4. Can I now try a different path that actually solves the problem?

   Yes. Put timing scopes, blockers, negative rows, and evidence paths on the
   same page as the ratios.
