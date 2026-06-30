# Goal 193: v0.4 Direction Decision Review

Date: 2026-04-09
Status: closed after revised-neighbor-search review

## Why this reopened

The earlier closed direction package assumed `v0.4` would continue into bounded
3D work. That direction is now superseded by the explicit user decision:

- `v0.4` should not touch 3D as the main milestone

So the current strategy round must be re-reviewed against the revised
nearest-neighbor package.

## Current review target

- [goal193_v0_4_direction_decision_2026-04-09.md](goal193_v0_4_direction_decision_2026-04-09.md)
- [goal194_v0_4_content_package_2026-04-09.md](goal194_v0_4_content_package_2026-04-09.md)

## Current live conclusion

The revised live package now says:

- `v0.4` should be a 2D/non-graphical nearest-neighbor workload release
- first accepted public workload:
  - `fixed_radius_neighbors`
- second workload in the same family:
  - `knn_rows`
- Hausdorff distance is supporting evidence for later expansion, not the
  headline scope of `v0.4`

## Final resolved decision

The revised package is now externally challenged and closed:

- headline workload family:
  - nearest-neighbor search
- first accepted public workload:
  - `fixed_radius_neighbors`
- second workload in the same family:
  - `knn_rows`

Main reviewer corrections already applied:

- stale `point_in_volume` finish-line text removed
- concrete external baseline naming added
- backend transfer risk made explicit
