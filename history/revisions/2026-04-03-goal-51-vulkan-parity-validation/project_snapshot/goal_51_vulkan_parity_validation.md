# Goal 51: Vulkan KHR Parity Validation

## Purpose

Validate the newly integrated Vulkan KHR ray-tracing backend against the native C/C++ oracle across the standard RTDL workload suite. 

This goal moves the Vulkan backend from "integrated" to "verified" by proving exact-row parity (within float32 tolerances) on synthetic and small real-data samples.

## Target Hardware

- GPU: Any Vulkan KHR ray-tracing capable device (e.g., NVIDIA GTX 1070/RTX series, AMD RX 6000 series).
- Driver: Must support `VK_KHR_ray_tracing_pipeline` and `VK_KHR_acceleration_structure`.
- Dependencies: `libvulkan.so`, `libshaderc.so`.

## Validation Suite

### 1. Synthetic Authored Cases
Run the minimal authored kernels for all six workloads:
- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

Requirement: **Exact parity** for ID fields; floating-point results must match within $10^{-5}$ absolute tolerance.

### 2. Bounded Real-Data (County/Zipcode)
Run the Goal 28D/34 slice ladder (`1x4` to `1x12`) for `lsi` and `pip` using the Vulkan backend.

Requirement: **Parity with CPU oracle** results previously validated for the same slices.

## Performance Baseline
Record execution time for:
- JIT compilation (GLSL to SPIR-V)
- First-run pipeline creation
- Warm execution (subsequent calls)

## Acceptance
- New test harness `tests/rtdsl_vulkan_test.py` passes locally.
- A summary report `docs/reports/goal51_vulkan_parity_results.md` documents parity results across all targets.
- The Vulkan backend can be upgraded from provisional to accepted status for RTDL v0.1.
