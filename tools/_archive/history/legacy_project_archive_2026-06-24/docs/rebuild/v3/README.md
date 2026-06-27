# V3 Rebuild Control

Status: Phase H capability/quality branch, not released.

This is the current authority for V3 work. Old V3/V4 user-facing docs have been
depublished from the front door. Phase A did not prove a broad high-performance
V3-over-V2 release. V3 must now be completed as an honest capability/quality
branch instead of defended by old wording.

## Objective

V3 must prove that RTDL solves a real user problem better than the V2.x line:
users should be able to write Python-hosted RTDL programs for serious
RT-shaped workloads, choose explicit supported backends/partners, and get
measured benefit on exact M7-qualified row-scoped rows without writing a custom
engine for each application.

## Why V3 Exists

V2.x proved important capability, but it left users facing a research-shaped
system:

- many benchmark and proof-app routes existed, but the user-facing language
  story was fragmented;
- performance evidence was row-scoped and useful, but not organized into a
  dependable app-author release surface;
- backend and partner choices required too much project-history knowledge;
- old reports, tutorials, and release packets made it too easy for users to
  read stale claims as current truth;
- a serious user could not yet ask "what can I safely build with RTDL today?"
  and get one clean answer.

V3 must fix that. V3 is the first version that should feel like a usable
language release rather than a pile of experiments. It must give users:

Short rule: V3 must be a usable language release, not an experiment bundle.

- one stable Python-hosted RTDL programming contract;
- a small set of serious, runnable, M7-qualified row-scoped workloads after
  capability-branch authorization;
- explicit backend and partner rules;
- same-contract performance evidence against the V2.x line where performance
  is claimed;
- polished tutorials and examples that teach only the current truth;
- clear non-claims so users do not fall into old information.

If V3 cannot do those things, it is not acceptable as V3.

V3 is not accepted because a directory exists, a tutorial sounds polished, or a
benchmark once ran. V3 is accepted only when its claims survive current pod
evidence and row-by-row classification.

The detailed design-intent answer is
[V3 Design Intent And V2.x Problem Statement](v3_design_intent_and_v2x_problem_statement_2026-06-20.md).

The controlling Phase A fork is now closed:
[Phoenix V3 Phase A Performance-Source Consensus](../../reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md).
Barnes-Hut proved trunk execution but stayed backend-bound; RTNN executed with
parity but moved the clustered/262144 frozen scorecard row only to `1.036x`.
The high-performance Phase B path is not entered. The current V3 branch is
Phase H capability/quality completion with exact row-scoped evidence and no
broad V3-over-V2 speedup claim.

The current Phase H status and remaining work are recorded in
[Phoenix V3 Phase H Capability/Quality Branch Status](phoenix_v3_phase_h_capability_branch_status_2026-06-24.md).

The historical goal completion audit is
[V3 Historical Goal Completion Audit](v3_historical_goal_completion_audit_2026-06-20.md).

The M0-M150 technical work map is
[V3 M0-M150 Technical Work Map](v3_m0_m150_technical_work_map_2026-06-20.md).

The historical Phoenix high-performance candidate matrix is
[Phoenix V3 High-Performance Candidate Matrix](phoenix_v3_high_performance_candidate_matrix_2026-06-20.md).

The Phoenix alignment audit against the formal Goal4392 V3 overall plan is
[Phoenix V3 Goal4392 Alignment Audit](phoenix_v3_goal4392_alignment_audit_2026-06-20.md).

The current Phoenix M1-M7 compliance table is
[Phoenix V3 M1-M7 Compliance Table](phoenix_v3_m1_m7_compliance_table_2026-06-20.md).

The current machine-readable P0 route-to-generic-capability map is planning
evidence only. M7 qualification is tracked by the row classification packet and
focused final-review packets:
[Phoenix V3 P0 Route Capability Map](phoenix_v3_p0_route_capability_map_2026-06-20.json).

The current Phoenix release surface has thirteen exact row-scoped/supplemental
M7 rows across nine planned capability families. The row classification packet,
release-surface breadth gate, and focused final-review packets together define
that surface: grouped_reduction, AABB candidate stream, RTDBSCAN
component_union, Triangle prepared_graph_chunk, RTNN ranked_summary,
Barnes-Hut aggregate_frontier, Hausdorff threshold_summary, Robot Collision
collision_flag_stream, and one bounded Spatial point_location_topology_stream
row. All other rows remain internal, blocked, or focused no-go:
[Phoenix V3 M7 Row Classification Packet](phoenix_v3_m7_row_classification_packet_2026-06-20.md).
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M7 Row Classification Packet](../../reviews/codex_phoenix_v3_m7_row_classification_packet_2ai_consensus_2026-06-20.md).
The RTDBSCAN row-count refresh is
[Codex 2-AI Refresh Consensus: Phoenix V3 M7 Row Classification Packet After RTDBSCAN](../../reviews/codex_phoenix_v3_m7_row_classification_packet_rtdbscan_refresh_2ai_consensus_2026-06-21.md).
The current distance-to-release summary is
[Phoenix V3 Readiness Distance Packet](phoenix_v3_readiness_distance_packet_2026-06-22.md).
The requirement-by-requirement completion audit is
[Phoenix V3 Release Completion Audit](phoenix_v3_release_completion_audit_2026-06-22.md).
The user-facing performance dossier is
[Phoenix V3 User-Facing Performance Dossier](phoenix_v3_user_facing_performance_dossier_2026-06-22.md).
The packet records no immediate next M7 promotion candidates from current
evidence; after Phase A, this is internal row-scoped evidence for the
capability/quality branch, not an aggregate high-performance release surface.
The external-review process guard is
[Phoenix V3 Bounded External Review Protocol](phoenix_v3_bounded_external_review_protocol_2026-06-22.md):
Claude/Gemini no-output states are recorded blockers, not reasons to stall
Phoenix V3 engineering work.
The current continuation handoff for successor agents and reviewers is
[Phoenix V3 Current Handoff](../../handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md).

