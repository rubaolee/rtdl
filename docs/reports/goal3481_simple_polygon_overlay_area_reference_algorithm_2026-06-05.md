# Goal3481 - Simple Polygon Overlay-Area Reference Algorithm

## Status

Implemented locally.

Goal3481 adds a CPU reference algorithm for the next scalar exact-area
continuation: triangulate each simple polygon with deterministic ear clipping,
then sum convex triangle-triangle overlap areas using Sutherland-Hodgman style
clipping.

## Why This Route

Goal3479 set `scalar_exact_area` as the P0 v2.8 continuation target. A direct
general polygon Boolean kernel is too large to write safely without a smaller
reference shape. Triangulation gives the future GPU path a generic prepared
payload:

- one shape becomes a sequence of triangles;
- each active relation row becomes bounded triangle-pair work;
- each triangle-pair overlap is convex clipping;
- output can remain a scalar `float64` area plus status.

This is still not the production GPU continuation. It is a reference algorithm
for simple polygons without holes or multipolygon topology. Topology repair and
multi-component geometry remain separate preparation-layer work.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full overlay completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3481_simple_polygon_overlay_area_reference_algorithm_test`

