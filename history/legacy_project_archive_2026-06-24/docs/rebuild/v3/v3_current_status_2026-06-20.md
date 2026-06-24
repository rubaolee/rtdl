# V3 Current Status

Status timestamp: updated 2026-06-22.

This is a Phoenix V3 status note. It is not a release report.

## Short Answer

V3 is `redo_required`: it is not release-ready, and the current scoped rows are
not enough for a major RTRDL language/runtime release.

The earlier release-readiness consensus on 2026-06-21 reviewed a bounded
six-row exact-claim surface and blocked major-release wording. Later
grouped-reduction device-column, AABB native query-handle, RTNN prepared
repeat50, Barnes-Hut fused-partner, and Spatial guarded topology-stream reviews
increased the current row-scoped/supplemental release surface to 13 rows across
9 / 9 planned capability families. The old eleven-row and twelve-row reviews
remain historical. The current thirteen-row surface is internal evidence; the
major-version performance mandate now controls the release decision:

```text
status: redo_required
Phoenix M7-qualified release rows: 13
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
  - current_core_gap_external_review_blocks_release
```

See
[Phoenix V3 Readiness Distance Packet](phoenix_v3_readiness_distance_packet_2026-06-22.md),
[Phoenix V3 Release Surface Breadth Gate](phoenix_v3_release_surface_breadth_gate_2026-06-21.md),
[Codex Subagent Review - Phoenix V3 Aggregate Release Readiness 13-Row](../../reviews/codex_subagent_phoenix_v3_aggregate_release_readiness_13_row_review_2026-06-22.md),
and
[Codex Fallback Consensus - Phoenix V3 Aggregate Release Readiness 13-Row](../../reviews/codex_phoenix_v3_aggregate_release_readiness_13_row_2ai_fallback_consensus_2026-06-22.md).
The fallback consensus is not a Claude/Gemini external authorization.

Current release gate blocker summary:

```text
broad_v2x_performance_not_proven
serious_all_app_paired_evidence_failed_release_bar
current_scoped_13_row_surface_not_v3_major_release
```

We are RTRDL language/runtime designers, not benchmark-app developers.
Benchmark apps exist to force and verify reusable runtime capabilities.

Focused generic runtime progress after the serious paired run:

```text
docs/reports/phoenix_v3_barnes_hut_symbol_cache_focused_evidence_2026-06-22.md
status: focused_generic_runtime_fix_validated_not_release
scope: PreparedOptixFixedRadiusCountThreshold2D library/symbol cache
largest recovered rows:
  goal2626_large Barnes-Hut OptiX: 0.622x old V3 vs V2.14 -> 0.999x patched V3 vs V2.14
  goal2636_stress Barnes-Hut OptiX 32768: 0.591x old V3 vs V2.14 -> 1.038x patched V3 vs V2.14
release_authorized: false
```

Second focused generic runtime progress after the serious paired run:

```text
docs/reports/phoenix_v3_librts_aabb_count_cache_focused_evidence_2026-06-22.md
status: focused_generic_runtime_fix_validated_not_release
scope: Embree AABB_INDEX_QUERY_2D prepared count query packing/symbol cache
recovered row:
  goal2626_large LibRTS Embree AABB count-only: 0.869x old V3 vs V2.14 -> repeat=3 1.705x and repeat=9 1.923x patched V3 vs V2.14
open note:
  LibRTS OptiX AABB row is unstable/inconclusive and needs separate route analysis
release_authorized: false
```

Third focused generic runtime hygiene after the serious paired run:

```text
docs/reports/phoenix_v3_rtnn_neighbor_symbol_cache_focused_evidence_2026-06-22.md
status: focused_generic_runtime_hygiene_validated_no_material_speedup
scope: Prepared Embree/OptiX fixed-radius 3-D neighbor optional-symbol cache
result:
  RTNN stress focused rerun patched V3 vs V2.14: 12-row geomean 1.001x
  rows faster by >5%: 1
  rows within +/-5%: 11
  rows slower by >5%: 0
release_authorized: false
```

Fourth focused generic runtime progress after the serious paired run:

```text
docs/reports/phoenix_v3_fixed_radius_symbol_cache_focused_evidence_2026-06-22.md
status: focused_generic_runtime_fix_validated_not_release
scope: generic Embree/OptiX prepared fixed-radius count-threshold symbol/library cache
result:
  same-pod focused rerun patched V3 vs V2.14: 17-row geomean 1.062x
  rows faster by >5%: 4
  rows within +/-5%: 12
  rows slower by >5%: 1
interpretation:
  useful generic runtime cleanup, concentrated in Hausdorff XHD OptiX rows;
  not enough to authorize release or rerun full all-app evidence yet
release_authorized: false
```

Fifth focused generic runtime contract progress after the serious paired run:

```text
docs/reports/phoenix_v3_fixed_radius_graph_self_query_refresh_focused_evidence_2026-06-22.md
status: focused_generic_runtime_contract_fix_validated_no_material_speedup
scope: grouped-stream core-flag refresh uses prepared self-query device-search columns
result:
  same-pod CuPy A/B after-vs-before: 3-row geomean 0.998x
  signatures unchanged: 3 / 3
  count refresh adapter changed from host-query prepared-scene route to prepared self-query route
  transfer_mode changed from host_query_points_to_device_threshold_columns to prepared_device_search_points_self_count_threshold_columns
environment:
  CuPy evidence requires /root/rtdl_v3_rebuild_20260620/venv_partner_py312 on the pod
  Numba grouped-stream remains blocked by CUDA_ERROR_UNSUPPORTED_PTX_VERSION
interpretation:
  device-residency/contract cleanup, not material performance progress
release_authorized: false
```

Current redo-era dominant hotpath selection:

```text
docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md
status: active_p0_prepared_execution_session_runner_not_release
selected_p0: prepared_execution_session_runner
reason:
  productize one prepared execution/session layer that actually routes reusable
  primitives with explicit backend/partner choice, phase accounting, residency
  metadata, and release/public-claim flags false
full_all_app_rerun_authorized_now: false
release_authorized: false
```

Current external review of the core-gap packet:

```text
review: docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
intake: docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json
status_line: external_verdict_obtained_claude_approve_blocked_not_release
verdict: approve_blocked_not_release
direction_decision: continue_with_redirect
release_authorized: false
major_version_mandate_overridden: false
```

Claude's companion Set A / Set B scorecard proposal is recorded at
`docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`.
It is a recommendation only, not an authorization and not a gate change by
itself. Its practical instruction for current engineering is accepted as
non-release workflow: do not spend another all-app pod run until the productized
execution path actually executes on at least two Set-A probes and the A/B
classification is frozen before the run.

Gap-1 M1 runner smoke progress:

```text
docs/reports/phoenix_v3_prepared_execution_session_runner_m1_smoke_2026-06-22.md
status: m1_generic_runner_smoke_validated_not_release
code: src/rtdsl/prepared_execution.py
test: tests/v3_phoenix_prepared_execution_session_runner_test.py
runtime_executed: true for caller-supplied smoke primitive
release_authorized: false
pod_performance_evidence: none yet
```

Gap-1 M1.1 fixed-radius self-query runner binding progress:

```text
docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md
status: m1_1_fixed_radius_self_query_runner_binding_validated_not_release
code: src/rtdsl/prepared_execution.py
test: tests/v3_phoenix_prepared_execution_session_runner_test.py
primitive_family: fixed_radius_count_threshold_self_query
adapter: fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns
runtime_executed: true in local contract test
release_authorized: false
public_speedup_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
pod_performance_evidence: none yet
next: make the runner-backed primitive visible in one real Set-A benchmark
  probe route, then run focused pod A/B if correctness and claim gates pass
```

Gap-1 M1.2 grouped-stream runner route progress:

```text
docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md
status: m1_2_runner_backed_fixed_radius_probe_route_validated_not_release
probe_route: PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run
primitive_family: fixed_radius_count_threshold_self_query
productized_execution_path_visible_in_route: true
release_authorized: false
public_speedup_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
pod_performance_evidence: neutral A/B, not material speedup
pod_ab_report: docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
geomean_before_over_after_speedup: 0.9978812011247638
next: route a second Set-A family through the runner or remove reusable runner
  overhead across multiple runner-backed routes
```

Gap-1 M2 AABB native query-handle runner contract progress:

```text
docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md
status: m2_aabb_native_query_handle_runner_contract_validated_not_release
code: src/rtdsl/prepared_execution.py
test: tests/v3_phoenix_prepared_execution_session_runner_test.py
primitive_family: aabb_index_query_2d_native_query_handle
helper: run_aabb_index_query_2d_range_intersection_prepared_session
runtime_executed: true in local contract test
set_a_probe_candidate: true
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
route_status: m2_1_aabb_runner_backed_contact_route_validated_not_release
route: examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py::aabb_broadphase_witness_rows
productized_execution_path_visible_in_route: true
route_test: tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py::test_contact_aabb_route_uses_productized_prepared_session_runner
route_runtime_executed_count_in_test: 3
route_cache_hit_count_in_test: 2
pod_performance_evidence: focused same-pod A/B exists through this route
pod_ab_report: docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
pod_ab_call_for_review: docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
pod_ab_summary: docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json
pod_ab_status: m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7
productized_runner_visible_for_prepared_backends: true
optix_over_embree_cold_plus_collect_wall_speedup: 1.34595769645315
optix_over_embree_query_total_speedup: 1.73787303873785
runtime_executed_count: embree=50 optix=50
cache_hit_count: embree=49 optix=49
m7_reopen_candidate_pending_2ai_review: true
next: send the focused M2.1 AABB runner-backed pod evidence through bounded
  external review before any M7 reclassification; do not use it as release,
  public-speedup, broad V3-over-V2, or all-app authorization
```

This supersedes the practical next-work interpretation of the old closed
generic-engine queue after the serious paired run. The old
`phoenix_v3_next_generic_engine_work_queue_2026-06-21.json` remains historical
for the scoped 13-row surface; it must not be used to conclude that Phoenix V3
has no redo-era engine work left.

Final public-surface wording gate progress:

```text
docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json
gate_level: final_public_surface_claim_boundary_gate
final_public_surface_gate: true
missing_expected_m7_row_ids: []
violations: []
release_authorized: false
```

This closes the old "first-pass wording scanner only" ambiguity as a
claim-boundary gate. It does not authorize release.

Broad V3-over-V2 speedup remains a forbidden claim constraint:

```text
broad_v3_faster_than_v2_claim_authorized: false
```