The first focused M7 feasibility attempt is
[Phoenix V3 Grouped-Reduction M7 Feasibility](phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md).
It keeps `grouped_reduction` unpromoted, but makes the repeat-aware hot/cold
timing story explicit.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Feasibility](../../reviews/codex_phoenix_v3_grouped_reduction_m7_feasibility_2ai_consensus_2026-06-20.md).

The fresh grouped-reduction M7 rerun packet is
[Phoenix V3 Grouped-Reduction M7 Rerun Packet](phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md).
It was reviewed before execution and kept M7 promotion false before the run.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Rerun Packet](../../reviews/codex_phoenix_v3_grouped_reduction_m7_rerun_packet_2ai_consensus_2026-06-20.md).

The fresh grouped-reduction M7 pod evidence is
[Phoenix V3 Grouped-Reduction M7 Pod Evidence](phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md).
It completed successfully and still records zero M7-qualified release rows
pending fresh-result external review and a public prepared-query contract.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction M7 Pod Evidence](../../reviews/codex_phoenix_v3_grouped_reduction_m7_pod_evidence_2ai_consensus_2026-06-20.md).
That consensus accepts the result only as
`grouped_reduction_m7_post_run_intake_not_promoted`.

The grouped-reduction prepared-query contract draft is
[Phoenix V3 Grouped-Reduction Prepared-Query Contract](phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md).
It turns the fresh evidence blocker into a user contract for fixed-schema,
repeat-aware prepared queries, but it still records
`prepared_query_contract_draft_not_release` and zero M7-qualified release rows.
Its Claude/Codex 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Prepared-Query Contract](../../reviews/codex_phoenix_v3_grouped_reduction_prepared_query_contract_2ai_consensus_2026-06-20.md).
That closure advances only the sum rows to M7 candidate wording review; count
rows stay internal.

The current sum-only grouped-reduction M7 candidate wording packet is
[Phoenix V3 Grouped-Reduction Sum M7 Candidate Wording](phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md).
It is now `sum_only_actual_repeat100_candidate_wording_not_release`: the older
modeled repeat100 candidate values are superseded by actual repeat100 pod
evidence in
[Phoenix V3 Grouped-Reduction Sum Actual Repeat100 Pod Evidence](phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md).
The current local numbers use the follow-up
[Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization Pod Evidence](phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md),
which removes full-length constant ray direction/tmax arrays from the generic
3-D ray packer path and reruns actual repeat100 evidence.
The current final-review packet is
[Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet](phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md).
It promotes only `grouped_reduction_sum_scalar_broadcast_repeat100_262144` to
row-scoped M7 qualification after Claude/Codex review, with 200.353x actual
repeat100 loop speedup and 27.917x cold-plus-loop speedup. It remains not V3
release authorization, not whole-app RayDB wording, and not broad
V3-over-V2 wording.
The public-surface closure note is
[Phoenix V3 Grouped-Reduction Sum 262144 M7 Public Surface Closure](phoenix_v3_grouped_reduction_sum_262144_m7_public_surface_closure_2026-06-21.md).
The earlier blocked review attempt remains recorded at
[External Review Blocked: Phoenix V3 Grouped-Reduction Sum 262144 M7 Final Review Packet](../../reviews/external_review_blocked_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md).

The current RTDBSCAN component-union M7 feasibility packet is
[Phoenix V3 RTDBSCAN Component-Union M7 Feasibility](phoenix_v3_rtdbscan_component_union_m7_feasibility_2026-06-20.md).
It is superseded for current row classification: the 1483.603x all-app ratio
row still remains forbidden, but the later optimized same-contract packet below
promotes one exact component_union row.

