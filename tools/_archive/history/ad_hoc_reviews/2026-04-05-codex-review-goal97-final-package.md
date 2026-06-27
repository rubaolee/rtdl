# Codex Review: Goal 97 Final Package

Date: 2026-04-05
Reviewer: Codex
Verdict: APPROVE

## Findings

- No blocking technical or claim-surface issues found in the final Goal 97
  package.

## Agreement and Disagreement

- Agree that Goal 97 should be published only as a correctness/demo RTDL goal,
  not as a performance goal.
- Agree with the adjusted geometry construction:
  - build segment `(x_i, 0) -> (x_i, x_i + 1)`
  - probe segment `(0, x_i + 0.5) -> (F, x_i + 0.5)`
- Agree with the duplicate semantics:
  - `hit_count`
  - `original_index` tie-break
- Agree that Python `sorted(...)` and the explicit quicksort reference are the
  right external correctness checks.
- Agree that the Goal 97 report is honest about the available-backend boundary:
  small accepted case parity was verified on Linux across
  `cpu_python_reference`, `cpu`, `embree`, `vulkan`, and `optix`.
- Agree that the OptiX `lsi` kernel repair in
  `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp` is a real backend
  fix discovered by Goal 97 rather than an unrelated opportunistic change.

## Recommended next step

- Publish Goal 97 as a correctness/demo goal, then use it as a reusable RTDL
  example for non-spatial-join user-authored programs.
