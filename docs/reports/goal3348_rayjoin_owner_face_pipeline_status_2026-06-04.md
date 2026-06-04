# Goal3348: RayJoin Owner-Face Pipeline Status

Date: 2026-06-04

Status: internal status report. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## What We Know

The current generic fast PIP count route is not broadly valid for all RayJoin/CDB inputs.

Evidence:

- Soil slice validates: exact `1471`, fast `1471`.
- County start256 slice fails: exact `1417`, fast `1429`, delta `+12`.
- Full county also fails.
- The county failure is seven overcounted point ids with concrete extra shape ids, not a random instability.
- Extra shape ids are topology-adjacent to exact shape ids through shared face ids.

## What We Added

Generic, app-agnostic pieces:

- `chains_to_topology_rows(...)`
- `chains_to_incident_face_candidate_rows(...)`
- `OptixNativeDevicePairColumnOutput.as_cupy_columns()`
- `filter_closed_shape_membership_candidates_by_owner_face(...)`
- `select_unique_owner_faces_from_incident_candidates(...)`
- `select_owner_faces_from_incident_candidates_with_priority(...)`
- `owner_face_ids_by_point_from_selection_rows(...)`

Primitive discovery now routes `candidate.closed_shape_topology_membership_count_2d` to the end-to-end Python reference pipeline.

## What The Pipeline Proves

For the seven known county mismatches:

1. Incident topology exposes the needed owner face.
2. A simple left/right point-chain rule is insufficient.
3. A simple incident-frequency rule is insufficient because candidates tie.
4. Explicit caller/data priority rows can break the ties.
5. Priority-selected owner faces can filter fast candidate shape ids back to the known exact shape ids.

This proves expressiveness of the generic pipeline, not automatic RayJoin support.

## What Remains Blocked

Still blocked:

- broad fast PIP count correctness,
- automatic owner-face derivation,
- native/device lowering of priority owner-face filtering,
- RayJoin paper reproduction claims,
- RTDL-beats-RayJoin claims,
- broad RT-core speedup claims.

## Next Engineering Target

The next useful target is one of these, in order:

1. Define a deterministic generic owner-face priority derivation contract.
2. Build a device/native version of the explicit-priority owner-face filter once the contract is stable.
3. Expand topology event streams only if the derivation contract needs richer evidence than incident face candidate rows provide.

The native engine must continue to consume explicit generic columns. It must not infer CDB or RayJoin policy internally.

## Validation Checkpoints

- Local full chain: `Ran 59 tests in 0.063s OK`.
- Pod focused chain after fast-forward: `Ran 17 tests in 0.002s OK`.
