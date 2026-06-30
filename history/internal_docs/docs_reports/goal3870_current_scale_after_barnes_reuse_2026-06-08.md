# Goal3870 Current 10-App Scale Refresh After Barnes-Hut Output Reuse

Date: 2026-06-08

Status: A5000-validated current-scale refresh.

## Purpose

Goal3870 refreshes the current ten-benchmark scale-profile packet after
Goal3866 made RayJoin representative and Goal3869 added resident output-column
reuse to the Barnes-Hut no-RawKernel Numba force-summary path.

This is an internal scale packet only. It does not authorize release action,
public speedup wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording,
or app-specific native-engine logic.

## A5000 Evidence

Artifact:

`docs/reports/goal3870_current_scale_after_barnes_reuse_a5000/summary.json`

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`8b94659e`

GPU:

`NVIDIA RTX A5000, 580.126.09`

The runner used a fresh clean checkout. The artifact directory was added to the
pod clone's local `.git/info/exclude` before the run so child payloads did not
see the artifact directory as an untracked source change.

## Results

| App | Status | Elapsed sec | Row |
| --- | --- | ---: | --- |
| Hausdorff/X-HD | pass | 1.752 | `hausdorff_xhd_scale_default_optix_threshold` |
| Spatial RayJoin | pass | 10.006 | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` |
| RT-DBSCAN | pass | 3.503 | `rt_dbscan_optix_numba_scale_default_65536_no_validation` |
| Robot collision | pass | 1.542 | `robot_collision_optix_scale_default_1024_no_probe_reference` |
| Contact manifold | pass | 0.751 | `contact_manifold_optix_scale_default_grid64` |
| RayDB-style | pass | 2.002 | `raydb_style_optix_count_scale_default_262k` |
| Barnes-Hut | pass | 1.752 | `barnes_hut_numba_scale_default_8192` |
| LibRTS spatial index | pass | 2.002 | `librts_spatial_index_optix_scale_default_32768` |
| RTNN | pass | 2.753 | `rtnn_prepared_optix_scale_default_65536` |
| Triangle counting | pass | 1.502 | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` |

Summary:

- `all_pass: true`;
- `json_pass_count: 10`;
- claim-boundary violations: none;
- registry validation status: `accept`.

## Barnes-Hut Note

The Barnes-Hut row now records resident force-output reuse in its payload:

- `partner_metadata.output_columns_reused: true`;
- `partner_metadata.prepared_force_output_columns_reused: true`;
- median force-kernel/adapter timing: `0.008777748793363571` seconds.

The process-level row remains about `1.75` seconds because import, Numba setup,
body generation, and process startup dominate the file-backed scale-profile
command. Goal3869 is therefore a resident repeated-call improvement, not a
whole-app cold-process speedup claim.

In short: this is not a whole-app cold-process speedup claim.

## RayJoin Note

The RayJoin representative child payload has an empty `git_status_short` in
this packet. Its route remains:

- one-shot PIP: Numba CUDA JIT scalar count;
- repeated PIP: RTDL/OptiX prepared batch executor;
- LSI scalar count: RTDL/OptiX prepared segment-pair count;
- overlay active count: RTDL/OptiX prepared shape-pair active count.

This is not a RayJoin paper reproduction or universal PIP-dominance claim.

## Claim Boundary

Goal3870 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, AMD performance wording, paper-reproduction wording, or
app-specific native-engine logic.
