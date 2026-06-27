# Goal3899 Current Scale After RT-DBSCAN Signature Optimization

## Purpose

Goal3899 reruns the full ten-app A5000 scale-profile packet after Goal3898's
RT-DBSCAN Numba segmented-count signature path.

The goal is to verify that the promoted ten-app scale runner still passes and
that the current RT-DBSCAN row now carries the faster app payload strategy.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- Fresh pod clone: `/root/rtdl_goal3899_scale_after_rtdbscan_1780901208`
- Source commit: `84c860a3`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Artifact:
  `docs/reports/goal3899_current_scale_after_rt_dbscan_signature_a5000/summary.json`

The runner captured runtime provenance before creating the output directory:

- `runtime_environment.working_tree_clean`: `true`
- `runtime_environment.git_status_short`: `[]`

## Result

- `exit_code`: `0`
- `all_pass`: `true`
- `json_pass_count`: `10`
- selected row count: `10`

| Row | Status | Process elapsed sec |
| --- | --- | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | `2.002` |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | `11.008` |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `3.753` |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `1.752` |
| `contact_manifold_optix_scale_default_grid64` | pass | `0.752` |
| `raydb_style_optix_count_scale_default_262k` | pass | `2.252` |
| `barnes_hut_numba_scale_default_8192` | pass | `2.002` |
| `librts_spatial_index_optix_scale_default_32768` | pass | `2.003` |
| `rtnn_prepared_optix_scale_default_65536` | pass | `2.753` |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.502` |

## RT-DBSCAN Delta

The full packet's RT-DBSCAN process elapsed remains about `3.753` seconds,
which is dominated by Python process startup, imports, setup, and Numba/OptiX
context effects. The meaningful app payload timing improved:

| Metric | Goal3894 clean packet | Goal3899 packet | Ratio |
| --- | ---: | ---: | ---: |
| RT-DBSCAN payload elapsed sec | `0.115497` | `0.080346` | `1.437x` faster |
| RT-DBSCAN column-signature sec | `0.041711` | `0.007145` | `5.838x` faster |

The Goal3899 RT-DBSCAN payload records:

- `column_signature_strategy`: `numba_segmented_count_all_core_labels`
- `column_signature_uses_numba_segmented_count`: `true`
- `column_signature_materializes_point_ids`: `false`
- `column_signature_materializes_core_flags`: `false`

## Interpretation

Goal3899 confirms the current promoted scale packet remains green after a real
RT-DBSCAN app-continuation improvement. It also reinforces a measurement rule:
the scale-runner process elapsed is pod-budget evidence, while each benchmark
payload's internal hot timing is the better engineering signal.

## Boundary

Goal3899 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal current-scale refresh after Goal3898, not a public
performance comparison and not a release packet.

It is not a public performance comparison.
