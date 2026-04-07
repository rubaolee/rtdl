# Goal 130 External Review Handoff

Please review the finished Goal 130 package for repo accuracy, technical
honesty, and whether the claimed execution/results are really supported by the
files listed below.

Return only:

1. Verdict
2. Findings
3. Summary

## Scope

The package is about the current RTDL v0.2 test-plan-and-execution surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- the narrow generate-only workflow

## Files to review

- [goal_130_v0_2_test_plan_and_execution.md](/Users/rl2025/rtdl_python_only/docs/goal_130_v0_2_test_plan_and_execution.md)
- [goal130_v0_2_test_plan_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_test_plan_2026-04-06.md)
- [goal130_v0_2_test_execution_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_test_execution_2026-04-06.md)
- [run_test_matrix.py](/Users/rl2025/rtdl_python_only/scripts/run_test_matrix.py)
- [test_matrix_runner_test.py](/Users/rl2025/rtdl_python_only/tests/test_matrix_runner_test.py)
- [goal118_segment_polygon_linux_large_perf.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal118_segment_polygon_linux_large_perf.py)
- [goal128_segment_polygon_anyhit_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal128_segment_polygon_anyhit_postgis.py)
- [goal118_segment_polygon_linux_large_perf_test.py](/Users/rl2025/rtdl_python_only/tests/goal118_segment_polygon_linux_large_perf_test.py)
- [goal128_segment_polygon_anyhit_postgis_test.py](/Users/rl2025/rtdl_python_only/tests/goal128_segment_polygon_anyhit_postgis_test.py)
- [goal130_v0_2_large_scale_artifacts_2026-04-06](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_large_scale_artifacts_2026-04-06)

## Review focus

- Does the package overclaim the current v0.2 test surface?
- Are the repaired issues described honestly?
- Are the Linux/PostGIS findings consistent with the saved artifacts?
- Is the `run_test_matrix.py` repair a real improvement rather than a cosmetic
  change?
- Does the package maintain the project’s honesty boundary around
  environment-gated Vulkan/Linux/native rows?
