# Codex Consensus: Goal 166 Windows Earth-like 10s Demo

## Verdict

Approve.

Goal 166 is materially complete as a bounded `v0.3` visual-demo milestone.

## Why

The repo now has:

- a finished Windows Embree `10s` movie artifact
- a focused Earth-like demo program
- focused fast tests for the orbit demo
- a saved report that states the strongest path and limits honestly
- external review coverage from:
  - Claude code review
  - Gemini package/progress review

## Most Important Honest Boundaries

- this is a successful RTDL-plus-Python visual demo
- it is **not** a claim that RTDL is now a general rendering engine
- Windows Embree is the correct primary path for this demo line
- Python shading still dominates end-to-end runtime on the workstation
- Linux OptiX is not the delivery path for this movie

## Intake Notes

Claude found two real issues during this line:

1. ignored `spin_speed` in the older spinning demo
2. brittle shadow-ray ID scheme in the orbit demo

Both were fixed and the focused test surface was rerun cleanly.

## Final Position

Goal 166 should be treated as closed once the package files are staged together:

- `/Users/rl2025/rtdl_python_only/docs/goal_166_windows_earthlike_10s_demo.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_windows_earthlike_10s_demo_2026-04-07.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_windows_earthlike_10s_demo_review_2026-04-07.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_external_review_claude_2026-04-07.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal166_external_review_gemini_2026-04-07.md`
- `/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py`
