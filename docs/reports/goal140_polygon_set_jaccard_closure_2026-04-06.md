# Goal 140 Polygon Set Jaccard Closure

## Status

Accepted as a narrow aggregate closure.

## What landed

- API predicate:
  - `polygon_set_jaccard(exact=False)`
- Python reference path
- native CPU/oracle path
- lowering support with honest `native_loop` boundary
- authored example:
  - [rtdl_polygon_set_jaccard.py](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_set_jaccard.py)
- PostGIS validation helper:
  - [goal140_polygon_set_jaccard_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal140_polygon_set_jaccard_postgis.py)
  - [goal140_polygon_set_jaccard_postgis_validation.py](/Users/rl2025/rtdl_python_only/scripts/goal140_polygon_set_jaccard_postgis_validation.py)
- focused tests:
  - [goal140_polygon_set_jaccard_test.py](/Users/rl2025/rtdl_python_only/tests/goal140_polygon_set_jaccard_test.py)
  - [goal140_polygon_set_jaccard_postgis_test.py](/Users/rl2025/rtdl_python_only/tests/goal140_polygon_set_jaccard_postgis_test.py)

## Semantic contract actually implemented

- polygons must use integer-grid vertices
- polygons must have orthogonal edges
- set area is computed as covered unit cells over the whole polygon set
- the workload emits one aggregate row for the left/right set pair

## Local results

- `python3 -m py_compile` on the new example/helper/script:
  - clean
- local focused Goal 140 tests:
  - `6 tests`, `OK`, `1 skipped`
- local broader Goal 138 + Goal 140 slice:
  - `9 tests`, `OK`, `2 skipped`
- authored example run:
  - one row emitted with:
    - `intersection_area = 5`
    - `left_area = 13`
    - `right_area = 11`
    - `union_area = 19`
    - `jaccard_similarity = 0.2631578947368421`

The local skip is the known Mac native-oracle `geos_c` linkage limitation, not a new Goal 140 defect.

## Linux results

- focused tests on `lestat@192.168.1.20`:
  - `6 tests`, `OK`
- authored PostGIS validation:
  - Python parity vs PostGIS: `true`
  - native CPU parity vs PostGIS: `true`
  - PostGIS timing: `0.666102 s`

Authored aggregate row:

| intersection_area | left_area | right_area | union_area | jaccard_similarity |
| --- | --- | --- | --- | --- |
| `5` | `13` | `11` | `19` | `0.263158` |

Artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal140_polygon_set_jaccard_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal140_polygon_set_jaccard_artifacts_2026-04-06/summary.md)

## Honest boundary

This is **not** generic polygon-set Jaccard.

It is a narrow pathology-style aggregate built on the same orthogonal integer-grid unit-cell semantics accepted in Goals 137 and 138. That is why PostGIS parity was checked only on an authored orthogonal set case where continuous coverage and unit-cell coverage are intentionally aligned.

## Review outcome

- internal review verdict:
  - approve with notes
- notes resolved before final close:
  - lowering commentary no longer claims a non-overlap assumption that the implementation does not require
  - focused tests now include empty-set behavior and invalid non-orthogonal input rejection

## Recommended next goals

- Goal 141: Linux/public-data audit
- Goal 142: docs and generate-only expansion
