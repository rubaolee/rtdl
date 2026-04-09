Goal 167 working note

Scope

- Continue the Windows Embree Earth-like v0.3 demo line.
- Add an optional NumPy host-side fast path to the orbit demo.
- Preserve the requested diagonal highlight path from upper-right to lower-left.
- Review with Claude before executing.

Code slice

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`

Local verification

- `python3 -m compileall examples/visual_demo/rtdl_orbiting_star_ball_demo.py examples/rtdl_spinning_ball_3d_demo.py tests/goal166_orbiting_star_ball_demo_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 8 tests`
  - `OK`

Claude review

- Saved at:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal167_external_review_claude_2026-04-07.md`
- Real finding:
  - the NumPy shading path was initially unreachable because `_render_orbit_frame` converted the background array into a plain list before dispatch
- Fix applied:
  - preserve the NumPy array via `source_image.copy()` when the background image is an array

NumPy smoke verification

- Local isolated venv:
  - `/tmp/rtdl_numpy_demo`
- NumPy-enabled smoke:
  - `render_orbiting_star_ball_frames(... width=32, height=32, frame_count=1 ...)`
  - summary showed:
    - `numpy_fast_path = true`

Windows execution prep

- Copied updated demo files to:
  - `C:\\Users\\Lestat\\rtdl_python_only_win\\examples`
- Copied local wheel to:
  - `C:\\Users\\Lestat\\Downloads\\numpy-2.4.4-cp311-cp311-win_amd64.whl`
- Installed NumPy on Windows from the copied wheel.

Windows smoke verification

- `64x64`
- `2` frames
- backend:
  - `embree`
- compare backend:
  - `cpu_python_reference`
- result:
  - `matches = true`
  - `numpy_fast_path = true`

Current long render

- Host:
  - `lestat@192.168.1.14`
- Output dir:
  - `C:\\Users\\Lestat\\rtdl_python_only_win\\build\\win_embree_earthlike_10s_32fps_diag_numpy_1024`
- Target:
  - `1024 x 1024`
  - `320` frames
  - `96 x 192` bands
  - `jobs = 12`
