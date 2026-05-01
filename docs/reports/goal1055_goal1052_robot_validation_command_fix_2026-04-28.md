# Goal1055 Goal1052 Robot Validation Command Fix

Date: 2026-04-28

## Verdict

ACCEPT.

## Problem

Goal1052 correctly required the post-Goal1048 diagnostic reruns for
`facility_knn_assignment` and `robot_collision_screening` to remove
`--skip-validation`, but the generated robot command still used:

```text
--input-mode packed_arrays --result-mode pose_count
```

`scripts/goal760_optix_robot_pose_flags_phase_profiler.py` intentionally
rejects oracle validation for that compact performance mode. Sending that
command to the next paid RTX pod would fail after environment setup, wasting
cloud time.

## Fix

Goal1055 changes only the post-Goal1048 diagnostic robot rerun in
`scripts/goal1052_post_goal1048_cloud_batch_manifest.py`:

- Keeps `--skip-validation` removed.
- Switches robot diagnostic evidence to `--input-mode python_objects`.
- Switches robot diagnostic evidence to `--result-mode pose_flags`.
- Uses bounded validation scale: `--pose-count 4096`,
  `--obstacle-count 256`, `--iterations 3`.
- Regenerates Goal1052 JSON/Markdown and the Goal1053 shell/JSON runner.

The large packed-array `pose_count` path remains the performance-oriented mode,
but it is not used as a validation-enabled diagnostic rerun until the profiler
has a true oracle path for packed arrays.

## Consensus

- Gemini process guidance from Goals 1051-1054 requires one batched pod run,
  strict validation on diagnostic reruns, and no `--skip-validation` for the
  two blocked diagnostic rows.
- Codex identified and fixed the local command-validity gap before cloud
  execution: validation-enabled commands must be accepted by their target
  profiler before a paid pod is started.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal1052_post_goal1048_cloud_batch_manifest_test \
  tests.goal1053_post_goal1048_cloud_batch_runner_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal1051_post_goal1048_followup_plan_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal760_optix_robot_pose_flags_phase_profiler_test
```

Result: 35 tests, OK.

`git diff --check`: OK.

## Boundary

This is a local pod-preparation remediation. It does not run cloud, authorize
release, or authorize public RTX speedup wording.
