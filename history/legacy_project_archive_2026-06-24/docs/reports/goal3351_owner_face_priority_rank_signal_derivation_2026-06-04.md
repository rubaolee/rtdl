# Goal3351: Owner-Face Priority Rank-Signal Derivation

Date: 2026-06-04

Status: internal v2.8 Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3349 formalized an explicit-priority owner-face pipeline, but it intentionally required `priority_rows` to come from the caller/data layer. Goal3351 adds a generic helper for one safe case: when caller-supplied rank signals are already present, RTDL can deterministically convert those rank signals into `priority_rows`.

New helper:

- `derive_owner_face_priority_rows_from_rank_signals(...)`

## Contract

Inputs:

- rows with `point_id`,
- rows with `face_id`,
- one or more caller-declared `rank_fields`.

Output:

- `priority_rows(point_id,face_id,priority,priority_rank_key)`

Rule:

1. Rank fields are interpreted as a tuple in caller-declared order.
2. Lower rank tuple receives lower priority.
3. Priorities restart per `point_id`.
4. missing, duplicate, or tied evidence fails closed by default.
5. `tie_policy="drop"` can omit tied rows, which keeps downstream selection fail-closed if those priorities are required.

## Boundary

This helper does not infer ownership, CDB policy, RayJoin assignment semantics, map/entity lookup, or paper-system logic. The caller supplies the rank fields and their meaning. RTDL only performs deterministic ordering over generic columns.

The helper is registered in the Goal3349 contract as an optional priority-derivation helper. It does not promote `candidate.closed_shape_topology_membership_count_2d` beyond `candidate_behavior`.

## Why This Helps

The next native/device lowering target needs stable semantics before any code moves closer to OptiX. This helper makes the priority-row seam explicit:

- apps or data loaders can provide rank signals,
- RTDL can validate and rank them in a reproducible way,
- ambiguous data remains blocked rather than guessed,
- the native engine still only consumes explicit generic columns.

## Validation

Goal3351 tests cover:

- lower rank tuple becomes lower priority,
- derived priorities feed `select_owner_faces_from_incident_candidates_with_priority(...)`,
- empty rank fields fail,
- missing rank fields fail,
- duplicate point/face rank signals fail,
- tied rank tuples fail by default,
- optional `tie_policy="drop"` omits tied rows,
- the Goal3349 contract lists the helper,
- the report keeps claim and ownership boundaries visible.
