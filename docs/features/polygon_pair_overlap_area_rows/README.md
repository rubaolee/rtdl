# Polygon-Pair Overlap Area Rows

## Purpose

`polygon_pair_overlap_area_rows` is the narrow overlap-area primitive for the
current Jaccard line.

Use it when you want one row per polygon pair with overlap and set-area values
under the current orthogonal integer-grid unit-cell contract.

## Docs

- canonical example:
  - [rtdl_polygon_pair_overlap_area_rows.py](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_pair_overlap_area_rows.py)
- PostGIS parity helper:
  - [goal138_polygon_overlap_postgis.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal138_polygon_overlap_postgis.py)
- closure report:
  - [goal138_polygon_pair_overlap_area_rows_closure_2026-04-06.md](/Users/rl2025/rtdl_python_only/docs/reports/goal138_polygon_pair_overlap_area_rows_closure_2026-04-06.md)

Kernel shape:

```python
left = rt.input("left", rt.Polygons, role="probe")
right = rt.input("right", rt.Polygons, role="build")
candidates = rt.traverse(left, right, accel="bvh")
rows = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows(exact=False))
return rt.emit(
    rows,
    fields=[
        "left_polygon_id",
        "right_polygon_id",
        "intersection_area",
        "left_area",
        "right_area",
        "union_area",
    ],
)
```

## Code

- predicate:
  - `rt.polygon_pair_overlap_area_rows(exact=False)`
- canonical reference kernel:
  - [polygon_pair_overlap_area_rows_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_pair_overlap_area_rows.py)

## Example

Run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_polygon_pair_overlap_area_rows.py
```

## Best Practices

- use only orthogonal integer-grid polygons that fit the unit-cell contract
- explain area as covered unit cells, not generic continuous polygon area
- use this primitive when you need pairwise overlap rows before an aggregate like Jaccard

## Try

- pathology-style mask overlap rows
- pairwise overlap reports on rectilinear unit-cell polygons
- narrow Jaccard pipelines

## Try Not

- generic continuous polygon overlay
- arbitrary freehand polygon area claims
- claiming this closes full GIS polygon intersection

## Limitations

- narrow contract only: orthogonal integer-grid unit-cell polygons
- not full polygon overlay
- current backend maturity is intentionally narrower than the segment/polygon line
