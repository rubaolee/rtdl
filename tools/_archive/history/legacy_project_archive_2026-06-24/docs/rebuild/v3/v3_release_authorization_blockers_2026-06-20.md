# V3 Release Authorization Blockers

Status: Phoenix V3 capability/quality pre-release review blocker ledger, updated
2026-06-24.

This file records what blocks Phoenix V3 publication after the Phase A fork.
The high-performance V3 path did not prove its performance source and remains
blocked. The active V3 completion path is now the Phase H capability/quality
branch: Python-hosted RTDL, productized prepared execution, exact row-scoped
evidence, clean docs/tutorials, and no broad V3-over-V2 speed claim.

Historical high-performance branch rule, preserved so scanners and reviewers do
not forget the failed claim boundary:

V3 major release requires broad V2.x performance superiority.

```text
capability_release_status: pending_release_owner_authorization
high_performance_release_status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - release_owner_authorization_not_obtained
  - high_performance_branch_broad_v2x_performance_not_proven
resolved_reasons:
  - capability_branch_external_review_obtained_claude_and_antigravity
blocked_high_performance_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
```

## Current Open P0 Blockers

| Blocker | Why it matters | Done when |
| --- | --- | --- |
| Release owner authorization is not obtained | Local gates and external AI reviews do not themselves publish V3. | The release owner explicitly authorizes the final capability/quality wording. |
| Broad V2.x performance superiority is not proven for the high-performance branch | The same-RT-hardware evidence says the same-row geomean is only `1.012x`; Phase A re-runs did not find a scorecard-moving runtime performance source. | This is not a blocker for the capability/quality branch, but it permanently blocks high-performance, broad V3-over-V2, and all-app speedup wording for this V3. |

## Resolved Phase H/G Review Gate

Claude and Antigravity both reviewed the Phase H/G capability/quality candidate
and returned `accept_phase_h_g_capability_release_ready`:

```text
docs/reviews/claude_phoenix_v3_phase_h_g_capability_completion_candidate_amendment_review_2026-06-24.md
docs/reviews/antigravity_phoenix_v3_phase_h_g_capability_completion_candidate_review_2026-06-24.md
```

These reviews allow the packet to be forwarded to the release owner. They do not
authorize public release, public speedup wording, all-app victory, V4,
embedding, C ABI, external zero-copy, or package-install claims.

## Current Scoped Surface

The current surface has thirteen exact M7-qualified/supplemental row-scoped claims:

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

Rows outside this list remain internal, blocked, no-go, historical, or future
work unless a focused evidence packet and review promotes them.

## Closed, Scoped, Or Non-Claim Items

These items are not the current open release blocker, but their boundaries must
remain visible.

| Item | Current state | Boundary |
| --- | --- | --- |
| Historical repair-pass P0 findings | Superseded by focused Phoenix V3 gates, the 13-row surface integrity manifest, and the current completion audit. | Do not use old smaller-surface reviews as release authorization. |
| Public docs and tutorials | Current docs have been reset; old V3/V4 user-facing material is quarantined; the public documentation map and tutorial README provide a short safe learner path. | This is local user-surface cleanup, not release authorization. |
| Final public-surface wording gate is complete but still does not authorize speed claims | `final_public_surface_gate: true`; `final_public_surface_claim_boundary_gate`; wording gate scans the current front-door/docs/tutorial/evidence surface and passes. | Keep `release_authorized: false` and `public_speedup_claim_authorized: false` until the major performance gate passes. |
| General release installer is not packaged, but scoped installer blocker is closed | `staged_pod_gate_present_general_release_installer_not_ready`; `release_scope: source_tree_pod_gated_thirteen_row`; `installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row`; `--accept-experimental-pod-gate` remains required. | The staged script is not a general release installer and does not authorize package-install wording. |
| Current 13-row installer scope extension is reviewed | `source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true`; `aggregate_13_row_installer_scope_review_required: false`. | This closes only the source-tree/pod-gated thirteen-row installer scope. |
| Secondary RT hardware scope waiver is reviewed | `secondary_rt_hardware_scope_waiver_reviewed: true`; `secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod`; `compatibility_confirmed_hardware_scope_waiver_reviewed_not_release`. | No broad hardware portability or secondary-RT performance confirmation is authorized. |
| Negative and mixed rows are explained | `docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md` explains the tiny `spatial_rayjoin` `0.034x` row and `librts_spatial_index` `0.065x` row as route-health / non-paper-equivalent rows. | These rows are not public OptiX speedup claims. |
| Broad V3-over-V2 speedup remains forbidden claim wording | Same-RT-hardware paired timing reports same-metric geomean `1.012x`; `broad_v3_faster_than_v2_claim_authorized: false`. | Do not publish broad V3-over-V2 speedup wording without a later explicit evidence packet and review. |
| Generic engine work queue is closed for this scoped release | `generic_engine_work_queue_closed_not_release`; `existing_evidence_promotable_now: false`. | Closing the queue does not authorize public Spatial speedup, true zero-copy, or broad V3-over-V2 wording. |
| Phoenix M7 scoped surface has thirteen rows but is not V3 major release authorization | The surface breadth gate records 13 rows, 9 / 9 capability families, no missing capability families, and machine-checked row integrity. | Keep the rows as internal evidence for the redo; do not call them V3 release authorization. |
| System Python packaging gap | The source-tree/pod-gated scope uses the rebuild environment and staged setup path. | No general package-install claim is authorized. |

