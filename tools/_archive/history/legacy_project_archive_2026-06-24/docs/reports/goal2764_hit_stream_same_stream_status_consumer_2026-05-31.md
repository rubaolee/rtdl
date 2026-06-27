# Goal2764: Hit-Stream Same-Stream Status Consumer

Date: 2026-05-31

Status: implemented and pod-validated, pending external review.

## Purpose

Goal2762 made hit-stream row count, hit-event count, and overflow available as
caller-owned CUDA status buffers, but the producer still synchronized before
Python could launch a partner continuation. Goal2764 adds the harder proof step:
an OptiX hit-stream producer can enqueue onto a caller-provided CUDA stream, and
a bounded same-stream CuPy RawKernel consumer can read the device-resident
status on that same stream with no producer-side host scalar sync.

This is deliberately narrow. It proves a reusable runtime pattern for bounded
device-status continuations. It does not authorize true zero-copy wording, broad
partner continuation claims, and does not authorize public speedup claims.

## New Native ABI

New OptiX symbol:

`rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream`

The symbol accepts caller-owned CUDA output columns, caller-owned CUDA status
buffers, and a caller-provided nonzero CUDA stream pointer. The launch path:

- enqueues status-buffer initialization on the provided stream;
- enqueues the OptiX hit-stream launch on the same stream;
- returns without reading row count, hit-event count, or overflow back to host;
- returns an async-launch owner handle for temporary ray, flag, and launch-param
  storage that must outlive the producer and consumer work.

New release symbol:

`rtdl_optix_release_ray_triangle_hit_stream_async_launch`

The release path synchronizes the recorded stream before freeing temporary
native launch storage. This synchronization is a cleanup safety guard, not a
producer-side scalar read before the partner consumer.

## Python Runtime Surface

New method:

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_same_stream_status_summary(...)`

The method launches the native producer on a nonzero CUDA stream, then launches a
CuPy RawKernel consumer on `cupy.cuda.ExternalStream(cuda_stream_ptr)`. The
consumer reads:

- `row_count` from the device status buffer;
- `hit_event_count` from the device status buffer;
- `overflow` from the device status buffer;
- a bounded first witness row from the caller-owned output columns.

Only the final summary is materialized on the host after the consumer completes.
The metadata explicitly records:

- `producer_consumer_stream_ordering = same_stream`;
- `producer_host_synchronization_used = False`;
- `host_scalar_read_before_consumer = False`;
- `bounded_partner_consumer_executed = True`;
- `async_partner_continuation_authorized = True` for this bounded proof;
- `async_partner_continuation_authorization_scope =
  bounded_same_stream_status_consumer_only`;
- `general_partner_continuation_authorized = False`;
- `true_zero_copy_authorized = False`;
- `public_speedup_claim_authorized = False`.

The caller-provided CUDA stream is part of the lifetime contract: it must remain
valid until the async launch owner is released after the consumer completes.

## Boundary

This goal proves that RTDL can pass device-resident hit-stream status from an
RT producer to a bounded partner consumer on the same stream. It does not prove:

- arbitrary partner continuations;
- event-based cross-stream continuation;
- full hit-stream row consumers beyond the bounded status-summary proof;
- true zero-copy release wording;
- public performance claims.

Those remain separate v2.5 follow-up gates.

## Validation Plan

Local static tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal2764_hit_stream_same_stream_status_consumer_test`

Pod runtime tests require:

- CUDA-capable Torch;
- CuPy;
- current OptiX backend built from this commit;
- `RTDL_OPTIX_LIBRARY` pointing at `build/librtdl_optix.so`.

Expected runtime smoke result:

- one triangle, one ray;
- device status consumer observes `row_count = 1`;
- device status consumer observes `hit_event_count = 1`;
- device status consumer observes `overflow = 0`;
- first witness is `(ray_id=11, primitive_id=0)`.
- overflow smoke with zero row capacity observes `row_count = 1`,
  `hit_event_count = 1`, `overflow = 1`, `bounded_row_count = 0`, and no
  first witness.

## Validation Evidence

Local Windows static validation:

`$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2764_hit_stream_same_stream_status_consumer_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test`

Result: 15 tests ran; 12 passed and 3 skipped for local CUDA/OptiX runtime
availability.

Pod:

`ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`

Pod checkout before patch: `c2d0c389`.

Final pushed commit validation: pod reset to `origin/main` at `363300dc`,
rebuilt `build/librtdl_optix.so`, and reran the corrected hit-stream gate
successfully.

Pod setup note: `cupy` was already importable. `torch` initially failed because
the pod Python environment lacked `pytest`; installing `pytest` with
`python3 -m pip install --break-system-packages pytest` made
`torch 2.8.0+cu128` import successfully with `torch.cuda.is_available() == True`.

Build:

`make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Result: `build/librtdl_optix.so` rebuilt successfully.

Live same-stream smoke:

`PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python3 -m unittest -v tests.goal2764_hit_stream_same_stream_status_consumer_test`

Result: 6 tests passed, 0 skipped. The live runtime tests observed:

- `row_count = 1`;
- `hit_event_count = 1`;
- `overflow = False`;
- `first_ray_id = 11`;
- `first_primitive_id = 0`;
- zero-capacity overflow smoke: `row_count = 1`, `hit_event_count = 1`,
  `overflow = True`, `bounded_row_count = 0`, no first witness;
- metadata recorded `producer_consumer_stream_ordering = same_stream`;
- metadata recorded `producer_host_synchronization_used = False`;
- metadata recorded `host_scalar_read_before_consumer = False`;
- metadata recorded `async_partner_continuation_authorization_scope =
  bounded_same_stream_status_consumer_only`;
- metadata recorded that the caller stream must remain valid until async owner
  release;
- metadata kept `true_zero_copy_authorized = False` and
  `public_speedup_claim_authorized = False`.

External review note: Claude reviewed the implementation and gave
`accept-with-boundary`, specifically calling out the synchronous input upload
gap, caller stream-lifetime contract, and scoped authorization naming risk as
non-blocking follow-ups. Goal2764 metadata/report now explicitly records the
scoped authorization and stream-lifetime contract; making input uploads fully
host-async remains future work.

Corrected hit-stream gate:

`PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python3 -m unittest tests.goal2704_native_hit_stream_output_abi_contract_test tests.goal2706_native_optix_hit_stream_device_columns_test tests.goal2710_raydb_native_device_hit_stream_path_test tests.goal2719_native_hit_stream_materialization_proof_metadata_test tests.goal2720_raydb_prepared_device_hit_stream_steady_state_test tests.goal2737_native_hit_stream_owner_lifecycle_guard_test tests.goal2738_native_hit_stream_stream_ordering_boundary_test tests.goal2746_optix_hit_stream_host_sync_ordering_test tests.goal2750_hit_stream_transfer_stream_ordering_gate_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2758_reusable_hit_stream_buffer_perf_probe_test tests.goal2760_hit_stream_async_promotion_requirements_test tests.goal2762_hit_stream_device_status_buffers_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Result: 58 tests passed. The same 58-test gate also passed after resetting the
pod checkout to pushed commit `363300dc` and rebuilding OptiX from that commit.

## Review Requirement

This is a code-bearing v2.5 runtime-contract goal. It needs at least one
external AI review before it can be treated as accepted internal evidence, and
3-AI consensus before any public zero-copy or release-level wording changes.
