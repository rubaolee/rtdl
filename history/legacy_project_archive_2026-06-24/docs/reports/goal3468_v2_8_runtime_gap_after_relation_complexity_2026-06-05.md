# Goal3468 - v2.8 Runtime Gap After Relation Complexity Probe

## Status

Implemented locally.

Goal3468 refreshes the v2.8 benchmark runtime gap map after Goal3467. Spatial
RayJoin is no longer described as merely waiting for an unspecified exact
overlay continuation. The map now records the measured active-row shape:

- 4,543 public-CDB active relation rows
- 4,375 rows require general-overlay handling
- 168 rows are both-convex
- 1,033 rows exceed the 64-vertex simple threshold on at least one side
- max active pair vertex count is 1,132

## Design Consequence

A convex-only clipping continuation is a useful routed fast path, but it cannot
close the RayJoin public-CDB exact-overlay gap. The next real primitive must be
a generic simple-polygon overlay-area continuation for non-integer,
non-orthogonal, mostly nonconvex polygons.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3468_v2_8_runtime_gap_after_relation_complexity_test`

