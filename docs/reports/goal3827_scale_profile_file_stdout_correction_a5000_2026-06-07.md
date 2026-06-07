# Goal3827 Scale-Profile File-Stdout Correction On A5000

Date: 2026-06-07

Status: implemented locally.

## Purpose

Goal3827 corrects the Goal3826 scale-profile interpretation. The Goal3826
manual probe used `Popen(..., stdout=PIPE)` and waited without draining stdout.
That can block any app that emits a large JSON payload. Barnes-Hut and robot
collision were false negatives under that harness.
Barnes-Hut and robot collision were false negatives under the undrained-pipe
probe, not app-level failures.

Goal3827 reruns the ten larger candidates with
stdout and stderr redirected to files, while still printing 30-second heartbeat
progress lines.

## Artifact

`docs/reports/goal3827_scale_profile_file_stdout_a5000/summary.json`

## Corrected Result

| Candidate | Status | Elapsed seconds | JSON bytes | Reading |
| --- | --- | ---: | ---: | --- |
| `hausdorff_xhd_scale` | pass | 1.752 | 4009 | safe but still short |
| `spatial_rayjoin_pip_count_repeat` | pass | 1.502 | 3152 | safe but still short |
| `rt_dbscan_numba_65536` | timeout | 300.145 | 0 | validation-inclusive command; later Goal3830 no-validation row passes |
| `robot_collision_4096` | pass | 73.591 | 139902 | heavy but valid stress profile |
| `contact_manifold_grid64` | pass | 0.752 | 7671 | safe but short |
| `raydb_style_count_262k` | pass | 2.252 | 40921 | safe medium profile |
| `barnes_hut_numba_8192` | pass | 2.002 | 893215 | safe when stdout is file-backed |
| `librts_spatial_index_32768` | pass | 1.752 | 1848 | safe medium profile |
| `rtnn_prepared_optix_65536` | pass | 2.753 | 4807 | safe medium profile |
| `triangle_counting_native_2048` | pass | 1.753 | 2257 | safe but short |

## Interpretation

Nine of ten larger candidates pass under the corrected file-stdout harness.
The only remaining timeout in this artifact is RT-DBSCAN at 65k points, but
that command still included CPU reference validation. Goal3830 later shows the
same 65k performance row passes when validation is explicitly separated.
Earlier Barnes-Hut and robot timeouts were harness artifacts caused by large
stdout JSON payloads.

This changes the next engineering target:

- Do not treat Barnes-Hut Numba exact-force as a P0 scalability bug based on
  Goal3826.
- Use file-backed stdout, `subprocess.run(..., capture_output=True)`, or active
  pipe draining for future benchmark probes.
- For scale-profile defaults, use calibrated rows rather than validation-heavy
  commands: RT-DBSCAN 65k with `--no-validation` plus a separate small
  correctness row, robot 1024 for default and 4096 for stress, Barnes-Hut 8192
  with file-backed stdout.

## Boundary

Goal3827 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a corrected probe-methodology and scale-calibration packet.
