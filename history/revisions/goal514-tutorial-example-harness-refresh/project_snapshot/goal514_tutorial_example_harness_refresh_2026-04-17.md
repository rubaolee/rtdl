# Goal 514: Tutorial/Example Harness Refresh

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal514 refreshes the older tutorial/example command harness so it matches the
current v0.8 app-building public surface. Goal513 added a narrow front-page
smoke test; Goal514 keeps the broader cross-platform command matrix aligned
with the newer examples and dependency boundaries.

## Changes Made

- Updated `/Users/rl2025/rtdl_python_only/scripts/goal410_tutorial_example_check.py`.
- Added Linux-gated command cases for the v0.8 app backends now advertised in
  public docs:
  - `examples/rtdl_hausdorff_distance_app.py --backend optix`
  - `examples/rtdl_hausdorff_distance_app.py --backend vulkan`
  - `examples/rtdl_robot_collision_screening_app.py --backend optix`
  - `examples/rtdl_barnes_hut_force_app.py --backend optix`
  - `examples/rtdl_barnes_hut_force_app.py --backend vulkan`
- Added explicit Python-module dependency gating for the chunked video example:
  - `imageio`
  - `imageio_ffmpeg`
- Added `/Users/rl2025/rtdl_python_only/tests/goal514_tutorial_example_harness_refresh_test.py`.

## Reasoning

The broad tutorial/example harness should not fail a local source-tree check
just because optional video-packaging dependencies are missing from the current
interpreter. Those dependencies are declared in `requirements.txt`, but the
harness is also used during partial local audits; explicit skip accounting is a
more honest result than a runtime crash.

The v0.8 app commands must also be present in the broader harness because
release-facing docs now advertise Linux OptiX/Vulkan app backend commands for
Hausdorff and Barnes-Hut, and Linux OptiX for robot collision screening.

## Validation

Command:

```bash
python3 scripts/goal410_tutorial_example_check.py --machine local-goal514 --output build/goal514_tutorial_example_check.json
```

Result: `37 passed`, `0 failed`, `12 skipped`, `49 total`.

Local skip reasons:

- `linux_only`: 11 cases
- `missing_python_module_imageio`: 1 case

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal514_tutorial_example_harness_refresh_test tests.goal513_public_example_smoke_test -v
```

Result: `Ran 5 tests`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile scripts/goal410_tutorial_example_check.py tests/goal514_tutorial_example_harness_refresh_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal514 is accepted. The broader tutorial/example command harness is refreshed
for the current v0.8 app-building public surface.

## AI Review Consensus

- Claude review: `APPROVED`; all five new Linux-gated v0.8 app backend cases
  are present with correct args/backend requirements, and the optional video
  dependency skip is clean and honest.
- Gemini Flash review: `ACCEPT`; the harness includes the public v0.8
  OptiX/Vulkan app commands and handles optional video dependencies with
  explicit skips.
- Codex conclusion: `ACCEPT`; Goal514 closes the broader harness drift that
  Goal513's narrower front-page smoke test intentionally did not cover.
