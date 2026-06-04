# Goal3349: Owner-Face Priority Pipeline Contract

Date: 2026-06-04

Status: internal v2.8 engineering contract. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3345 proved that explicit caller/data priority rows can reconcile the seven known county overcount mismatches after the fast point/closed-shape candidate path. Goal3349 turns that reference sequence into a named contract so future native/device work has a stable target rather than an informal helper chain.

The new exported contract id is:

- `OWNER_FACE_PRIORITY_PIPELINE_CONTRACT = "rtdl.closed_shape.owner_face_priority_pipeline.v1"`

## Contract

The validated contract is available through:

- `owner_face_priority_pipeline_contract()`
- `validate_owner_face_priority_pipeline_contract()`

Required inputs:

- `incident_face_candidate_rows(point_id,face_id,incident_face_count)`
- `priority_rows(point_id,face_id,priority)`
- `candidate_rows(point_id,shape_id)`
- `topology_rows(shape_id|chain_id,left_face_id,right_face_id)`

Reference steps:

- `select_owner_faces_from_incident_candidates_with_priority(...)`
- `owner_face_ids_by_point_from_selection_rows(...)`
- `filter_closed_shape_membership_candidates_by_owner_face(...)`

Outputs:

- `point_id`
- `shape_id`
- `membership`
- `owner_face_id`

## Selection Rule

The rule is intentionally explicit and fail-closed:

1. Higher `incident_face_count` wins.
2. If incident counts tie, lower caller-supplied `priority` wins.
3. Missing priority fails closed.
4. Tied priority fails closed.
5. The native engine must not infer or invent the priority rows.

The caller/data priority rows are mandatory for ambiguous topology. They are a policy input, not an RTDL native-engine decision.

## Boundary

This is still a Python reference contract only:

- `status = python_reference_contract_only`
- `native_lowering_status = blocked_until_contract_stable_and_validated`
- `native_engine_may_infer_app_ownership = false`
- `caller_policy_required = true`

The native engine may later consume explicit generic columns if the contract is promoted, but it must not infer CDB, RayJoin, GIS, or application ownership internally.

## Promotion Requirements

Before this can become a default native/device path:

- deterministic priority derivation contract or explicit caller priority columns,
- same-contract tests against the Python reference,
- pod/native evidence for any lowered implementation,
- claim-boundary review before public performance or paper-reproduction wording.

## Validation

The focused Goal3349 test verifies:

- the contract is exported from `rtdsl`,
- strict claim boundaries remain false,
- `priority_rows` are required,
- pipeline step names point to callable reference helpers,
- the Goal3345 county mismatch reference pipeline still recovers the known exact rows,
- the report keeps the boundary wording visible.

This keeps the next v2.8 step clean: either define deterministic priority derivation outside the native engine, or lower this explicit-column contract while preserving the same semantics.
