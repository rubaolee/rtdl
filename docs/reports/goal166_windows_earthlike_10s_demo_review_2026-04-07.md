# Goal 166 Review Note

## Package

- Goal:
  - `/Users/rl2025/rtdl_python_only/docs/goal_166_windows_earthlike_10s_demo.md`
- Report:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal166_windows_earthlike_10s_demo_2026-04-07.md`

## Main Evidence

- final Windows movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/win_embree_earthlike_10s_1024.gif`
- representative frame:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/frame_180.png`
- summary:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_1024/summary.json`

## Test Surface

- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal164_spinning_ball_3d_demo_test.py`

Combined local result:

- `python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal164_spinning_ball_3d_demo_test`
- `Ran 16 tests`
- `OK`
- `6 skipped`

## Important Honesty Notes

- the strongest current path is Windows Embree, not Linux OptiX
- the movie is real and complete
- Python shading still dominates end-to-end runtime on the Windows workstation
- the package claims a successful RTDL-plus-Python visual demo, not a full rendering-engine closure

## Review Intake

- Claude code review previously found:
  - ignored `spin_speed`
  - brittle shadow-ray ID scheme
- both issues were fixed before this package review note was finalized

Accepted saved external review artifacts for closure:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_external_review_claude_2026-04-07.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_external_review_gemini_2026-04-07.md`
