# Goal 222: Windows And Harness Portability Closure

Date: 2026-04-10
Status: in progress

## Goal

Close the remaining Windows and harness portability gaps that were exposed by
the broad Windows pre-release reruns and by the repo-wide command/test surface.

## Acceptance

- Windows oracle native builds no longer assume Unix shared-library defaults
- release-facing command surfaces stop hard-coding `python3`
- baseline integration includes the new nearest-neighbor workloads
- Embree evaluation metadata includes the new nearest-neighbor workloads
- the Goal 15 / Goal 19 native helper path works on Windows with Embree runtime
  DLL resolution
- local regression for the portability slice passes

## Scope

Files expected in this goal include:

- `src/rtdsl/oracle_runtime.py`
- `src/rtdsl/embree_runtime.py`
- `src/native/oracle/rtdl_oracle_api.cpp`
- `src/rtdsl/evaluation_matrix.py`
- `scripts/run_test_matrix.py`
- `scripts/run_full_verification.py`
- `scripts/goal15_compare_embree.py`
- `scripts/goal19_compare_embree_performance.py`
- `tests/report_smoke_test.py`
- `tests/baseline_integration_test.py`
- `tests/test_matrix_runner_test.py`
- release-facing command docs that still used `python3`

## Notes

- This goal is about portability and harness honesty, not about new workload
  semantics.
- It is allowed to improve Windows behavior by using batch-wrapper compilation
  and explicit runtime PATH propagation.
- This goal should stay separate from the later Vulkan harness exposure goal.
