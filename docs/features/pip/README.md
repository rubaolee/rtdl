# Point-in-Polygon (PIP)

## Purpose

`pip` is RTDL's point-in-polygon workload.

Use it when the probe side is points, the build side is polygons, and you want
one row per accepted containment hit.

`pip` is one of RTDL's root workloads. It is the positive-hit
spatial-filter primitive behind the early RayJoin-facing work and remains a
building block for polygon applications that need containment/candidate rows.

For CDB/planar-map workloads that need point-location rows or closest-edge
counts, use the prepared planar-map front door:

```python
from rtdsl import load_cdb, prepare_planar_map_point_location_2d_optix

base = load_cdb("base_Point.cdb")
points = [(1, -73.9, 40.7), (2, -74.0, 40.8)]

with prepare_planar_map_point_location_2d_optix(base, query_map_id=1) as pip:
    rows = pip.run(points)
```

This front door hides the legacy CDB point-location execution bridge inside
RTDL. Application code should not set `RTDL_RAYJOIN_CDB_*` variables directly.
It is point-location/PIP, not polygon overlay.  This prepared front door is
currently OptiX-only; the lower compatibility bridge is guarded and restored by
RTDL, but overlapping calls through this front door are serialized.

When an application needs point-location together with planar-map LSI on the
same pair of maps, use `prepare_planar_map_workspace_2d_optix`. The workspace
prepares both public primitives once and keeps topology-specific continuation
in application code.

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
- prepared CDB/planar-map point-location front door:
  - `prepare_planar_map_point_location_2d_optix(base).run(points)`
- reusable CDB/planar-map workspace:
  - `prepare_planar_map_workspace_2d_optix(left, right).run_left_points_in_right()`
- canonical reference kernel:
  - [point_in_counties_reference](../../../examples/reference/rtdl_language_reference.py)
- current support contract:
  - [Engine Feature Support Contract](../engine_support_matrix.md)

## Current Backend Notes

- The prepared CDB/planar-map point-location front door is currently an
  OptiX-only public front door over a historical native route.  It is an API
  cleanup, not a claim that RTDL has a fully generalized native planar-map
  point-location ABI on every backend.
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

For release-facing performance/correctness claims, use the current support
matrix and performance table.

## Best Practices

- use explicit `boundary_mode="inclusive"`
- cite a data-bearing correctness artifact before claiming exact agreement with
  an external implementation
- validate new semantics against PostGIS on Linux when external correctness matters
- keep point ids and polygon ids stable so downstream audit rows stay usable
- treat the current app and support matrices as the trust anchor for this feature line

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
