# Goal 769: RTX Pod One-Shot Runner

Date: 2026-04-23

## Purpose

The user requirement is to avoid repeatedly restarting or stopping the paid RTX pod for small isolated runs. Goal 769 adds a one-shot pod runner so the next cloud session can execute a larger validation batch in one pass.

## Runner

New script:

```text
/Users/rl2025/rtdl_python_only/scripts/goal769_rtx_pod_one_shot.py
```

Default behavior on the pod:

1. Fetch and check out `origin/codex/rtx-cloud-run-2026-04-22`.
2. Ensure driver-compatible OptiX development headers are available, defaulting to NVIDIA `optix-dev` tag `v9.0.0`.
3. Run Goal 763 bootstrap: build `librtdl_optix.so` and run focused native OptiX tests.
4. Run Goal 761: execute every Goal 759 RTX benchmark manifest entry.
5. Run Goal 762: analyze generated artifacts into JSON and markdown.
6. Bundle the relevant JSON/markdown outputs into one `.tgz` file for local pullback.

## Companion Update

`scripts/goal762_rtx_cloud_artifact_report.py` now records robot-specific `input_mode`, `result_mode`, `prepare_pose_indices_sec`, and scalar `colliding_pose_count` fields. This lets the next report distinguish the old pose-flag path from the Goal 768 scalar pose-count path.

## Verification

Focused local verification:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal760_optix_robot_pose_flags_phase_profiler_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal763_rtx_cloud_bootstrap_check_test \
  tests.goal769_rtx_pod_one_shot_test

Ran 30 tests in 0.710s
OK (skipped=6)
```

Additional checks:

```text
python3 -m py_compile scripts/goal769_rtx_pod_one_shot.py scripts/goal762_rtx_cloud_artifact_report.py
git diff --check
```

Both passed.

## Boundary

This goal improves execution discipline and batching only. It does not itself produce new RTX performance evidence and does not authorize any public speedup claim. The next pod session should use this runner only after the local optimization batch is ready.

