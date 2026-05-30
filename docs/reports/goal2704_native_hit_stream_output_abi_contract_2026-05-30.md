# Goal2704 Native Hit-Stream Output ABI Contract

Date: 2026-05-30
Status: local implementation; pod validation still required
Depends on: Goals2685, 2692, 2694, 2698, 2700, 2703

## Purpose

Goal2704 defines the next native OptiX target before implementing CUDA-resident
hit-column output. Earlier v2.5 slices made the Python/partner side explicit:
neutral buffer seams, partner support planning, gather partner selection, RayDB
planner integration, and lease state transitions. The remaining bottleneck is
still native: the current OptiX hit-stream implementation downloads and sorts
host rows before Python sees them.

This goal gives that native work a precise ABI target without pretending it has
already been proven on hardware.

## What Changed

Added native-output ABI metadata in `src/rtdsl/hit_stream_handoff.py`:

- `GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS`
- `GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS`
- `describe_v2_5_native_hit_stream_output_abi(...)`
- `RtdlRawCudaColumn`
- `RtdlNativeDeviceHitStreamOutput`
- `prepare_native_device_hit_stream_columns_from_abi(...)`

The OptiX target symbol is:

```text
rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns
```

The expected native result shape is:

```text
ray_ids_device_ptr:uint64
primitive_ids_device_ptr:uint64
row_count:uint64
capacity:uint64
hit_event_count:uint64
overflow:uint32
device_ordinal:int32
owner_handle:uint64
traversal_seconds:float64
```

The helper can wrap raw CUDA pointers as neutral `__cuda_array_interface__`
columns and feed the existing `RtdlHitStreamColumnHandoff` metadata path. This
keeps the Python side ready for the native producer while preserving the current
claim boundary:

- native device pointers can be observed;
- native ownership is marked `native_owned_pending_state_machine`;
- overflow remains fail-closed;
- true zero-copy remains unauthorized;
- public speedup remains unauthorized;
- promotion still requires pod evidence and a native release/cleanup entrypoint.

`src/rtdsl/optix_runtime.py` now names the future native symbol, but does not
bind or silently emulate it.

## Validation

Added `tests/goal2704_native_hit_stream_output_abi_contract_test.py`.

Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 37 tests in 0.343s
OK
```

Expanded Windows v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
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
Ran 94 tests in 7.995s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\hit_stream_handoff.py src\rtdsl\__init__.py \
  src\rtdsl\optix_runtime.py \
  tests\goal2704_native_hit_stream_output_abi_contract_test.py
OK
```

Independent Gemini review:

```text
docs/reviews/goal2705_gemini_review_goal2704_native_hit_stream_output_abi_2026-05-30.md
Verdict: accept
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`7508632c59a19b526ca40685be0817b0a1933fd4`:

```text
PYTHONPATH=src:. python3 -m unittest \
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
Ran 94 tests in 2.596s
OK (skipped=5)

python3 -m py_compile src/rtdsl/hit_stream_handoff.py src/rtdsl/__init__.py \
  src/rtdsl/optix_runtime.py \
  tests/goal2704_native_hit_stream_output_abi_contract_test.py
OK
```

## Current Native Blocker

The current OptiX implementation still does this inside
`src/native/optix/rtdl_optix_workloads.cpp`:

1. allocates a device row buffer;
2. launches the OptiX any-hit path;
3. downloads row counters;
4. downloads row structs to host;
5. sorts host rows for deterministic order;
6. returns host materialized rows.

Goal2704 does not change that native path. It defines the contract the native
path must implement next.

## Next Work

Native Goal2705 should implement the OptiX producer side:

1. add the C ABI struct and function named above;
2. emit or split CUDA-resident `int64` ray-id and primitive-id columns;
3. return a native owner handle that can free the device columns;
4. expose a release/failure cleanup entrypoint;
5. bind the function in Python without host-row fallback;
6. prove on a pod that the returned pointers feed the partner continuation
   without host row materialization;
7. only then consider any removed-bottleneck or zero-copy wording.

## Boundary

This goal is not performance evidence. It is not true zero-copy evidence. It is
not native promotion. It is the last no-pod contract slice before real OptiX
CUDA output work.
