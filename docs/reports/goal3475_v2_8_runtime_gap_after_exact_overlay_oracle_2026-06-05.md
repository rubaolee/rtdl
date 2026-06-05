# Goal3475 - v2.8 Runtime Gap After Exact Overlay Oracle

## Status

Implemented locally.

Goal3475 refreshes the v2.8 benchmark runtime gap map after Goal3474. Spatial
RayJoin now records an exact Shapely/GEOS CPU oracle target for all public-CDB
active relation rows selected by the RTDL/OptiX relation stream.

## What Changed

Goal3474 validated:

- active relation rows: 4,543
- positive exact-area rows: 1,090
- zero exact-area rows: 3,453
- topology/oracle exceptions: 0
- total exact overlay area: 26.08321766231042
- Shapely exact-oracle median time: 0.4146229340694845 seconds
- RTDL/OptiX relation steady min time: 0.004817125387489796 seconds

## Interpretation

This is a correctness target, not a runtime win. The oracle proves the exact
area total and row distribution that a future generic GPU simple-polygon
overlay-area continuation must reproduce. It also sharpens the remaining gap:
the convex fast path covers 168 rows and contributes only
0.05788295450020087 area, while the exact oracle finds 1,090 positive rows and
26.08321766231042 total area.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_test`

