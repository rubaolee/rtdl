# Goal 166 Report: Windows Earth-like 10s Demo

## Result

The Earth-like Windows demo is now real and saved as a local movie artifact.

Primary artifact:

- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/win_embree_earthlike_10s_1024.gif`

Representative frame:

- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/frame_180.png`

Summary:

- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/summary.json`

Direct Windows folder:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_10s_1024`

## Final Scene

The accepted scene is:

- one large static dark-blue hero ball
- no visible tiny sun by default
- one moving sun-like light direction
- broad bright/dark sweep across the visible hemisphere
- moving ground-light cue

This is cleaner than the earlier spinning/swirling versions and reads more
like an Earth/day-night visual than a local spotlight test.

## Final Windows Run

From `summary.json`:

- backend:
  - `embree`
- frames:
  - `240`
- resolution:
  - `1024 x 1024`
- sphere mesh:
  - `36480` triangles
- jobs:
  - `12`
- wall clock:
  - `746.5615147999488`
- query share:
  - `0.14244960427330064`

Interpretation:

- the final movie is real and complete
- Windows Embree is the correct primary render path for this demo line
- Python shading still dominates total runtime on this workstation
- RTDL still provides the real geometric-query core, but this movie is not yet
  a “RTDL dominates end-to-end runtime” demonstration on the Windows box

## Comparison

Smaller apples-to-apples preview comparison:

- Windows Embree preview:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_preview_256_v2/summary.json`
  - `256 x 256`
  - `24` frames
  - `64 x 128` bands
  - `jobs = 8`
  - wall clock:
    - `12.165992899797857`

- Linux OptiX preview:
  - `/Users/rl2025/rtdl_python_only/build/linux_optix_earthlike_preview_256/summary.json`
  - `256 x 256`
  - `24` frames
  - `64 x 128` bands
  - `jobs = 1`
  - wall clock:
    - `148.5952258160105`

So for this demo as currently implemented:

- Windows Embree is much faster
- Linux OptiX is not the delivery path

## Code and Test Surface

Main demo:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py`

Supporting 3D file updated during this line:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`

Focused new tests:

- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`

Focused legacy 3D test slice rerun after Claude findings:

- `/Users/rl2025/rtdl_python_only/tests/goal164_spinning_ball_3d_demo_test.py`

Local test results:

- `python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `OK`
- `python3 -m unittest tests.goal164_spinning_ball_3d_demo_test`
  - `OK`

## Review Intake

Claude review found two real issues in the current local visual line:

1. `spin_speed` in the older spinning demo was ignored
2. the orbit demo shadow-ray ID scheme was brittle if expanded later

Both were fixed before this package report was finalized.

Saved Claude review artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_external_review_claude_2026-04-07.md`

## Honest Boundary

This goal does **not** claim:

- RTDL is now a general rendering engine
- the Windows movie is already fully optimized
- Linux OptiX is competitive for this demo line today

It **does** claim:

- the repo now has a real cinematic 3D RTDL-plus-Python demo artifact
- the strongest current execution path is Windows Embree
- the movie is technically real, saved, and reproducible from the current repo
