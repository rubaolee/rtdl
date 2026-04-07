# Goal 138 Polygon Pair Overlap Area Rows Closure

## Status

Accepted as a narrow primitive-first closure.

## What landed

- API predicate:
  - `polygon_pair_overlap_area_rows(exact=False)`
- Python reference path
- native CPU/oracle path
- lowering support with honest `native_loop` boundary
- authored example:
  - [rtdl_polygon_pair_overlap_area_rows.py](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_pair_overlap_area_rows.py)
- PostGIS validation helper:
  - [goal138_polygon_overlap_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal138_polygon_overlap_postgis.py)
  - [goal138_polygon_overlap_postgis_validation.py](/Users/rl2025/rtdl_python_only/scripts/goal138_polygon_overlap_postgis_validation.py)
- focused tests:
  - [goal138_polygon_pair_overlap_area_rows_test.py](/Users/rl2025/rtdl_python_only/tests/goal138_polygon_pair_overlap_area_rows_test.py)
  - [goal138_polygon_overlap_postgis_test.py](/Users/rl2025/rtdl_python_only/tests/goal138_polygon_overlap_postgis_test.py)

## Semantic contract actually implemented

- polygons must use integer-grid vertices
- polygons must have orthogonal edges
- overlap area is computed as covered unit cells
- emitted rows are positive-overlap rows only

## Local results

- `python3 -m py_compile` on the new example/helper/scripts:
  - clean
- local focused tests:
  - `5 tests`, `OK`, `1 skipped`
- local broader slice:
  - `10 tests`, `OK`, `1 skipped`

The local skip is the known Mac native-oracle `geos_c` linkage limitation, not a new Goal 138 defect.

## Linux results

- focused tests on `lestat@192.168.1.20`:
  - `5 tests`, `OK`
- authored PostGIS validation:
  - Python parity vs PostGIS: `true`
  - native CPU parity vs PostGIS: `true`
  - PostGIS timing: `0.004517 s`

Authored rows:

| left_polygon_id | right_polygon_id | intersection_area | left_area | right_area | union_area |
| --- | --- | --- | --- | --- | --- |
| `1` | `10` | `4` | `9` | `9` | `14` |
| `2` | `11` | `1` | `4` | `2` | `5` |

Artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal138_polygon_pair_overlap_area_rows_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal138_polygon_pair_overlap_area_rows_artifacts_2026-04-06/summary.md)

## Honest boundary

This is **not** generic polygon overlap support.

It is a first accepted primitive for pathology-style orthogonal integer-grid polygons. That is why PostGIS parity was checked only on authored orthogonal cases where continuous area and unit-cell area are intentionally aligned.

## Recommended next goals

- Goal 139: public pathology data acquisition and conversion
- Goal 140: `polygon_set_jaccard` closure on top of this primitive
- Goal 141: Linux/public-data audit
- Goal 142: docs and generate-only expansion