The current Spatial RayJoin M7 feasibility packet is
[Phoenix V3 Spatial RayJoin M7 Feasibility](phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md).
It keeps Spatial RayJoin unpromoted after Claude/Codex boundary review: the tiny
standard row is a required negative-route lesson, the M5 topology rows are
strong internal same-contract evidence, and RayJoin author RT is still faster
than RTDL OptiX on the PIP row.
The current topology-stream accounting contract is
[Phoenix V3 Spatial RayJoin Topology-Stream Contract](phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.md).
It records `spatial_rayjoin_topology_stream_contract_candidate_not_m7`,
`M7 rows added by this packet: 0`, and the actual gap: RayJoin author remains
5.728x faster than RTDL OptiX wall on the PIP row while RTDL OptiX still shows
about 32.6% visible non-traversal overhead. The next valid work is a full M3
phase table and generic topology-stream overhead reduction, not app-specific
RayJoin tuning or RTDL-beats-RayJoin wording.
The current M3 gap analysis is
[Phoenix V3 Spatial RayJoin M3 Gap Analysis](phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md).
It keeps `spatial_rayjoin_m3_gap_analysis_not_m7`, but records the useful old
large-PIP direction: when the query point stream stays resident inside RTDL's
prepared route, OptiX hot wall moves from 273.922ms to 120.060ms (2.282x) and
the visible residual after native transfer falls from 140.988ms to 1.373ms.
This is a generic `point_location_topology_stream` optimization target, not
true zero-copy, not a public Spatial RayJoin win, and not V4/embedding work.
After the M3 gap packet, the prepared OptiX Spatial RayJoin payload now emits
non-authorizing `topology_stream_m3_phase_table_v1` and
`topology_stream_prepared_handle_v1` metadata through the generic V3
topology-stream accounting helper. That is interface progress only: the next
step is still a fresh POD packet using this table/handle path, with M7,
public-speedup, true-zero-copy, and RTDL-beats-RayJoin wording false until
fresh evidence and review say otherwise.
The checked-in runner for that next packet is
`scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`. The
fresh exact-executor RTX 4000 Ada POD packet is
[Phoenix V3 Spatial RayJoin Topology-Stream Exact-Executor POD Evidence](phoenix_v3_spatial_rayjoin_topology_stream_exact_executor_pod_evidence_2026-06-21.md):
it collected 5 samples with repeat=50, stable exact row count `47,262`, full
M3 phase table, and all release/M7/public-speedup flags false. The matching
intake packet is
[Phoenix V3 Spatial RayJoin Exact-Executor Intake](phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.md).
It records the current generic bottleneck: topology continuation/exact refine
is `52.893x` the RT traversal/candidate-emission median and accounts for
`99.663%` of prepared-query median time. It also records the rejected
device-filtered probe (`47,570 != 47,262`) as a correctness blocker, not a fast
route. A follow-up validated relation-status corrected executor probe is
[Phoenix V3 Spatial RayJoin Relation-Status Corrected Executor No-Go](phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md).
It failed exact public-county validation at `47,259 != 47,262`, so that fused
route is diagnostic-only and cannot be used as a shortcut.

A later exact-f64 native scalar-count repair is
[Phoenix V3 Spatial RayJoin Relation-Status Exact-F64 Intake](phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md).
It preserves the no-go history, but changes the reusable native scalar-count
path to evaluate the full closed-shape predicate on the device for each AABB
candidate. The RTX repeat50/sample5 public-county packet is exact and stable at
`47,262` rows, moves prepared-query median from `0.023218s` to `0.006309s`
(`3.680x`) versus the exact executor, and moves runner wall from `2.893971s` to
`1.974891s` (`1.465x`). The review gate is
[Phoenix V3 Spatial RayJoin Relation-Status Exact-F64 Review Gate](phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md).
It records `spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7`
because Claude/Gemini did not produce an external verdict and author/adverse
subset gates remain open. No release/public speedup/RTDL-beats-RayJoin/true
zero-copy/broad V3-over-V2 wording is authorized. The work queue now records
Spatial as `spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7`.

The latest Spatial relation-status zero-prefilter experiment is
[Phoenix V3 Spatial Relation-Status Prefilter-Zero Experiment](phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md).
It records `spatial_relation_status_prefilter_zero_near_miss_not_m7`: the
legal public-county RTDL route improves from `5.406518 ms` to `1.903493 ms`
(`2.840x`) with exact count `47,262`, but RayJoin author Query remains faster
at `1.865660 ms`. The remaining author gap is `0.037833 ms`. The rejected
boundary-helper variant changed the exact count to `47,259`, so it is not a
shortcut. M7 rows added remain zero, and the queue reopen bar is now a stable
RTDL median below `1.865660 ms`, full M3 evidence, exact count `47,262`, and
same-packet author timing/count evidence or a scoped external-review decision.
The external-review attempt for this new near-miss is recorded as blocked, not
as consensus:
[External AI Blocked: Phoenix V3 Spatial Prefilter-Zero Near-Miss](../../reviews/external_ai_blocked_phoenix_v3_spatial_prefilter_zero_near_miss_2026-06-21.md).

The count-only/no-diagnostics follow-up is closed as a no-go:
[Phoenix V3 Spatial Count-Only/No-Diagnostics No-Go](phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.md).
It preserved exact count `47,262`, but the median moved the wrong way:
`1.903873 ms` versus the diagnostic prefilter-zero median `1.897592 ms`
(`+0.006281 ms`). The failed experimental flag is not retained in source and
adds no M7 row.

The fresh RTDBSCAN same-contract pod evidence is
[Phoenix V3 RTDBSCAN Same-Contract Pod Evidence](phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md).
It replaces the misleading 1483.603x reading with a fair compact-threshold plus
Numba component-signature comparison. The serious rows show only 1.150x,
1.079x, and 1.071x OptiX speedups, and 262,144/524,288-point rows are dominated
by the shared continuation. It is
`rtdbscan_same_contract_pod_evidence_not_promoted`.
The current generic code optimization for that bottleneck is
[Phoenix V3 RTDBSCAN Component-Signature Optimization](phoenix_v3_rtdbscan_component_signature_optimization_2026-06-21.md).
It reuses the generic Numba label/flag-count continuation in the prepared-grid
column-signature path.

