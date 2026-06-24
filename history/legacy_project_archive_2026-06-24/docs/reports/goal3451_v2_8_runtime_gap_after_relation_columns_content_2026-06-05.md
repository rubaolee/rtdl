# Goal3451 - v2.8 Runtime Gap Refresh After Relation Columns and Content Proof

## Status

Implemented locally.

Goal3451 refreshes the v2.8 benchmark runtime gap map after the Goal3447-3450 RayJoin relation-column chain.

## What Changed

The `spatial_rayjoin` gap row now records that RTDL has:

- generic resident active relation columns with `left_id`, `right_id`, `requires_segment_intersection`, and `requires_point_containment`
- pod evidence for relation-column count parity from Goal3447
- a generic compact grouped-count continuation by id from Goal3449
- sparse-id content correctness against host materialized rows from Goal3450
- Claude review boundary from Goal3448

This means the old wording "remaining work is device-resident relation-row output" was too coarse. A resident relation-column stream now exists. The still-open RayJoin work is narrower and harder:

- exact relation witnesses
- overlay-area continuation
- large-scale content-reference oracles beyond counts/grouping
- boundary-witness ownership at serious scale

## Claim Boundary

This goal does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full overlay relation-row or overlay-area completion claims
- app-specific native-engine logic
- hidden partner selection

The intended claim is only a status-map correction: the RayJoin benchmark gap is now relation-witness/overlay-area continuation, not merely active-count or active-relation-id residency.

## Validation

- `py -3 -m unittest tests.goal3451_v2_8_runtime_gap_after_relation_columns_content_test tests.goal3446_v2_8_runtime_gap_after_rayjoin_active_count_device_default_test tests.goal3450_shape_pair_relation_device_column_content_test`

## Remaining Work

The next engineering target should build a bounded, generic witness/area continuation over resident relation columns. It must stay app-agnostic in the engine and keep RayJoin-specific interpretation in the benchmark app layer.
