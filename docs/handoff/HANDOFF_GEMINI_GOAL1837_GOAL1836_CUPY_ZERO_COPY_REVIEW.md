# Handoff: Gemini Review For Goal1836

Please perform an independent read-only review of Goal1836.

## Context

RTDL v2.0 partner work is moving from GPU-resident packing toward true
zero-copy, direct device-pointer handoff. Goal1834 proved the OptiX prepared
2-D ray/triangle any-hit primitive can consume Torch-owned CUDA ray columns,
triangle columns, and a partner-owned `float32[N, 6]` AABB tensor without RTDL
ray/triangle/AABB staging or repacking.

Goal1836 adds CuPy conformance for that same exact input zero-copy contract.
CuPy reports contiguous strides in bytes, while Torch reports them in elements,
so the Python boundary now accepts both forms while still rejecting
non-contiguous inputs.

## Files To Review

- `src/rtdsl/optix_runtime.py`
- `scripts/run_goal1828_optix_device_column_pod_validation.py`
- `tests/goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_test.py`
- `docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_2026-05-13.md`
- `docs/reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_pod_validation.json`

## Checks Requested

1. Confirm the CuPy stride handling is narrow: it accepts contiguous byte
   strides for the known dtypes/layouts but does not allow arbitrary
   non-contiguous buffers.
2. Confirm the pod artifact demonstrates CuPy source protocols for both ray and
   triangle metadata, with `observed_count == expected_count == 1`.
3. Confirm the claim boundary remains narrow: true zero-copy is authorized only
   for this exact OptiX prepared 2-D any-hit input path, while RT-core speedup
   and v2.0 release readiness remain blocked.
4. Confirm the script still defaults to Torch for older Goal1828/1834 usage and
   adds CuPy through the explicit `--partner cupy` option.

## Output

Write the review to:

`docs/reviews/goal1837_gemini_review_goal1836_cupy_zero_copy_2026-05-13.md`

Use one of the accepted verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict if the evidence holds: Goal1836 `accept-with-boundary`;
v2.0 release readiness `needs-more-evidence`.
