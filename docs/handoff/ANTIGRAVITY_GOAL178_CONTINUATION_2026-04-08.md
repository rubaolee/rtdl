# Antigravity Goal 178 Continuation

Continue Goal 178 from the current smooth camera-orbit state.

## Repo

- `/Users/rl2025/rtdl_python_only`

## Reminder

- reread `/Users/rl2025/refresh.md`
- every goal still needs `2+` AI consensus before closure

## Goal 178 Scope

- smoother application-side 3D demo
- fixed lights
- moving camera on a front-side arc
- keep RTDL as the geometric-query core
- reduce moving-light temporal instability

## Implemented Files

- `/Users/rl2025/rtdl_python_only/examples/rtdl_smooth_camera_orbit_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py`

## Current Docs

- `/Users/rl2025/rtdl_python_only/docs/goal_178_smooth_camera_orbit_demo.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal178_smooth_camera_orbit_demo_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal178_smooth_camera_orbit_demo_review_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL178_GEMINI_ONE_SENTENCE_HANDOFF.md`

## Verified State

Local tests:

- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`
- result:
  - `Ran 7 tests`
  - `OK`
  - `2 skipped`

Local preview:

- `/Users/rl2025/rtdl_python_only/build/goal178_smooth_camera_orbit_preview_small/summary.json`
- `/Users/rl2025/rtdl_python_only/build/goal178_smooth_camera_orbit_preview_small/frame_004.png`

Windows smoke:

- `64 x 64`
- `1` frame
- backend `embree`
- `jobs = 12`
- output:
  - `C:\Users\Lestat\rtdl_python_only_win\build\goal178_windows_smooth_diag`

Windows tests:

- `py -3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`
- result:
  - `Ran 7 tests`
  - `OK`
  - `2 skipped`

## Current Windows Production Run

Host:

- `lestat@192.168.1.8`

Output:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_smooth_camera_hd_1024_uniform_320f`

Settings:

- `1024 x 1024`
- `320` frames
- `jobs = 12`
- backend `embree`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`

At the last confirmed probe:

- output directory existed
- many Windows `python.exe` workers were visible
- no frames had landed yet

## Next Steps

1. wait until frames start appearing
2. wait for `summary.json`
3. package Windows MP4 using the existing Python `imageio` path once the render finishes
4. copy back:
   - MP4
   - preview PNG
   - summary
5. get external review
6. write Codex consensus
7. commit the bounded Goal 178 slice
