# RTDL

RTDL is a Python-hosted DSL and runtime/compiler stack for **non-graphical
ray-tracing-based applications**. The project goal is to let users write
high-level kernels once and execute them across multiple ray-tracing backends
without programming backend-specific details directly.

## Current Position

RTDL is no longer only a design sketch.

Current validated execution surface:

- native C/C++ oracle via `rt.run_cpu(...)`
- Intel Embree backend via `rt.run_embree(...)`
- NVIDIA OptiX backend via `rt.run_optix(...)` on `192.168.1.20`
- provisional Vulkan KHR Ray-Tracing backend via `rt.run_vulkan(...)`

## Current supported workloads:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

Current v0.1 application slice:

- RayJoin-style workloads
- exact-source and bounded reproduction work on Embree
- first real-data OptiX validation on the Linux GPU host
- bounded PostGIS ground-truth closure on accepted Linux packages
- first bounded four-system `overlay-seed analogue` closure
- initial Vulkan KHR cross-vendor GPU backend kept as provisional code

Important current boundaries:

- precision is still `float_approx`
- RTDL does not claim robust/exact computational geometry yet
- the generated OptiX/CUDA skeleton path is not the trusted runtime path
- large-scale GPU scaling still needs further work
- current `overlay` is still a seed-generation analogue, not full polygon overlay materialization
- Vulkan backend is float32-only and still provisional pending stronger parity/scaling validation

## Project Goal

The whole-project goal is broader than RayJoin and broader than the currently
validated backends.

RTDL is intended to become a language and runtime system for non-graphical
ray-tracing applications across multiple backend families, including:

- CPU-based ray-tracing libraries such as Intel Embree
- NVIDIA OptiX/CUDA-based GPU backends
- Vulkan KHR ray-tracing-based GPU backends
- AMD HIP RT-based backends

## Roadmap

- [v0.1 Roadmap](docs/v0_1_roadmap.md)
