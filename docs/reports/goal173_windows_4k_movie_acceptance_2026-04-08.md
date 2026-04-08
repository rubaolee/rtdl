# Goal 173 Report: Windows 4K Movie Acceptance

## Result

Goal 173 succeeded.

The finished Windows Embree 4K movie artifact is now accepted as-is as a real
`v0.3` output.

## Artifact

- MP4:
  - [win_embree_earthlike_4k_10s_32fps_yellow_jobs8.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_4k_10s_32fps_yellow_jobs8/win_embree_earthlike_4k_10s_32fps_yellow_jobs8.mp4)
- preview:
  - [frame_180.png](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_4k_10s_32fps_yellow_jobs8/frame_180.png)
- run summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_4k_10s_32fps_yellow_jobs8/summary.json)

## Run Facts

- host:
  - `lestat@192.168.1.8`
- backend:
  - `embree`
- size:
  - `3840 x 2160`
- frames:
  - `320`
- jobs:
  - `8`
- wall clock:
  - `4560.900055999999 s`
- query share:
  - `0.13930404469895155`

## Important Honesty Note

The movie is accepted as-is, not as a perfect final cinematic artifact.

There is still a visible left-bottom dark blink in some frames. The current
understanding is:

- it is a scene/light temporal artifact
- not a codec/container issue
- and not a claim that the render is fully polished

This acceptance therefore means:

- the 4K artifact is real
- the repo may present it as a finished output
- but the remaining temporal artifact is still honestly acknowledged

## Boundary

- RTDL remains the geometric-query core
- Python remains responsible for scene, shading, and media output
