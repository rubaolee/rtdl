# Goal3472 - v2.8 Runtime Gap After Convex Overlay Fast Path

## Status

Implemented locally.

Goal3472 refreshes the v2.8 benchmark runtime gap map after Goal3471. Spatial
RayJoin now records that RTDL has a generic exact convex overlay-area fast path
over the resident relation stream.

## What Changed

Goal3471 validated:

- synthetic convex fixture area: expected 1.0, measured 1.0
- public-CDB active relation rows: 4,543
- supported both-convex rows: 168
- positive supported-area rows: 161
- unsupported nonconvex rows: 4,375
- median convex fast-path continuation time: 0.001791 seconds

## Interpretation

This is good engineering, but not full RayJoin overlay closure. The fast path is
exact for supported convex rows and fail-closed for unsupported rows. The main
remaining gap is still a generic simple-polygon overlay-area continuation for
nonconvex/high-vertex rows.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3472_v2_8_runtime_gap_after_convex_overlay_fast_path_test`

