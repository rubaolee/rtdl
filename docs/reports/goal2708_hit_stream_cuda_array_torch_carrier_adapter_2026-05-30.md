# Goal2708 - CUDA-Array Hit-Stream to Torch Carrier Adapter

Date: 2026-05-30

Status: local implementation complete; pod performance evidence still required.

## Purpose

Goal2706 added a native OptiX producer that can return RT hit streams as two
CUDA-resident columns: `ray_ids:int64` and `primitive_ids:int64`. That removed
the native need to download/sort host hit rows, but the Python continuation seam
still had a practical gap: `gather_typed_payload_columns_for_hit_stream(...)`
could execute Triton only when the columns were already torch tensors.

Goal2708 closes that adapter gap without promoting a public claim. The v2.5
handoff can now explain and execute an explicit CUDA-array-interface to torch
carrier route for Triton continuation:

1. Existing torch tensors remain the direct carrier path.
2. Raw CUDA-array-interface columns become torch carrier candidates through
   DLPack, using a CuPy bridge when the source object has no usable
   `__dlpack__` implementation.
3. Host columns still require `allow_explicit_copy=True`; otherwise the Triton
   gather path fails closed.

## Code Changes

- Added `GENERIC_TORCH_CARRIER_ADAPTER_MODES`.
- Added `describe_v2_5_hit_stream_torch_carrier_adapter(...)`.
- Extended `gather_typed_payload_columns_for_hit_stream(...)` so
  `partner="triton"` accepts:
  - existing torch tensors;
  - CUDA-array-interface columns that can be adapted through DLPack/CuPy;
  - host columns only with explicit copy permission.
- Added `_torch_from_cuda_array_interface(...)`, which attempts:
  - direct `torch.from_dlpack(value)` when the source supports DLPack;
  - `cupy.asarray(value)` followed by `torch.from_dlpack(...)` otherwise.
- Kept all zero-copy and speedup claim fields set to `False`.

## Boundary

This is a bridge implementation and contract hardening step. It does not prove
true zero-copy and does not authorize any public performance claim. Promotion
still requires an RTX pod run that verifies:

- native OptiX emits CUDA hit columns;
- the adapter preserves the same device pointers without host staging;
- the owner/release path remains valid until the partner continuation finishes;
- Triton continuation runs on accepted hardware (`sm_70+`);
- timings improve over the host-row bridge for the same RayDB workload.

## Validation

Windows focused validation:

```text
py -3 -m unittest \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test \
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

Ran 101 tests in 7.393s
OK (skipped=5)
```

Local Linux validation on `192.168.1.20`:

```text
cd /home/lestat/work/rtdl_goal2692_linux_check
git reset --hard origin/main
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python3 -m unittest ...

HEAD: 0258e7e72a7a51bd91524746fb3fee0ea0537240
Ran 101 tests in 2.955s
OK (skipped=5)
```

## Next Work

The next useful no-pod check is local Linux source/build validation. The next
claim-relevant step needs a real RTX pod: run RayDB with the native OptiX device
hit-stream producer feeding the new adapter into Triton, then record same-pointer
and no-host-stage evidence.
