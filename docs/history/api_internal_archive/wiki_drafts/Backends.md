# Historical Wiki Draft Note

This page was imported from a parallel checkout on 2026-04-10 as a preserved
draft artifact. It is **not** the current live source of truth for RTDL docs.
For current backend support language, use the support matrices under
[docs/release_reports](../release_reports).

---

# Backend Guide

RTDL's power lies in its ability to target diverse hardware through a single abstraction layer.

## Available Backends

### 1. CPU (Python Reference)
*   **API**: `rt.run_cpu_python_reference(...)`
*   **Maturity**: Canonical Ground Truth.
*   **Description**: A slow but 100% accurate Python implementation using `shapely` and `geos`. Used primarily for unit tests and verifying the results of native backends.

### 2. CPU (Native - Embree)
*   **API**: `rt.run_embree(...)`
*   **Maturity**: Primary Production Surface.
*   **Description**: Leverages Intel Embree (Version 4.x) for high-performance CPU ray-tracing traversal. It is the most stable and feature-complete backend for desktop and server environments.

### 3. GPU (Native - NVIDIA OptiX)
*   **API**: `rt.run_optix(...)`
*   **Maturity**: Emerging / Research Surface.
*   **Description**: Utilizes NVIDIA's RTX-optimized OptiX SDK. It provides massive throughput for ray-join and hit-counting workloads on modern GPUs. Requires `libnvrtc.so` and compatible NVIDIA drivers.

### 4. GPU (Native - Vulkan)
*   **API**: `rt.run_vulkan(...)`
*   **Maturity**: Emerging / Research Surface.
*   **Description**: A cross-vendor GPU backend. Provides hardware-agnostic acceleration for devices supporting Vulkan Ray Tracing extensions.

## Hardware Support Matrix

| Backend | Platform | Hardware | Prerequisites |
| :--- | :--- | :--- | :--- |
| **Python** | Linux/macOS/Win | CPU (Any) | `geos`, `shapely` |
| **Embree** | Linux/macos | CPU (x86/ARM) | `libembree4` |
| **OptiX** | Linux/Win | GPU (NVIDIA) | CUDA Toolkit, OptiX SDK |
| **Vulkan** | Linux/Win | GPU (Any) | Vulkan SDK, RT-capable driver |

## Troubleshooting Native Libraries
RTDL uses a robust loader that checks for common library paths (Homebrew on macOS, standard `/usr/lib` on Linux). If a native library is not found, the system will raise an `ImportError` with details on the missing `.so` or `.dylib` file.
