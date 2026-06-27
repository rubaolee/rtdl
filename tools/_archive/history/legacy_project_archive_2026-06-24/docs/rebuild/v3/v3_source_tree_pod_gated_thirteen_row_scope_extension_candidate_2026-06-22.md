# V3 Source-Tree / Pod-Gated Thirteen-Row Scope Extension Candidate

Status: `source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release`

This packet prepares a narrow installer/reproducibility scope-extension review
for Phoenix V3. It does not authorize release, package-install wording, broad
hardware portability, broad V3-over-V2 speedup, or public unscoped benchmark
claims.

## Why This Exists

The current Phoenix V3 release surface has 13 exact M7/supplemental row-scoped
evidence rows across all 9 planned capability families.

The current installer/reproducibility closure is narrower:

```text
release_scope: source_tree_pod_gated_twelve_row
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
```

That scope must not be silently broadened. This candidate asks whether the
already-reviewed source-tree/pod-gated reproducibility path can be extended to
the current 13-row surface after adding the reviewed Spatial supplemental row.

## Proposed Scope

Candidate scope:

```text
source_tree_pod_gated_thirteen_row
```

Candidate status if accepted by external review and Codex consensus:

```text
release_authorized: false
release_scope: source_tree_pod_gated_thirteen_row
general_release_installer_ready: false
package_install_claim_authorized: false
source_tree_pod_gated_candidate_reviewed: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
secondary_rt_performance_confirmation_authorized: false
multi_gpu_performance_portability_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Until that review exists, the current accepted scope remains:

```text
source_tree_pod_gated_twelve_row
```

## Required Gate Script Delta If Accepted

If and only if a fresh external review plus Codex consensus accepts this
extension, update `scripts/v3_phoenix_install_reproducibility_gate.py` as
follows:

- change `SCOPED_RELEASE_SCOPE` from `source_tree_pod_gated_twelve_row` to
  `source_tree_pod_gated_thirteen_row`;
- add `source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true` to
  the payload;
- keep `installer_closes_release_blocker: true`;
- keep `release_authorized: false`;
- keep `general_release_installer_ready: false`;
- keep `package_install_claim_authorized: false`;
- keep the gate status
  `staged_pod_gate_present_general_release_installer_not_ready`;
- keep the explicit `--accept-experimental-pod-gate` requirement;
- keep the wording that this is not a general release installer.
- set `aggregate_13_row_installer_scope_review_required` to false.

No package-install, release-ready, broad-speedup, second-hardware, or whole-app
claim may change in this update.

## Current Thirteen Rows

This scope extension would apply only to these exact current rows:

1. `grouped_reduction_sum_scalar_broadcast_repeat100_262144`
2. `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
3. `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`
4. `aabb_candidate_stream_all_count_only_float32_32768`
5. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
6. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`
7. `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
8. `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`
9. `component_union_clustered3d_65536_524288_repeat5_row_scoped`
10. `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`
11. `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`
12. `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`
13. `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`

## Increment Since Twelve-Row Scope

The only row added after the twelve-row source-tree/pod-gated closure is:

```text
point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7
```

It is a bounded Spatial supplemental row for:

```text
point_location_topology_stream
```

It does not authorize public Spatial speedup, RTDL-beats-RayJoin, whole Spatial
RayJoin, true zero-copy, package-install readiness, or release readiness.

The Spatial POD evidence carries a `git_commit: null` provenance gap because
the remote source copy was not a git checkout. This is acceptable for this
source-tree/pod-gated installer scope extension because the Spatial packet
records the local native source SHA and the built OptiX library SHA. It does not
close the future requirement for a versioned git-tagged public release artifact.

## Install-Script Coverage Confirmation

`v3_install_gpu_pod_env.sh` covers the Spatial
`point_location_topology_stream` default-path configuration without
modification.

All Python packages required by the Spatial default-path route are already
covered by the existing twelve-row install path:

- standard-library modules from the runner and packet scripts;
- source-tree imports under `src/rtdsl` and `examples`;
- the existing native OptiX runtime loaded through `RTDL_OPTIX_LIBRARY` /
  `RTDL_OPTIX_LIB`;
- the already-pinned CuPy/Numba/CUDA-wheel set used by the staged pod gate.

No new package pins, build steps, or environment variables are required for the
Spatial row beyond the existing runbook's native build and runtime variables.
The default-path POD command was captured in an environment consistent with the
install-script-configured pod:

```text
PYTHONPATH=src:.
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
python3 scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py
```

The `git_commit: null` provenance gap from the Spatial promotion review does
not affect install-path coverage because the scope is explicitly source-tree /
pod-gated and the Spatial packet records both the local native source SHA and
the pod-built OptiX library SHA. It remains insufficient for a general public
release artifact.

## Required Existing Basis

The extension depends on these already-reviewed or current artifacts:

- `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`
- `docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `scripts/v3_install_gpu_pod_env.sh`
- `scripts/v3_phoenix_install_reproducibility_gate.py`

## Review Question

Please decide one narrow question:

```text
Can the reviewed source-tree/pod-gated reproducibility closure be extended from
source_tree_pod_gated_twelve_row to source_tree_pod_gated_thirteen_row for the
current 13 exact row-scoped/supplemental Phoenix V3 evidence surface?
```

If yes, state the exact allowed machine-field changes and all fields that must
remain false.

If no, identify the required fix: stronger scoped wording, a fresh pod rerun
bundle, a general installer, or another evidence artifact.

## Forbidden Wording

Do not say:

```text
V3 is release-ready.
V3 is finished.
V3 has a general package installer.
pip install rtdl gives a finished V3 GPU release.
V3 performance is confirmed across RT-core hardware.
V3 broadly beats V2.x.
All benchmark apps are release-ready.
The 13 rows imply full-app acceleration.
The Spatial row means RTDL beats RayJoin.
The Spatial row proves true zero-copy.
```

## Goal-Level Decision Audit

Decision: prepare a non-release 13-row installer/reproducibility scope-extension
candidate, without changing the accepted machine scope yet.

1. Was I foolish?
   No. The current installer closure is still scoped to twelve rows, so the
   responsible move is to ask for an explicit 13-row scope-extension review
   instead of silently broadening the scope.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be changing the install gate from
   `source_tree_pod_gated_twelve_row` to `source_tree_pod_gated_thirteen_row`
   without external review and consensus.
3. Was there another path that would have avoided being stuck on this idea?
   Yes. Build a general package installer first. That remains a future path,
   but it is larger than the current source-tree/pod-gated release surface.
4. Can I now try a different path that actually solves the problem?
   Yes. Send this packet to Claude after quota reset; if accepted, update the
   install gate to a reviewed thirteen-row source-tree/pod-gated scope while
   keeping release authorization false until aggregate release-readiness review.
