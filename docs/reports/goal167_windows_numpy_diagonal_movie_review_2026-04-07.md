Goal 167 review note

Review coverage

- Claude review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal167_external_review_claude_2026-04-07.md`
- Gemini review:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal167_external_review_gemini_2026-04-07.md`

Most important review result

- Claude found one real issue:
  - the NumPy shading path was unreachable because the background image was converted into a list before dispatch
- that issue was fixed before the final Windows run

Post-fix verification basis

- local fallback tests:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `OK`
- local isolated NumPy smoke:
  - `numpy_fast_path = true`
- Windows NumPy smoke:
  - `64x64`
  - `2` frames
  - `embree` vs `cpu_python_reference`
  - parity clean
- final Windows movie:
  - `320` frames
  - `1024 x 1024`
  - `numpy_fast_path = true`

Closure

- the code slice is reviewed
- the real review finding is fixed
- the final artifact is rendered and copied back
- Goal 167 satisfies the project `2+` review rule