The current RTDBSCAN row-scoped final evidence packet is
[Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence](phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md).
It promotes exactly `component_union_clustered3d_65536_524288_repeat5_row_scoped`:
prepared OptiX fixed-radius threshold columns feeding the same Numba component
signature are 1.102x to 1.236x faster end-to-end than the same-contract Embree
route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to
524,288 points on an RTX 4000 Ada pod. Large-row correctness is OptiX/Embree
intra-run component-signature agreement, not independent CPU reference
validation, and the Numba continuation still dominates wall time at 262,144 and
524,288 points. This does not authorize RTDBSCAN paper, full DBSCAN,
whole-app, V2 comparison, noisy-dataset, or hardware-generalized claims.

The first Phoenix P0 pod rerun packet is
[Phoenix V3 M4 Grouped-Continuation Rerun Packet](phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md).
Its 2-AI execution consensus is
[Codex 2-AI Consensus: Phoenix V3 M4 Grouped-Continuation Rerun Packet](../../reviews/codex_phoenix_v3_m4_grouped_continuation_rerun_packet_2ai_consensus_2026-06-20.md).
The resulting internal pod evidence report is
[Phoenix V3 M4 Grouped-Continuation Pod Evidence](phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md).
Its final internal-evidence 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M4 Grouped-Continuation Evidence](../../reviews/codex_phoenix_v3_m4_grouped_continuation_evidence_2ai_consensus_2026-06-20.md).
The focused M10 accounting interpretation is
[Phoenix V3 M10 Same-Stream Accounting Interpretation](phoenix_v3_m10_same_stream_accounting_interpretation_2026-06-20.md).
It preserves the raw `pass_internal_with_accounting_warning` classification,
but records that the retained CUDA event samples are
`per_sample_event_ordering_clean` and that the CuPy warning is an
`independent_median_non_additivity_note`, not an event-ordering failure. It also
records the Numba zero event-pointer explanation and the open
`phoenix_m4_system_python_missing_cupy_numba` gap. It is not release evidence
and has `current_packet_2ai_consensus_status:
claude_codex_consensus_complete_internal_not_m7`; its review records are
[Claude Review: Phoenix V3 M10 Same-Stream Accounting Interpretation](../../reviews/claude_phoenix_v3_m10_same_stream_accounting_interpretation_review_2026-06-21.md)
and
[Codex 2-AI Consensus: Phoenix V3 M10 Same-Stream Accounting Interpretation](../../reviews/codex_phoenix_v3_m10_same_stream_accounting_interpretation_2ai_consensus_2026-06-21.md).
The next Phoenix P0 packet is
[Phoenix V3 M5 Topology Rerun Packet](phoenix_v3_m5_topology_rerun_packet_2026-06-20.md).
Its 2-AI execution consensus is
[Codex 2-AI Consensus: Phoenix V3 M5 Topology Rerun Packet](../../reviews/codex_phoenix_v3_m5_topology_rerun_packet_2ai_consensus_2026-06-20.md).
The resulting internal pod evidence report is
[Phoenix V3 M5 Topology Pod Evidence](phoenix_v3_m5_topology_pod_evidence_2026-06-20.md).
Its current author-code-complete 2-AI closure is
[Codex 2-AI Consensus: Phoenix V3 M5 Author-Code Recovery](../../reviews/codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md).
The current internal M6 aggregate-frontier/vector evidence report is
[Phoenix V3 M6 Barnes-Hut Pod Evidence](phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md).
Its 2-AI internal route-parity closure is
[Codex 2-AI Consensus: Phoenix V3 M6 Barnes-Hut Evidence](../../reviews/codex_phoenix_v3_m6_barnes_hut_evidence_2ai_consensus_2026-06-20.md).
The current internal RayDB grouped-reduction evidence report is
[Phoenix V3 RayDB M28 Grouped-Reduction Pod Evidence](phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md).
Its 2-AI internal-evidence closure is
[Codex 2-AI Consensus: Phoenix V3 RayDB M28 Grouped-Reduction Evidence](../../reviews/codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md).
The current Triangle prepared-graph candidate intake is
[Phoenix V3 Triangle Prepared-Graph Candidate Intake](phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md).
Its 2-AI internal-candidate closure is
[Codex 2-AI Consensus: Phoenix V3 Triangle Prepared-Graph Candidate Intake](../../reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md).
The current Triangle tutorial-candidate packet is
[Phoenix V3 Triangle Prepared-Graph Tutorial Candidate](phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md).
It adds [Triangle Prepared-Graph Chunk](../../../tutorials/current/10_triangle_prepared_graph_chunk.md)
to the rebuild tutorial path. A later exact-row packet promotes only
`prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` as
row-scoped M7-qualified after Claude external refresh review and Codex consensus, while keeping
public release, paper, graph-database, M113 graph-capture, automatic partner
selection, full-app, and V3-over-V2 claims blocked.
The current RTNN ranked-summary candidate intake is
[Phoenix V3 RTNN Ranked-Summary Candidate Intake](phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md).
Its 2-AI internal-candidate closure is
[Codex 2-AI Consensus: Phoenix V3 RTNN Ranked-Summary Candidate Intake](../../reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md).
The current RTNN tutorial-boundary packet is
[Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary](phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.md).
It adds [RTNN Ranked-Summary Boundary](../../../tutorials/current/11_rtnn_ranked_summary_boundary.md)
to the rebuild tutorial path and keeps RTNN not M7-qualified because OptiX
loses wall timing on all three current distributions.
The current RTNN M112 reconciliation packet is
[Phoenix V3 RTNN M112 Reconciliation Packet](phoenix_v3_rtnn_m112_reconciliation_packet_2026-06-21.md).
It reconciles M104-M112 with Phoenix M7: RTNN has real large-route
`ranked_summary` progress, but promotes zero RTNN rows because M104 has a
tie-sensitive kth checksum mismatch, M106 is `float32`/`exact=false`, and
author/RTDL output contracts differ.
The active RTNN rerun entrypoint is now
`scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py`. It stages
the M112-approved `rtnn_full_batch_float32_same_contract_m7_rerun` path by
requiring an RTDL OptiX full-batch float32 aggregate plus a same-contract CuPy
grid reference, phase/wall timing, source manifest, parity checks, and later
2-AI review.
The fresh RTX evidence packet is
[Phoenix V3 RTNN Full-Batch Float32 Same-Contract RTX Evidence](phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md).
It records a 1,048,576-point repeat5 same-contract run on an RTX 4000 Ada pod:
parity passes and prepared OptiX hot query is 7.790x faster than the CuPy grid
reference, but cold-plus-query wall is 0.393x and runner wall is 0.627x because
load, pack, and OptiX preparation dominate. The current review gate is
[Phoenix V3 RTNN Full-Batch Float32 Review Gate](phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.md).
It records `rtnn_full_batch_float32_review_blocked_not_m7`: the `7.790x`
prepared-hot-query signal is preserved as internal evidence, but `0.393x`
cold-plus-query wall, `0.627x` runner wall, missing external review, unreviewed
prepared-hot-query scope, and unsolved pack/prepare amortization block M7. It
adds no M7 row, no RTNN whole-app claim, and no end-to-end speedup claim.
The current generic OptiX CUBIN cache packet is
[Phoenix V3 RTNN OptiX CUBIN Cache Evidence](phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.md).
It adds a content-addressed CUBIN disk cache to the generic OptiX backend,
controlled by `RTDL_OPTIX_CUBIN_CACHE_DIR` and
`RTDL_OPTIX_DISABLE_CUBIN_CACHE`. On the same 1,048,576-point repeat5 RTNN
evidence harness, warm-cache execution prepare drops from `3.337s` to
`0.564s` (`5.914x`), cold-plus-query drops from `5.418s` to `2.635s`
(`2.056x`), and runner wall drops from `6.122s` to `3.431s` (`1.785x`).
This is real reusable engine progress, but it is still not M7: warm-cache
OptiX/CuPy cold-plus-query is `0.794x`, runner wall is only `1.098x`, and
public/release/broad V3-over-V2 claims remain false. The next RTNN work is
generic input-pack/device-column reuse or persistent prepared-session
amortization, not RTNN-specific tuning.
The current AABB candidate-stream feasibility packet is
[Phoenix V3 AABB Candidate-Stream M7 Feasibility](phoenix_v3_aabb_candidate_stream_m7_feasibility_2026-06-21.md).
It adds [AABB Candidate Stream](../../../tutorials/current/12_aabb_candidate_stream.md)
as a strong generic count-only candidate while keeping paper, authors-code,
V2-speedup, and M7 claims blocked.
The focused AABB final-review packet is
[Phoenix V3 AABB Candidate-Stream 32768 M7 Final Review Packet](phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.md).
It promotes only `aabb_candidate_stream_all_count_only_float32_32768` to
row-scoped M7 qualification after Claude/Codex review and the required
float32-inclusive wording fix. It remains not V3 release authorization, not
LibRTS paper/authors-code wording, not full spatial-index acceleration, not
float64 exact-geometry wording, and not broad V3-over-V2 wording.
The public-surface closure note is
[Phoenix V3 AABB Candidate-Stream 32768 M7 Public Surface Closure](phoenix_v3_aabb_candidate_stream_32768_m7_public_surface_closure_2026-06-21.md).
The current AABB prepare-reuse contract packet is
[Phoenix V3 AABB Prepare-Reuse Contract](phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md).
It adds generic `aabb_index_query_2d` prepared-session residency metadata to
the contact broadphase harness and keeps M7 rows added at zero. The next M7
path requires repeated-session POD evidence with CPU-reference parity,
overflow behavior, separate prepare/query/collect/wall phases, and an OptiX
wall win after prepare reuse. Claude/Codex consensus accepts this only as
`claude_codex_consensus_complete_queue_advancement_not_m7`.
The serious evidence entrypoint is now
`scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`; it defaults to the
32,768-indexed-AABB / 32,768-query-AABB scale floor and writes prepare, query,
collect, and wall phases, but it does not authorize M7 promotion without a
fresh RTX run and external review.
The current scale evidence packet is
[Phoenix V3 AABB Prepare-Reuse Scale Evidence](phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.md).
It records that 32,768 AABBs reached only 1.140x OptiX/Embree
cold-plus-collect wall speedup and 65,536 AABBs fell to 1.087x, both below the
1.20 material floor. AABB prepare-reuse therefore remains not M7; the next work
is generic prepare/query/collect overhead reduction, not scale-shopping.
The current overhead gate is
[Phoenix V3 AABB Prepare-Reuse Overhead Gate](phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.md).
It records `aabb_prepare_reuse_overhead_gate_blocked_not_m7`: OptiX prepare is
slower on both serious rows, query-total wins are not valid public claims
without wall clearance, collect is neutral or slower, and the route cannot
reopen M7 until generic overhead is reduced.
The latest query-record cache evidence is
[Phoenix V3 AABB Query-Cache Evidence](phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.md).
It records that the generic Python query-record cache is real, with one
range-intersection cache entry, one miss, and 52 hits per backend on both
serious rows. It is still not M7: the 32,768 row reaches only `1.188x`
cold-plus-collect wall speedup, the 65,536 row reaches only `1.135x`, both
below the 1.20 material floor, and query-total speedup remains forbidden as a
public V3 win. The next AABB work is lower-level generic packed-query buffer
reuse, prepare-cost reduction, and collect/compaction overhead reduction, not
more scale-only attempts.
The latest native query-handle evidence is
[Phoenix V3 AABB Native Query-Handle Evidence](phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md).
It implements that lower-level generic step: OptiX `range_intersection_rows`
can reuse prepared native box-query handles through
`rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries`.
On the RTX 4000 Ada pod, the same serious runner now clears the material floor:
32,768 indexed/query AABBs reach `1.719x` OptiX/Embree cold-plus-collect wall
speedup and 65,536 reaches `1.637x`, with native query-handle cache evidence
of one miss and 52 hits. This is a real V3 generic-engine M7 candidate, but it
is not yet an M7 promotion: external review is blocked, no 2-AI consensus
exists for this packet, and release/public/broad V3-over-V2 claims remain
false.
The current Hausdorff threshold-summary final evidence packet is
[Phoenix V3 Hausdorff Threshold-Summary Repeat=5 RTX Evidence](phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md).
It updates [Hausdorff Threshold Summary](../../../tutorials/current/13_hausdorff_threshold_summary.md)
after Claude/Codex review: exactly
`hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` is
M7-qualified. The approved row is threshold `0.4`, 1,048,576 points per side,
single RTX 4000 Ada pod, five independent paired process samples, query mean
1.639x, phase-total mean 1.240x, and weakest phase-total 1.224x. Phase-total
includes scene preparation. Smaller Hausdorff threshold-summary rows are query
wins but not phase-total wins.
The current Robot Collision flag-stream final evidence packet is
[Phoenix V3 Robot Collision Flag-Stream No-Probe Paired RTX Evidence](phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md).
It updates [Robot Collision Flag Stream](../../../tutorials/current/14_robot_collision_flag_stream.md)
after Claude/Codex review: exactly
`collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
is M7-qualified. The approved row is a discrete sampled probe contract on one
RTX 4000 Ada pod: tail prepared query execution mean 5.086x, total-run window
mean 5.075x, and no-probe wrapper mean 1.171x OptiX over Embree. CPU
probe-reference validation was run separately and matched both backends.
The current Contact Manifold broadphase boundary packet is
[Phoenix V3 Contact Manifold Broadphase Boundary](phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md).
It adds [Contact Manifold Broadphase Boundary](../../../tutorials/current/15_contact_manifold_broadphase_boundary.md)
as a generic AABB candidate-stream plus bounded-row lesson: query and collect-k
timing win, CPU reference matches, but wall timing is slower and full contact
solver claims remain blocked.

The current interim status is
[V3 Current Status](v3_current_status_2026-06-20.md).

The current pod evidence report is
[V2.14 Versus V3 Rebuild Pod Evidence](v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md).

The current same-RT-hardware paired timing report is
[V2.14 vs Current V3 Same RT Hardware Paired Benchmark](v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md).

The current all-app serious OptiX-vs-Embree evidence is
[V3 Claim-Grade All-Benchmark Results](v3_claim_grade_all_benchmark_results_2026-06-20.md).
The current one-page user/reviewer performance map is
[Phoenix V3 User-Facing Performance Dossier](phoenix_v3_user_facing_performance_dossier_2026-06-22.md).

The required explanation for slow or negative OptiX rows is
[V3 Negative Route Explanations](v3_negative_route_explanations_2026-06-20.md).

The current setup/rerun guide is
[V3 Setup And Rerun Runbook](v3_setup_and_rerun_runbook_2026-06-20.md).

The current release blocker list is
[V3 Release Authorization Blockers](v3_release_authorization_blockers_2026-06-20.md).

## V3 Acceptance Bar

A rebuilt V3 is acceptable only when a serious new user can:

1. read the front page and understand exactly what RTDL solves;
2. run the first tutorial without reading history;
3. choose a supported backend or partner without guessing;
4. inspect which benchmark rows are M7-qualified row-scoped;
5. reproduce the evidence for any performance wording;
6. know when RTDL is the right tool and when it is not.

## Current Non-Claims

Until the rebuild gate passes, do not claim:

- V3 is finished;
- V3 has release authorization;
- V3 is faster than V2.x broadly;
- any grouped-sum row beyond
  `grouped_reduction_sum_scalar_broadcast_repeat100_262144` is M7-promoted;
- `grouped_reduction_sum_scalar_broadcast_repeat100_262144` authorizes V3
  release, whole-app RayDB speedup, or broad V3-over-V2 speedup;
- any AABB row beyond `aabb_candidate_stream_all_count_only_float32_32768` is
  M7-promoted;
- `aabb_candidate_stream_all_count_only_float32_32768` authorizes LibRTS
  paper/authors-code timing, full spatial-index acceleration, float64
  exact-geometry wording, V3 release, or broad V3-over-V2 speedup;
- `component_union_clustered3d_65536_524288_repeat5_row_scoped` authorizes
  RTDBSCAN paper reproduction, full DBSCAN acceleration, noisy or irregular
  dataset generalization, other hardware, V3 release, or broad V3-over-V2
  speedup;
- `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`
  authorizes full Hausdorff distance, witness materialization, X-HD
  reproduction, other thresholds, other sizes, other GPUs, V3 release, or broad
  V3-over-V2 speedup;
- `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
  authorizes full robot planning, exact solid collision, continuous collision,
  zero-copy, V3 release, broad V3-over-V2 speedup, or 5x end-to-end prepared
  setup speedup;