Installer/reproducibility progress after that review:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md
source_tree_pod_gated_candidate_present: true
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
release_scope: source_tree_pod_gated_thirteen_row
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
general_release_installer_ready: false
release_authorized: false
```

Secondary hardware-scope progress after that review:

```text
docs/rebuild/v3/v3_secondary_rt_hardware_scope_waiver_candidate_2026-06-21.md
docs/reviews/claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md
status: compatibility_confirmed_hardware_scope_waiver_reviewed_not_release
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
secondary_rt_performance_confirmation_authorized: false
multi_gpu_performance_portability_claim_authorized: false
release_authorized: false
```

The current Phoenix evidence produced clean current-side pod results:

- `goal2626_standard_all_rows`: 22 ok / 0 failed.
- `goal2636_standard_all_rows`: 28 ok / 0 failed.
- `goal3828_full_clean`: 10 pass / 0 fail.
- GPU Python environment gate: CuPy RawKernel, Torch CUDA, and Numba CUDA JIT
  all pass.

The current evidence report is
[V2.14 Versus V3 Rebuild Pod Evidence](v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md).

The current same-RT-hardware paired timing report is
[V2.14 vs Current V3 Same RT Hardware Paired Benchmark](v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md).

The current all-app serious OptiX-vs-Embree evidence is
[V3 Claim-Grade All-Benchmark Results](v3_claim_grade_all_benchmark_results_2026-06-20.md).

The current Phoenix M4 grouped-continuation pod evidence is
[Phoenix V3 M4 Grouped-Continuation Pod Evidence](phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md).
Its final internal-evidence 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M4 Grouped-Continuation Evidence](../../reviews/codex_phoenix_v3_m4_grouped_continuation_evidence_2ai_consensus_2026-06-20.md).

The focused M10 same-stream accounting interpretation is
[Phoenix V3 M10 Same-Stream Accounting Interpretation](phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.md).
It records `m10_same_stream_accounting_interpreted_not_release`: the raw M4
index still preserves `pass_internal_with_accounting_warning` and
`clean_pass: false`, but the retained M10 CUDA event samples are
`per_sample_event_ordering_clean`. The remaining CuPy warning is an
`independent_median_non_additivity_note`, not an event-ordering failure. This
packet records the Numba zero event-pointer explanation and the open
`phoenix_m4_system_python_missing_cupy_numba` gap. It does not authorize public
same-stream wording, true-zero-copy wording, or M7 promotion. Its current review
records are
[Claude Review: Phoenix V3 M10 Same-Stream Accounting Interpretation](../../reviews/claude_phoenix_v3_m10_same_stream_accounting_interpretation_review_2026-06-21.md)
and
[Codex 2-AI Consensus: Phoenix V3 M10 Same-Stream Accounting Interpretation](../../reviews/codex_phoenix_v3_m10_same_stream_accounting_interpretation_2ai_consensus_2026-06-21.md).

The current Phoenix M5 topology pod evidence is
[Phoenix V3 M5 Topology Pod Evidence](phoenix_v3_m5_topology_pod_evidence_2026-06-20.md).
Its current author-code-complete 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M5 Author-Code Recovery](../../reviews/codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md).

The current Phoenix M6 Barnes-Hut aggregate-frontier/vector pod evidence is
[Phoenix V3 M6 Barnes-Hut Pod Evidence](phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md).
Its 2-AI internal route-parity closure is
[Codex 2-AI Consensus: Phoenix V3 M6 Barnes-Hut Evidence](../../reviews/codex_phoenix_v3_m6_barnes_hut_evidence_2ai_consensus_2026-06-20.md).

The current RayDB grouped-reduction pod evidence is
[Phoenix V3 RayDB M28 Grouped-Reduction Pod Evidence](phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md).
Its 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 RayDB M28 Grouped-Reduction Evidence](../../reviews/codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md).
The Phoenix redo alignment is
[Phoenix V3 RayDB Grouped-Reduction Redo Alignment](phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md).
It retains exactly three grouped_reduction rows as reusable engine evidence,
while keeping release, whole-app RayDB, true-zero-copy, Gap-1 completion, and
broad V3-over-V2.x claims blocked.

The current Triangle prepared-graph candidate intake is
[Phoenix V3 Triangle Prepared-Graph Candidate Intake](phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md).
Its 2-AI internal-candidate closure is
[Codex 2-AI Consensus: Phoenix V3 Triangle Prepared-Graph Candidate Intake](../../reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md).
The current Triangle tutorial-candidate packet is
[Phoenix V3 Triangle Prepared-Graph Tutorial Candidate](phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md).
It adds [Triangle Prepared-Graph Chunk](../../../tutorials/current/10_triangle_prepared_graph_chunk.md)
as a rebuild lesson with 116.060x / 347.232x hot-query wins shown beside
1.677x / 6.342x wall-time wins. The later final-review packet promotes only
`prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` as
row-scoped M7-qualified after Claude external refresh review and Codex
consensus. It is synthetic non-graph stream evidence, not RT-Graph paper
reproduction, not graph-database acceleration, not M113 graph-capture
readiness, not automatic partner selection, not full Triangle app speedup, and
not V3-over-V2 speedup.

The current RTNN ranked-summary candidate intake is
[Phoenix V3 RTNN Ranked-Summary Candidate Intake](phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md).
Its 2-AI internal-candidate closure is
[Codex 2-AI Consensus: Phoenix V3 RTNN Ranked-Summary Candidate Intake](../../reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md).
The current RTNN tutorial-boundary packet is
[Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary](phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.md).
It adds [RTNN Ranked-Summary Boundary](../../../tutorials/current/11_rtnn_ranked_summary_boundary.md)
as a rebuild lesson: clustered/shell/uniform hot metrics are 3.333x, 1.182x,
and 1.084x, but wall ratios are 0.625x, 0.316x, and 0.303x, so RTNN remains
`rtnn_ranked_summary_wall_time_boundary_not_m7`.
The current AABB candidate-stream feasibility packet is
[Phoenix V3 AABB Candidate-Stream M7 Feasibility](phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.md).
It adds [AABB Candidate Stream](../../../tutorials/current/12_aabb_candidate_stream.md)
as a rebuild lesson: the 32,768/32,768 generic count-only row has 814.339x
query and 132.753x wall OptiX-over-Embree current-side speedups. The focused
final-review packet first promoted
`aabb_candidate_stream_all_count_only_float32_32768` as row-scoped M7-qualified
after Claude/Codex review and the required float32-inclusive wording fix. It is
not LibRTS paper/authors-code timing, not full spatial-index acceleration, not
float64 exact geometry, and not V3-over-V2 speedup.
A later AABB native prepared-query-handle review promotes exactly two
additional row-scoped rows:
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
and
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`.
They are scoped to jittered-grid `range_intersection_rows` with cold prepare
plus collect wall speedups of 1.719x and 1.637x on one RTX 4000 Ada pod.
OptiX prepare alone remains slower than Embree, so no prepare-only, Contact
Manifold solver, broad AABB-index, or V3-over-V2 claim is allowed.
The current Hausdorff threshold-summary final evidence packet is
[Phoenix V3 Hausdorff Threshold-Summary Repeat=5 RTX Evidence](phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md).
It updates [Hausdorff Threshold Summary](../../../tutorials/current/13_hausdorff_threshold_summary.md):
exactly `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`
is M7-qualified after Claude/Codex review. The approved row is threshold `0.4`,
1,048,576 points per side, single RTX 4000 Ada pod, five independent paired
process samples, query mean 1.639x, phase-total mean 1.240x, and weakest
phase-total 1.224x. Phase-total includes scene preparation. Smaller Hausdorff
threshold-summary rows remain blocked because they are not phase-total wins.
The current Robot Collision flag-stream final evidence packet is
[Phoenix V3 Robot Collision Flag-Stream No-Probe Paired RTX Evidence](phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md).
It updates [Robot Collision Flag Stream](../../../tutorials/current/14_robot_collision_flag_stream.md)
after Claude/Codex review: exactly
`collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
is M7-qualified. The approved wording says the 5.086x tail and 5.075x
total-run-window speedups are prepared query execution phase metrics, while
1.171x wrapper is the conservative process-level bound excluding only the CPU
probe-reference oracle.
The current Contact Manifold broadphase boundary packet is
[Phoenix V3 Contact Manifold Broadphase Boundary](phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md).
It adds [Contact Manifold Broadphase Boundary](../../../tutorials/current/15_contact_manifold_broadphase_boundary.md)
as a rebuild lesson: query timing is 1.235x, collect-k is 2.759x, and
`matches_cpu_reference: true`, but wall timing is 0.803x and full contact solver
claims remain blocked. It remains
`contact_manifold_broadphase_boundary_not_m7`.

The base Phoenix M7 row classification packet is
[Phoenix V3 M7 Row Classification Packet](phoenix_v3_m7_row_classification_packet_2026-06-20.md).
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M7 Row Classification Packet](../../reviews/codex_phoenix_v3_m7_row_classification_packet_2ai_consensus_2026-06-20.md).
The RTDBSCAN row-count refresh is
[Codex 2-AI Refresh Consensus: Phoenix V3 M7 Row Classification Packet After RTDBSCAN](../../reviews/codex_phoenix_v3_m7_row_classification_packet_rtdbscan_refresh_2ai_consensus_2026-06-21.md).
It classifies the original 19 route-map candidate rows across 10 apps and then
adds reviewed supplemental rows. Five route-map rows (AABB, RTDBSCAN
component_union, Triangle, Hausdorff threshold_summary, and Robot Collision
collision_flag_stream) and seven supplemental rows (three grouped_sum rows, two
AABB native query-handle rows, one RTNN prepared repeat50 row, and one
Barnes-Hut fused-partner aggregate-tree row) are now M7-qualified; all other
rows remain internal, blocked, or focused no-go. It also records no immediate
next M7 promotion candidates from old evidence; remaining work is in the
generic-engine queue. The current release-surface breadth gate then adds one
bounded Spatial supplemental row:
`point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`.
The Phoenix redo alignment for that row is
[Phoenix V3 Spatial Topology-Stream Redo Alignment](phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md).
It retains exactly one `point_location_topology_stream` row as internal reusable
engine evidence while keeping public Spatial speedup, `RTDL beats RayJoin`,
RayJoin paper reproduction, broad V3-over-V2.x, and Gap-1 productized
execution-path completion claims blocked.
Together, the current release surface records:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 13
```

