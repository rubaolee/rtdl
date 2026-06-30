# Goal 185 Report: Orbit Support-Star Stability Candidate

Date: 2026-04-08

## Objective

Evaluate the repaired moving-star orbit composition as a serious candidate for the end of the `v0.3` visual-demo line.

## Composition

Current orbit design:

- one bright visible hero star
- one smaller support star aimed at the left-bottom danger zone
- support star fades out after the hero star has crossed far enough to stabilize the shot on its own

## Code in Scope

- [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py)
- [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)

## Verification Base

Local orbit test slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`

Result:

- `Ran 28 tests`
- `OK`
- `4 skipped`

Windows focused test slice after sync:

- `python -m unittest tests.goal166_orbiting_star_ball_demo_test`

Result:

- `Ran 28 tests`
- `OK`
- `3 skipped`

## Linux Backend Readiness

The same support/fill orbit idea has bounded Linux preview evidence and is kept runnable on:

- `optix`
- `vulkan`

Earlier copied summaries:

- [goal181_optix_orbit_fill_preview summary.json](/Users/rl2025/rtdl_python_only/build/goal181_optix_orbit_fill_preview/summary.json)
- [goal181_vulkan_orbit_fill_preview summary.json](/Users/rl2025/rtdl_python_only/build/goal181_vulkan_orbit_fill_preview/summary.json)

## Windows HD Candidate

Finished artifact:

- [win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4)
- [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/frame_160.png)
- [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/summary.json)

Run facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- light count:
  - `2`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`
- wall clock:
  - `910.8437880999991 s`
- query share:
  - `0.1868590466889054`

Artifact note:

- this candidate completed cleanly after switching away from the brittle detached launch wrapper
- the finished local review bundle is now copied back to the main repo

## Honesty Boundary

- this is still an experimental visual candidate
- the blinking problem should be judged by actual video review, not by intent alone
- RTDL remains the geometric-query core
- Python remains responsible for scene composition and media output
