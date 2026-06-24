# Independent Audit: Goal1827 Gemini Review of Goal1826 OptiX Device Triangle Scene (2026-05-13)

I am Gemini, operating independently from Codex. This review assesses Goal1826: "OptiX Partner Device-Triangle Scene Preparation," based on the provided handoff documentation, source code, test files, and relevant release gate reports.

## Goal1826 Review: OptiX Partner Device-Triangle Scene Preparation

**Purpose:** Goal1826 extends the device-ray column bridge (introduced in Goal1823) to include partner-owned CUDA triangle columns. This allows for the preparation of an OptiX any-hit scene directly from CUDA device columns, bypassing Python/host memory staging for triangles.

**Evidence of Changes and Implementation:**

1.  **Native Export:** The new native export `rtdl_optix_prepare_ray_anyhit_2d_device_triangles` is present in `src/native/optix/rtdl_optix_api.cpp` and its declaration in `src/native/optix/rtdl_optix_prelude.h`. Its integration is confirmed by the test `tests/goal1826_optix_partner_device_triangle_scene_test.py`, specifically `test_native_sources_and_report_record_device_triangle_boundary`.
2.  **CUDA Kernel:** The `pack_triangle2d_device_columns` CUDA kernel is implemented within `src/native/optix/rtdl_optix_core.cpp`, responsible for packing partner triangle columns into RTDL's internal format on the GPU.
3.  **OptiX Acceleration Structure Build:** The `build_custom_accel_from_device_aabbs` function, located in `src/native/optix/rtdl_optix_core.cpp`, is added to enable OptiX GAS (Geometry Acceleration Structure) construction from device-generated AABBs.
4.  **Python API:**
    *   A new public helper function `pack_optix_ray_any_hit_2d_device_triangle_inputs` is introduced in `src/rtdsl/optix_runtime.py`.
    *   A new public prepared-scene constructor `prepare_optix_ray_triangle_any_hit_2d_device_triangles` is also added to `src/rtdsl/optix_runtime.py`.
    *   These Python interfaces are validated in `tests/goal1826_optix_partner_device_triangle_scene_test.py`, demonstrating proper metadata (e.g., `transfer_mode="device_columns_gpu_pack_gas_build"`, `true_zero_copy_authorized=False`) and wiring to the native symbol.

**Boundary Conditions and Limitations:**

The provided documentation (`docs/reports/goal1826_optix_partner_device_triangle_scene_2026-05-13.md`) and test assertions clearly indicate that Goal1826 is *not* a true zero-copy solution. This is due to:
*   RTDL packing partner triangle columns on the GPU into its internal triangle layout.
*   RTDL materializing AABBs for OptiX GAS construction.
*   OptiX GAS construction inherently creating backend-owned acceleration data.

**Validation Performed by Codex:**

Local validation covered `py_compile` for Python files, focused test passes on Windows and Linux, successful `make build-optix`, and confirmation of native symbol presence via `nm -D build/librtdl_optix.so`. However, the `docs/reports/goal1826_optix_partner_device_triangle_scene_2026-05-13.md` explicitly states: "RTX pod validation remains required before this can count as hardware execution evidence for the strict v2.0 birth gate."

**Verdict for Goal1826:** `accept-with-boundary`

Goal1826 successfully implements the intended functionality of extending device-column input for OptiX triangle scene preparation. The implementation correctly identifies and bounds the claim by explicitly stating that it is not true zero-copy. The local validation evidence supports the integrity of the changes. However, full hardware execution evidence (RTX pod validation) is pending, which is a key boundary.

## v2.0 Release Readiness Verdict

**Verdict:** `needs-more-evidence`

As per `docs/reports/goal1814_v2_0_strict_birth_gate_2026-05-13.md` and `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`, the v2.0 release has a strict birth gate with several blockers that must be explicitly solved or removed. Goal1826, while significant progress, does not satisfy these overarching requirements for v2.0 release readiness.

Specifically, Goal1814 states: "RTDL still performs GPU packing and OptiX GAS construction into backend-owned data, so true zero-copy and v2.0 release readiness remain blocked pending RTX pod evidence and broader claim review." This directly applies to Goal1826's current status.

## Device-Column Input Coverage and Zero-Copy Status

Goal1826, in combination with Goal1823 ("OptiX Partner Device-Ray Columns Partial ABI"), achieves complete device-column input coverage for the narrow prepared any-hit primitive for both rays and triangles. This allows both ray and triangle inputs to originate from partner-owned CUDA columns into the OptiX pipeline.

However, this **still does not authorize true zero-copy or v2.0 release.** The process involves GPU-side packing of partner data into RTDL's internal format and subsequent OptiX GAS construction, which are explicitly not considered true zero-copy. The `true_zero_copy_authorized` flag remains `False` in the test assertions, reinforcing this boundary. Further RTX pod validation and broader review are necessary to address the stricter requirements for v2.0.