The installer/reproducibility closure is reviewed under
`source_tree_pod_gated_thirteen_row`; the
[thirteen-row scope-extension candidate](v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md)
and Claude/Codex consensus are complete. This closes only the scoped
source-tree/pod-gated installer blocker. It does not authorize a general
package installer, public speedup wording, or the V3 release.

The first focused M7 feasibility attempt is
[Phoenix V3 Grouped-Reduction M7 Feasibility](phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md).
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Feasibility](../../reviews/codex_phoenix_v3_grouped_reduction_m7_feasibility_2ai_consensus_2026-06-20.md).
It does not promote `grouped_reduction` to M7. It shows that hot prepared-query
wins are real, while cold/setup and repeat-count policy must be part of the
public contract before any release row exists.

The fresh grouped-reduction M7 rerun packet is
[Phoenix V3 Grouped-Reduction M7 Rerun Packet](phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md).
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Rerun Packet](../../reviews/codex_phoenix_v3_grouped_reduction_m7_rerun_packet_2ai_consensus_2026-06-20.md).
It standardizes the next pod run at warmup=3 for 262,144-row and 524,288-row
count/sum Embree/OptiX rows. It was executed after review and did not authorize
M7 promotion before the run.

The fresh grouped-reduction M7 pod evidence is
[Phoenix V3 Grouped-Reduction M7 Pod Evidence](phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md).
The run completed with `m7_execution.status: 0` and produced warmup=3
post-run intake. It still does not promote `grouped_reduction` to M7: hot-query
wins are strong, but repeat-1 end-to-end results are weak or negative for three
of four rows.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Pod Evidence](../../reviews/codex_phoenix_v3_grouped_reduction_m7_pod_evidence_2ai_consensus_2026-06-20.md).
That closure accepts the evidence as
`grouped_reduction_m7_post_run_intake_not_promoted`, not a public row.

The current grouped-reduction prepared-query contract draft is
[Phoenix V3 Grouped-Reduction Prepared-Query Contract](phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md).
It defines fixed-schema, cold/setup, hot-query, repeat-count, and forbidden
claim rules for a possible repeat 100 grouped_sum row. It is still
`prepared_query_contract_draft_not_release`, not M7 promotion.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Prepared-Query Contract](../../reviews/codex_phoenix_v3_grouped_reduction_prepared_query_contract_2ai_consensus_2026-06-20.md).
The accepted next action is sum-only M7 candidate wording review for
262,144/sum and 524,288/sum; count rows remain internal.

The current sum-only grouped-reduction M7 candidate wording packet is
[Phoenix V3 Grouped-Reduction Sum M7 Candidate Wording](phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md).
It now uses actual repeat100 pod evidence and keeps
`sum_only_actual_repeat100_candidate_wording_not_release`,
`public_speedup_claim_authorized: false`, and `Phoenix M7-qualified release
rows: 0`.
The actual repeat100 evidence packet is
[Phoenix V3 Grouped-Reduction Sum Actual Repeat100 Pod Evidence](phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md).
It superseded the older modeled repeat100 candidate values. The current
optimized evidence packet is
[Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization Pod Evidence](phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md):
262,144 rows has 27.917x cold-plus-loop speedup, while 524,288 rows has only
2.983x after cold prepare is counted. The current final-review packet is
[Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet](phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md).
It promotes only `grouped_reduction_sum_scalar_broadcast_repeat100_262144` to
row-scoped M7 qualification with
`m7_qualified_row_scoped_after_claude_codex_consensus`. V3 release,
whole-app RayDB speedup, 524,288-row grouped-sum wording, count-row wording,
and broad V3-over-V2 speedup remain unauthorized. The earlier blocked review
attempt remains recorded at
[External Review Blocked: Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet](../../reviews/external_review_blocked_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md).
The previous scalar-broadcast review is also blocked because Claude hit a
session limit and Gemini failed authentication; that blockage report is
[External Review Blocked: Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization](../../reviews/external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization_2026-06-20.md).
The current redo alignment packet is
[Phoenix V3 RayDB Grouped-Reduction Redo Alignment](phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md).
It retains the scalar-broadcast row plus two reviewed `cupy_device_columns`
grouped_sum rows as internal reusable-capability evidence. It also records the
forward rule: do not spend more Phoenix time on RayDB-specific grouped_sum
variants unless the work lands in a shared grouped_reduction or productized
runner primitive.

