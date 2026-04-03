# Vision

## Whole-Project Goal

Build a DSL and runtime/compiler stack for **non-graphical, re-purposed
ray-tracing-based applications** across multiple backend libraries, hardware
targets, and software ecosystems.

RTDL is not intended to be:

- only a RayJoin reimplementation
- only an Embree wrapper
- only an OptiX experiment
- only a Vulkan exercise

It is intended to become a language/runtime system for writing a broader class
of RT-style applications once and mapping them onto different backend families.

## Thesis

Today, non-graphics RT systems often require users to simultaneously manage:

- problem decomposition
- ray-tracing reformulation
- backend-specific launch/runtime details
- backend-specific precision/performance tradeoffs
- dataset and memory layout details

RTDL aims to separate those concerns:

1. the user writes a compact kernel in Python
2. the compiler owns lowering into RT-style execution structure
3. the backend owns realization for the available runtime

## Backend Ambition

The long-term backend picture includes:

- CPU-based ray-tracing libraries such as Intel Embree
- NVIDIA OptiX/CUDA-based GPU backends
- Vulkan KHR ray-tracing-based GPU backends
- AMD HIP RT-based backends
- Intel ray-tracing hardware/software platforms
- Apple ray-tracing platforms
- Qualcomm and other mobile ray-tracing platforms

The current repo validates only a subset of that ambition, but the project
framing should stay multi-backend.

## Current v0.1 Slice

The current **v0.1** slice is intentionally narrower than the whole vision.

Validated backends:

- **Intel Embree**: high-precision CPU baseline
- **NVIDIA OptiX**: high-performance CUDA-based GPU path
- **Vulkan KHR**: provisional cross-vendor GPU path retained in the repo, but not yet validated to the same level as Embree/OptiX

Target workloads:

- RayJoin workload family (LSI, PIP, Overlay, etc.)
- exact-source real-data validation
- performance characterization vs research baseline
- external ground-truth comparison against indexed PostGIS queries on the Linux host