- every app in `examples/current/` is public-ready;
- old release packets are current documentation;
- any performance result without exact artifact paths.

## Required Gate

The V3 rebuild gate has five parts:

1. Documentation reset: no old release/tutorial track appears as current user
   guidance.
2. Design reconstruction: V3 user problem, contract, and benchmark rows are
   written down clearly.
3. Evidence run: V2.x versus V3 is measured on serious pod workloads, not toy
   examples.
4. Row classification: every benchmark/app row becomes
   `m7-qualified-row-scoped`,
   `needs-repair`, `internal-only`, or `removed`.
5. User rebuild: only M7-qualified row-scoped rows return to tutorials,
   examples, and public performance wording after aggregate release
   authorization.
6. Negative-row explanation: any row that appears to conflict with paper-style
   expectations must explain fixture size, timing scope, and paper-reproduction
   status before it appears in user-facing docs.

## Initial Evidence Commands

These are the starting candidates for the evidence gate. They may be refined
after the source tree and old V2.x baseline are inspected.

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --json
PYTHONPATH=src:. python scripts/run_test_matrix.py --group v3_rebuild
PYTHONPATH=src:. python scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --build-native
PYTHONPATH=src:. python scripts/goal2636_strengthen_benchmark_rows.py --tier standard --build-native
PYTHONPATH=src:. python scripts/rtdl_human_scale_rt_vs_embree_comparison.py
```

No command result is public by itself. The output must be attached to an
artifact directory, reviewed, and classified.

## 2026-06-20 Phoenix Pod Observations

Current pod:

- host: `213.173.108.14:11592`;
- GPU: NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, driver CUDA
  capability reported as `12.4`;
- OptiX SDK headers: `/workspace/vendor/optix-dev-8.0.0`;
- current and `v2.14` native Embree/OptiX libraries build successfully when
  `OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0` is set.

Repair-pass result:

- `goal2626_standard_all_rows`: 22 ok / 0 failed.
- `goal2636_standard_all_rows`: 28 ok / 0 failed.
- `goal3828_full_clean`: 10 pass / 0 fail.
- GPU Python environment gate: CuPy RawKernel, Torch CUDA tensor, and Numba
  CUDA JIT all pass.

Repair-pass artifacts:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058
```

