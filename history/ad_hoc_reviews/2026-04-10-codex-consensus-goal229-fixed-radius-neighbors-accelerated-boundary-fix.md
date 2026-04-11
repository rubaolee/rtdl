# Codex Consensus: Goal 229 fixed_radius_neighbors Accelerated Boundary Fix

Date: 2026-04-10
Consensus: accept pending Gemini review

## Judgment

The fix addresses a real shared accelerated correctness bug exposed by the
heavy Goal 228 benchmark.

The core design is defensible:

- widen candidate collection where float-path loss occurs
- keep exact public acceptance at double precision before returning rows

That is a better correction than weakening the public radius contract.

## Evidence

- local focused regression:
  - `Ran 24 tests`
  - `OK (skipped=18)`
- Linux focused regression:
  - `Ran 24 tests`
  - `OK`
- Linux heavy-case parity rerun:
  - CPU `45632`
  - Embree `45632`
  - OptiX `45632`
  - Vulkan `45632`
  - indexed PostGIS `45632`

## Remaining Honest Boundaries

- `knn_rows` GPU distance values still remain `float_approx` relative to
  PostGIS double precision even when row identity matches
- the release handoff should still be treated as a checklist until final
  packaging is explicitly authorized
