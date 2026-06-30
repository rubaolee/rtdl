# Goal 137 Jaccard Workload Charter

## Decision

Goal 137 accepts a narrow first implementation line for the Jaccard idea:

- `polygon_pair_overlap_area_rows`

This is the primitive that should come before `polygon_set_jaccard`.

## Accepted semantics

- left/right inputs are polygon sets
- rows are emitted only for positive overlap pairs
- polygons must be orthogonal integer-grid polygons
- areas are counted as covered unit cells
- output fields are:
  - `left_polygon_id`
  - `right_polygon_id`
  - `intersection_area`
  - `left_area`
  - `right_area`
  - `union_area`

## Why this is the right first step

- It preserves RTDL’s spatial-workload identity.
- It matches pathology/image-grid reasoning better than generic set similarity.
- It is small enough to implement honestly on current RTDL CPU/oracle surfaces.
- It can be checked against PostGIS on authored orthogonal grid cases.

## Explicit honesty boundary

Goal 137 does **not** claim:

- generic polygon overlay support
- continuous exact polygon-intersection geometry support
- public pathology data closure
- multi-backend RT maturity

## Next goals

- Goal 138: CPU/Python/PostGIS primitive closure
- Goal 139: public pathology data acquisition and conversion
- Goal 140: `polygon_set_jaccard` workload closure
- Goal 141: Linux/public-data correctness and performance audit
- Goal 142: docs and generate-only expansion
