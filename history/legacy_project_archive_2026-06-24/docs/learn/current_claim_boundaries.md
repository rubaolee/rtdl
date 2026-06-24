# Current Claim Boundaries

Status: Phoenix V3 capability/quality claim boundary, updated 2026-06-24.

This page is the short source of truth for what may be said while V3 is being
completed as a capability/quality branch.

## Allowed Claims Now

RTDL may currently be described as:

- a Python-hosted RT-shaped DSL/runtime in the source tree;
- a project completing V3 from serious evidence as a capability/quality branch;
- a system with runnable development examples under `examples/current/`;
- a system with a productized prepared-execution/runtime trunk, while broad
  V3-over-V2 performance remains unproven;
- a system with a reviewed source-tree/pod-gated reproducibility path for the
  current thirteen-row surface under `source_tree_pod_gated_thirteen_row`
  scope;
- a system whose current release surface has thirteen exact
  row-scoped/supplemental rows, while release authorization still requires a
  separate capability-branch release review;
- a system whose current-side Phoenix V3 benchmark artifacts pass
  `goal2626`, `goal2636`, `goal3828`, and the GPU Python environment gate on
  the 2026-06-20 pod;
- a system whose old release/tutorial material is preserved for audit, not
  promoted to users.

The Phase A performance-source gate is closed:
[Phoenix V3 Phase A Performance-Source Consensus](../reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md).
It authorizes no release and no speed wording; it says V3 must proceed as a
capability/quality branch.

Current Phoenix row-scoped M7 qualifications may be described only with their
exact row names and blockers attached:

- `grouped_reduction_sum_scalar_broadcast_repeat100_262144`;
- `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`;
- `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`;
- `aabb_candidate_stream_all_count_only_float32_32768`;
- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`;
- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`;
- `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`;
- `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`;
- `component_union_clustered3d_65536_524288_repeat5_row_scoped`;
- `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`;
- `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`;
- `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`;
- `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`.

Three exact `aabb_candidate_stream` rows are M7-qualified; that does not make
full spatial-index acceleration, Contact Manifold solver acceleration, LibRTS
paper reproduction, float64 exact-geometry parity, OptiX-prepare-only speedup,
other hardware, or V2 comparison wording qualified.

One exact `component_union` row is M7-qualified; that does not make full
RTDBSCAN, full DBSCAN, noisy datasets, other hardware, or V2 comparison
wording qualified.

One exact `threshold_summary` row is M7-qualified; that does not make full
Hausdorff distance, witness materialization, X-HD paper reproduction, other
thresholds, other sizes, other GPUs, or V2 comparison wording qualified.

One exact `collision_flag_stream` row is M7-qualified; that does not make full
robot planning, exact solid collision, continuous collision, zero-copy, full
app end-to-end, or V2 comparison wording qualified.

One exact `ranked_summary` row is M7-qualified only for RTNN prepared repeat50
session amortization; that does not make one-shot nearest-neighbor search,
cold-start RTNN, whole RTNN, RTNN paper reproduction, other ANN baselines, other
scales, other precision modes, or V2 comparison wording qualified.

One exact `aggregate_frontier` row is M7-qualified only for Barnes-Hut-shaped
fused partner weighted-vector aggregation; that does not make full force
calculation, prepared OptiX superiority, automatic partner selection, other
scales, or V2 comparison wording qualified.

One bounded supplemental `point_location_topology_stream` row is in the current
release surface only for guarded squared-boundary Spatial topology-stream
status. That does not make RTDL beat RayJoin, full spatial join acceleration,
PIP acceleration, true zero-copy, other counties/samples, or V2 comparison
wording qualified.

These are not V3 release authorization, not whole-application speedup claims,
not paper-reproduction claims, and not broad V3-over-V2 claims.

## Blocked Claims Now

Do not claim any of the following until the Phase H capability/quality release
gate proves it:

- V3 has release authorization;
- V3 is finished or released;
- V3 is the highest-performance line;
- V3 beats V2.x broadly;
- all benchmark apps are release-authorized;
- the thirteen row-scoped/supplemental qualifications imply full-app acceleration or a
  complete V3 release surface;
- the current `source_tree_pod_gated_thirteen_row` installer/reproducibility
  closure authorizes release, package-install wording, hardware portability, or
  broad speedup claims;
- old tutorial tracks are current;
- old release reports are current user documentation;
- selecting a backend by itself proves acceleration;
- a benchmark row proves whole-application speedup;
- any performance sentence without exact command, hardware, baseline, and
  artifact path.

## Evidence Rule

Every future performance claim must name:

- the benchmark or primitive row;
- the V2.x baseline or other same-contract baseline;
- the V3 route;
- the backend and partner, if used;
- the hardware;
- the command line;
- the output contract;
- the reviewed artifact path;
- the row classification.

The current Phoenix evidence entry point is
[V2.14 Versus V3 Rebuild Pod Evidence](../rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md).

## Row Classification

Every row must be classified against the Phoenix M7 packet as one of:

- exact row-scoped M7-qualified;
- boundary lesson, not M7;
- internal evidence, not M7;
- negative route, not a speed claim.

Rows without serious pod evidence, row-level wording, and review are not
M7-qualified.

## Current Authority

- [V3 Rebuild Control](../rebuild/v3/README.md)
- [Phoenix V3 Capability Branch Status](../rebuild/v3/phoenix_v3_phase_h_capability_branch_status_2026-06-24.md)
- [Phoenix V3 Phase A Performance-Source Consensus](../reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md)
- [Phoenix V3 Readiness Distance Packet](../rebuild/v3/phoenix_v3_readiness_distance_packet_2026-06-22.md)
- [V3 Benchmark Evidence](../rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md)
- [Project Front Page](../../README.md)
- [Tutorials Status](../../tutorials/README.md)
- [Examples Status](../../examples/README.md)
- [Quarantined Old Release Surface](../history/quarantine_v3_v4_reset_2026-06-20/README.md)
