# Goal3470 - Generic Simple-Polygon Overlay-Area Continuation Design

## Status

Design checkpoint; no release claim.

Goal3470 records the engineering conclusion after Goals3463-3468. The current
Spatial RayJoin relation stream is useful and app-agnostic: it gives resident
relation rows, grouped count, bounds-overlap proxy area, witness columns, and
row-complexity classification. It still does not compute exact polygon overlay
area for the public-CDB benchmark.

## Measured Starting Point

Goal3467 measured the active public-CDB relation stream:

| Measure | Value |
| --- | ---: |
| active relation rows | 4,543 |
| both-convex active rows | 168 |
| nonconvex active rows | 4,375 |
| rows above 64 vertices on at least one side | 1,033 |
| max active pair vertex count | 1,132 |

The consequence is simple: a convex-only continuation is a fast path, not the
answer. The exact overlay lane needs a generic simple-polygon continuation.

## Required Primitive Shape

The primitive should consume the existing generic relation-stream contract:

- `left_id`, `right_id`
- `left_ordinal`, `right_ordinal`
- `requires_segment_intersection`, `requires_point_containment`
- `left_polygon_refs`, `right_polygon_refs`
- `left_vertices_x/y`, `right_vertices_x/y`
- optional relation witnesses from `shape_pair_relation_witness_cupy`
- optional complexity columns from `shape_pair_relation_complexity_cupy`

It should emit a typed continuation result:

- `left_id`, `right_id`
- `intersection_area_f64`
- `status`
- optional witness/ownership columns for boundary policy
- optional grouped reductions by left or right id

## Candidate Implementation Routes

1. Convex fast path:
   Use the Goal3467 complexity classifier to route both-convex rows into a
   bounded Sutherland-Hodgman-style clipping continuation. This is useful but
   covers only 168 of 4,543 public-CDB active rows.

2. General simple-polygon continuation:
   Build a generic device-side arrangement, sweep, triangulation, or equivalent
   clipping continuation that supports nonconvex simple rings and high vertex
   counts. This is the real RayJoin public-CDB closure route.

3. External robust-library bridge:
   Use a well-defined generic bridge to a robust polygon overlay implementation
   as a reference/oracle or as a CPU fallback, but do not let library-specific
   app semantics become the RTDL engine contract.

## Acceptance Bars

The primitive cannot be promoted unless all of these are true:

- exact oracle policy for non-integer, non-orthogonal polygons is documented
- boundary/witness ownership policy is deterministic
- unsupported topology fails closed with explicit status, not silent partial area
- same-contract CPU/reference oracle is available
- public-CDB pod evidence covers representative nonconvex/high-vertex rows
- all release, public speedup, RT-core, true-zero-copy, RayJoin reproduction,
  RTDL-beats-RayJoin, and full-overlay claims remain blocked until reviewed
- independent AI review accepts the contract and evidence boundary

## App-Agnostic Boundary

This primitive must be named and implemented as generic geometry continuation.
The engine should not contain RayJoin, county, map, CDB, parcel, or GIS-app
terms. RayJoin remains a benchmark app that chooses this generic primitive and
interprets the output.

## Next Engineering Step

Implement a bounded convex fast path only if it is explicitly labeled as a
routed subset. The main v2.x work item is the general simple-polygon
overlay-area continuation over typed relation streams.

