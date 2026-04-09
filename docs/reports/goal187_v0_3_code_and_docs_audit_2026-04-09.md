# Goal 187 Report: v0.3 Code And Docs Audit

Date: 2026-04-09

## Objective

Audit the current bounded `v0.3` code and live docs together, then verify the line with unit tests plus tiny system-smoke checks rather than long render reruns.

## Files In Scope

Code:

- [rtdl_smooth_camera_orbit_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_smooth_camera_orbit_demo.py)
- [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py)

Tests:

- [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)
- [goal178_smooth_camera_orbit_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py)
- [goal179_smooth_camera_linux_backend_test.py](/Users/rl2025/rtdl_python_only/tests/goal179_smooth_camera_linux_backend_test.py)
- [goal187_v0_3_audit_test.py](/Users/rl2025/rtdl_python_only/tests/goal187_v0_3_audit_test.py)

Live docs:

- [README.md](/Users/rl2025/rtdl_python_only/README.md)
- [docs/README.md](/Users/rl2025/rtdl_python_only/docs/README.md)
- [current_milestone_qa.md](/Users/rl2025/rtdl_python_only/docs/current_milestone_qa.md)

## Code/Doc Consistency Fixes Made

The main live-doc inconsistency found was that the docs still described the orbiting-star demo as the stronger current example even though the selected `v0.3` flagship baseline is now the true one-light smooth-camera movie.

Fixes applied:

- [README.md](/Users/rl2025/rtdl_python_only/README.md)
  - now points readers to the preserved smooth-camera baseline first
  - still preserves the orbit demo as the comparison path
- [docs/README.md](/Users/rl2025/rtdl_python_only/docs/README.md)
  - now names the smooth-camera demo as the preserved flagship baseline
  - still keeps the orbit demo visible as the moving-light comparison path
- [current_milestone_qa.md](/Users/rl2025/rtdl_python_only/docs/current_milestone_qa.md)
  - now distinguishes the smooth-camera baseline from the orbit comparison example

## New Audit Test Module

Added:

- [goal187_v0_3_audit_test.py](/Users/rl2025/rtdl_python_only/tests/goal187_v0_3_audit_test.py)

This module checks:

- live front-surface docs use the current Shorts URL
- live docs point to the smooth-camera baseline
- the smooth-camera CLI runs a tiny one-light system smoke
- the orbit CLI runs a tiny support-star system smoke

## Local Verification

Compile check:

- `python3 -m compileall examples/visual_demo/rtdl_orbiting_star_ball_demo.py examples/visual_demo/rtdl_smooth_camera_orbit_demo.py tests/goal166_orbiting_star_ball_demo_test.py tests/goal178_smooth_camera_orbit_demo_test.py tests/goal179_smooth_camera_linux_backend_test.py tests/goal187_v0_3_audit_test.py`

Bounded local test slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test tests.goal187_v0_3_audit_test`

Result:

- `Ran 43 tests in 1.173s`
- `OK`
- `10 skipped`

## Linux Verification

Validation host:

- `lestat@192.168.1.20`

Bounded backend/build slice:

- `make build-vulkan`
- `make build-optix`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test tests.goal178_smooth_camera_orbit_demo_test tests.goal179_smooth_camera_linux_backend_test`

Result:

- `Ran 39 tests in 2.738s`
- `OK`
- `1 skipped`

Observed note:

- Python `multiprocessing` on Linux emitted a fork deprecation warning in one test path
- this did not cause a failure
- it is not treated as a correctness issue for the bounded `v0.3` audit

## Honesty Boundary

- this audit does not claim new renderer maturity
- it does not claim the moving-light blinking problem is solved
- it does confirm that the current `v0.3` code, tests, and live docs are materially aligned under the bounded demo/application story
