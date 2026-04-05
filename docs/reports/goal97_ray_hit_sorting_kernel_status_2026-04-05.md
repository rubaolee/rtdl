# Goal 97 Status: Ray-Hit Sorting Kernel

Date: 2026-04-05
Status: ready for review and publish

## Added

- RTDL example kernel and helpers:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_goal97_ray_hit_sorting.py`
- demo script:
  - `/Users/rl2025/rtdl_python_only/scripts/goal97_ray_hit_sorting_demo.py`
- test suite:
  - `/Users/rl2025/rtdl_python_only/tests/goal97_ray_hit_sorting_test.py`

## Current acceptance target

- correctness and portability first
- stable duplicate handling
- CPU/python/native parity first
- backend parity on available backends for the small accepted cases

## Current result

- local example, demo script, and test suite exist
- local validation passes
- Linux available-backend validation passes
- accepted small duplicate-containing case is parity-clean across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `vulkan`
  - `optix`
- Goal 97 exposed and repaired one real OptiX `lsi` backend issue in:
  - `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`

## Remaining step

- final external review
- then publish as a correctness/demo RTDL goal
