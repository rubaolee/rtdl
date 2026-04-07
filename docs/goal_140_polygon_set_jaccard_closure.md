# Goal 140: Polygon Set Jaccard Closure

## Purpose

Close the first aggregate workload built on the Goal 138 overlap-area primitive.

## Feature

- `polygon_set_jaccard`

## Accepted implementation scope

- Python reference
- native CPU/oracle
- authored example
- focused tests
- authored Linux/PostGIS parity

## Accepted semantics

- compare one left polygon set to one right polygon set
- orthogonal integer-grid polygons only
- no hole support claimed
- area = count of covered unit cells
- emit one aggregate row for the whole left/right set pair

## Expected output fields

- `intersection_area`
- `left_area`
- `right_area`
- `union_area`
- `jaccard_similarity`

## Not claimed

- generic continuous polygon-set Jaccard
- full polygon overlay materialization
- large public pathology closure
- broad backend support beyond Python/native CPU

## Validation target

- local authored tests
- local compile/lower checks
- Linux focused test pass
- Linux PostGIS parity on the authored set case
