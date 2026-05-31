# Goal2744 - Native Hit-Stream Release Enforcement Audit

Date: 2026-05-30

Status: local Codex audit complete; validation pending.

## Purpose

Goal2739 and Goal2741 both correctly kept native hit-stream ownership/lifetime
as a boundary risk. Goal2744 narrows that risk with a current source audit.

The question is not whether RTDL can publicly claim true zero-copy. It cannot.
The question is whether the OptiX device-column path has the required native
release entrypoint and whether Python fails closed if that cleanup ABI is
missing.

## Findings

The current source has the required release path:

- `src/native/optix/rtdl_optix_prelude.h` declares
  `rtdl_optix_release_ray_triangle_hit_stream_device_columns`.
- `src/native/optix/rtdl_optix_api.cpp` exports the release C ABI and forwards
  it to `release_ray_triangle_hit_stream_device_columns_optix(...)`.
- `src/native/optix/rtdl_optix_workloads.cpp` transfers ownership with
  `columns_out->owner_handle = owner.release();` and deletes the native owner in
  `release_ray_triangle_hit_stream_device_columns_optix(...)`.
- `src/rtdsl/optix_runtime.py` checks that both the device-column producer symbol
  and release symbol exist before launching the native producer.
- `_OptixNativeHitStreamDeviceColumnsOwner.close()` is idempotent, nulls the
  handle, invokes the release symbol, and is also called from `__del__` as a
  fallback.

## Test

`tests/goal2744_native_hit_stream_release_enforcement_audit_test.py` verifies:

- release symbol naming is consistent across Python, prelude, and API export;
- native owner transfer and deletion are present;
- Python checks the release symbol before calling the native producer;
- Python owner close is idempotent and invokes the release symbol;
- handoff metadata exposes `owner_close_supported` without authorizing true
  zero-copy.

## Boundary

This audit reduces the "native release entrypoint unknown" risk. It does not
close all native-lifetime risk:

- multi-GPU and multi-driver validation remains future evidence work;
- stream/event ordering remains not proven unless explicitly recorded;
- Python-side source audits are not a substitute for memory-checking native
  hardware runs;
- true zero-copy and public speedup claims remain unauthorized.

## Validation

```text
py -3 -m unittest \
  tests.goal2744_native_hit_stream_release_enforcement_audit_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2737_native_hit_stream_owner_lifecycle_guard_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test
16 tests OK

py -3 -m py_compile \
  tests/goal2744_native_hit_stream_release_enforcement_audit_test.py \
  tests/goal2706_native_optix_hit_stream_device_columns_test.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/hit_stream_handoff.py
clean
```

Pod validation on `root@69.30.85.171:22167` after pulling commit `e80fcf1d`:

```text
python3 -m unittest \
  tests.goal2744_native_hit_stream_release_enforcement_audit_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2737_native_hit_stream_owner_lifecycle_guard_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test
16 tests OK
```
