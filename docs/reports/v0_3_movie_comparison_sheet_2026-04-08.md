# v0.3 Movie Comparison Sheet

Date: 2026-04-08

## Purpose

Collect the major finished Windows `v0.3` movie candidates in one place so the visual comparison is explicit instead of spread across thread history.

This sheet is for human review first:

- watch the movies
- compare temporal stability
- compare intuitive visual storytelling
- compare overall polish

## Candidate A: Warm-Fill Smooth Camera

- movie:
  - [win_embree_smooth_camera_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/win_embree_smooth_camera_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/frame_160.png)

![Warm-Fill Smooth Camera](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/frame_160.png)

Quick read:

- smoother than the earlier moving-light orbit line
- visually calmer
- still somewhat dim and less intuitive than the moving-star concept

## Candidate B: White-Fill Smooth Camera

- movie:
  - [win_embree_smooth_camera_whitefill_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/frame_160.png)

![White-Fill Smooth Camera](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/frame_160.png)

Quick read:

- brighter and cleaner than Candidate A
- still a two-light shot
- smoother, but not obviously the final flagship

## Candidate C: Pseudo-One-Star Smooth Camera

- movie:
  - [win_embree_smooth_camera_onestar_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/win_embree_smooth_camera_onestar_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/frame_160.png)

![Pseudo-One-Star Smooth Camera](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/frame_160.png)

Quick read:

- attempted to simplify the light story
- still has `light_count = 2`
- not acceptable as the true one-light answer the user asked for

## Candidate D: True One-Light Smooth Camera

- movie:
  - [win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/summary.json)

![True One-Light Smooth Camera](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/frame_160.png)

Quick read:

- this is the first candidate with `light_count = 1`
- it is the cleanest direct comparison against Candidate C
- it should answer whether the hidden second light was helping or simply muddying the shot

## Candidate E: Orbit Support-Star Repair

- movie:
  - [win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/win_embree_orbit_supportstar_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/summary.json)

![Orbit Support-Star Repair](/Users/rl2025/rtdl_python_only/build/win_embree_orbit_supportstar_hd_1024_uniform_320f/frame_160.png)

Quick read:

- this keeps the more intuitive fixed-camera flying-star story alive
- uses one hero moving star plus one smaller support star for the left-bottom danger zone
- it is the strongest current answer to the blinking problem without abandoning the moving-star concept
- it is still a visual candidate, not an already-accepted flagship

## Decision Standard

The eventual `v0.3` flagship movie should be whichever candidate best satisfies:

- temporal stability
- intuitive visual story
- visual polish
- honesty about remaining limits
