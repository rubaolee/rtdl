# Handoff: External Review For Goal1838

Please perform an independent read-only review of Goal1838.

## Context

RTDL v2.0 partner work is moving from GPU-resident packing toward true
zero-copy, direct device-pointer handoff. Goals 1834 and 1836 proved the OptiX
prepared 2-D ray/triangle any-hit primitive can read Torch/CuPy CUDA ray
columns, triangle columns, and a partner-owned AABB tensor without RTDL-owned
input staging buffers.

Goal1838 adds the first partner-owned output path for that same primitive:
OptiX writes one `uint32` any-hit flag per ray directly into a Torch or CuPy
CUDA output vector.

## Files To Review

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/run_goal1828_optix_device_column_pod_validation.py`
- `tests/goal1838_optix_partner_owned_output_flags_zero_copy_test.py`
- `docs/reports/goal1838_optix_partner_owned_output_flags_zero_copy_2026-05-13.md`
- `docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json`
- `docs/reports/goal1838_optix_partner_owned_output_flags_torch_pod_validation.json`

## Checks Requested

1. Confirm the new native entry point writes to the provided partner-owned
   `uint32*` output buffer and does not allocate an RTDL-owned output staging
   buffer for this mode.
2. Confirm the path remains narrow: it requires a triangle-column zero-copy
   prepared scene and does not expand arbitrary partner acceleration claims.
3. Confirm both pod artifacts prove `[1, 0]` flags for CuPy and Torch and keep
   `rt_core_speedup_claim_authorized` and `v2_0_release_authorized` false.
4. Confirm Python validation is fail-closed on output dtype, shape, stride, and
   device.

## Output

Write one review to either:

- `docs/reviews/goal1839_gemini_review_goal1838_output_zero_copy_2026-05-13.md`
- `docs/reviews/goal1839_claude_review_goal1838_output_zero_copy_2026-05-13.md`

Use one of the accepted verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict if the evidence holds: Goal1838 `accept-with-boundary`;
v2.0 release readiness `needs-more-evidence`.
