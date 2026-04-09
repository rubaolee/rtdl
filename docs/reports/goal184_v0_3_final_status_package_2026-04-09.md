# Goal 184 Report: v0.3 Final Status Package

Date: 2026-04-09

## Objective

Summarize the final bounded `v0.3` state of the RTDL visual-demo line.

## What v0.3 Proved

`v0.3` proved that RTDL can act as the geometric-query core inside real Python-hosted 3D demo applications.

Specifically:

- the bounded 3D ray/triangle demo surface was closed on Linux
- that closure covers:
  - `embree`
  - `optix`
  - `vulkan`
- Python successfully wrapped RTDL into real application logic for:
  - scene setup
  - animation
  - shading
  - temporal blending
  - image/video packaging
- Windows Embree produced real finished HD/4K movie artifacts

## Public-Facing Demo Surface

The chosen public-facing video surface is now:

- [RTDL Visual Demo Video](https://youtube.com/shorts/O07Mg5luap8)

This is the front-door artifact readers should see first.

## Strongest Preserved Local Review Artifacts

### True One-Light Smooth-Camera Baseline

This preserved local baseline should be read as the bridge from the released
`v0.2.0` core into the newer `v0.3` application/demo layer:

- `v0.2.0` remains the stable workload/package release on `main`
- `v0.3` shows that the same RTDL core can sit inside Python-hosted graphics applications

- [win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4](../../build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4)
- [frame_160.png](../../build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/frame_160.png)
- [summary.json](../../build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/summary.json)

Key facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- light count:
  - `1`
- query share:
  - `0.36087708147453185`

### Moving-Star Repair Candidate

- [win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4](../../build/win_embree_orbit_supportstar_hd_1024_uniform_320f/win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4)
- [frame_160.png](../../build/win_embree_orbit_supportstar_hd_1024_uniform_320f/frame_160.png)
- [summary.json](../../build/win_embree_orbit_supportstar_hd_1024_uniform_320f/summary.json)

Key facts:

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
- query share:
  - `0.1868590466889054`

### Full Local Comparison Set

- [v0_3_movie_comparison_sheet_2026-04-08.md](v0_3_movie_comparison_sheet_2026-04-08.md)

That sheet preserves the major Windows comparison candidates side by side.

## Linux Supporting Backend Package

The bounded Linux supporting package is now explicit and review-backed.

Main package:

- [goal_182_linux_smooth_camera_supporting_package.md](../goal_182_linux_smooth_camera_supporting_package.md)
- [goal182_linux_smooth_camera_supporting_package_2026-04-08.md](goal182_linux_smooth_camera_supporting_package_2026-04-08.md)

Supporting artifacts:

- OptiX:
  - [summary.json](../../build/goal179_optix_smooth_preview/summary.json)
- Vulkan:
  - [summary.json](../../build/goal179_vulkan_smooth_preview/summary.json)

Both Linux summaries record frame `0` compare-clean parity against `cpu_python_reference`.

## Honesty Boundary

This final `v0.3` package does not claim:

- that RTDL is a general rendering engine
- that all movie variants are equally polished
- that the moving-light blinking problem is perfectly solved
- that all backends are equally mature for public movie delivery

What it does claim is narrower and true:

- RTDL can serve as the heavy geometric-query core in real Python-hosted graphics/demo applications
- Linux backend closure for the bounded 3D demo surface is real
- Windows Embree movie production is real
- supporting OptiX and Vulkan Linux artifacts are real

## What Remains Future Work

- stronger visual art direction
- more stable and intuitive moving-light shots
- further temporal-polish work on the orbit-style line
- any broader claim beyond the bounded `v0.3` demo/application scope
