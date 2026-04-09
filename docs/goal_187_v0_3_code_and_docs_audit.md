# Goal 187: v0.3 Code And Docs Audit

## Why

The `v0.3` line now has multiple preserved demo variants, multiple review packages, and a final status package. Before treating the line as closure-ready, the repo needs one bounded audit that checks:

- the active `v0.3` code paths
- the bounded unit and system-smoke coverage
- the live front-surface and milestone docs
- consistency between the selected flagship baseline and the live narrative

## Scope

- audit the current `v0.3` code paths:
  - `examples/rtdl_smooth_camera_orbit_demo.py`
  - `examples/rtdl_orbiting_star_ball_demo.py`
- audit the bounded `v0.3` tests:
  - orbit demo tests
  - smooth-camera tests
  - Linux smooth-camera backend tests
- add one dedicated audit test module for:
  - live-doc URL consistency
  - live-doc example consistency
  - tiny CLI/system smokes for the two main demo entrypoints
- run bounded local and Linux verification without long movie renders
- fix any live-doc/code inconsistencies found

## Success Criteria

- missing live-doc/code inconsistencies are corrected
- the new audit test module exists and passes
- bounded local verification passes
- bounded Linux verification passes
- the package receives external Claude review, external Gemini review, and Codex consensus

## Out of Scope

- rerunning long Windows movie production
- claiming final cinematic perfection
- reopening already-closed backend correctness goals