## Row-Family Boundaries

| Family | Current public-surface state | Forbidden expansions |
| --- | --- | --- |
| Grouped reduction | Three exact grouped-sum rows are M7-qualified. | Count rows, whole-app RayDB, true zero-copy, pure backend-only Embree/device-column ratios, and broad V3-over-V2 claims. |
| AABB candidate stream | Three exact AABB rows are M7-qualified. | LibRTS paper reproduction, authors-code comparison, full spatial-index acceleration, float64 exact-geometry parity, Contact Manifold solver acceleration, and other AABB rows. |
| RTDBSCAN | One exact `component_union` row is M7-qualified. | RTDBSCAN paper reproduction, full DBSCAN acceleration, noisy/irregular dataset generalization, other hardware, full-app speedup, and broad V3-over-V2 claims. |
| Spatial RayJoin | One bounded supplemental `point_location_topology_stream` row closes the capability-family breadth gap. | Public Spatial RayJoin speedup, RTDL-beats-RayJoin wording, true zero-copy, or whole Spatial claims. |
| Triangle | One exact `prepared_graph_chunk` row is M7-qualified. | RT-Graph paper reproduction, graph-database acceleration, full Triangle app speedup, M113 graph-capture readiness, and automatic partner selection. |
| RTNN | One exact repeat50 prepared-session `ranked_summary` row is M7-qualified. | Whole-RTNN acceleration, one-shot or cold-start speedup, paper-equivalent nearest neighbor claims, and other scales/baselines. |
| Barnes-Hut | One exact Numba CUDA fused-partner aggregate-tree vector row is M7-qualified. | Barnes-Hut RT-core speedup, whole Barnes-Hut acceleration, paper reproduction, and automatic backend selection. |
| Hausdorff | One exact threshold-summary row is M7-qualified. | Full Hausdorff distance, witness materialization, X-HD reproduction, other thresholds/sizes/GPUs, and full-app speedup. |
| Robot Collision | One exact collision flag-stream row is M7-qualified. | Full robot planning, exact solid collision, continuous collision, zero-copy, and 5x end-to-end prepared setup speedup. |
| Contact Manifold | Scoped broadphase lesson only; no M7 row. | Full contact solver, physics, wall-speedup, broad V3-over-V2, and larger overflow claims. |

## Evidence And Gates

Current proof surface and gate history:

```text
docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_release_completion_audit_2026-06-22.md
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json
docs/reviews/call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md
```

Historical scoped-surface validation before Phase H/G:

```text
focused current-surface suite: 27 tests OK
full v3_rebuild matrix: 106 modules / 509 tests OK
wording gate: pass
readiness gate: redo_required
```

Current Phase H/G validation:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_major_performance_mandate_gate_test tests.v3_rebuild_reset_test tests.goal4278_source_tree_doctor_test
19 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
final_public_surface_gate: true
violations: []

py -3 scripts/rtdl_source_tree_doctor.py --json --run-smoke
ok: true
status: v3_capability_branch_ready
required_failures: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 148
tests: 754
status: OK
```

The matrix count increased from the earlier 106 modules / 509 tests because the
Phoenix rebuild line added Phase H/G front-door, source-tree-doctor, capability
branch, and later Phoenix V3 route/gate tests. The current authoritative local
matrix result is 148 modules / 754 tests OK.

## Current Release Authorization

```text
release_authorized: false
capability_release_authorized: false
high_performance_release_authorized: false
external_phase_h_g_review_obtained: true
release_owner_authorization_required: true
```

The correct next action is not another all-app performance run. The correct
next action is release-owner decision on the externally reviewed
capability/quality candidate.

## Goal-Level Decision Audit

Decision: rewrite the blocker list so the failed high-performance mandate no
longer prevents an honest capability/quality V3, while still blocking every
performance claim that the evidence did not earn.

1. Was I foolish? Yes.
2. If yes, what actions made it foolish? I treated the only acceptable V3 shape
   as a high-performance release after Phase A already falsified that route,
   which would keep V3 blocked forever or tempt us to fake a number.
3. Was there another path? Yes. Keep the high-performance branch blocked, but
   complete V3 honestly as a capability/quality branch with strict claim
   boundaries and external review.
4. Can I now try a different path? Yes. Finish Phase H/G, preserve the
   high-performance no-go, and ask external reviewers to judge the capability
   branch directly.