The current serious tutorial walkthroughs now include:
[Grouped Sum Prepared Query](../../../tutorials/current/07_grouped_sum_prepared_query.md).
It ties the tiny runnable grouped_sum example to the serious prepared-query pod
evidence and the final 262,144-row M7 review packet while keeping release
authorization blocked.
[Spatial RayJoin Route Split](../../../tutorials/current/08_spatial_rayjoin_route_split.md)
teaches why the 0.034x tiny route-health row, M5 same-contract topology row,
and authored tiled hot-route rows cannot be mixed into one claim.
[RTDBSCAN Component-Signature Route Split](../../../tutorials/current/09_rtdbscan_component_signature_route_split.md)
teaches why the approved component_union row, same-contract history, M23
grouped-stream evidence, and the old 1483x row cannot be mixed into one claim.
[Triangle Prepared-Graph Chunk](../../../tutorials/current/10_triangle_prepared_graph_chunk.md)
teaches the synthetic prepared-graph chunk signal while preserving the
hot-query versus wall-time boundary.
[RTNN Ranked-Summary Boundary](../../../tutorials/current/11_rtnn_ranked_summary_boundary.md)
teaches why a hot ranked-summary signal is not enough when wall timing regresses.
[AABB Candidate Stream](../../../tutorials/current/12_aabb_candidate_stream.md)
teaches the exact M7-qualified generic count-only AABB row while keeping LibRTS
paper, authors-code, full spatial-index, float64 exact-geometry, and V2
large-row claims blocked.
[Hausdorff Threshold Summary](../../../tutorials/current/13_hausdorff_threshold_summary.md)
teaches scoped threshold-summary evidence without full exact Hausdorff witness
claims.
[Robot Collision Flag Stream](../../../tutorials/current/14_robot_collision_flag_stream.md)
teaches one exact row-scoped M7 `collision_flag_stream` claim with 5.086x tail
prepared query execution mean, 5.075x total-run-window mean, and 1.171x
no-probe wrapper mean, while preserving the sampled-probe boundary.
[Contact Manifold Broadphase Boundary](../../../tutorials/current/15_contact_manifold_broadphase_boundary.md)
teaches generic AABB broadphase/collect-k evidence with 1.235x query, 2.759x
collect-k, CPU-reference pass, and 0.803x wall timing.

The current Spatial RayJoin M7 feasibility packet is
[Phoenix V3 Spatial RayJoin M7 Feasibility](phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md).
It records `spatial_rayjoin_m7_feasibility_not_promoted`: Spatial RayJoin is
strong internal topology-stream evidence, but RayJoin author RT is still faster
than RTDL OptiX on the PIP row and no Spatial RayJoin row is M7-promoted after
Claude/Codex boundary review.
The latest Spatial relation-status zero-prefilter experiment is
[Phoenix V3 Spatial Relation-Status Prefilter-Zero Experiment](phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md).
It records `spatial_relation_status_prefilter_zero_near_miss_not_m7`: the
legal public-county RTDL route improved from `5.406518 ms` to `1.903493 ms`
(`2.840x`) with exact count `47,262`, but RayJoin author Query remains faster
at `1.865660 ms` by `0.037833 ms`. The failed boundary-helper fast path changed
the exact count to `47,259` and was rejected. M7 rows added remain zero, and no
RTDL-beats-RayJoin, true-zero-copy, whole Spatial RayJoin, or broad V3-over-V2
claim is authorized.
The count-only/no-diagnostics follow-up is also closed as
`spatial_relation_status_count_only_no_diagnostics_no_go_not_m7`: it preserved
exact count `47,262`, but was slower than the diagnostic prefilter-zero route
(`1.903873 ms` versus `1.897592 ms`, delta `+0.006281 ms`), so the experimental
flag was not retained in source.

The current RTDBSCAN component-union M7 feasibility packet is
[Phoenix V3 RTDBSCAN Component-Union M7 Feasibility](phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.md).
It records the old `rtdbscan_component_union_m7_feasibility_not_promoted`
boundary for the 1483.603x all-app ratio and M23 grouped-stream row. It is
superseded for current row classification by the optimized same-contract packet
below.

The fresh RTDBSCAN same-contract pod evidence is
[Phoenix V3 RTDBSCAN Same-Contract Pod Evidence](phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md).
It records `rtdbscan_same_contract_pod_evidence_not_promoted`: the fair
compact-threshold plus Numba component-signature route passes the 4,096-point
reference control and large same-signature checks, but serious OptiX speedups
are only 1.150x, 1.079x, and 1.071x, with the shared continuation dominating
OptiX at 262,144 and 524,288 points. This older packet remains historical
negative evidence; it is superseded for current row classification by the
optimized same-contract packet below.
External review is blocked by current Claude quota and Gemini auth failures;
the blockage report is
[External Review Blocked: Phoenix V3 RTDBSCAN Same-Contract Pod Evidence](../../reviews/external_review_blocked_phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md).

The current RTDBSCAN continuation-bottleneck decision packet is
[Phoenix V3 RTDBSCAN Continuation-Bottleneck No-Go](phoenix_v3_rtdbscan_continuation_bottleneck_no_go_2026-06-21.md).
It records `rtdbscan_continuation_bottleneck_no_go_not_promoted`: RTDBSCAN is
not M7 from current evidence because the same-contract large rows are dominated
by the shared Numba continuation, while M23 grouped-stream component-signature
evidence is a different contract with no same-scale Embree baseline.
The current code optimization for this blocker is
[Phoenix V3 RTDBSCAN Component-Signature Optimization](phoenix_v3_rtdbscan_component_signature_optimization_2026-06-21.md).
It changes the prepared-grid column-signature path to reuse the generic Numba
label/flag-count continuation instead of host-materializing `point_ids` and
`core_flags`.

