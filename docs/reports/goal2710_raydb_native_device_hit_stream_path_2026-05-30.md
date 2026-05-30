# Goal2710 - RayDB Native Device Hit-Stream Path Wiring

Date: 2026-05-30

Status: implemented and Windows validated; accepted RTX pod evidence still
required before performance or zero-copy claims.

## Purpose

Goal2706 proved that the native OptiX layer can emit generic ray/triangle hit
streams as CUDA-resident columns. Goal2708 added the Python-side adapter that can
feed CUDA-array-interface columns into a Triton/Torch carrier path. Goal2710
wires those pieces into the RayDB-style benchmark path so the next pod run tests
the intended v2.5 pipeline rather than the older host-row bridge.

## Code Changes

- Added experimental generic front door:
  `run_generic_ray_triangle_hit_stream_device_columns_3d(...)`.
- The front door is intentionally OptiX-only for now and fails closed for other
  backends.
- Imported the front door at `rtdsl` module level but did not add it to
  `rtdsl.__all__`; this keeps it available for internal benchmark wiring without
  promoting it as stable public API.
- Updated
  `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
  so `paper_rt_optix_device_hit_stream_triton` uses native device hit-stream
  columns when it is not in reference-fallback mode.
- Added metadata flags:
  - `native_device_column_path_used`
  - `host_row_bridge_bypassed`

## Boundary

This is still not a release claim. The code is now arranged so the next pod run
can measure the real path:

```text
OptiX RT traversal
  -> native CUDA hit-stream columns
  -> CUDA-array-interface / DLPack torch carrier adapter
  -> Triton grouped continuation
  -> Python result presentation
```

The following remain blocked until pod validation:

- same-pointer/no-host-stage proof;
- owner lifetime cleanup under real continuation;
- Triton execution on accepted `sm_70+` hardware;
- speedup over the host-row bridge.

## Validation

Windows focused validation:

```text
py -3 -m unittest \
  tests.goal2710_raydb_native_device_hit_stream_path_test \
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

Ran 105 tests in 8.850s
OK (skipped=5)
```

Local Linux validation on `192.168.1.20`:

```text
cd /home/lestat/work/rtdl_goal2692_linux_check
git reset --hard origin/main
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python3 -m unittest ...

HEAD: c208b414f73b8656002332318e179259906fcc3a
Ran 105 tests in 2.961s
OK (skipped=5)
```

## Next Work

Run this path on an RTX pod with Torch, CuPy, Triton, CUDA, and OptiX available.
The minimum pod evidence should compare:

- old `paper_rt_optix_hit_stream_triton` host-row bridge;
- new `paper_rt_optix_device_hit_stream_triton` native device-column path;
- same fixture, mode, repeat/warmup, and source commit.
