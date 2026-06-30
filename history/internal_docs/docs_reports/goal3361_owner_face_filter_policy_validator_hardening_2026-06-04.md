# Goal3361: Owner-Face Filter Policy Validator Hardening

Date: 2026-06-04

Status: internal v2.8 hardening. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3360 Claude follow-up review accepted the Goal3358-3359 closure and noted one minor future hardening item: `topology_face_presence_columns` was tested, but the validator only enforced `missing_owner` and `missing_topology`.

Goal3361 closes that minor note.

## Change

`validate_owner_face_priority_pipeline_contract()` now also enforces:

- `filter_policy.topology_face_presence_columns = gate_left_and_right_face_ids_when_present`

This means all three filter-policy strings are both documented and validator-checked:

- `missing_owner = fail_closed_by_default`
- `missing_topology = drop_candidate`
- `topology_face_presence_columns = gate_left_and_right_face_ids_when_present`

## Boundary

This is a validator hardening only. It does not promote the owner-face pipeline beyond Python reference status and does not authorize any release, speedup, RT-core, true zero-copy, or RayJoin reproduction wording.

Native/device lowering still requires pod/native evidence and same-contract validation.
