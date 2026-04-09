# Codex Windows v0.3 Follow-Up Handoff

Use this to continue independent Windows-side testing after the `v0.3` 3D-demo closure.

## Goal

Run bounded follow-up checks on the accepted Windows Embree flagship path without reopening the finished `v0.3` demo-selection work.

## Canonical Windows Host

- host:
  - `lestat@192.168.1.8`
- checkout:
  - `C:\Users\Lestat\rtdl_python_only_win`

SSH key auth from the Mac side is already configured and working.

## Accepted Public-Facing Artifact

- public Shorts URL:
  - `https://youtube.com/shorts/O07Mg5luap8`
- preserved local counterpart in the repo:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_192f_6s/win_embree_smooth_camera_true_onelight_hd_1024_uniform_192f_6s.mp4`

## Final Preserved Artifact Set

- Windows flagship:
  - `build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_192f_6s/win_embree_smooth_camera_true_onelight_hd_1024_uniform_192f_6s.mp4`
- Linux OptiX support:
  - `build/goal188_optix_smooth_camera_256_noblend/goal188_optix_smooth_camera_256_noblend_hq.mp4`
- Linux Vulkan support:
  - `build/goal188_vulkan_smooth_camera_256_noblend/goal188_vulkan_smooth_camera_256_noblend_hq.mp4`

Rejected later experiments:

- `build/goal188_optix_smooth_camera_256_ssaa2/goal188_optix_smooth_camera_256_ssaa2.mp4`
- `build/goal188_vulkan_smooth_camera_256_ssaa2/goal188_vulkan_smooth_camera_256_ssaa2.mp4`

Do not promote the rejected `ssaa2` Linux movies as the chosen support artifacts.

## RTDL / Python Boundary

Keep the honesty boundary explicit:

- RTDL owns:
  - geometric-query core
  - ray/triangle traversal / hit-count work
- Python owns:
  - scene setup
  - animation
  - shading
  - temporal blending
  - image/video output

The remaining quality issues are mostly demo/application-layer issues, not RTDL-core correctness issues, except for the already-fixed historical OptiX seam hit-count bug.

## Current Known Quality State

### Windows

- the `6s` cut is the best public-facing artifact
- `0–6s` is much cleaner than the longer tail
- the later part of the original longer movie showed mild whole-frame shimmer
- treat the `6s` cut as the accepted flagship unless a clearly better bounded replacement appears

### Linux

- OptiX and Vulkan both produced real support movies
- older HQ no-blend outputs were better than the later `ssaa2` experiments
- Linux support movies are secondary backend-proof artifacts, not equal-polish flagship claims

## Safe Independent Follow-Up Tests

Allowed:

- re-encode experiments on the Windows flagship frames
- bounded quality probes on the first `192` frames only
- tiny render smokes
- packaging tests
- diagnostic scripts that measure frame-to-frame brightness/contrast drift

Avoid:

- reopening the whole flagship selection unless a change is clearly better
- replacing the accepted public URL casually
- promoting Linux movies to flagship status

## Suggested Windows Follow-Up Tasks

1. measure frame-to-frame global brightness drift on the accepted `192`-frame cut
2. compare raw `PPM` frames against encoded MP4 frames to quantify compression shimmer
3. test higher-quality Windows MP4 encode parameters without changing scene logic
4. keep the accepted `6s` cut unless a new bounded encode is objectively cleaner

## Useful Files

- main final status package:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal184_v0_3_final_status_package_2026-04-09.md`
- main comparison sheet:
  - `/Users/rl2025/rtdl_python_only/docs/reports/v0_3_movie_comparison_sheet_2026-04-08.md`
- current smooth-camera code:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_smooth_camera_orbit_demo.py`
- current orbit comparison code:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py`
- bounded audit package:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal187_v0_3_code_and_docs_audit_2026-04-09.md`

## Definition of Done for This Follow-Up

Any Windows-side follow-up should end with one of these outcomes:

- confirm the accepted `6s` cut remains the best bounded artifact
- or produce a clearly better bounded Windows encode variant with concise evidence

Do not broaden back into a new open-ended demo-design cycle unless explicitly asked.
