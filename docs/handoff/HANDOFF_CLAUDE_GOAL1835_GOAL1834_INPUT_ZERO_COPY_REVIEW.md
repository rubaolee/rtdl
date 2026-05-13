# Claude Task: Review Goal1834 Whole-Primitive Input Zero-Copy Evidence

You are Claude performing an independent review distinct from Codex. Please audit Goal1834 and write your review to:

`docs/reviews/goal1835_claude_review_goal1834_input_zero_copy_2026-05-13.md`

Review these files:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `scripts/run_goal1828_optix_device_column_pod_validation.py`
- `docs/reports/goal1834_optix_whole_primitive_input_zero_copy_2026-05-13.md`
- `docs/reports/goal1834_optix_whole_primitive_input_zero_copy_pod_validation.json`
- `tests/goal1834_optix_whole_primitive_input_zero_copy_test.py`

Questions:

1. Does the native path remove RTDL ray, triangle, and AABB input staging/repacking for the prepared 2-D ray/triangle any-hit primitive when the partner supplies ray columns, triangle columns, and a contiguous CUDA `float32[N,6]` OptiX AABB tensor?
2. Does the RTX A4500 artifact prove the narrow observed claim with `observed_count == expected_count == 1`?
3. Is `true_zero_copy_authorized: true` acceptable for this exact whole-primitive input path, while still saying that OptiX GAS output remains native acceleration state?
4. Does the report avoid overclaiming v2.0 release readiness, RT-core speedup, whole-app acceleration, arbitrary partner acceleration, or no-native-state behavior?
5. What still blocks v2.0?

Use only these verdict values:

- `accept`
- `accept-with-boundary`
- `reject`
- `needs-more-evidence`

Expected verdicts:

- Goal1834: likely `accept-with-boundary`
- v2.0 release readiness: `needs-more-evidence`

Please explicitly state that you are Claude and that this is an independent review, not Codex authoring.