The current RTDBSCAN row-scoped final evidence packet is
[Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence](phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md).
It promotes exactly `component_union_clustered3d_65536_524288_repeat5_row_scoped`:
prepared OptiX fixed-radius threshold columns feeding the same Numba component
signature are 1.102x to 1.236x faster end-to-end than the same-contract Embree
route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to
524,288 points on an RTX 4000 Ada pod. Large-row correctness is OptiX/Embree
intra-run component-signature agreement, not independent CPU reference
validation, and the Numba continuation still dominates wall time at 262,144 and
524,288 points. It does not authorize RTDBSCAN paper, full DBSCAN, whole-app,
V2 comparison, noisy-dataset, or hardware-generalized claims.
The Phoenix redo alignment is
[Phoenix V3 RTDBSCAN Component-Union Redo Alignment](phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.md).
It retains exactly one `component_union` row as reusable engine evidence while
preserving the old no-go limits: no full RTDBSCAN/DBSCAN claim, no paper
reproduction, no broad V3-over-V2.x claim, and no Gap-1 productized
execution-path completion.

## What V3 Is Supposed To Solve

V3 must make RTDL feel like a usable language release rather than a research
bundle.

It must solve the main V2.x user problem:

```text
A serious user could see capability in V2.x, but could not get one clean answer
to what they could safely build, which backend/partner to choose, and what
current evidence supported that choice.
```

V3 must therefore provide:

- one current front door;
- one current teaching path;
- one Python-hosted RTDL contract;
- clear backend and partner rules;
- serious M7-qualified row-scoped workloads after aggregate release
  authorization;
- exact pod evidence for any performance claim;
- explicit non-claims for rows that are not ready.

## Current Completed Work

Completed reset work:

- old V3/V4 user-facing material has been moved out of the current user path;
- current README/docs/tutorial/example front doors now say V3 is being rebuilt,
  not released;
- the current tutorial ladder now includes serious grouped-sum, Spatial
  RayJoin, RTDBSCAN, Triangle, RTNN, AABB, and Hausdorff walkthroughs that
  separate syntax, route-health, hot-query, wall-time, and pod evidence from
  public claims;
- `VERSION` is now `v3-rebuild-2026-06-20`;
- `scripts/rtdl_source_tree_doctor.py` checks the V3 rebuild state;
- `scripts/run_test_matrix.py` has a `v3_rebuild` group;
- `tests/v3_rebuild_reset_test.py` guards against obvious old-surface leaks;
- V4 exports and active V4 make targets were removed from the current front
  door;
- a handoff file exists for Claude or another agent:
  `docs/handoff/CLAUDE_V3_REBUILD_TAKEOVER_HANDOFF_2026-06-20.md`.

Completed Phoenix evidence work:

- fixed the Spatial RayJoin prepared all-workload route so it completes;
- installed and gated PyTorch CUDA for RayDB partner-resident rows;
- installed and gated the Numba CUDA 12.4 nvcc/libnvvm path for Numba rows;
- repaired the CuPy NVRTC/runtime package mismatch;
- reran the current-side benchmark suites on the pod;
- copied the repaired artifacts under `docs/rebuild/v3/evidence/`.

## Current Pod Evidence

Pod:

- `root@213.173.108.14 -p 11592`
- key: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, 20475 MiB
- V2.x baseline: `v2.14`, commit
  `8384a38376567fe518d89721453eb4433de08312`

Repair-pass artifact roots:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058
```

All-app claim-grade candidate artifact:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620
```

This run covered all ten promoted benchmark apps: 40 rows ok, 0 failed, 19
Embree-vs-OptiX ratios. It replaces the earlier tiny RayJoin and small LibRTS
rows as the evidence to use when rebuilding user-facing performance docs.

Same-RT-hardware paired V2.14-vs-current-V3 artifact:

```text
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
```

That run used the same RTX 4000 Ada pod and the same benchmark runners where
both versions could run. It produced:

- `goal2626_standard`: V2.14 20 ok / 2 failed; current V3 22 ok / 0 failed.
- `goal2636_standard`: V2.14 26 ok / 2 failed; current V3 28 ok / 0 failed.
- `goal3828_full`: V2.14 9 pass / 1 failed; current V3 10 pass / 0 failed.
- 46 same-metric timing comparisons: 10 V3 faster by more than 5%, 32 within
  +/-5%, 4 V3 slower by more than 5%.
- Same-row geomean V3 speedup vs V2.14: 1.012x.

Second-machine documentation/test confirmation:

```text
docs/rebuild/v3/evidence/v3_all_benchmark_lx1_confirmation_20260620
```

That confirmation ran on `lx1` with an NVIDIA GeForce GTX 1070, driver
`580.126.09`, and 8192 MiB. It passed the V3 rebuild test matrix, release
wording gate, and source-tree doctor from a clean mirror. It is not a second
machine performance run.

Phoenix M4 grouped-continuation artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620
```

This internal run produced serious-scale M4 evidence:

- M9: 65,536-point grouped partner row passed.
- M10: 65,536-point same-stream row remains raw-classified as
  `pass_internal_with_accounting_warning`, not as a clean pass; the focused
  M10 interpretation packet records per-sample event ordering clean and treats
  the CuPy warning as an independent-median additivity note, not an event-
  ordering failure.
- M11: 65,536-point measured-window no-hidden-copy row passed.
- M18: 65,536 rays / 1,024 groups device-side grouped contract passed.
- M23: 524,288-point DBSCAN component-signature bridge passed.
- M28: 262,144-row RayDB grouped reduction passed with four independent
  Embree/OptiX count/sum rows.

This run is internal Phoenix M4 evidence only:

```text
release_authorized=false
public_speedup_claim_authorized=false
Phoenix M7-qualified release rows=0
```

Claude/Codex 2-AI consensus now closes M4 only as internal
grouped-continuation evidence. M23 RTDBSCAN component-signature reuse is
accepted as internal component-union evidence, not as a public RTDBSCAN speedup
or whole-app claim.

Phoenix M5 topology artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620
```

