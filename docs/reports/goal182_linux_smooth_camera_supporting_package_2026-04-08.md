# Goal 182 Report: Linux Smooth-Camera Supporting Package

Date: 2026-04-08

## Objective

Record the Linux OptiX and Vulkan smooth-camera preview artifacts as the bounded supporting backend package for the end of the `v0.3` line.

## Source Goal

- [goal_182_linux_smooth_camera_supporting_package.md](/Users/rl2025/rtdl_python_only/docs/goal_182_linux_smooth_camera_supporting_package.md)

## Inputs

This package is built on the already-executed Goal 179 smooth-camera Linux validation slice.

Key files in scope:

- [rtdl_smooth_camera_orbit_demo.py](/Users/rl2025/rtdl_python_only/examples/rtdl_smooth_camera_orbit_demo.py)
- [goal178_smooth_camera_orbit_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py)
- [goal179_smooth_camera_linux_backend_test.py](/Users/rl2025/rtdl_python_only/tests/goal179_smooth_camera_linux_backend_test.py)

## Validation Host

- Linux:
  - `lestat@192.168.1.20`

## Verification Base

Linux backend builds:

- `make build-vulkan`
- `make build-optix`

Focused test slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`

Recorded result:

- `Ran 11 tests`
- `OK`

## Supporting Artifacts

### OptiX

- artifact summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/summary.json)
- preview frame:
  - [frame_004.png](/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/frame_004.png)

Key facts:

- backend:
  - `optix`
- size:
  - `192 x 192`
- frames:
  - `8`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`
- frame `0` compare backend:
  - `cpu_python_reference`
  - `matches = true`
- `query_share = 0.5202295155002821`

### Vulkan

- artifact summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/summary.json)
- preview frame:
  - [frame_004.png](/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/frame_004.png)

Key facts:

- backend:
  - `vulkan`
- size:
  - `192 x 192`
- frames:
  - `8`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`
- frame `0` compare backend:
  - `cpu_python_reference`
  - `matches = true`
- `query_share = 0.5202198855279668`

## Honesty Boundary

- these are supporting Linux backend artifacts
- the Windows Embree movie path remains the flagship public surface
- RTDL remains the geometric-query core
- Python remains responsible for camera motion, shading, blending, and media output
