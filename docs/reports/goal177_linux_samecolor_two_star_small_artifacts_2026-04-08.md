# Goal 177 Report: Linux Same-Color Two-Star Small Artifacts

## Result

Goal 177 succeeded.

The synchronized two-star Linux supporting artifacts now use one unified warm
yellow light family and a fully symmetric equator pass:

- OptiX:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal177_optix_two_star_equator_small/summary.json)
  - [frame_000.ppm](/Users/rl2025/rtdl_python_only/build/goal177_optix_two_star_equator_small/frame_000.ppm)
  - [goal177_optix_two_star_equator_small.gif](/Users/rl2025/rtdl_python_only/build/goal177_optix_two_star_equator_small/goal177_optix_two_star_equator_small.gif)
- Vulkan:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal177_vulkan_two_star_equator_small/summary.json)
  - [frame_000.ppm](/Users/rl2025/rtdl_python_only/build/goal177_vulkan_two_star_equator_small/frame_000.ppm)
  - [goal177_vulkan_two_star_equator_small.gif](/Users/rl2025/rtdl_python_only/build/goal177_vulkan_two_star_equator_small/goal177_vulkan_two_star_equator_small.gif)

## Code Change

The synchronized two-star scene changed in:

- [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py)
- [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)

The key change is:

- the secondary star remains present across the whole clip
- the secondary star now uses the same warm yellow family as the primary
- the secondary star remains slightly dimmer than the primary
- both stars now fly horizontally on the equator
- the two stars are mirrored left/right frame by frame

## Local Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 24 tests`
  - `OK`
  - `4 skipped`

## Linux Artifact Validation

### OptiX

- backend:
  - `optix`
- compare backend:
  - `cpu_python_reference`
- size:
  - `256 x 192`
- mesh:
  - `24 x 48`
- frames:
  - `16`
- frame `0` compare result:
  - `matches = true`
- light count:
  - `2`
- temporal blend alpha:
  - `0.15`

### Vulkan

- backend:
  - `vulkan`
- compare backend:
  - `cpu_python_reference`
- size:
  - `256 x 192`
- mesh:
  - `24 x 48`
- frames:
  - `16`
- frame `0` compare result:
  - `matches = true`
- light count:
  - `2`
- temporal blend alpha:
  - `0.15`

## Important Honesty Notes

- this goal is a visual-composition follow-up on top of the already-tested Linux
  backend line
- it does not replace the Windows Embree public movie path
- it does not claim Linux GPU parity for larger production-sized movies
- RTDL still owns the geometric-query work while Python still owns scene setup,
  shading, and media output
