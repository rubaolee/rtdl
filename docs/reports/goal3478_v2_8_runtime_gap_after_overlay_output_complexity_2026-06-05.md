# Goal3478 - v2.8 Runtime Gap After Overlay Output Complexity

## Status

Implemented locally.

Goal3478 refreshes the v2.8 benchmark runtime gap map after Goal3477. Spatial
RayJoin now separates two generic runtime targets:

- near-term: GPU-resident scalar exact overlay-area continuation for active
  relation rows;
- later: streamed full overlay-geometry output with component/vertex ownership.

## What Changed

Goal3477 validated:

- active relation rows: 4,543
- positive exact-area rows: 1,090
- boundary-only/touch rows: 3,452
- empty rows: 1
- positive `Polygon` rows: 433
- positive `MultiPolygon` rows: 609
- positive `GeometryCollection` rows: 48
- total polygon components in exact outputs: 2,801
- total output vertices in exact outputs: 42,314
- max polygon components in one row: 22
- max output vertices in one row: 586

## Interpretation

The benchmark can reasonably target scalar exact area first, because the
measured app-level value is area/count style. But a full overlay-geometry
contract is not a small extension of a scalar result: the public-CDB oracle has
multi-component and mixed geometry outputs, so a future full-output path needs
streamed component and vertex columns with explicit ownership/witness policy.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, true-zero-copy wording, RayJoin paper reproduction claims,
RTDL-beats-RayJoin claims, or full exact overlay-area completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3478_v2_8_runtime_gap_after_overlay_output_complexity_test`

