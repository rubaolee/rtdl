# Goal3980: Current Scale Hot-Path Metric Contract

Date: 2026-06-08

## Purpose

Goal3978 showed the current scale-profile packet is reproducible, but Goal3979
showed that two short rows cannot be made claim-grade by blindly increasing
repeat counts. The scale runner's wrapper elapsed time is useful pod-budget
evidence, but it is not always the hot-path performance metric.

Goal3980 makes that boundary machine-readable in
`src/rtdsl/current_benchmark_scale_profiles.py`.

## Change

Each current scale-profile row now records:

- `timing_metric_scope`:
  `wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric`
- `representative_hot_path_metric`
- `hot_path_duration_target_sec`
- `scale_calibration_status`

The validator fails closed if a row tries to use wrapper elapsed as a hot-path
claim scope, omits a representative hot-path metric, or sets an invalid target.

The two rows from the Goal3979 negative calibration probe are explicitly
marked:

- `robot_collision_optix_scale_default_1024_no_probe_reference`:
  `short_row_repeat_calibration_rejected_goal3979`
- `raydb_style_optix_count_scale_default_262k`:
  `short_row_repeat_calibration_rejected_goal3979`

## Interpretation

This does not change any benchmark app and does not change the scale-profile
commands. It changes the metadata contract so future reports and reviewers know
how to read the timings:

- wrapper elapsed is pod-budget and orchestration evidence;
- payload/app phase timing is the engineering signal for hot-path performance;
- short rows need either data-size/batch scaling or a specific hot-path target,
  not repeat-count inflation.

## Boundary

This is an internal benchmark-metadata hardening step. It does not authorize
release, public-speedup wording, whole-app acceleration wording, broad RT-core
wording, true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
