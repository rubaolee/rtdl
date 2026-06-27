# Codex Review: Goal 81 OptiX Long Exact Raw-Input Win

Date: 2026-04-04
Reviewer: Codex
Verdict: APPROVE

## Scope Reviewed

- `/Users/rl2025/rtdl_python_only/docs/goal_81_optix_long_exact_raw_input_win.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal50_postgis_ground_truth.py`
- `/Users/rl2025/rtdl_python_only/tests/goal80_runtime_identity_fastpath_test.py`

## Findings

No blocking issues found in the Goal 81 slice.

The report is honest:

- first raw-input call is still slower than PostGIS
- repeated raw-input calls beat PostGIS on the long exact-source surface
- parity is exact on all reruns

The imported Linux artifact supports the stated claim:

- PostGIS: about `3.12` to `3.15 s`
- OptiX repeated reruns: about `1.09` to `1.16 s`
- row count and digest match

## Residual Risk

The cold first-call path remains slower than PostGIS. That is a valid next
goal, not a blocker for Goal 81 as stated.
