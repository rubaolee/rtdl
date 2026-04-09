# Goal 190 Report: Visual Demo Example Reorganization

## Outcome

Completed.

The visual demo programs were moved out of the flat `examples/` root into
`examples/visual_demo/`, and the move was carried through across code, tests,
live docs, preserved reports, and handoff files.

## Moved Programs

- `examples/rtdl_smooth_camera_orbit_demo.py` -> `examples/visual_demo/rtdl_smooth_camera_orbit_demo.py`
- `examples/rtdl_orbiting_star_ball_demo.py` -> `examples/visual_demo/rtdl_orbiting_star_ball_demo.py`
- `examples/rtdl_orbit_lights_ball_demo.py` -> `examples/visual_demo/rtdl_orbit_lights_ball_demo.py`
- `examples/rtdl_lit_ball_demo.py` -> `examples/visual_demo/rtdl_lit_ball_demo.py`

## Code Fixes Required By The Move

- Updated the moved demo scripts to compute `REPO_ROOT` from the deeper package location.
- Updated smooth-camera imports so it now imports the orbit demo helpers from
  `examples.visual_demo.rtdl_orbiting_star_ball_demo`.
- Updated the move-affected tests to import the new module paths.
- Updated the Goal 187 audit test to use the current public Shorts URL.
- Updated the project-level audit script's special-case path handling for
  `rtdl_lit_ball_demo.py`.

## Documentation Sweep

Repo-wide stale references to the old flat demo paths were removed from:

- live docs
- reports
- handoff files
- tests
- one preserved historical Codex consensus note

The scan used for closure returned no remaining references to the old flat demo paths or
old `examples.rtdl_*` imports.

## Verification

Bounded checks passed:

- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal178_smooth_camera_orbit_demo_test tests.goal187_v0_3_audit_test`
  - `Ran 43 tests in 1.292s`
  - `OK`
  - `6 skipped`
- `PYTHONPATH=src:. python3 -m unittest tests.goal169_optix_orbit_demo_test tests.goal169_vulkan_orbit_demo_test tests.goal176_linux_gpu_backend_regression_test tests.goal179_smooth_camera_linux_backend_test`
  - `Ran 9 tests`
  - `OK`
  - `9 skipped`
- `python3 -m compileall examples/visual_demo tests/goal166_orbiting_star_ball_demo_test.py tests/goal169_optix_orbit_demo_test.py tests/goal169_vulkan_orbit_demo_test.py tests/goal176_linux_gpu_backend_regression_test.py tests/goal178_smooth_camera_orbit_demo_test.py tests/goal179_smooth_camera_linux_backend_test.py tests/goal187_v0_3_audit_test.py`
- direct CLI smoke:
  - `python3 examples/visual_demo/rtdl_smooth_camera_orbit_demo.py --backend cpu_python_reference --compare-backend cpu_python_reference --width 20 --height 20 --latitude-bands 6 --longitude-bands 12 --frames 2 --jobs 1 --temporal-blend-alpha 0.10 --phase-mode uniform --output-dir build/tmp_visual_demo_cli_smoke`
  - completed successfully and wrote `summary.json`

## Conclusion

This change improves repo structure without changing the public technical story.
The 3D demos now live in a directory that matches their role: application-style
visual proofs, not flat first-class workload examples.
