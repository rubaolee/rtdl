# Goal3479 - Overlay-Area Continuation Contract

## Status

Implemented locally.

Goal3479 turns the Goal3474/3477 oracle evidence into an executable v2.8
contract for the next Spatial RayJoin engineering step.

## Contract

The new module is:

- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`

It declares two generic targets over the existing
`shape_pair_relation_flags_with_ordinals_and_geometry_payload` input contract:

| Target | Priority | Output |
| --- | --- | --- |
| `scalar_exact_area` | P0 | row-aligned `float64` exact area plus status |
| `streamed_overlay_geometry` | P1 | component/vertex stream plus owner rows |

## Why Scalar First

Goal3474 gives a scalar target: 4,543 active rows, 1,090 strict-positive rows
using a raw `>0` test, 3,453 strict-zero rows, 0 exceptions, and total exact
area 26.08321766231042. Later Goals3492-3494 use the v2.8 row absolute
tolerance and establish 1,086 thresholded positive rows for the current
acceptance path.

Goal3477 shows full geometry is a larger contract: 609 positive `MultiPolygon`
rows, 48 positive `GeometryCollection` rows, 2,801 polygon components, 42,314
output vertices, and one row with 22 polygon components / 586 output vertices.

So v2.8 should pursue scalar exact area first for the benchmark path, while
keeping full overlay geometry as a later streamed component/vertex contract.

## Boundary

This is contract metadata, not a runtime kernel and not a release claim. It
does not authorize public speedup wording, broad RT-core speedup wording,
true-zero-copy wording, RayJoin paper reproduction claims, RTDL-beats-RayJoin
claims, hidden partner selection, hidden dispatch, full overlay completion
claims, or app-specific native-engine behavior.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3479_overlay_area_continuation_contract_test`
