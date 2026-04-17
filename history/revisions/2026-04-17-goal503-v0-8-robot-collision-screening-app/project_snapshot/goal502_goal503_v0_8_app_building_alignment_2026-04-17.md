# Goal502/Goal503 v0.8 App-Building Alignment

Date: 2026-04-17

## Decision

The app work that started after Goal499 is the beginning of `v0.8`.

`v0.8` is not primarily a new primitive-design release. Its working theme is:

- build apps using existing RTDL language features
- keep Python responsible for app orchestration, data shaping, domain logic, and
  reporting
- let RTDL own the reusable query kernel rows
- add new RTDL features only when app implementation proves a reusable gap

## Goals Covered

Goal502:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- App pattern: point sets become `knn_rows(k=1)` nearest-neighbor rows; Python
  reduces those rows to directed and undirected Hausdorff distances.
- Version interpretation: `v0.8` app-building goal, even though the structured
  history round was initially recorded under the then-current `v0.7.0` line.

Goal503:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`
- App pattern: robot link edge rays and obstacle triangles become
  ray/triangle hit-count rows; Python maps those rows back to pose/link
  collision flags.
- Version interpretation: `v0.8` app-building goal.

## History Note

The pushed Goal502 history entry is not rewritten. This note corrects the
release-line interpretation going forward: Goal502 and later paper-derived app
work should be read as `v0.8` development work built on top of the released
`v0.7.0` language/runtime surface.
