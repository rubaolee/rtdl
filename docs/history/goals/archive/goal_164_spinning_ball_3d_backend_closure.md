# Goal 164: Spinning-Ball 3D Backend Closure

## Why

Goal 161 chartered a real `v0.3` visual demo where RTDL owns the heavy
geometric-query work and Python owns scene setup, shading, and media output.

That charter is only convincing if the 3D ray-triangle path works on the real
backend surface, not just on `cpu_python_reference`.

## Goal

Close the first true 3D spinning-ball demo slice across:

- `cpu_python_reference`
- `embree`
- `optix`
- `vulkan`

with deterministic row-level parity on Linux.

## Scope

This goal covers:

- public RTDL 3D ray/triangle records and layouts
- runtime packing and dispatch for 3D `ray_triangle_hit_count`
- native 3D backend entry points for Embree, OptiX, and Vulkan
- the spinning-ball 3D demo
- deterministic row-level backend parity tests
- bounded Linux smoke renders against the same 3D demo path

This goal does not claim:

- a general rendering system
- a broad new 3D language surface beyond this ray/triangle line
- optimized Vulkan 3D performance maturity

## Acceptance

- the 3D spinning-ball demo exists and runs on `cpu_python_reference`
- Linux row-level parity passes for:
  - `embree`
  - `optix`
  - `vulkan`
  against `cpu_python_reference`
- the parity test covers:
  - a trivial one-ray/one-triangle case
  - a medium sphere-mesh case
  - the actual demo-scene ray/triangle pack
- bounded Linux smoke renders report per-frame parity against
  `cpu_python_reference`
- review coverage includes at least one Claude or Gemini review before closure
