# v0.3 Status Summary

Date: 2026-04-08

## Current Repo State

- current `main` head before the in-progress Goal 172 work:
  - `8fe24eb`
- released line:
  - `v0.2.0`
- active development line:
  - `v0.3`

## What Is Already Closed

### Visual-demo foundation

- Goal 161:
  - visual-demo charter
- Goal 164:
  - bounded 3D ray/triangle backend closure on Linux across:
    - `embree`
    - `optix`
    - `vulkan`

### Main public visual artifact

- Windows Embree remains the premier public movie path
- current recommended public artifact:
  - [win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4)

### Linux supporting artifacts

- Goal 170 is closed and online
- saved Linux GPU-supporting artifacts:
  - OptiX:
    - [goal170_optix_orbit_small.gif](/Users/rl2025/rtdl_python_only/build/goal170_optix_orbit_small/goal170_optix_orbit_small.gif)
  - Vulkan:
    - [goal170_vulkan_orbit_medium_fix.gif](/Users/rl2025/rtdl_python_only/build/goal170_vulkan_orbit_medium_fix/goal170_vulkan_orbit_medium_fix.gif)

### Front-surface refresh

- Goal 171 is closed and online
- the repo front surface now says clearly:
  - Windows Embree MP4 is the main public artifact
  - Linux OptiX/Vulkan GIFs are supporting artifacts
  - RTDL remains the geometric-query core while Python handles scene, shading,
    and media output

## Current In-Progress Goal

### Goal 172: Temporal Stability Option

Goal 172 is currently in progress and not yet committed.

Objective:

- add a bounded optional temporal blend to the orbiting-star demo to reduce
  abrupt frame-to-frame visual pops

Current code changes:

- [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py)
- [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)

What is already done for Goal 172:

- added optional:
  - `temporal_blend_alpha`
- default remains:
  - `0.0`
- added focused tests for:
  - PPM payload blending
  - file-level temporal blend behavior
  - summary persistence
- local verification passed:
  - `python3 -m compileall examples/rtdl_orbiting_star_ball_demo.py tests/goal166_orbiting_star_ball_demo_test.py`
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
    - `Ran 19 tests`
    - `OK`
    - `4 skipped`

Goal 172 preview artifact:

- [summary.json](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/summary.json)
- [frame_000.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_000.png)
- [frame_001.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_001.png)
- [frame_005.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_005.png)

Preview facts:

- backend:
  - `cpu_python_reference`
- size:
  - `96 x 96`
- frames:
  - `6`
- `temporal_blend_alpha`:
  - `0.2`
- `query_share`:
  - `0.550872244096217`

## Goal 172 Review State

- Gemini review is in progress from:
  - [GOAL172_GEMINI_ONE_SENTENCE_HANDOFF.md](/Users/rl2025/rtdl_python_only/docs/handoff/GOAL172_GEMINI_ONE_SENTENCE_HANDOFF.md)
- Codex consensus draft already exists:
  - [2026-04-08-codex-consensus-goal172-temporal-stability-option.md](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-08-codex-consensus-goal172-temporal-stability-option.md)
- Goal 172 docs already exist but are not yet committed:
  - [goal_172_temporal_stability_option.md](/Users/rl2025/rtdl_python_only/docs/goal_172_temporal_stability_option.md)
  - [goal172_temporal_stability_option_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal172_temporal_stability_option_2026-04-08.md)
  - [goal172_temporal_stability_option_review_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal172_temporal_stability_option_review_2026-04-08.md)

## Important Working Rules

- every goal must satisfy `2+` AI consensus before closure
- if Claude is unavailable, use Gemini first and retry patiently
- keep RTDL honesty explicit:
  - RTDL owns the geometric-query core
  - Python owns scene setup, shading, post-process, and media output
- do not overclaim polish work as backend or renderer maturity
