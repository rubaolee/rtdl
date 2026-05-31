# Goal2746 - OptiX Hit-Stream Host-Synchronized Ordering

Date: 2026-05-30

Status: local Codex implementation complete; validation pending.

## Purpose

Goal2738 added explicit producer/consumer stream-ordering metadata and kept the
default native-output state as `not_proven`. Goal2742 made sure the OptiX runtime
does not drop this field during handoff reconstruction.

Goal2746 records the stronger state that the current OptiX device-column
producer actually provides: the native function synchronizes its CUDA stream
before returning the native owner handle to Python. Therefore the Python runtime
can honestly mark the OptiX device-column handoff as
`host_synchronized_before_consumer`.

## Change

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_device_columns(...)`
now passes:

```python
producer_consumer_stream_ordering="host_synchronized_before_consumer"
```

into `prepare_native_device_hit_stream_columns_from_abi(...)`.

The native source already contains:

```cpp
CU_CHECK(cuStreamSynchronize(stream));
...
columns_out->owner_handle = owner.release();
```

so the owner is handed to Python only after the producer stream has completed.

## Boundary

This is an ordering claim for the current OptiX producer path. It is not a true
zero-copy claim and not a public speedup claim.

Remaining future work:

- replace device-wide/host synchronization with event-based producer/consumer
  ordering when appropriate;
- validate multi-GPU and multi-driver behavior;
- keep `true_zero_copy_authorized` false until same-pointer, no-host-stage,
  stream-ordering, lifetime, and external-review evidence all exist.

## Validation

```text
py -3 -m unittest \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2744_native_hit_stream_release_enforcement_audit_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test
23 tests OK

py -3 -m py_compile src/rtdsl/optix_runtime.py \
  tests/goal2746_optix_hit_stream_host_sync_ordering_test.py
clean
```

Pod validation on `root@69.30.85.171:22167` after pulling commit `00e5cf32`:

```text
python3 -m unittest \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2744_native_hit_stream_release_enforcement_audit_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test
23 tests OK
```
