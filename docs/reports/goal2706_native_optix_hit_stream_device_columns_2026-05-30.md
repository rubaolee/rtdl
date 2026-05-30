# Goal2706 Native OptiX Hit-Stream Device Columns

Date: 2026-05-30
Status: implemented; local Linux functional smoke passed; pod performance evidence still required
Depends on: Goal2704

## Purpose

Goal2704 defined the Python/native ABI target for CUDA-resident hit-stream
columns. Goal2706 implements the first native OptiX producer for that ABI.

The goal is narrow: remove host row materialization from the hit-stream handoff
path by returning native-owned CUDA columns for `ray_ids:int64` and
`primitive_ids:int64`. This is still not a public zero-copy or speedup claim.
It is the native plumbing needed before pod performance work.

## What Changed

Native OptiX:

- Added `RtdlNativeDeviceHitStreamColumns` to
  `src/native/optix/rtdl_optix_prelude.h`.
- Added the C ABI:
  `rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns`.
- Added the matching cleanup ABI:
  `rtdl_optix_release_ray_triangle_hit_stream_device_columns`.
- Added a dedicated OptiX any-hit pipeline that writes CUDA-resident
  `ray_ids` and `primitive_ids` arrays directly.
- Added a native owner object that frees those CUDA arrays through the release
  entrypoint.

Python runtime:

- Added `_RtdlNativeDeviceHitStreamColumns` ctypes binding.
- Added `_OptixNativeHitStreamDeviceColumnsOwner`.
- Added `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_device_columns(...)`.
- Added `ray_triangle_hit_stream_device_columns_3d_optix(...)`.
- The Python method wraps the native pointers through
  `prepare_native_device_hit_stream_columns_from_abi(...)`.

## Boundary

This path now avoids the old host row array download/sort path for the new
device-column method. It still does not authorize:

- true zero-copy wording;
- public speedup wording;
- v2.5 release promotion;
- Triton end-to-end performance claims.

The metadata deliberately leaves
`native_device_column_output_proven_on_hardware=False` until pod evidence is
collected under the accepted hardware/performance environment. Local Linux has
a GTX 1070 and is useful for compile/functional smoke, not final v2.5 Triton
performance evidence.

## Validation

Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 98 tests in 7.738s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\hit_stream_handoff.py src\rtdsl\__init__.py \
  src\rtdsl\optix_runtime.py \
  tests\goal2706_native_optix_hit_stream_device_columns_test.py \
  tests\goal2704_native_hit_stream_output_abi_contract_test.py
OK
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check` with the Goal2706 source patch:

```text
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
OK

PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 -m unittest \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test
Ran 10 tests in 0.030s
OK
```

Local Linux functional smoke:

```text
{'row_count': 2,
 'capacity': 2,
 'overflow': False,
 'source_mode': 'native_device_columns',
 'device': 'cuda:0',
 'host_rows': False,
 'proven': False}
```

Independent Gemini review:

```text
docs/reviews/goal2707_gemini_review_goal2706_native_optix_hit_stream_device_columns_2026-05-30.md
Verdict: accept-with-boundary
```

## Next Work

Goal2707 should run the path on a real RTX pod with the v2.5 RayDB continuation:

1. build OptiX from current `main`;
2. call `ray_triangle_hit_stream_device_columns(...)`;
3. feed the returned native CUDA columns into the explicit gather/partner
   planner path;
4. measure phase timings against the host-row bridge;
5. record same-pointer/no-host-stage evidence;
6. only then decide whether the removed-bottleneck wording can be promoted.
