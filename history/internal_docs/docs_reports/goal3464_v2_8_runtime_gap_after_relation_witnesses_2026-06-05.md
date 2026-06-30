# Goal3464 - v2.8 Runtime Gap Refresh After Relation Witnesses

## Status

Implemented locally.

Goal3464 refreshes the v2.8 Spatial RayJoin runtime gap map after Goal3463.

## What Changed

Goal3463 added a generic CuPy witness continuation over resident relation ids, flags, ordinals, and geometry payload columns. On the public CDB pair, it emitted witnesses for all 4,543 active relation rows:

- 4,539 segment-edge witnesses
- 4 containment witnesses
- 0 unresolved witness rows

The gap map now records that exact relation witnesses are no longer merely pending for this relation-column stream.

## Remaining Gap

The remaining RayJoin work is exact overlay-area continuation for non-integer, non-orthogonal polygons. The future primitive needs to compute exact or explicitly bounded polygon overlay area/witness results over the resident payload without adding RayJoin-specific native-engine logic.

Boundary-witness ownership and exact area/witness policy at serious scale also remain open.

## Boundary

Goal3464 does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full exact overlay-area completion claims

## Validation

- `py -3 -m unittest tests.goal3464_v2_8_runtime_gap_after_relation_witnesses_test tests.goal3463_shape_pair_relation_witness_continuation_test tests.goal3461_v2_8_runtime_gap_after_large_relation_oracle_test`
