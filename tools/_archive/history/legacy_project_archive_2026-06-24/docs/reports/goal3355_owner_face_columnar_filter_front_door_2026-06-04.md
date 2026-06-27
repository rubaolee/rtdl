# Goal3355: Owner-Face Columnar Filter Front Door

Date: 2026-06-04

Status: internal v2.8 Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3353 and Goal3354 made the priority-derivation and owner-face-selection stages available as columnar Python reference front doors. Goal3355 adds the final columnar membership-filter stage.

New helper:

- `filter_closed_shape_membership_candidate_columns_by_owner_face_columns(...)`

Together, Goals 3353-3355 provide a complete columnar Python reference pipeline:

1. rank-signal columns to priority columns,
2. incident-face and priority columns to selected owner-face columns,
3. candidate/topology/owner-face columns to filtered membership columns.

## Contract

Inputs:

- `candidate_point_ids`
- `candidate_shape_ids`
- `topology_shape_ids`
- `topology_left_face_ids`
- `topology_right_face_ids`
- optional topology face-presence columns,
- `owner_point_ids`
- `owner_face_ids`

Outputs:

- `point_id`
- `shape_id`
- `membership`
- `owner_face_id`

The helper normalizes columns into `filter_closed_shape_membership_candidates_by_owner_face(...)`, so it shares the row-filter semantics exactly:

- candidate rows remain generic point/shape ids,
- topology rows remain generic shape/face ids,
- owner-face rows are explicit input columns,
- missing owner policy is fail-closed by default.

## Boundary

This is not a native/device lowering. It is a Python reference columnar contract so future native/device work has an exact schema and same-contract oracle.

The native engine still must not infer CDB/RayJoin ownership, map/entity lookup, assignment semantics, or paper-system behavior. It may only consume explicit generic columns after a future lowered implementation is reviewed and validated.

## Validation

Goal3355 tests verify:

- the full columnar reference pipeline reaches filtered membership columns,
- the columnar filter matches the existing row filter,
- candidate, topology, and owner column length errors fail closed,
- missing owner rows fail closed by default,
- `missing_owner_policy="drop"` preserves empty output,
- the Goal3349 contract lists the columnar filter helper,
- the report keeps reference-only and claim-boundary wording visible.
