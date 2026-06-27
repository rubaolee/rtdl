# Codex Review: Goal 85/86 Final Package

**Date:** 2026-04-04  
**Verdict:** APPROVE-WITH-NOTES

## Findings

- Goal 85 is honest about what was actually achieved on hardware:
  - the revised Vulkan positive-hit path runs on Linux hardware
  - the goal51 validation ladder is parity-clean
  - the new positive-hit Vulkan tests execute and pass on hardware
  - Vulkan still does not join the long exact-source closure because the
    worst-case candidate allocation guardrail blocks that surface
- The code/test changes are justified:
  - `tests/rtdsl_vulkan_test.py` now exercises the accepted positive-hit kernel
    contract instead of incorrectly passing `result_mode="positive_hits"` to the
    runtime entry point
  - `src/rtdsl/baseline_runner.py` is now tolerant of canonical point objects in
    `points_from_records(...)`, which is consistent with the repo's canonical
    geometry path
  - `scripts/goal85_vulkan_prepared_exact_source_county.py` is a narrow harness
    for a real hardware comparison and matches existing goal71-style report shape
- Goal 86 draws the right conclusion:
  - OptiX and Embree are the mature long exact-source performance backends
  - Vulkan is hardware-validated and bounded, but still blocked from the same
    long prepared row by the candidate-allocation contract

## Agreement and Disagreement

- I agree with publishing Goal 85 and Goal 86 together.
- I do not agree with any stronger Vulkan claim than the current one. The
  backend is improved and validated, but it is not yet part of the long
  exact-source performance closure.

## Recommended next step

- Publish Goal 85 and Goal 86 as the current Vulkan/backend status closure.
- If Vulkan work resumes later, target the candidate-allocation contract
  directly so the backend can actually run the same long exact-source package as
  OptiX and Embree.