Same-RT-hardware V2.14-vs-current-V3 paired artifact:

```text
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
```

This paired run produced the current direct answer: V3 is stronger on
runability and route health, but not broadly faster than V2.14 in same-row raw
timing. The same-metric timing geomean is 1.012x, with 10 rows faster by more
than 5%, 32 rows within +/-5%, and 4 rows slower by more than 5%.

All-app calibrated evidence:

```text
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620
```

This all-app run produced 40 ok rows, 0 failed rows, and 19 comparable
Embree-vs-OptiX ratios across all ten promoted benchmark apps. It is serious
candidate evidence, not release authorization.

Phoenix M5 topology evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620
```

This M5 run passed internal intake for RTDL same-contract topology rows and a
recovered RayJoin author-code comparison: 100,000-point PIP point-location after
rejecting 1 exact-row tie candidate, RayJoin author `query_exec` on the same PIP
files, and overlay active-count on the 512x512 CDB slice. It remains internal
evidence only: RayJoin author RT is faster than RTDL OptiX on the PIP row, and
all release/public claim flags remain false until M7 row review.

Phoenix M6 Barnes-Hut aggregate-frontier/vector evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620
```

This M6 run used partitioned 32,768 / 65,536 / 131,072-body reruns to avoid the
historical runner's raw-payload memory retention. Intake passed as internal
route-parity evidence. The fused Numba CUDA route was fastest on all three
current rerun scales; prepared RTDL/OptiX+Numba was 7.328x, 5.120x, and 13.912x
slower than the fastest route. This is not a Barnes-Hut RT-core speedup claim
and not release authorization.

