# Goal3454 - v2.8 Runtime Gap Refresh After Relation Geometry Payload

## Status

Implemented locally.

Goal3454 refreshes the v2.8 benchmark runtime gap map after Goal3453 added pod-validated generic geometry payload columns to the resident shape-pair relation stream.

## Status Update

For Spatial RayJoin, RTDL v2.8 now has:

- resident active relation id/flag columns
- generic compact grouped-count continuation over those resident ids
- sparse-id content correctness for relation id/flag columns
- resident generic geometry payload columns:
  - left/right polygon refs
  - left/right vertex-x and vertex-y arrays
  - left/right bounds arrays

This changes the next engineering target. We are no longer blocked on exposing the geometry payload. We are now blocked on a bounded, generic witness/area continuation that consumes the relation columns and geometry payload columns without moving RayJoin logic into the native engine.

## Claim Boundary

Goal3454 does not authorize:

- v2.8 release
- public speedup wording
- RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay witness or area completion claims
- app-specific native-engine logic
- hidden partner selection

## Validation

- `py -3 -m unittest tests.goal3454_v2_8_runtime_gap_after_geometry_payload_test tests.goal3453_shape_pair_relation_geometry_payload_test tests.goal3451_v2_8_runtime_gap_after_relation_columns_content_test`

## Next Target

Add a bounded generic witness/area continuation over relation ids, relation flags, and shape-pair geometry payload columns. A narrow first version can compute axis-aligned bounds overlap area as a payload-consumption proof, but full polygon overlay area requires a later exact continuation.
