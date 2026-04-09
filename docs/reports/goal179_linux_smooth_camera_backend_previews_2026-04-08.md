# Goal 179 Linux Smooth Camera Backend Previews

## Intent

Exercise the new smooth camera-orbit demo shape on Linux GPU backends with the same correctness-first standard used elsewhere in `v0.3`.

## Claude-Written Code

Claude was used for a bounded code-writing task:

- author a focused Linux backend unittest module for the new smooth camera-orbit demo

Claude-authored base file:

- `/Users/rl2025/rtdl_python_only/tests/goal179_smooth_camera_linux_backend_test.py`

Codex review applied one small cleanup before execution:

- removed an unused `json` import from Claude’s returned draft

## Files in Scope

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_smooth_camera_orbit_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal179_smooth_camera_linux_backend_test.py`

## Local Verification

- `python3 -m compileall tests/goal179_smooth_camera_linux_backend_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`

Result:

- `Ran 11 tests`
- `OK`
- `6 skipped`

## Linux Validation Host

- `lestat@192.168.1.20`

Backend builds:

- `make build-vulkan`
  - `VULKAN:0`
- `make build-optix`
  - `OPTIX:0`

Linux focused test slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`

Result:

- `Ran 11 tests`
- `OK`

## Linux Preview Artifacts

OptiX preview:

- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/frame_004.png`

OptiX facts:

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

Vulkan preview:

- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/frame_004.png`

Vulkan facts:

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

- these Linux previews are supporting backend artifacts
- the Windows Embree movie path remains the primary delivery surface
- RTDL still owns the geometric-query core
- Python still owns camera motion, shading, and media output
