# Goal 178 Claude 4K Windows Review Handoff

Please review the Windows 4K visual-demo code path and the observed failure
pattern for repo accuracy and likely technical causes.

Primary files to read:

- [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py)
- [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)
- [goal_173_windows_4k_movie_acceptance.md](/Users/rl2025/rtdl_python_only/docs/goal_173_windows_4k_movie_acceptance.md)
- [goal173_windows_4k_movie_acceptance_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal173_windows_4k_movie_acceptance_2026-04-08.md)
- [goal173_windows_4k_movie_acceptance_review_2026-04-08.md](/Users/rl2025/rtdl_python_only/docs/reports/goal173_windows_4k_movie_acceptance_review_2026-04-08.md)

Important current code facts:

- the current two-star line uses:
  - same warm-yellow family for both stars
  - horizontal equator flight
  - full in-and-out pass
  - optional `phase_mode`
- new `phase_mode="uniform"` was added to avoid weighted sampling causing the
  clip to appear to end too quickly after the stars meet

Important observed Windows behavior:

- finished single-star Windows 4K artifact already exists and was accepted:
  - [4K MP4](/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_4k_10s_32fps_yellow_jobs8/win_embree_earthlike_4k_10s_32fps_yellow_jobs8.mp4)
- but repeated Windows two-star 4K runs did not finish cleanly
- known Windows two-star directories:
  - `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_two_star_yellow_red_jobs8`
  - `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_two_star_yellow_red_jobs8_clean`
  - `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_two_star_yellow_red_jobs8_foreground`
- directory status observed:
  - plain `jobs8`:
    - `ppm=0`
    - `summary.json = false`
  - `jobs8_clean`:
    - `ppm=85`
    - `summary.json = false`
  - `jobs8_foreground`:
    - `ppm=88`
    - `summary.json = false`
- so the two-star 4K runs produced partial frame sets but no final summary or
  packaged movie
- there was no active Windows Python process afterward

Important HD follow-up context:

- a safer HD rerun target is now being attempted:
  - `1024 x 1024`
  - `320` frames
  - `embree`
  - intended `jobs=12`
- but current Windows process observation suggests only one Python process is
  visible, so the frame-level multiprocessing path may not actually be
  materializing correctly in the current Windows launch method

What to review:

1. likely reasons the Windows two-star 4K path fails repeatedly
2. whether the problem looks more like:
   - Python multiprocessing / Windows spawn behavior
   - launch/orchestration fragility
   - memory/resource pressure
   - code-level bug in the render loop
3. whether the current `jobs` behavior on Windows looks trustworthy
4. what the safest next fix should be before trusting another long Windows run

Return exactly three short sections titled:

- Verdict
- Findings
- Summary
