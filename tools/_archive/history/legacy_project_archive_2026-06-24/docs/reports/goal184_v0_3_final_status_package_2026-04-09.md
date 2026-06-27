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

- [RTDL Visual Demo Video](https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes)

This is the front-door artifact readers should see first.

Current preserved public-facing local counterpart:

- [win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4](../../build/windows_goal168_import/goal168_hidden_star_rtdl_shadow_handoff_2026-04-09/artifacts/1024/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4)

## Strongest Preserved Local Review Artifacts

### Hidden-Star Stable RTDL-Shadow Baseline

This preserved local baseline should be read as the bridge from the released
`v0.2.0` core into the newer `v0.3` application/demo layer:

- `v0.2.0` remains the stable workload/package release on `main`
- `v0.3` shows that the same RTDL core can sit inside Python-hosted graphics applications

- [win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4](../../build/windows_goal168_import/goal168_hidden_star_rtdl_shadow_handoff_2026-04-09/artifacts/1024/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4)
- [summary.json](../../build/windows_goal168_import/goal168_hidden_star_rtdl_shadow_handoff_2026-04-09/artifacts/1024/summary.json)

Key facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `1`
- light count:
  - `1`
- shadow mode:
  - `rtdl_light_to_surface`

The earlier smooth-camera and moving-star candidates remain preserved as
comparison history, but they are no longer the primary `v0.3` demo source.

### Full Local Comparison Set

- [v0_3_movie_comparison_sheet_2026-04-08.md](v0_3_movie_comparison_sheet_2026-04-08.md)

That sheet preserves the earlier Windows comparison candidates side by side.

## Linux Supporting Backend Package

The bounded Linux supporting package is now explicit and review-backed.

Current selected supporting artifacts for the same hidden-star line:

- OptiX:
  - [goal168_hidden_star_optix_256.mp4](../../build/goal168_hidden_star_optix_256/goal168_hidden_star_optix_256.mp4)
  - [summary.json](../../build/goal168_hidden_star_optix_256/summary.json)
- Vulkan:
  - [goal168_hidden_star_vulkan_256.mp4](../../build/goal168_hidden_star_vulkan_256/goal168_hidden_star_vulkan_256.mp4)
  - [summary.json](../../build/goal168_hidden_star_vulkan_256/summary.json)

Why these are the preserved Linux movies:

- they use the same hidden-star RTDL-shadow design as the current main Windows demo source
- they are good enough to show the Linux OptiX/Vulkan backend application story for the same user-level scene
- they are not being presented as equally polished flagship movies

## Honesty Boundary

This final `v0.3` package does not claim:

- that RTDL is a general rendering engine
- that all movie variants are equally polished
- that the moving-light blinking problem is perfectly solved
- that all backends are equally mature for public movie delivery

What it does claim is narrower and true:

- RTDL can serve as the heavy geometric-query core in real Python-hosted graphics/demo applications
- Linux backend closure for the bounded 3D demo surface is real
- Windows Embree movie production is real, with the hidden-star RTDL-shadow Earth movie as the current public-facing artifact
- supporting OptiX and Vulkan Linux artifacts are real, but secondary and less polished than the Windows Embree artifact

## What Remains Future Work

- stronger visual art direction
- more complex RTDL-shadow scenes with real occluding geometry
- stronger cross-backend polish beyond the bounded hidden-star line
- any broader claim beyond the bounded `v0.3` demo/application scope
