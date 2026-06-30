# Goal 182: Linux Smooth-Camera Supporting Package

## Why

Goal 179 proved that the newer smooth-camera demo shape runs compare-clean on the Linux GPU backend paths. Goal 182 is the packaging step that turns those bounded validation runs into explicit supporting `v0.3` artifacts instead of leaving them as only an execution note.

## Scope

- package the Linux smooth-camera backend previews as supporting `v0.3` artifacts
- include:
  - `optix`
  - `vulkan`
- require frame `0` compare-clean parity against `cpu_python_reference`
- keep these artifacts explicitly secondary to the Windows Embree flagship movie path
- preserve the RTDL/Python honesty boundary:
  - RTDL owns the geometric-query core
  - Python owns camera motion, shading, blending, and media output

## Artifact Set

### OptiX

- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_optix_smooth_preview/frame_004.png`

### Vulkan

- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal179_vulkan_smooth_preview/frame_004.png`

## Success Criteria

- both Linux preview artifacts are documented explicitly
- both summaries record:
  - `compare_backend = cpu_python_reference`
  - `matches = true` for frame `0`
- Linux validation stays clearly framed as supporting backend evidence, not the flagship public movie surface
- the package receives external review plus Codex consensus before closure

## Out of Scope

- replacing the Windows Embree movie as the main public artifact
- claiming final polished Linux movie quality
- reopening already-accepted backend correctness work
