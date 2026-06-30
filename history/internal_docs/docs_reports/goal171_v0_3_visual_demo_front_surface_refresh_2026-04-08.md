# Goal 171 Report: v0.3 Visual Demo Front-Surface Refresh

## Summary

The `v0.3` visual-demo line now has a cleaner public story:

- the recommended public artifact remains the Windows Embree `softvis` MP4
- Linux OptiX and Vulkan now also have saved, compare-clean supporting GIF
  artifacts
- RTDL remains the geometric-query core and Python remains the scene/shading
  and media layer

## Recommended Public Artifact

- MP4:
  - [win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4)
- preview:
  - [frame_180.png](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/frame_180.png)

## Supporting Linux Backend Artifacts

- Vulkan:
  - [goal170_vulkan_orbit_medium_fix.gif](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/goal170_vulkan_orbit_medium_fix.gif)
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/summary.json)
- OptiX:
  - [goal170_optix_orbit_small.gif](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/goal170_optix_orbit_small.gif)
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/summary.json)

## What Is Proven

1. RTDL can serve as the geometric-query core inside a real application-style
   3D visual program.
2. The bounded 3D ray/triangle visual-demo backend surface is closed on Linux
   across:
   - `embree`
   - `optix`
   - `vulkan`
3. The current strongest polished public artifact is the Windows Embree MP4.
4. Linux OptiX and Vulkan now also have saved supporting GIF artifacts with
   compare-clean summaries against `cpu_python_reference`.

## Important Honesty Boundary

- The polished public movie path is still Windows Embree.
- Linux OptiX and Vulkan are now represented by small saved supporting
  artifacts, not by a competing Linux movie flagship.
- RTDL is still not being presented as a general rendering engine.
