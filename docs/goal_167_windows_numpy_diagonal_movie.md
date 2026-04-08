Goal 167: Windows NumPy Diagonal Earth-like Movie

Purpose

- Continue the Windows Embree v0.3 visual-demo line after Goal 166.
- Add an optional NumPy host-side fast path for the orbiting-star Earth-like demo.
- Preserve the requested diagonal light sweep from upper-right to lower-left.
- Produce a new final Windows movie artifact from the reviewed code.

Acceptance

- The orbit demo keeps the static dark-blue hero ball.
- The visible light sweep reads diagonally, from upper-right toward lower-left.
- The Windows Embree run uses the NumPy host-side fast path.
- The new movie is rendered on `lestat@192.168.1.14` and copied back into the repo.
- Claude review is saved.
- Gemini review is saved.
- Codex consensus is saved.

Main files

- `/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`

Artifacts

- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/win_embree_earthlike_10s_32fps_diag_numpy_1024.gif`
- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/frame_180.png`
- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_1024/summary.json`
