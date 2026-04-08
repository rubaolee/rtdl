# Goal 176 Report: Linux GPU Backend Test Execution

## Result

Goal 176 succeeded.

The Linux OptiX and Vulkan regression surface for the `v0.3` orbiting-star 3D
demo is now materially stronger than the earlier smoke-only state.

## Implemented Test Expansion

New regression module:

- [goal176_linux_gpu_backend_regression_test.py](/Users/rl2025/rtdl_python_only/tests/goal176_linux_gpu_backend_regression_test.py)

It adds bounded regression coverage for:

- Vulkan two-frame compare parity on a denser scene
- OptiX two-frame compare parity on a denser scene
- top-level summary metadata:
  - `light_count = 2`
  - `show_light_source = true`
  - non-zero `temporal_blend_alpha`

## Linux Execution Platform

- host:
  - `lestat@192.168.1.20`
- fresh execution clone:
  - `/home/lestat/work/rtdl_goal176_gpu_tests`

## Linux Build And Test Result

Commands:

- `make build-vulkan`
- `make build-optix`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_vulkan_orbit_demo_test tests.goal169_optix_orbit_demo_test tests.goal176_linux_gpu_backend_regression_test`

Result:

- `Ran 29 tests in 17.368s`
- `OK`
- `1 skipped`

## Saved Medium Compare Evidence

Vulkan:

- [summary.json](/Users/rl2025/rtdl_python_only/build/goal176_vulkan_medium/summary.json)
- [frame_000.ppm](/Users/rl2025/rtdl_python_only/build/goal176_vulkan_medium/frame_000.ppm)

Key facts:

- `backend = vulkan`
- `128 x 128`
- `2` frames
- compare frame `0` vs `cpu_python_reference`:
  - `matches = true`
- `light_count = 2`
- `show_light_source = true`
- `temporal_blend_alpha = 0.15`

OptiX:

- [summary.json](/Users/rl2025/rtdl_python_only/build/goal176_optix_medium/summary.json)
- [frame_000.ppm](/Users/rl2025/rtdl_python_only/build/goal176_optix_medium/frame_000.ppm)

Key facts:

- `backend = optix`
- `128 x 96`
- `2` frames
- compare frame `0` vs `cpu_python_reference`:
  - `matches = true`
- `light_count = 2`
- `show_light_source = true`
- `temporal_blend_alpha = 0.15`

## Boundary

- this strengthens the Linux GPU regression surface for the 3D demo
- it does not claim Linux GPU movie polish parity with the Windows Embree ad
  artifact
- it does not change the RTDL/Python architecture boundary