This internal run produced internal M5 topology evidence with author-code
comparison recovered:

- hardware/env gates passed on the RTX 4000 Ada pod;
- PIP point-location used a backend-parity-filtered 100,000-point stream;
- one exact-row tie candidate was rejected before timing;
- OptiX and Embree PIP rows matched exactly on 100,000 materialized rows;
- RayJoin author `query_exec` was rebuilt from upstream commit
  `02bf6220d6d20b04af77ee20364eced75cc029c9`;
- RayJoin RT author Query median was 0.470115 ms; RTDL OptiX wall median was
  2.692629 ms; RTDL Embree wall median was 5.169664 ms;
- RayJoin author RT was 5.728x faster than RTDL OptiX on the wall-vs-Query
  comparison and 3.861x faster than RTDL OptiX native traversal, so this is not
  an `RTDL beats RayJoin` result;
- overlay active-count matched on OptiX and Embree with active count 174;
- M5 remains internal because no row is M7-qualified for public release.

This run is internal Phoenix M5 evidence only:

```text
release_authorized=false
public_speedup_claim_authorized=false
Phoenix M7-qualified release rows=0
m5_author_code_comparison_status=complete
```

Claude/Codex 2-AI consensus closes the bounded M5 author-code recovery only as
internal author-code-complete evidence. RayJoin author RT remains faster than
RTDL OptiX on the PIP row, so no `RTDL beats RayJoin` claim is allowed.

Phoenix M6 Barnes-Hut aggregate-frontier/vector artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620
```

This internal run produced serious-scale M6 route-parity evidence:

- a single-process 32,768 / 65,536 / 131,072-body attempt failed with CUDA OOM
  in the prepared OptiX route and is preserved in the log;
- the successful run used one body count per process and merged the artifacts;
- 32,768 / 65,536 / 131,072 bodies all had four routes present and checksum
  parity across fused CPU/Numba, fused Numba CUDA, prepared OptiX+Numba, and
  prepared OptiX+CuPy;
- fused Numba CUDA was fastest on all three current rerun scales;
- prepared RTDL/OptiX+Numba was 7.328x, 5.120x, and 13.912x slower than the
  fastest route;
- this confirms that the current Barnes-Hut performance path is fused
  continuation, not the prepared aggregate-frontier OptiX contract.

This run is internal Phoenix M6 evidence only:

```text
release_authorized=false
public_speedup_claim_authorized=false
rt_core_speedup_claim_authorized=false
Phoenix M7-qualified release rows=0
```

Claude/Codex 2-AI consensus closes M6 only as internal route-parity evidence.
The accepted current result is that fused Numba CUDA is the fastest Barnes-Hut
route on the rerun scales, not prepared OptiX.

The later Barnes-Hut fused-partner M7 packet is
[Phoenix V3 Barnes-Hut Fused Partner M7 Candidate](phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md).
After Claude review and Codex consensus it promotes exactly
`aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`
as a row-scoped generic aggregate-tree fused weighted-vector partner row. The
allowed claim is 45.493 ms wall-repeat median at 131,072 bodies, 4.082x faster
than CPU/Numba fused. The 13.591x comparison against the current prepared
RTDL/OptiX frontier-emission route is supporting no-go metadata only, not a
primary speedup claim, and not an RT-core claim.

RayDB M28 grouped-reduction artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620
```

This internal run produced a 524,288-row / 2,048-group same-contract
grouped-reduction artifact:

- count: Embree 14.881 ms, OptiX 1.700 ms, 8.752x Embree/OptiX;
- sum: Embree 2104.065 ms, OptiX 13.316 ms, 158.010x Embree/OptiX;
- CPU reference matched on all rows;
- no partner continuation was required;
- the 1,048,576-row exploratory attempt exceeded the bounded-goal time budget
  before producing JSON and is preserved as an overlarge attempt;
- ratios are prepared hot-query ratios only, not end-to-end application timing,
  because the sum row has 213s+ workload/build/cold-prepare costs.

This run is internal RayDB grouped-reduction evidence only:

```text
release_authorized=false
public_speedup_claim_authorized=false
whole_app_speedup_claim_authorized=false
Phoenix M7-qualified release rows=0
```

Claude/Codex 2-AI consensus accepts this bounded M28 packet only as internal
generic grouped-reduction evidence after P1 documentation/test hardening. It is
not an M7 release row.

The later final packets and Phoenix redo alignment now retain exactly three
RayDB grouped_reduction rows in the current internal 13-row / 9-capability
surface. They close grouped_reduction as reusable engine evidence, but still do
not authorize V3 release, whole-RayDB/database acceleration, true-zero-copy,
Gap-1 productized execution-path completion, or broad V3-over-V2.x wording.

Triangle prepared-graph candidate intake:

```text
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620
```

This intake extracts the 20,000- and 80,000-clique synthetic RT-Graph 2A1 rows
from the all-app calibrated artifact. It passes as internal candidate evidence
with oracle match, same-contract OptiX/Embree timing, accepted phase timing, and
all claim flags blocked. It remains not M7-qualified because it is a synthetic
K4 clique ladder, not a paper dataset, graph database workload, or reviewed
prepared-graph release row.

RTNN ranked-summary candidate intake:

```text
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620
```

This intake extracts the 65,536-point clustered, shell, and uniform
ranked-summary rows from the all-app calibrated artifact. OptiX wins on the hot
elapsed metric for all three distributions, but OptiX wall timing is slower
than Embree for all three rows. Therefore RTNN remains internal candidate
evidence only, not a universal RTNN acceleration claim and not M7-qualified.

## Current Performance Signal

Current V3 has measured OptiX wins over Embree on serious row-scoped workloads
across all ten promoted benchmark apps:

