# Goal3354: Owner-Face Columnar Selection Front Door

Date: 2026-06-04

Status: internal v2.8 Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3353 made priority derivation available as columns. Goal3354 adds the matching columnar front door for owner-face selection, so a future device/native lowering target can be described as typed columns end to end for the selection stage.

New helper:

- `select_owner_faces_from_incident_candidate_columns_with_priority_columns(...)`

## Contract

Inputs:

- `incident_point_ids`
- `incident_face_ids`
- `incident_face_counts`
- `priority_point_ids`
- `priority_face_ids`
- `priorities`

Outputs:

- `point_id`
- `owner_face_id`
- `incident_face_count`
- `candidate_count`
- `selection_status`

The helper normalizes columns into `select_owner_faces_from_incident_candidates_with_priority(...)`, so it shares the row selector semantics exactly:

- unique maximum incident count wins,
- tied incident counts require explicit priorities,
- missing priorities fail closed by default,
- tied priorities fail closed by default,
- invalid column lengths fail before selection.

## Boundary

This is not a native/device implementation. It is a Python reference columnar contract, useful because native/device work can later target the same schema and prove parity against it.

The native engine still must not infer CDB/RayJoin ownership. It may only consume explicit generic columns if a future lowered implementation is accepted.

## Validation

Goal3354 tests verify:

- columnar selector output matches the expected row-selector semantics,
- Goal3353 priority columns feed Goal3354 selection columns,
- invalid incident column lengths fail,
- invalid priority column lengths fail,
- missing priority evidence fails closed,
- the Goal3349 contract lists the columnar selector helper,
- the report keeps the reference-only and claim-boundary wording visible.
