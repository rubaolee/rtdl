# Codex Consensus: Goal 222 Windows/Harness Portability Closure

Date: 2026-04-10
Reviewer: Codex
Status: accepted pending one external review artifact

## Verdict

This slice is the right bounded follow-up to the broad Windows reruns. It does
not change workload semantics. It closes concrete portability and harness gaps:

- Windows oracle native build/export behavior
- Windows Embree helper compile/launch behavior
- release-facing command surfaces that wrongly assumed `python3`
- evaluation and baseline metadata drift for the new nearest-neighbor workloads

## Why this goal is valid

- the earlier Windows reruns isolated real problems
- the changed files are exactly the files that own those problems
- local regression covers the expected harness surface
- the slice is small enough to review honestly

## Local verification seen by Codex

- `PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test tests.report_smoke_test tests.evaluation_test tests.baseline_integration_test tests.test_matrix_runner_test`
  - `Ran 22 tests in 53.797s`
  - `OK`
- `python3 -m compileall scripts src/rtdsl tests/report_smoke_test.py tests/baseline_integration_test.py tests/test_matrix_runner_test.py`
  - `OK`

## Residual boundary

- this goal does not yet expose Vulkan as a first-class baseline-runner backend
- that should remain a separate later goal
