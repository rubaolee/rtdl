# Goal 175 Report: Two-Star 4K Variant

## Status

Goal 175 is in progress.

## Implemented So Far

- the orbiting-star demo now uses two lights per frame:
  - a primary yellow light that keeps the diagonal sweep
  - a delayed red secondary light that moves horizontally from left to right
- the render summary now records:
  - `light_count = 2`
- focused local tests were added for:
  - delayed red-light activation
  - left-to-right secondary-light motion
  - two-light summary metadata

## Preview Evidence

Preview run:

- backend:
  - `cpu_python_reference`
- size:
  - `96 x 96`
- frames:
  - `6`
- output:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/goal175_two_star_preview/summary.json)

Important preview signal:

- frame `0`: `shadow_rays = 6982`
- frame `2`: `shadow_rays = 13964`

That means the secondary light is not active at the beginning, then becomes
active later in the clip, which matches the intended design.

## Boundary

- RTDL remains the ray/triangle geometric-query core
- Python remains responsible for scene definition, light timing, shading,
  overlays, and media output
- this is a scene-level improvement, not a backend/runtime semantics change

## Current Windows Artifact Step

The full Windows Embree 4K artifact step is already running.

- host:
  - `lestat@192.168.1.8`
- render size:
  - `3840 x 2160`
- frames:
  - `320`
- jobs:
  - `8`
- temporal blend:
  - `0.15`
- remote output directory:
  - `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_two_star_yellow_red_jobs8_foreground`

Prepared Windows packaging script:

- `C:\Users\Lestat\win_encode_goal175_4k_mp4.py`

At the latest confirmed probe before final completion:

- the render was actively writing frames
- `88` frames were already present
- `summary.json` was not present yet, which is expected before the final write
