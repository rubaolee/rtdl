# Goal3342: Priority Owner-Face Selector Reference

Date: 2026-06-04

Status: Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3339 correctly fails closed when incident face counts tie. Goal3342 adds an explicit caller-priority extension:

- `select_owner_faces_from_incident_candidates_with_priority(...)`

Selection rule:

1. Higher `incident_face_count` wins.
2. If counts tie, lower caller-supplied `priority` wins.
3. Missing or tied priorities fail closed by default.

## Boundary

The helper does not infer priorities. Priority rows are caller/data policy. This keeps RTDL generic:

- RTDL can execute the count/priority selection contract.
- The app or data loader must explain why a face has higher priority.
- Native code must not guess CDB or RayJoin ownership semantics.

## RayJoin Relevance

Using the Goal3335 incident-face rows, caller-supplied priorities can select the same owner faces used by the Goal3330 reconciliation. That proves the contract is expressive enough, not that RTDL has solved automatic owner-face derivation.

The current fast RayJoin PIP route remains validated-domain-only.
