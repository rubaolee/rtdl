# Goal3902 Current Scale Packet With Payload Timing Summaries

## Purpose

Goal3902 reruns the promoted ten-app A5000 scale packet after Goal3901 added
generic payload timing extraction to the scale runner.

The main purpose is not another tuning round. The purpose is to make each app's
internal hot timings visible inside the scale packet, so process-wrapper time is
not confused with benchmark payload time.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- Fresh pod clone: `/root/goal3902_payload_timing_clean_1780901894`
- Artifact root on pod:
  `/root/goal3902_payload_timing_clean_1780901894_artifacts/goal3902_current_scale_with_payload_timing_a5000`
- Source commit: `1a3aaa86`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Local artifact:
  `docs/reports/goal3902_current_scale_with_payload_timing_a5000/summary.json`

The clean run wrote artifacts outside the fresh clone, so runtime provenance
stayed clean:

- `runtime_environment.working_tree_clean`: `true`
- `runtime_environment.git_status_short`: `[]`

## Result

- `exit_code`: `0`
- `all_pass`: `true`
- `json_pass_count`: `10`
- selected row count: `10`

| Row | Status | Process elapsed sec | Timing scalar count | Hot metric scope |
| --- | --- | ---: | ---: | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | `1.752` | `14` | n/a |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | `10.256` | `19` | `per_contract_hot_medians_not_wrapper_wall_time` |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `3.503` | `14` | n/a |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `1.580` | `0` | n/a |
| `contact_manifold_optix_scale_default_grid64` | pass | `1.002` | `2` | n/a |
| `raydb_style_optix_count_scale_default_262k` | pass | `2.002` | `7` | n/a |
| `barnes_hut_numba_scale_default_8192` | pass | `2.002` | `2` | n/a |
| `librts_spatial_index_optix_scale_default_32768` | pass | `2.002` | `6` | n/a |
| `rtnn_prepared_optix_scale_default_65536` | pass | `2.753` | `10` | n/a |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.252` | `4` | n/a |

The robot-collision payload remains valid JSON but does not currently expose
scalar keys with the standard timing suffixes, so its timing count is `0`.
That is useful evidence too: it identifies the next documentation/instrumentation
gap without inventing a timing.

## RayJoin Timing Clarity

The RayJoin row is the reason this timing summary matters. Its wrapper elapsed
time is about `9.021` seconds, while the representative hot-path metrics are
per-contract medians:

| Contract | Numba hot median sec | RTDL/OptiX hot median sec | RTDL/OptiX vs Numba | Recommendation |
| --- | ---: | ---: | ---: | --- |
| PIP one-shot | `0.000515` | `0.002186` | `0.236x` | Numba scalar count |
| LSI scalar count | `0.020649` | `0.000092` | `223.258x` | RTDL/OptiX prepared scalar count |
| Overlay active count | `0.048766` | `0.000195` | `249.906x` | RTDL/OptiX prepared active count |
| PIP repeated requests | `0.203378 ms/request` single | `0.023952 ms/request` batched | `8.491x` per request | RTDL/OptiX prepared batch |

The packet now records this scope directly as
`representative_hot_path_metric_scope =
per_contract_hot_medians_not_wrapper_wall_time` and sets
`scale_runner_elapsed_sec_is_not_hot_path_metric = true`.

## RT-DBSCAN Timing Clarity

The RT-DBSCAN row preserves the Goal3898 segmented-count signature path:

- `column_signature_strategy`: `numba_segmented_count_all_core_labels`
- `column_signature_uses_numba_segmented_count`: `true`
- `column_signature_materializes_point_ids`: `false`
- `column_signature_materializes_core_flags`: `false`

The app payload elapsed time is `0.079370` seconds, while the process wrapper
takes `3.503` seconds. The payload timing summary now exposes both the top-level
payload elapsed time and the internal host-observed timing scalars, including:

- `prepare_sec`: `1.048068`
- `adapter_run_sec`: `0.074041`
- `column_signature_sec`: `0.005328`

This reinforces the current measurement rule: process elapsed is pod-budget evidence; payload hot timing is the engineering signal.

## Boundary

Goal3902 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal current-scale packet with improved instrumentation, not a public performance comparison and not a release packet.
