# Goal 170 Report: Linux Backend Small Demo Artifacts

## Result

Goal 170 succeeded.

Both Linux GPU-facing backends now have saved, copied-back small demo artifacts
for the orbiting-star 3D demo line:

- Vulkan:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/summary.json)
  - [frame_000.png](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/frame_000.png)
  - [goal170_vulkan_orbit_medium_fix.gif](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/goal170_vulkan_orbit_medium_fix.gif)
- OptiX:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/summary.json)
  - [frame_000.png](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/frame_000.png)
  - [goal170_optix_orbit_small.gif](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/goal170_optix_orbit_small.gif)

## Linux Host

- host:
  - `lestat@192.168.1.20`
- synced working tree:
  - `/home/lestat/work/rtdl_linux_progress`

## Validation

### Vulkan

- post-fix denser Linux test:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal169_vulkan_orbit_demo_test`
  - `Ran 2 tests`
  - `OK`
- stronger Linux compare run:
  - backend:
    - `vulkan`
  - compare backend:
    - `cpu_python_reference`
  - size:
    - `256 x 256`
  - mesh:
    - `24 x 48`
  - frames:
    - `2`
  - frame `0` compare result:
    - `matches = true`

### OptiX

- Linux small compare run:
  - backend:
    - `optix`
  - compare backend:
    - `cpu_python_reference`
  - size:
    - `256 x 256`
  - mesh:
    - `24 x 48`
  - frames:
    - `2`
  - frame `0` compare result:
    - `matches = true`

## Important Honesty Notes

- Goal 169 closed bounded Linux backend support with one-frame parity and tests.
- Goal 170 adds small saved Linux demo artifacts on top of that closure.
- The Linux GPU path is still not the premier public movie path.
- The Windows Embree MP4 remains the main polished visual artifact.
- RTDL remains the geometric-query core while Python still owns scene setup,
  shading, and media output.
