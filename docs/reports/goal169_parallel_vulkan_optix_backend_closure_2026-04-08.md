# Goal 169 Report

## Summary

Goal 169 closes two parallel backend targets for the `v0.3` orbiting-star 3D
demo line on the primary Linux host `lestat@192.168.1.20`:

- Vulkan orbit-demo rendering
- OptiX 4K-oriented orbit-demo rendering

Both now have:

- backend-facing code in `main`
- focused tests in `main`
- fresh Linux build evidence
- one-frame render parity against `cpu_python_reference`

## Main Code Surface

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal169_optix_orbit_demo_test.py`

## Linux Validation

Fresh Linux goal directories:

- `/home/lestat/work/rtdl_v03_vulkan_goal169`
- `/home/lestat/work/rtdl_v03_optix_goal169`

Vulkan:

- `make build-vulkan`: success
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_vulkan_orbit_demo_test`
  - `Ran 15 tests`
  - `OK`
  - `1 skipped`
- one-frame orbit render:
  - backend: `vulkan`
  - compare backend: `cpu_python_reference`
  - `matches = true`

OptiX:

- `make build-optix`: success
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal169_optix_orbit_demo_test`
  - `Ran 14 tests`
  - `OK`
  - `1 skipped`
- one-frame orbit render:
  - backend: `optix`
  - compare backend: `cpu_python_reference`
  - `matches = true`

Local copies of those Linux smoke summaries are saved at:

- `/Users/rl2025/rtdl_python_only/build/goal169_vulkan_orbit_smoke/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal169_optix_orbit_smoke/summary.json`

## Main Results

Vulkan smoke:

- backend: `vulkan`
- `64 x 64`
- `1` frame
- `528` triangles
- compare match: `true`
- query share: `0.43573593750226186`
- wall clock: `1.5316750510000006`

OptiX smoke:

- backend: `optix`
- `64 x 64`
- `1` frame
- `528` triangles
- compare match: `true`
- query share: `0.4579661229238248`
- wall clock: `1.5145708199999959`

## Windows Status Note

The Windows Embree `4K` movie line remains separate ongoing work.

Current live state while this report is written:

- host: `lestat@192.168.1.8`
- output dir:
  - `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_yellow_jobs8`
- active Python workers:
  - `9`
- frames written so far:
  - `29`

That Windows work is not part of Goal 169 closure evidence.

## Honesty Boundary

This goal proves bounded backend closure for the orbiting-star RTDL demo line
on Linux for Vulkan and OptiX.  It does not claim:

- that RTDL is now a general rendering system
- that Vulkan or OptiX are the main public movie path
- that the Linux GPU line is now the premier polished artifact
