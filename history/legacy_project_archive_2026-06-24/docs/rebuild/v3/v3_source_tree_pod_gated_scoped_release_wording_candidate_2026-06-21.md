# V3 Source-Tree / Pod-Gated Scoped Release Wording Candidate

Status: `source_tree_pod_gated_scoped_release_wording_reviewed_not_release`

Path:
`docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`

This packet proposes a narrow release-scope wording path for Phoenix V3. It is
not release authorization. It is a candidate for external review of one
question: can the current reviewed source-tree/pod-gated reproducibility path
close the installer/reproducibility blocker if V3 is explicitly scoped as a
source-tree/pod-gated, row-scoped evidence release rather than a general
package-install release?

## Candidate Scope

Candidate product scope:

```text
source_tree_pod_gated_twelve_row
```

Candidate status fields:

```text
release_authorized: false
release_scope: source_tree_pod_gated_twelve_row
general_release_installer_ready: false
package_install_claim_authorized: false
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
secondary_rt_performance_confirmation_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The only pre-existing blocker field this 2-AI review changes is:

```text
installer_closes_release_blocker: false -> true
```

under the exact `source_tree_pod_gated_twelve_row` scope. This candidate does
not change `release_authorized`, `general_release_installer_ready`,
`package_install_claim_authorized`, secondary-RT confirmation, broad V3-over-V2
speedup, or final release readiness.

## Required Gate Script Changes

After Claude review and Codex consensus, Codex must apply exactly these changes
to `scripts/v3_phoenix_install_reproducibility_gate.py`:

- change `"installer_closes_release_blocker": False` to `True`;
- add `"installer_closes_release_blocker_scope": "source_tree_pod_gated_twelve_row"`;
- add `"release_scope": "source_tree_pod_gated_twelve_row"`;
- add `"source_tree_pod_gated_scoped_release_wording_reviewed": True`;
- keep `"release_authorized": False` unchanged;
- keep `"general_release_installer_ready": False` unchanged;
- keep `"package_install_claim_authorized": False` unchanged;
- keep the gate status
  `staged_pod_gate_present_general_release_installer_not_ready` unchanged;
- update `required_next_action` to:

```text
Obtain a new aggregate release-readiness external review that covers the scoped
installer closure and the reviewed single-RTX hardware waiver.
```

No other install-gate fields may change in this update pass.

After this scoped wording is accepted and the later aggregate release-readiness
review is recorded, the current open release blockers are:

1. `release_authorization_false`;
2. `twelve_row_surface_still_too_narrow_for_major_release`;
3. `missing_point_location_topology_stream_m7_capability_family`;
4. `twelve_row_release_readiness_consensus_blocks_release`.

Broad V3-over-V2 speedup remains a forbidden claim constraint, not a separate
scoped-release P0, while
`broad_v3_faster_than_v2_claim_authorized: false` stays false. These remain
unaffected by scoped installer closure.

## Allowed Wording If Accepted

If external review and Codex consensus accept this scoped wording, V3 may say:

```text
Phoenix V3 has a reviewed source-tree/pod-gated reproducibility path for its
current twelve exact row-scoped M7-qualified evidence rows on the documented
RTX 4000 Ada pod environment.
```

It may also say:

```text
The current V3 evidence can be rerun from the source tree using the documented
native Embree/OptiX build steps, staged Python GPU package set, Numba CUDA
toolchain exports, and Phoenix V3 gates.
```

It must still attach these boundaries:

```text
This is not a general package installer.
This does not authorize package-install wording.
This is source-tree/pod-gated evidence from a single RTX 4000 Ada pod.
This does not confirm performance across RT-core hardware classes.
This does not authorize broad V3-over-V2 speedup wording.
This does not confirm performance across RT-core hardware.
This does not authorize whole-app, paper-reproduction, or unscoped benchmark
speedup claims.
This does not by itself authorize V3 release.
```

## Forbidden Wording

Do not say:

```text
V3 is release-ready.
V3 is finished.
V3 has a general installer.
pip install rtdl gives a finished V3 GPU release.
V3 performance is confirmed across RT-core hardware.
Broad V3-over-V2 speedup is authorized.
All benchmark apps are release-ready.
The eleven M7 rows imply full-app acceleration.
```

## Current Twelve M7 Rows

The scoped wording applies only to these exact row IDs:

1. `grouped_reduction_sum_scalar_broadcast_repeat100_262144`
2. `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
3. `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`
4. `aabb_candidate_stream_all_count_only_float32_32768`
5. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
6. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`
7. `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
8. `component_union_clustered3d_65536_524288_repeat5_row_scoped`
9. `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`
10. `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`
11. `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
12. `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`

## Required Reproducibility Basis

The scoped wording depends on these already-reviewed artifacts:

- `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_2ai_consensus_2026-06-21.md`
- `scripts/v3_install_gpu_pod_env.sh`
- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`

The current install reproducibility gate reports:

```text
status: staged_pod_gate_present_general_release_installer_not_ready
staged_gpu_pod_gate_available: true
release_scope: source_tree_pod_gated_twelve_row
source_tree_pod_gated_candidate_present: true
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
general_release_installer_ready: false
package_install_claim_authorized: false
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
release_authorized: false
```

## Review Question

This candidate asks a narrow release-scope question:

```text
Phoenix V3 closes the installer/reproducibility blocker only under the exact
source_tree_pod_gated_twelve_row scope, while keeping all general installer,
package-install, release authorization, secondary-RT confirmation,
multi-GPU portability, and broad speedup fields false.
```

This is the accepted scoped closure path. The next path is aggregate
release-readiness review that covers the scoped installer closure and the
reviewed single-RTX hardware waiver.

## Goal-Level Decision Audit

Decision: accept scoped release-wording review for installer-blocker closure
under `source_tree_pod_gated_twelve_row`, without authorizing release.

1. Was I foolish?
   No. The install gate's required next action explicitly offered this path,
   Claude accepted it with P0 amendments, and this packet keeps every
   release-authorizing field false.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to close the installer blocker
   without a machine-readable scope or to let scoped closure imply release.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Build a general package installer first. That remains a future path if
   Phoenix later wants package-install release wording.
4. Can I now try a different path that actually solves the problem?
   Yes. Request a new aggregate release-readiness review that covers the scoped
   installer closure and the reviewed single-RTX hardware waiver.
