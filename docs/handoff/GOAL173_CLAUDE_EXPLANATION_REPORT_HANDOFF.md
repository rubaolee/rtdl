# Goal 173 Claude Explanation Report Handoff

Please write a concise explanation report for the current accepted Windows 4K
render program.

## Scope

- explain how the 4K render program works
- explain the RTDL versus Python responsibility split
- explain why Embree on Windows was the accepted backend path for the 4K movie
- explain the main runtime stages at a practical level
- explain the known remaining limitation honestly

## Important Boundary

- do not describe RTDL as a general rendering engine
- keep the explanation honest:
  - RTDL provides the geometric-query core
  - Python provides scene setup, shading, frame composition, temporal blend
    option, and media output

## Files To Read

- `/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py`
- `/Users/rl2025/rtdl_python_only/docs/goal_173_windows_4k_movie_acceptance.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal173_windows_4k_movie_acceptance_2026-04-08.md`
- `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_4k_10s_32fps_yellow_jobs8/summary.json`

## Output Requirements

Return a short markdown report with these exact section titles:

- `Overview`
- `Pipeline`
- `Runtime Split`
- `Known Limitation`

Keep it readable for project docs. Favor concrete explanation over marketing.
