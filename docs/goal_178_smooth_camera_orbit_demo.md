# Goal 178: Smooth Camera Orbit Demo

## Why

The moving-star variants produced visible temporal blinking in dark regions, especially near the lower-left ground/ball transition. The next bounded experiment is to keep RTDL as the geometric-query core while replacing moving-light drama with smoother camera motion.

## Scope

- add a new Python demo:
  - `examples/rtdl_smooth_camera_orbit_demo.py`
- keep RTDL responsible for:
  - primary ray/triangle query work
  - shadow ray/triangle query work
- keep Python responsible for:
  - camera motion
  - fixed-light scene composition
  - shading
  - image/video packaging
- add focused tests for:
  - camera path shape
  - fixed-light structure
  - local render smoke
  - backend wrapper behavior
- produce a small preview artifact locally
- produce a Windows Embree HD movie if the new motion model behaves better

## Success Criteria

- local focused test slice passes
- Windows smoke run succeeds
- the new motion model is visibly smoother than the moving-light two-star variant
- docs/review language remains explicit that this is an application-side demo refinement, not a new RTDL renderer claim

## Out of Scope

- claiming final cinematic perfection
- changing RTDL backend semantics
- replacing the current public YouTube surface before review and acceptance
