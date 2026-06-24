# Gemini Review Task: Goal2706 Native OptiX Hit-Stream Device Columns

Please perform an independent read-only review of Goal2706.

## Files To Inspect

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/optix_runtime.py`
- `tests/goal2706_native_optix_hit_stream_device_columns_test.py`
- `docs/reports/goal2706_native_optix_hit_stream_device_columns_2026-05-30.md`

## Review Questions

1. Does the new native C ABI remain generic and app-agnostic?
2. Does the native OptiX path actually avoid downloading/sorting host hit rows
   in the new device-column method?
3. Does the owner/release path look adequate for experimental native CUDA
   buffers, with obvious risks called out?
4. Does the Python binding preserve claim boundaries by keeping
   `native_device_column_output_proven_on_hardware=False` and zero-copy/speedup
   claims unauthorized?
5. What risks must be checked on the next RTX pod run before promotion?

## Required Output

Write your review to:

`docs/reviews/goal2707_gemini_review_goal2706_native_optix_hit_stream_device_columns_2026-05-30.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
