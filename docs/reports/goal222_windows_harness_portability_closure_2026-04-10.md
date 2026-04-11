# Goal 222 Report: Windows And Harness Portability Closure

Date: 2026-04-10
Status: implemented

## Summary

This goal closes the Windows/harness portability issues that were still left as
local drift after the broader `v0.4` work.

The main fixes are:

- Windows-aware oracle and Embree native build wrappers using temporary batch
  scripts and `vcvars64.bat`
- Windows DLL/runtime-path propagation for the Goal 15 and Goal 19 native
  helper paths
- `sys.executable` instead of hard-coded `python3` in release-facing test and
  verification scripts
- new nearest-neighbor workload coverage in the Embree evaluation matrix
- new nearest-neighbor workload mapping in baseline integration tests
- Windows-facing docs updated from `python3` to `python` where appropriate

## Files Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_4_application_examples.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal15_compare_embree.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal19_compare_embree_performance.py`
- `/Users/rl2025/rtdl_python_only/scripts/run_full_verification.py`
- `/Users/rl2025/rtdl_python_only/scripts/run_test_matrix.py`
- `/Users/rl2025/rtdl_python_only/src/native/oracle/rtdl_oracle_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/evaluation_matrix.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/baseline_integration_test.py`
- `/Users/rl2025/rtdl_python_only/tests/report_smoke_test.py`
- `/Users/rl2025/rtdl_python_only/tests/test_matrix_runner_test.py`

## Verification

Local regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test tests.report_smoke_test tests.evaluation_test tests.baseline_integration_test tests.test_matrix_runner_test`
- result:
  - `Ran 22 tests in 53.797s`
  - `OK`

Compile pass:

- `python3 -m compileall scripts src/rtdsl tests/report_smoke_test.py tests/baseline_integration_test.py tests/test_matrix_runner_test.py`
- result:
  - `OK`

## Boundary

- This goal improves Windows and harness portability.
- It does not yet make Vulkan a first-class baseline-runner backend.
- That remaining finish work belongs to the next harness-surface goal.
