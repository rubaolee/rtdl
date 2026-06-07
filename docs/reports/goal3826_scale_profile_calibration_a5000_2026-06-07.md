# Goal3826 Scale-Profile Calibration On A5000

Date: 2026-06-07

Status: superseded by Goal3827 due probe-harness stdout backpressure.

## Purpose

Goal3823 and Goal3825 prove the current ten benchmark front doors execute and
keep their claim boundaries. Goal3826 asked a different question: which larger
profiles are reasonable candidates for future performance packets?

Important correction: the Goal3826 probe harness used
`Popen(..., stdout=PIPE)` and waited without draining stdout. Large JSON
outputs can fill the pipe and block the child process. Goal3827 reruns the
scale probe with stdout redirected to files and supersedes the timeout
interpretation here.

This is not a release packet and not a public speedup claim. Treat the raw
Goal3826 artifacts as harness-diagnosis evidence only.

## Artifacts

- `docs/reports/goal3826_scale_profile_candidate_a5000/summary.json`
- `docs/reports/goal3826_scale_profile_calibration_a5000/summary.json`
- `docs/reports/goal3826_barnes_hut_calibration_a5000/summary.json`

All runs used the A5000 pod at commit `b00286c5`.

Superseding corrected artifact:

`docs/reports/goal3827_scale_profile_file_stdout_a5000/summary.json`

## First Candidate Sweep

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `hausdorff_xhd_scale` | pass | 1.752 | safe but still too short for a long timing profile |
| `spatial_rayjoin_pip_count_repeat` | pass | 1.752 | safe but still too short for a long timing profile |
| `rt_dbscan_numba_65536` | timeout | 241.517 | validation-inclusive command; later Goal3830 shows the no-validation perf row passes |
| `robot_collision_4096` | timeout | 240.336 | superseded by Goal3827; file-stdout probe passes in 73.591s |
| `contact_manifold_grid64` | pass | 0.751 | safe but too short |
| `raydb_style_count_262k` | pass | 2.252 | safe medium profile candidate |
| `barnes_hut_numba_8192` | timeout | 300.350 | superseded by Goal3827; file-stdout probe passes in 2.002s |
| `librts_spatial_index_32768` | pass | 2.003 | safe medium profile candidate |
| `rtnn_prepared_optix_65536` | pass | 3.003 | safe medium profile candidate |
| `triangle_counting_native_2048` | pass | 1.752 | safe but still short |

## Calibration Follow-Up

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `rt_dbscan_numba_8192` | pass | 8.005 | good scale-profile candidate |
| `rt_dbscan_numba_16384` | pass | 23.262 | usable stress candidate |
| `rt_dbscan_numba_32768` | pass | 88.544 | heavy stress candidate, not default |
| `robot_collision_1024` | pass | 11.532 | good scale-profile candidate |
| `robot_collision_2048` | timeout | 180.394 | do not interpret; pipe backpressure made timeout rows unreliable |
| `barnes_hut_numba_2048` | timeout | 180.316 | do not interpret; pipe backpressure made timeout rows unreliable |
| `barnes_hut_numba_4096` | timeout | 240.322 | do not interpret; pipe backpressure made timeout rows unreliable |

## Barnes-Hut Ladder

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `barnes_hut_numba_1152` | timeout | 90.323 | do not interpret; later diagnosis identified stdout pipe backpressure |
| `barnes_hut_numba_1280` | timeout | 120.356 | do not interpret; later diagnosis identified stdout pipe backpressure |
| `barnes_hut_numba_1536` | timeout | 150.371 | do not interpret; later diagnosis identified stdout pipe backpressure |

## Interpretation

Goal3826 originally appeared to show three heavy failures. Goal3827 corrects
that interpretation:

- RT-DBSCAN 65k timed out only for the validation-inclusive command; later
  Goal3830 shows the no-validation performance row passes on A5000.
- Robot 4096 passes in the corrected file-stdout harness, but takes 73.591s.
- Barnes-Hut 8192 passes in the corrected file-stdout harness in 2.002s and
  writes about 893 KB of JSON; the earlier timeout was harness backpressure.

The still-useful calibration points are:

- RT-DBSCAN: use a separate small correctness row for CPU reference validation
  and a no-validation performance row for large scale; the 65k no-validation
  row is a viable scale profile after Goal3830.
- Robot collision: `1024` poses originally mixed CPU probe-reference validation
  with prepared OptiX timing; Goal3831 separates the large performance row with
  `--no-probe-reference`. Goal3827 shows `4096` poses is a heavy stress profile
  rather than a timeout.
- Barnes-Hut: `8192` bodies is safe when stdout is redirected to a file.

## Next Engineering Target

Use Goal3827's file-stdout harness for future scale-profile work. Do not use
undrained stdout pipes for benchmark apps that can emit large JSON payloads.

## Boundary

Goal3826 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a calibration packet for future scale-profile work.
