# Goal 78 Final Report: Vulkan Positive-Hit Sparse Redesign

**Date:** 2026-04-04  
**Status:** Accepted redesign; no hardware performance claim

## Scope

Goal 78 replaces the Vulkan positive-hit `pip` branch with a sparse GPU-candidate
generation path plus host exact finalization. The accepted scope is:

- preserve exact parity semantics
- preserve the public positive-hit `pip` contract
- leave the full-matrix path unchanged
- remove the legacy host-side `O(P x Q)` full scan from the `positive_only` branch

Goal 78 is **not** a performance publication. It is an implementation closure with a
bounded validation claim.

Final code review also corrected one Vulkan buffer-usage bug in the sub-copy path:

- the temporary `d_sub` buffer now includes both `VK_BUFFER_USAGE_TRANSFER_DST_BIT`
  and `VK_BUFFER_USAGE_TRANSFER_SRC_BIT`
- this matches its actual use as a `vkCmdCopyBuffer(...)` destination and then as the
  source for `download_from_buf(...)`

## Problem

The old Vulkan `positive_only` path in `run_pip_vulkan(...)` was a pure CPU nested loop:

- no GPU candidate generation
- no sparse output path
- exact finalization on every point/polygon pair

That defeated the purpose of the positive-hit contract on long workloads.

## Implemented Solution

The new Vulkan positive-hit path is a two-stage design:

1. **GPU sparse candidate generation**
   - one ray per point
   - polygon AABB traversal on the GPU
   - exact GLSL PIP test in the reused intersection shader
   - new any-hit shader `kPipPosRahit` atomically appends `(point_index, poly_index)`
     pairs to a compact candidate list

2. **Host exact finalization**
   - download only the candidate count and valid candidate rows
   - exact-finalize only those candidates with GEOS when available, otherwise
     `exact_point_in_polygon(...)`
   - emit only exact positive-hit rows

This changes the host exact-finalization cost from `O(P x Q)` to
`O(candidates)`, while keeping parity grounded on the host truth step.

## Files

Primary code:

- `src/native/rtdl_vulkan.cpp`

Focused tests:

- `tests/rtdsl_vulkan_test.py`

Supporting docs:

- `docs/goal_78_vulkan_positive_hit_sparse_redesign.md`
- `docs/reports/goal78_vulkan_positive_hit_sparse_redesign_plan_2026-04-04.md`
- `docs/reports/goal78_vulkan_positive_hit_sparse_redesign_status_2026-04-04.md`
- `docs/reports/goal78_gemini_review_claude_assessment_2026-04-04.md`

## Validation Performed

Local non-GPU validation:

```bash
python3 -m py_compile src/rtdsl/vulkan_runtime.py tests/rtdsl_vulkan_test.py
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test
```

Observed result:

- `Ran 3 tests in 0.004s`
- `OK (skipped=1)`

Interpretation:

- Python-layer Vulkan loader tests pass
- the GPU-dependent positive-hit tests are still skipped on this machine because no
  Vulkan runtime is present here

## Accepted Technical Claim

The accepted Goal 78 claim is:

- the Vulkan positive-hit implementation now follows the same broad architectural shape
  already accepted elsewhere in RTDL:
  - conservative accelerator-side candidate generation
  - host exact finalization for parity
- the old pure-CPU full scan in the Vulkan `positive_only` branch has been removed
- the full-matrix Vulkan path remains unchanged

## Explicit Non-Claims

Goal 78 does **not** claim:

- hardware-smoke-tested Vulkan success on this machine
- a new Vulkan performance win against PostGIS
- removal of worst-case candidate-buffer allocation risk

## Risks Kept Explicit

1. **Hardware validation still required**
   - the new GPU path must still be exercised on a Vulkan-capable host

2. **Worst-case candidate allocation remains**
   - the candidate buffer is still provisioned for `point_count x poly_count`
   - Goal 78 fixes the host scan and download waste, not the worst-case allocation bound

3. **Params naming asymmetry remains**
   - binary layout is compatible
   - this is a readability and maintenance issue, not a known runtime mismatch

## Conclusion

Goal 78 is accepted as an implementation and architecture closure:

- the redesign is sound
- the code matches the documented solution
- local non-GPU validation is clean
- the final review-fixed sub-copy buffer now matches Vulkan transfer-usage requirements

The next Vulkan goal, if pursued, should be a hardware-backed validation and
measurement package rather than more speculative redesign prose.
