# Review: Goal1823 OptiX Partner Device-Ray Columns Partial ABI

This is an independent audit by Gemini, a large language model, independent from Codex.

## Verdict for Goal1823: `accept-with-boundary`

Goal1823 successfully introduces a partial path for OptiX partner device-ray columns, demonstrating progress in direct device-pointer handoff with GPU-side ray packing. The implementation aligns with the stated goal of providing a measured, bounded solution without overclaiming broader zero-copy or performance benefits.

## Verdict for v2.0 Release Readiness: `needs-more-evidence`

While Goal1823 represents valuable progress, it does not fully satisfy the blockers outlined in `docs/reports/goal1814_v2_0_strict_birth_gate_2026-05-13.md` and `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`. Specifically, true zero-copy, full direct device-pointer handoff, and broad RT-core speedup claims require further evidence.

## Summary of Goal1823

Goal1823 focused on enabling OptiX to accept partner-owned CUDA ray columns, pack them into RTDL's internal `GpuRay` layout on the GPU, and then execute existing prepared-scene any-hit counters. This work was explicitly designed as a partial bridge, aiming to avoid host memory transfers for rays while deferring full zero-copy and comprehensive RT-core acceleration claims.

## Concrete Evidence

### Native ABI Additions and Design

*   **New Exported Symbol:** `rtdl_optix_count_prepared_ray_anyhit_2d_device_rays` is present in `src/native/optix/rtdl_optix_api.cpp` and declared in `src/native/optix/rtdl_optix_prelude.h`. This symbol adheres to generic primitive terminology, avoiding application-specific vocabulary.
*   **CUDA Packing Kernel:** The `pack_ray2d_device_columns` CUDA kernel is added in `src/native/optix/rtdl_optix_core.cpp` (though the provided excerpt was truncated, the handoff document explicitly mentions its addition). Its purpose is to efficiently reformat partner-provided ray columns into RTDL's internal `GpuRay` structure directly on the GPU.
*   **Existing Traversal Reuse:** The implementation reuses the `count_prepared_ray_anyhit_2d_gpu_optix` traversal, as noted in the handoff document and reflected in the workload flow.

**Evidence Source:**
    *   `src/native/optix/rtdl_optix_api.cpp` (API definition)
    *   `src/native/optix/rtdl_optix_prelude.h` (Declaration)
    *   `src/native/optix/rtdl_optix_workloads.cpp` (Implementation details using `count_prepared_ray_anyhit_2d_device_rays_optix`)
    *   `src/native/optix/rtdl_optix_core.cpp` (Contains CUDA kernels like `pack_ray2d_device_columns`)

### Python API Integrations

*   **New Helper Function:** `pack_optix_ray_any_hit_2d_device_ray_inputs` is introduced in `src/rtdsl/optix_runtime.py`. This helper is responsible for preparing the ray columns for native consumption.
*   **New Prepared Scene Method:** `PreparedOptixRayTriangleAnyHit2D.count_device_rays(ray_columns)` is added, allowing direct execution from device-resident ray data.
*   **Input Validation:** The Python layer performs crucial validation checks on `ray_columns` to ensure correct `dtype`, `shape`, contiguity, and consistent CUDA device usage, as confirmed by `tests/goal1823_optix_partner_device_ray_columns_partial_abi_test.py`. This ensures the native kernel receives data in the expected format.

**Evidence Source:**
    *   `src/rtdsl/optix_runtime.py` (Python API definitions)
    *   `tests/goal1823_optix_partner_device_ray_columns_partial_abi_test.py` (Unit tests for validation and wiring)

### Claim Boundary and Release Readiness

*   **Partial Handoff, No True Zero-Copy:** The official report `docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md` explicitly states: "True zero-copy, arbitrary partner acceleration, whole-app acceleration, and broad RT-core speedup claims remain blocked." This is consistent with the "accept-with-boundary" verdict.
*   **v2.0 Blockers Remain:** `docs/reports/goal1814_v2_0_strict_birth_gate_2026-05-13.md` and `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md` reiterate that v2.0 release requires resolution of blockers such as "True zero-copy", "Direct device-pointer handoff" (beyond this partial step), "Broad RT-core speedup," and "Whole-application acceleration." Goal1823 is noted as progress but does not fully resolve these.
*   **RTX Hardware Evidence Pending:** The `docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md` report also states, "Hardware validation is still pending. A local Linux OptiX build is useful as a compile/smoke gate, but release evidence still requires an RTX-class pod run." This further supports the `needs-more-evidence` verdict for v2.0.

**Evidence Source:**
    *   `docs/handoff/HANDOFF_GEMINI_GOAL1823_OPTIX_DEVICE_RAY_COLUMNS_REVIEW.md` (Handoff summary)
    *   `docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md` (Official report with claims)
    *   `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md` (v1.8/v2.0 roadmap and gates)
    *   `docs/reports/goal1814_v2_0_strict_birth_gate_2026-05-13.md` (Strict v2.0 birth gate requirements)
