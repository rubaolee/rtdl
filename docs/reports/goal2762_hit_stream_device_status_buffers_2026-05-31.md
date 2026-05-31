# Goal2762 Hit-Stream Device Status Buffers

Date: 2026-05-31

Status: implemented and validated on a patched RTX A5000 pod checkout

## Purpose

Goal2760 defined the next async-promotion blocker for generic v2.5 hit-stream
handoff: the runtime needs device-resident row-count and overflow state before a
partner continuation can consume a hit stream without a host scalar read.

Goal2762 adds that missing status carrier as a narrow, app-agnostic building
block. It does not remove the current producer synchronization, but it lets the
OptiX producer write the status values into caller-owned CUDA buffers in the
same generic call that writes `ray_ids:int64` and `primitive_ids:int64`.

## Native ABI

New OptiX symbol:

`rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status`

The symbol accepts caller-owned device pointers for:

- `ray_ids_device_ptr`;
- `primitive_ids_device_ptr`;
- `row_count_device_ptr`;
- `hit_event_count_device_ptr`;
- `overflow_device_ptr`.

The existing `RtdlNativeDeviceHitStreamColumns` ABI record now also includes:

- `row_count_device_ptr:uint64`;
- `hit_event_count_device_ptr:uint64`;
- `overflow_device_ptr:uint64`.

The native implementation passes the caller-owned status pointers directly into
the generic OptiX launch params, so the kernel writes counters to device memory.
The function still calls `cuStreamSynchronize(stream)` and downloads scalar
metadata before returning to Python. That is intentional for this goal: the new
status carrier is a prerequisite for async continuation, not proof that async
continuation already exists.

## Python Runtime

`PreparedOptixHitStreamDeviceColumnBuffers` now owns three additional CUDA
tensors:

- `row_count`;
- `hit_event_count`;
- `overflow`.

New method:

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_into_device_columns_with_status(...)`

The returned `RtdlHitStreamColumnHandoff` records:

- `device_resident_row_count_for_partner=True`;
- `device_resident_hit_event_count_for_partner=True`;
- `device_resident_overflow_for_partner=True`;
- `device_resident_status_for_partner=True`;
- `producer_consumer_stream_ordering="host_synchronized_before_consumer"`;
- `async_partner_continuation_authorized=False`;
- `true_zero_copy_authorized=False`.

## Boundary

This goal does not authorize async partner continuation, public speedup wording,
and does not authorize true zero-copy wording. It adds the device-resident status
channel needed by a future event/same-stream producer API, while keeping the
current runtime truth: `host_synchronized_before_consumer`.

## Files Changed

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2762_hit_stream_device_status_buffers_test.py`
- `docs/reports/goal2762_hit_stream_device_status_buffers_2026-05-31.md`
- `docs/research/future_version_to_do_list.md`

## Validation

Local static gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/hit_stream_handoff.py tests/goal2762_hit_stream_device_status_buffers_test.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2762_hit_stream_device_status_buffers_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test
```

Result: `17` tests passed, `2` skipped on the local non-CUDA Windows runtime.

Broader local v2.5 hit-stream gate:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2684_generic_rt_hit_stream_handoff_test tests.goal2685_device_resident_hit_stream_handoff_test tests.goal2690_post_goal2689_contract_honesty_test tests.goal2694_hit_stream_neutral_seam_metadata_test tests.goal2698_hit_stream_partner_continuation_plan_test tests.goal2700_explicit_hit_stream_gather_partner_test tests.goal2704_native_hit_stream_output_abi_contract_test tests.goal2706_native_optix_hit_stream_device_columns_test tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test tests.goal2719_native_hit_stream_materialization_proof_metadata_test tests.goal2734_v2_5_same_pointer_zero_copy_boundary_audit_test tests.goal2737_native_hit_stream_owner_lifecycle_guard_test tests.goal2738_native_hit_stream_stream_ordering_boundary_test tests.goal2740_hit_stream_cross_partner_transfer_plan_test tests.goal2744_native_hit_stream_release_enforcement_audit_test tests.goal2746_optix_hit_stream_host_sync_ordering_test tests.goal2750_hit_stream_transfer_stream_ordering_gate_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test tests.goal2754_current_v25_hit_stream_perf_probe_test tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test
```

Result: `107` tests passed, `3` skipped on the local non-CUDA Windows runtime.

Pod gate on `root@69.30.85.171:22167`, patched from pushed commit `ccc07b5f`:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so PYTHONPATH=src:. \
  python3 -m unittest \
    tests.goal2762_hit_stream_device_status_buffers_test \
    tests.goal2760_hit_stream_async_promotion_requirements_test \
    tests.goal2756_reusable_hit_stream_device_output_buffers_test \
    tests.goal2752_hit_stream_zero_copy_ordering_metadata_test
```

Result: OptiX rebuild completed, and `17` pod tests passed. The runtime smoke
proved that the native symbol loads, the device status pointers preserve
identity, and the status tensors hold `row_count=1`, `hit_event_count=1`, and
`overflow=0` for the smoke fixture.

## External Review

Claude review:

- `docs/reviews/goal2763_claude_review_goal2762_hit_stream_device_status_buffers_2026-05-31.md`
- verdict: `accept`
- boundary confirmation: the status buffers are a correct generic building block
  but the runtime remains `host_synchronized_before_consumer`, not async
  continuation and not true zero-copy.

Gemini Flash was retried for this review and failed with server-side
`MODEL_CAPACITY_EXHAUSTED`; no Gemini review is claimed.
