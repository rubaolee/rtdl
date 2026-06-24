# Goal3894 Current Scale Profile With Runtime Provenance

## Purpose

Goal3894 reruns the ten-app A5000 scale-profile smoke after Goal3892 so the
artifact itself carries clean source/hardware provenance.

This supersedes Goal3888 for provenance quality: Goal3888 was a valid scale
smoke, but its source commit and GPU identity lived in the markdown report.
Goal3894 records them in `summary.json`.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- Fresh pod clone: `/root/rtdl_goal3894_runner_1780899518`
- Source commit: `506bdf3c`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Artifact:
  `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000/summary.json`

## Result

- `exit_code`: `0`
- `all_pass`: `true`
- `json_pass_count`: `10`
- selected row count: `10`
- selected prepared-session-profiled rows: `4`
- `runtime_environment.source_commit_short`: `506bdf3c`
- `runtime_environment.working_tree_clean`: `true`
- `runtime_environment.git_status_short`: `[]`
- `runtime_environment.nvidia_smi`: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`

| Row | Status | Elapsed sec | Prepared-session profiled |
| --- | --- | ---: | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.751 | true |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.757 | false |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.753 | false |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.752 | false |
| `contact_manifold_optix_scale_default_grid64` | pass | 1.002 | false |
| `raydb_style_optix_count_scale_default_262k` | pass | 2.252 | false |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 | false |
| `librts_spatial_index_optix_scale_default_32768` | pass | 1.753 | true |
| `rtnn_prepared_optix_scale_default_65536` | pass | 2.752 | true |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.252 | true |

## Interpretation

The current ten-app promoted scale runner still passes from a clean A5000 clone
after the prepared-session reuse idiom and runner-provenance changes. The
runtime provenance now proves the source commit, clean Git status, working
directory, Python runtime, RTDL library env, and A5000 GPU identity inside the
artifact.

## Boundary

Goal3894 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

It is a clean latest-commit A5000 scale smoke with runtime provenance. It is
not a public performance comparison and not a release packet.

## Validation

Added `tests/goal3894_current_scale_with_runtime_provenance_a5000_test.py`.

The test checks:

- exit code `0`;
- ten passing JSON rows;
- empty claim-flag violation lists;
- four prepared-session-profiled rows;
- clean runtime provenance fields;
- RTNN remains on the promoted `prepared_optix_ranked_summary` path;
- the report preserves the non-authorizing boundary.