Phoenix Barnes-Hut/vector-accumulation contract packet:

```text
docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md
```

This packet records Barnes-Hut vector accumulation as a future-research record,
not an active Phoenix V3 P0 build target. It records that the current prepared
frontier-emission shape is not the V3 win: the missing future capability is an
app-agnostic aggregate-tree fused weighted-vector primitive that writes
source-id keyed vector/count output columns directly. M129/M131/M142 now bound
the current decision: the Python wrapper exists, naive all-node OptiX is
semantically blocked by subtree-skip/no-double-counting requirements, and the
current route surface is closed as mixed explicit guidance. M7 rows added by
this packet: 0.

Phoenix AABB prepare-reuse serious RTX evidence:

```text
docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_serious_20260621
docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_65536_r50_20260621
docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_32768_r50_20260621
docs/rebuild/v3/evidence/phoenix_v3_aabb_prepare_reuse_query_cache_stats_65536_r50_20260621
docs/rebuild/v3/evidence/phoenix_v3_aabb_native_query_handle_32768_r50_20260621
docs/rebuild/v3/evidence/phoenix_v3_aabb_native_query_handle_65536_r50_20260621
```

The RTX 4000 Ada prepare-reuse runs used 32,768 and 65,536 indexed/query AABBs,
with 50 repeated queries for the generic `aabb_candidate_stream`
prepared-reuse contract. They passed backend execution, CPU-reference parity,
complete candidate coverage, reuse observation, and phase-table checks. They
are still not M7: OptiX/Embree cold-plus-collect wall speedup was 1.140x at
32,768 and 1.087x at 65,536, both below the predeclared 1.20
material-speedup floor. The overhead gate blocks this as an M7 route because
OptiX prepare is slower on both rows, query-only wording is forbidden, and
collect is not a material win. M7 rows added by these packets: 0.

