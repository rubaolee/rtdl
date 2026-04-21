# Point-in-Polygon (PIP)

## Purpose

`pip` is RTDL's point-in-polygon workload.

Use it when the probe side is points, the build side is polygons, and you want
one row per accepted containment hit.

`pip` is one of RTDL's root workloads. It is the historical positive-hit
spatial-filter primitive behind the early RayJoin-facing work and remains a
building block for polygon applications that need containment/candidate rows.

## Docs

- canonical kernel pattern:
  - [rtdl_language_reference.py](../../../examples/reference/rtdl_language_reference.py)
- language contracts:
  - [dsl_reference.md](../../rtdl/dsl_reference.md)
  - [workload_cookbook.md](../../rtdl/workload_cookbook.md)

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
  - [point_in_counties_reference](../../../examples/reference/rtdl_language_reference.py)
- current Embree root-performance closure:
  - [Goal 742 LSI/PIP root workload refresh](../../reports/goal742_lsi_pip_root_workload_refresh_2026-04-21.md)

## Current Backend Notes

- Embree: native CPU ray-tracing candidate discovery through build-side polygon
  user geometry and point queries; positive-hit mode emits only accepted
  containment rows.
- Prepared Embree raw mode avoids Python dict materialization when the caller
  only needs compact native rows or a follow-up app reduction.
- OptiX, Vulkan, HIPRT, and Apple RT remain listed in the engine support matrix;
  exact performance evidence is backend-specific and should not be inferred
  from the Embree root refresh.

## Example

Start here:

- [rtdl_language_reference.py](../../../examples/reference/rtdl_language_reference.py)

Run from the repository root:

```bash
python examples/reference/rtdl_language_reference.py
```

Use `python3` instead if that is what your shell exposes.

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
- full matrix mode can be output-materialization-bound; positive-hit mode is
  the preferred high-performance app shape
