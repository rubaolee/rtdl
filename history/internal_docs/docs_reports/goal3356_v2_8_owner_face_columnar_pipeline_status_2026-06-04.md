# Goal3356: v2.8 Owner-Face Columnar Pipeline Status

Date: 2026-06-04

Status: internal v2.8 status packet. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Summary

The v2.8 RayJoin/CDB owner-face work has moved from diagnosis into a complete Python reference contract for the explicit-priority path.

The key design line remains unchanged:

- RTDL may expose generic topology, rank, priority, owner-face, and candidate columns.
- The native engine must not infer CDB/RayJoin ownership, map/entity lookup, assignment semantics, or paper-system behavior.
- Caller/data policy supplies priorities or rank signals.
- Ambiguous data fails closed by default.

## Goal Chain

| Goal | Purpose | Current status |
| --- | --- | --- |
| Goal3349 | Formalized `OWNER_FACE_PRIORITY_PIPELINE_CONTRACT`. | Python reference contract only. |
| Goal3350 | Pointed primitive discovery to the formal Goal3349 contract. | Catalog node remains `candidate_behavior`. |
| Goal3351 | Added row priority derivation from caller-supplied rank signals. | Fail-closed Python reference helper. |
| Goal3353 | Added columnar priority derivation from rank columns. | Columnar same-contract Python reference helper. |
| Goal3354 | Added columnar owner-face selection from incident/priority columns. | Columnar same-contract Python reference helper. |
| Goal3355 | Added columnar owner-face membership filter. | Complete columnar Python reference pipeline through final filtering. |

## Public Surface Added

The row helper:

- `derive_owner_face_priority_rows_from_rank_signals(...)`

The columnar helpers:

- `derive_owner_face_priority_columns_from_rank_signals(...)`
- `select_owner_faces_from_incident_candidate_columns_with_priority_columns(...)`
- `filter_closed_shape_membership_candidate_columns_by_owner_face_columns(...)`

Existing helpers still anchor the row oracle:

- `select_owner_faces_from_incident_candidates_with_priority(...)`
- `filter_closed_shape_membership_candidates_by_owner_face(...)`

## What This Proves

The current path proves that RTDL can express the owner-face correction as generic contracts:

1. Caller-supplied rank signals can become explicit priority columns.
2. Incident-face columns plus priority columns can select owner-face columns.
3. Candidate/topology/owner-face columns can filter membership candidates.
4. The columnar path shares row-reference semantics.

This is useful for future native/device lowering because the schema is now explicit.

## What This Does Not Prove

Still blocked:

- broad fast PIP count correctness,
- automatic owner-face derivation,
- native/device implementation,
- pod evidence for a lowered OptiX path,
- RayJoin paper reproduction claims,
- RTDL-beats-RayJoin claims,
- public speedup claims,
- broad RT-core speedup claims,
- true zero-copy claims.

This is not a native/device implementation. It is a Python reference columnar contract.

## Validation

Recent local validation:

- Goal3349 focused chain: `Ran 19 tests in 0.026s OK`
- Goal3350 catalog/discovery set: `Ran 30 tests in 0.093s OK`
- Broader owner-face chain after Goal3350: `Ran 53 tests in 0.026s OK`
- Goal3351 focused set: `Ran 18 tests in 0.021s OK`
- Broader owner-face chain after Goal3351: `Ran 59 tests in 0.027s OK`
- Goal3353 focused set: `Ran 15 tests in 0.018s OK`
- Broader owner-face chain after Goal3353: `Ran 64 tests in 0.028s OK`
- Goal3354 focused set: `Ran 20 tests in 0.020s OK`
- Broader owner-face chain after Goal3354: `Ran 69 tests in 0.031s OK`
- Goal3355 focused set: `Ran 26 tests in 0.024s OK`
- Broader owner-face chain after Goal3355: `Ran 75 tests in 0.031s OK`

## External Review State

Claude review was attempted for Goal3349 but the local Claude session was quota-blocked until `5:40pm (America/New_York)`.

Gemini Flash was attempted for Goal3349-3351 but produced only a pending template review, so the stub was removed and is not counted as evidence.

Review remains needed for the Goal3349-3355 chain.

## Next engineering steps

1. Get external review of Goals3349-3355.
2. Add a same-contract fixture that runs the complete row and columnar pipelines over the known seven county mismatch points.
3. Only after that, consider device/native lowering of the explicit-column pipeline.

The native engine must not infer ownership policy at any stage.
