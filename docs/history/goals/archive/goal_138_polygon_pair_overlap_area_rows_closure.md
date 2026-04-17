# Goal 138: Polygon Pair Overlap Area Rows Closure

## Purpose

Close the first Jaccard-line primitive accepted by Goal 137.

## Feature

- `polygon_pair_overlap_area_rows`

## Accepted implementation scope

- Python reference
- native CPU/oracle
- authored example
- focused tests
- authored PostGIS parity on Linux

## Accepted semantics

- polygon-vs-polygon positive-overlap rows
- orthogonal integer-grid polygons only
- no zero-length edges
- no hole support claimed
- area = count of covered unit cells

## Expected output fields

- `left_polygon_id`
- `right_polygon_id`
- `intersection_area`
- `left_area`
- `right_area`
- `union_area`

## Not claimed

- generic continuous overlay
- full GIS overlay materialization
- broad backend support beyond Python/native CPU
- public pathology dataset support

## Validation target

- local authored tests
- local compile/lower checks
- Linux focused test pass
- Linux PostGIS parity on authored rows
