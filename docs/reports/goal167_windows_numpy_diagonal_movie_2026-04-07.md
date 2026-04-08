Goal 167 report

Result

- Goal 167 is the first Windows Embree Earth-like movie slice that combines:
  - the diagonal upper-right-to-lower-left light sweep
  - the reviewed optional NumPy host-side fast path
  - a final copied-back movie artifact

Code changes

- `/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py`
  - added optional NumPy imports
  - added NumPy background generation
  - added NumPy vectorized per-hit shading
  - preserved the diagonal light path in `_frame_light`
  - preserved array copies in `_render_orbit_frame` so the NumPy fast path is actually reachable
- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`
  - `_write_ppm` now accepts either nested Python pixels or a NumPy image buffer
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
  - summary contract now records `numpy_fast_path`

Review and fix loop

- Claude review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal167_external_review_claude_2026-04-07.md`
- Claude found one real issue:
  - the NumPy shading path was initially unreachable because `_render_orbit_frame` converted the background array into a plain list before dispatch
- Fix applied:
  - preserve NumPy backgrounds with `source_image.copy()` instead of forcing a list conversion

Verification

- local fallback test:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 8 tests`
  - `OK`
- local isolated NumPy smoke:
  - `/tmp/rtdl_numpy_demo`
  - summary showed `numpy_fast_path = true`
- Windows NumPy smoke:
  - `64x64`
  - `2` frames
  - backend `embree`
  - compare backend `cpu_python_reference`
  - parity matched
  - summary showed `numpy_fast_path = true`

Final Windows run

- host:
  - `lestat@192.168.1.14`
- output dir on Windows:
  - `C:\\Users\\Lestat\\rtdl_python_only_win\\build\\win_embree_earthlike_10s_32fps_diag_numpy_1024`
- copied-back local dir:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024`
- settings:
  - `1024 x 1024`
  - `320` frames
  - `96 x 192` bands
  - `jobs = 12`

Final numbers

- `frame_count = 320`
- `triangle_count = 36480`
- `numpy_fast_path = true`
- `wall_clock_seconds = 712.3156405999325`
- `query_share = 0.1541423629457797`

Artifacts

- movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/win_embree_earthlike_10s_32fps_diag_numpy_1024.gif`
- representative frame:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/frame_180.png`
- summary:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/summary.json`

Honesty boundary

- This is a user-facing visual demo line, not a claim that RTDL has become a general rendering system.
- RTDL still owns the geometric-query work and Python still owns the scene/shading/media layer.
- Even with the NumPy fast path, Python-side work remains the larger share of total wall time on this Windows Embree movie.
