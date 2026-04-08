# Codex Consensus: Goal 170 Linux Backend Small Demo Artifacts

## Verdict

Approve.

## Basis

- Goal 170 is bounded correctly:
  - small Linux demo artifacts only
  - no broad Linux performance or production-movie claim
- Vulkan had a real stronger-scene mismatch before this follow-up.
- That mismatch was fixed in:
  - [rtdl_vulkan.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp)
- The denser Linux Vulkan compare test now passes in:
  - [goal169_vulkan_orbit_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal169_vulkan_orbit_demo_test.py)
- Both Linux backends now have copied-back compare-clean artifact packages:
  - Vulkan:
    - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/summary.json)
    - [goal170_vulkan_orbit_medium_fix.gif](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/goal170_vulkan_orbit_medium_fix.gif)
  - OptiX:
    - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/summary.json)
    - [goal170_optix_orbit_small.gif](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/goal170_optix_orbit_small.gif)

## Honesty Boundary

- RTDL remains the geometric-query core.
- Python still owns scene setup, shading, and artifact generation.
- The Windows Embree MP4 remains the premier public visual artifact.
- Linux Vulkan and OptiX are now supported by small saved demo artifacts, not by
  a new claim of large Linux movie readiness.
