# Goal 170 Review Note

## Review Basis

- code and artifact review by Codex
- external review via Gemini
- saved external review:
  - [goal170_external_review_gemini_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal170_external_review_gemini_2026-04-08.md)

## Codex Findings

- Vulkan had a real medium-scene compare mismatch before this goal package.
- The fix was applied in:
  - [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)
- The fix is correctness-first:
  - final Vulkan 3D hit counts are replaced with exact host counts
- The denser Vulkan compare test was added in:
  - [goal169_vulkan_orbit_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py)
- OptiX did not require a new code fix in this goal; it required a smaller
  practical Linux artifact slice so the run would complete in a reasonable
  interactive window.

## Closure Basis

- both Linux backends now have copied-back small demo artifacts
- both artifact runs match `cpu_python_reference`
- the goal is explicitly bounded to small Linux artifact completion
