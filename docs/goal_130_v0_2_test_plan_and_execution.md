# Goal 130: v0.2 Test Plan And Execution

Date: 2026-04-06
Status: accepted

## Goal

Produce a thorough test plan for the current RTDL v0.2 surface, review that
plan, execute the practical test matrix, fix any real issues found, and publish
the results with saved consensus.

Scope is limited to the current v0.2 line:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- the narrow generate-only workflow

## Required outcomes

1. one thorough v0.2 test plan authored from the current codebase
2. review of that plan for repo accuracy and overclaiming
3. execution of the practical local and Linux/PostGIS-backed test matrix
4. repair of any real problem found in code or process
5. one final execution report with saved review trail

## Accepted package

Goal 130 is now the test-and-execution closure package for the current v0.2
surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- the narrow generate-only workflow

The accepted outputs are:

- [goal130_v0_2_test_plan_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_test_plan_2026-04-06.md)
- [goal130_v0_2_test_execution_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_test_execution_2026-04-06.md)
- [goal130_v0_2_large_scale_artifacts_2026-04-06](/Users/rl2025/rtdl_python_only/docs/reports/goal130_v0_2_large_scale_artifacts_2026-04-06)

## What was found and repaired

- the initial Claude plan referenced nonexistent `tests.plan_schema_test`
- the test-matrix runner had gone stale and did not expose explicit v0.2 groups
- the Linux large-scale markdown renderers were incorrectly showing unsupported
  prepared modes as `0.000000` instead of `n/a`

Those issues were repaired in this goal before final reporting.
