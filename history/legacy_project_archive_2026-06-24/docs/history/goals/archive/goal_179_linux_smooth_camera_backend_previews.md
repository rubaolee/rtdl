# Goal 179: Linux Smooth Camera Backend Previews

## Why

Goal 178 introduced a smoother camera-orbit demo shape to replace the flicker-prone moving-light composition. Goal 179 extends that new demo to the Linux GPU backend paths so OptiX and Vulkan can both demonstrate the same smoother scene with bounded, compare-clean preview artifacts.

## Scope

- keep the smooth camera-orbit demo shape from Goal 178
- prove the new demo on Linux:
  - `optix`
  - `vulkan`
- accept only small bounded preview artifacts
- add a focused Linux backend regression module authored from the Claude flow
- verify compare-clean frame `0` parity against `cpu_python_reference`

## Success Criteria

- Linux backend builds succeed
- focused Linux backend test slice passes
- both Linux backend preview summaries record:
  - frame `0` compare backend
  - `matches = true`
- docs/review language remains explicit that these are supporting backend artifacts, not the flagship public movie path

## Out of Scope

- replacing the Windows Embree path as the main delivery surface
- claiming final polished Linux movie quality
- changing RTDL backend semantics
