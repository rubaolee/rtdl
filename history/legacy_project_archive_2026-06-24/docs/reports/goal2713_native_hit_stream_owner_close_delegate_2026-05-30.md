# Goal2713 - Native Hit-Stream Owner Close Delegate

Date: 2026-05-30

Status: implemented; local smoke motivated.

## Purpose

A local Linux smoke of the new generic device-column front door returned valid
native CUDA hit-stream columns, but cleanup required reaching through nested
ownership (`handoff.owner.owner.close()`). That is too easy to misuse before pod
testing.

Goal2713 adds a small close delegate to `RtdlNativeDeviceHitStreamOutput` so
callers can close `handoff.owner` directly.

## Code Change

`RtdlNativeDeviceHitStreamOutput` now provides:

- `close()`, delegating to the runtime owner when it exposes `close`;
- `__enter__`;
- `__exit__`.

The change does not alter ownership policy, pointer metadata, zero-copy claims,
or public API promotion.

## Validation

Windows focused validation:

```text
py -3 -m unittest \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test \
  tests.goal2710_raydb_native_device_hit_stream_path_test

Ran 14 tests in 0.006s
OK
```

Local Linux smoke on `192.168.1.20`:

```text
HEAD: c63ad5d4a6aeef1a98da40dcd1fc66a223035420
{'row_count': 2, 'capacity': 2, 'overflow': False,
 'source_mode': 'native_device_columns', 'device': 'cuda:0',
 'materializes_host_rows': False,
 'native_symbol': 'rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns',
 'proven': False}
[linux] closed owner through handoff.owner.close()
Ran 14 tests in 0.003s
OK
```

## Boundary

This is a lifecycle ergonomics fix. Pod validation is still required to prove
native owner lifetime across real partner continuation execution.