The follow-up query-cache runs prove the Python query-record cache is operating
as intended, but still fail the material wall floor: 32,768 improves only to
1.188x and 65,536 to 1.135x cold-plus-collect wall. This is useful generic
cleanup, not a V3 performance promotion. M7 rows added by the query-cache
packet: 0.

The native query-handle follow-up is materially different: the OptiX
range-intersection row collector now reuses prepared native box-query handles.
The 32,768 row reaches 1.719x and the 65,536 row reaches 1.637x
OptiX/Embree cold-plus-collect wall speedup, both above the 1.20 material
floor, with native cache stats showing one miss and 52 hits. This reopens AABB
as an M7 candidate pending external review. It still adds zero M7 rows now:
external review is blocked, no 2-AI consensus is closed, and public/broad V3
speedup wording remains false.

Phoenix Spatial RayJoin topology-stream exact-executor evidence:

```text
docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_exact_executor_pod_evidence_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621
docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621
docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md
docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621
```

The RTX 4000 Ada public-county run used the generic
`point_location_topology_stream` exact prepared-points executor with prepared
point columns. It collected 5 samples with repeat=50 and warmup=5. The exact row
count stayed stable at 47,262, all M3 table/handle checks passed, and the
prepared handle reports
`device_resident_prepared_point_probe_columns_with_reusable_exact_executor`.
This is not M7 and not a public speedup claim: the same evidence shows the hot
path is dominated by topology continuation/exact refinement, and the
device-filtered route was rejected by correctness (`47,570 != 47,262`).

The later exact-f64 native scalar-count repair keeps correctness first while
removing the host topology-continuation bottleneck from prepared-query timing.
On the same public-county RTX packet, exact-f64 device scalar count stayed at
47,262 rows and changed median prepared query from `0.023218s` to `0.006309s`
(`3.680x`) versus the exact executor. Runner wall improved from `2.893971s` to
`1.974891s` (`1.465x`). This is meaningful generic-engine progress for the
`point_location_topology_stream`/native scalar-count route, but the review gate
keeps it review-blocked/not M7 because it still needs unblocked external AI
review, Codex consensus response, same-dataset author timing basis,
adverse-subset parity, and public wording review before any release claim.

RayDB grouped-reduction evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620
```

This RayDB M28 run produced a 524,288-row / 2,048-group same-contract
grouped-reduction artifact. Prepared hot-query OptiX was 8.752x faster than
Embree for count and 158.010x faster for sum, with CPU-reference parity and no
partner continuation required. The sum row also has 213s+ workload/build/cold
prepare costs, so these are hot-query internal ratios, not end-to-end
application speedups.

The earlier Numba, RayDB, and Spatial RayJoin current-side blockers were
repaired or converted into explicit setup gates. This does not authorize a V3
release. It authorizes the next step: rebuild the public V3 docs/tutorials from
the repaired artifacts only.

## Goal-Level Decision Audit

For every goal-level decision during the rebuild, the working agent must answer:

1. Did I make a foolish decision?
2. If yes, what actions made it foolish?
3. Was there another path that avoided getting stuck in that thinking?
4. Can I now try a different path that truly solves the problem?

The purpose is not ritual self-attack. The purpose is to force course
correction before old mistakes become new release wording.

## Current Work Queue

| Priority | Work | Done when |
| --- | --- | --- |
| P0 | Remove misleading current release/tutorial front doors | Searches show no old release/tutorial path promoted to users. |
| P0 | Reconstruct exact V3 design intent | A single design document defines user problem, contract, rows, and non-claims. |
| P0 | Locate V2.x baseline and current V3 routes | Commands and revisions are documented before benchmark execution. |
| P0 | Run serious pod comparisons | Artifacts include raw logs, environment, command lines, and summaries. |
| P0 | Classify every row | Each row is m7-qualified-row-scoped, needs-repair, internal-only, or removed. |
| P1 | Repair required V3 rows | Failed release-critical rows have code fixes and rerun evidence. |
| P1 | Republish user docs | README, tutorials, examples, and claim pages are rebuilt from passing rows only. |
