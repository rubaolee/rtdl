# Independent Gemini Review: Goal2764 Hit-Stream Same-Stream Status Consumer

This is an independent Gemini review, not Codex.

## Review of Goal2764 Implementation

The Goal2764 implementation, as detailed in the provided files, successfully demonstrates a narrow same-stream producer plus bounded CuPy status consumer without a producer-side host scalar sync.

### Evidence for Narrow Same-Stream Producer and Bounded CuPy Status Consumer:

*   **Native API and Implementation:** The `rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream` function, declared in `rtdl_optix_prelude.h` and implemented in `rtdl_optix_api.cpp` and `rtdl_optix_workloads.cpp`, explicitly accepts a `cuda_stream_ptr`. The C++ implementation in `rtdl_optix_workloads.cpp` (as verified by `tests/goal2764_hit_stream_same_stream_status_consumer_test.py`) enqueues `cuMemsetD8Async`, `cuMemsetD32Async`, and `optixLaunch` onto this stream without any `cuStreamSynchronize(stream)` or `download(` calls on the producer side, thereby ensuring no producer-side host scalar sync.
*   **Python Runtime:** `optix_runtime.py` exposes `ray_triangle_hit_stream_same_stream_status_summary`, which leverages `cupy.cuda.ExternalStream` and `rtdl_hit_stream_same_stream_status_summary_u64` to instantiate a CuPy RawKernel consumer on the same stream. This confirms the bounded CuPy status consumer aspect.
*   **Handoff Metadata:** `hit_stream_handoff.py` defines `producer_consumer_stream_ordering: same_stream` and `zero_copy_compatible_stream_ordering` states, directly supporting the "same-stream" claim.
*   **Unit and Smoke Tests:** `tests/goal2764_hit_stream_same_stream_status_consumer_test.py` includes specific assertions:
    *   `test_native_async_stream_abi_has_lifetime_owner_and_no_producer_sync` confirms the absence of host synchronization in the native code.
    *   `test_python_runtime_exposes_same_stream_cupy_status_consumer` validates the Python runtime's correct exposure of the same-stream CuPy consumer and its metadata.
    *   `test_runtime_smoke_uses_device_status_without_preconsumer_host_scalar_sync` provides live runtime evidence that the device status consumer successfully reads `row_count`, `hit_event_count`, and `overflow` directly from device-resident buffers without host synchronization.

### Avoidance of Overclaiming:

The implementation, documentation, and tests consistently and explicitly avoid overclaiming broader capabilities:

*   **Explicit Disclaimers in Code and Documentation:**
    *   `RtdlHitStreamColumnHandoff.to_metadata()` and `RtdlNativeDeviceHitStreamOutput.to_metadata()` in `hit_stream_handoff.py` set `"true_zero_copy_authorized": False` and `"public_speedup_claim_authorized": False`.
    *   `describe_v2_5_hit_stream_async_promotion_requirements` in `hit_stream_handoff.py` clearly states `"current_runtime_async_promotion_authorized": False`, `"current_runtime_true_zero_copy_authorized": False`, and `"current_runtime_public_speedup_claim_authorized": False`.
    *   The `docs/reports/goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md` report explicitly notes: "This is deliberately narrow. It does not authorize true zero-copy wording, broad partner continuation claims, and does not authorize public speedup claims." and details precisely what it does and does not prove.
*   **Test Assertions:** The smoke test `test_runtime_smoke_uses_device_status_without_preconsumer_host_scalar_sync` verifies that `true_zero_copy_authorized` and `public_speedup_claim_authorized` remain `False` in the metadata, reinforcing the boundaries.

## Verdict

**accept**

The implementation successfully achieves its narrow goal of demonstrating a same-stream producer and bounded CuPy status consumer without producer-side host scalar synchronization, while meticulously avoiding overclaims regarding true zero-copy, broad async continuations, or public performance claims. The evidence from code, documentation, and tests is consistent and robust.