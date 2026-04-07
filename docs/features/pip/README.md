# PIP

## Purpose

`pip` is RTDL's point-in-polygon workload.

Use it when the probe side is points, the build side is polygons, and you want
one row per accepted containment hit.

## Docs

- canonical kernel pattern:
  - [rtdl_language_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)
- language contracts:
  - [dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)
  - [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

Kernel shape:

```python
points = rt.input("points", rt.Points, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(points, polygons, accel="bvh")
hits = rt.refine(
    candidates,
    predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
)
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

## Code

- predicate:
  - `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`
- canonical reference kernel:
  - [point_in_counties_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)

## Example

Start here:

- [rtdl_language_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_language_reference.py)

For the strongest historical performance/correctness story, see the accepted
`county_zipcode` positive-hit `pip` package in the v0.1 trust-anchor docs.

## Best Practices

- use explicit `boundary_mode="inclusive"`
- validate new semantics against PostGIS on Linux when external correctness matters
- keep point ids and polygon ids stable so downstream audit rows stay usable
- treat the v0.1 `county_zipcode` package as the trust anchor for this feature line

## Try

- point-in-district joins
- positive-hit spatial filtering
- audit rows where boundary-inclusive containment is acceptable

## Try Not

- full polygon overlap
- segment/polygon intersection
- alternative boundary semantics not currently accepted by the DSL

## Limitations

- the accepted public contract is boundary-inclusive only
- current paths are float-based, not robust exact geometry
- current `main` keeps this feature working, but the newest live docs emphasize newer v0.2 families rather than expanding `pip` further
