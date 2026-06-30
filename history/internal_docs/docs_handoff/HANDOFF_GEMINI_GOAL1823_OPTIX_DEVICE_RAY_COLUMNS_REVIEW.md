# Handoff: Goal1823 OptiX Partner Device-Ray Columns Partial ABI Review

Please independently review Goal1823 in the RTDL repository.

Scope:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/python_rtdl_app_purity.py`
- `tests/goal1823_optix_partner_device_ray_columns_partial_abi_test.py`
- `docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`
- `docs/reports/goal1814_v2_0_strict_birth_gate_2026-05-13.md`

What changed:

- Added native OptiX export `rtdl_optix_count_prepared_ray_anyhit_2d_device_rays`.
- Added CUDA kernel `pack_ray2d_device_columns` to pack partner-owned device ray columns into RTDL's internal `GpuRay` layout on GPU.
- Reused the existing prepared-triangle scene and `count_prepared_ray_anyhit_2d_gpu_optix` traversal.
- Added Python public helper `pack_optix_ray_any_hit_2d_device_ray_inputs`.
- Added `PreparedOptixRayTriangleAnyHit2D.count_device_rays(ray_columns)`.
- Kept all claim flags bounded: partial direct-device ray handoff only, no true zero-copy, no full v2.0 release claim, no full triangle-column handoff.

Validation already run by Codex:

- Windows: `py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py src\rtdsl\python_rtdl_app_purity.py`
- Windows: focused Python tests including Goal1823, Goal1821, Goal1819, Goal1814, Goal1818, Goal1777 passed.
- Local Linux `192.168.1.20`: patch applied to clean `origin/main`, `python3 -m unittest tests.goal1823_optix_partner_device_ray_columns_partial_abi_test tests.goal1821_optix_partner_device_descriptor_fail_closed_test` passed.
- Local Linux `192.168.1.20`: `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev` passed.
- Local Linux `192.168.1.20`: `nm -D build/librtdl_optix.so | grep rtdl_optix_count_prepared_ray_anyhit_2d_device_rays` confirmed the symbol.

Please write your review to:

`docs/reviews/goal1824_gemini_review_goal1823_optix_device_ray_columns_2026-05-13.md`

Required verdict values:

- Goal1823: `accept`, `accept-with-boundary`, or `needs-more-evidence`
- v2.0 release readiness: `needs-more-evidence` unless you can prove all Goal1814 blockers are satisfied

Pay special attention to:

- Whether the native ABI name is app-agnostic.
- Whether the Python dtype/device/shape validations are sufficient for the native kernel contract.
- Whether the docs avoid overclaiming true zero-copy or full direct device-pointer handoff.
- Whether this should count as partial progress toward the v2.0 direct device-pointer blocker, not the completion of v2.0.