| App / row group | Current-side signal |
| --- | --- |
| `spatial_rayjoin / rayjoin_overlay_seed_authored_tiled_x2048` | 30489.613x OptiX over Embree |
| `rt_dbscan / same-contract compact threshold component signature` | 1.150x, 1.079x, and 1.071x OptiX over Embree; old 1483.603x all-app row is not public evidence |
| `librts_spatial_index / aabb_index_all_count_only_large_32768` | 814.339x OptiX over Embree |
| `spatial_rayjoin / rayjoin_lsi_authored_tiled_x2048` | 516.792x OptiX over Embree |
| `raydb_style / raydb_grouped_count` and `raydb_grouped_sum` | 383.321x and 367.516x OptiX over Embree |
| `triangle_counting / triangle_count_rt_graph_2a1_cliques_80000` and `20000` | 347.232x and 116.060x OptiX over Embree |
| `spatial_rayjoin / rayjoin_pip_authored_tiled_x2048` | 10.703x OptiX over Embree |
| `robot_collision / prepared_collision_flags` | 5.166x OptiX over Embree |
| `rtnn / rtnn_clustered_65536_ranked_summary` | 3.333x OptiX over Embree |
| `hausdorff_xhd / threshold rows` | 1.595x to 2.000x OptiX over Embree |
| `barnes_hut / node-coverage rows` | 1.870x to 1.898x OptiX over Embree |
| `contact_manifold / generic_aabb_broadphase_collect_k` | 1.235x OptiX over Embree |
| `rtnn / shell` and `uniform` | 1.182x and 1.084x OptiX over Embree |

This is not a broad V3-vs-V2.x speedup claim. The paired V2.14-vs-current-V3
run shows mostly same-row timing parity. The clearest V3-over-V2.14 improvement
is runability and route health: V3 passes standard, strengthened, and
scale-profile rows that fail under V2.14 on the same RTX pod.

The two negative rows require explanation before any public release wording:
[V3 Negative Route Explanations](v3_negative_route_explanations_2026-06-20.md).
They are small or non-paper-equivalent route-health rows, not paper-reproduction
results and not public OptiX speedup claims.

The calibrated all-app run gives the performance-facing replacement for those
rows: RayJoin x2048 authored tiled routes and LibRTS-style 32768/32768 generic
AABB-index routes. RTDBSCAN is replaced by its focused same-contract packet,
which keeps it internal. These rows are still row-scoped and not paper
reproduction claims.

## Current Blocker

The earlier benchmark-code P0 blockers are repaired for the current tree, and
the old missing-`point_location_topology_stream` / surface-width blocker is now
closed. The current release surface has thirteen exact row-scoped/supplemental
M7 rows across all 9 / 9 planned capability families.

Current machine state:

```text
Phoenix M7-qualified release rows: 13
planned capability families: 9 / 9
missing capability families: none
generic_engine_work_queue_status: generic_engine_work_queue_closed_not_release
redo_era_p0_hotpath_status: active_p0_prepared_execution_session_runner_not_release
redo_era_p0_hotpath_packet: docs/rebuild/v3/phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md
redo_era_p0_m1_1_status: m1_1_fixed_radius_self_query_runner_binding_validated_not_release
redo_era_p0_m1_1_report: docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md
redo_era_p0_m1_2_status: m1_2_runner_backed_fixed_radius_probe_route_validated_not_release
redo_era_p0_m1_2_report: docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md
redo_era_p0_m1_2_pod_ab_status: m1_2_runner_route_pod_ab_neutral_not_release
redo_era_p0_m1_2_pod_ab_report: docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
redo_era_spatial_topology_stream_alignment_status: spatial_topology_stream_redo_aligned_internal_row_not_public_speedup
redo_era_spatial_topology_stream_alignment: docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md
core_gaps_external_verdict: approve_blocked_not_release
core_gaps_external_verdict_status_line: external_verdict_obtained_claude_approve_blocked_not_release
core_gaps_external_verdict_intake: docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json
full v3_rebuild matrix: 111 modules / 557 tests OK
full v3_rebuild matrix evidence: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json
latest local v3_rebuild matrix after M2.1 review packet: 111 modules / 557 tests OK
latest local v3_rebuild matrix evidence: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m2_1_review_packet_20260622.json
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The current release blocker is no longer a missing capability-family row or a
missing scoped review. It is broad V2.x performance proof for V3 as a reusable
RTRDL language/runtime:

```text
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
  - current_core_gap_external_review_blocks_release
core_gaps_external_review_status:
  external_verdict_obtained_claude_approve_blocked_not_release
release_authorized: false
```

That means Phoenix V3 has useful scoped technical evidence, but is still not
release-authorized because it has not proven broad V2.x performance superiority
as a language/runtime. Do not claim whole-app acceleration, paper/authors-code
reproduction, full spatial-index acceleration, graph-database acceleration,
robot-planning acceleration, exact/continuous collision, RT-core Barnes-Hut
speedup, broad V3-over-V2 speedup, hardware portability, package-install
readiness, or V3 release.

The historical no-output Claude/Gemini state is governed by
[Phoenix V3 Bounded External Review Protocol](phoenix_v3_bounded_external_review_protocol_2026-06-22.md):
record the missing external verdict as a blocker, do not retry indefinitely,
and continue non-release V3 cleanup. The current core-gap review has since
produced a valid Claude verdict:
`external_verdict_obtained_claude_approve_blocked_not_release`.

Therefore V3 remains in rebuild status.

## Current Decision

V3 is alive as a rebuild. It should continue.

The decision is:

```text
Do not publish V3 yet. Continue V3 because the current 13-row / 9-capability
surface, scoped installer closure, hardware-scope waiver, tutorial reset, and
full test matrix are real progress. Release remains blocked because the serious
same-hardware V2.14 vs current Phoenix V3 run failed the major-version
performance bar, and Claude's latest core-gap verdict explicitly says continue
with redirect, not release.
```

## Goal-Level Decision Audit

Decision: continue V3 responsibility after benchmark repair.

1. Did I make a foolish decision?

   No. The repaired evidence justifies continuing V3.

2. What action would make it foolish?

   Calling V3 released before docs/tutorials/setup gates are rebuilt from the
   repaired artifacts.

3. Was there another path?

   Yes: abandon V3 or hand it off immediately. That would discard repaired
   benchmark value.

4. What different path is now being used?

   Keep V3-only scope, use the repaired pod artifacts as the source of truth,
   and rebuild the user surface only from rows that passed.


