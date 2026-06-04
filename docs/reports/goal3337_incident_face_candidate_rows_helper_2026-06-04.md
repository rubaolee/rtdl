# Goal3337: Incident Face Candidate Rows Helper

Date: 2026-06-04

Status: generic dataset helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3335 showed that needed owner faces are present in local CDB incident topology, but simple frequency counts can tie. Goal3337 adds a reusable helper that exposes those candidate faces without choosing ownership:

- `chains_to_incident_face_candidate_rows(...)`

This helper complements:

- `chains_to_probe_points(...)`
- `chains_to_topology_rows(...)`
- `filter_closed_shape_membership_candidates_by_owner_face(...)`

## Contract

For each selected chain, the helper uses the chain's first point as the probe coordinate, matching `chains_to_probe_points(...)`. It then counts face ids from chains incident to that coordinate.

Output rows:

- `point_id`
- `face_id`
- `incident_face_count`
- `incident_chain_count`
- `probe_x`
- `probe_y`

The helper deliberately does not select an owner face. It makes ambiguity visible to app/data-layer code and future generic topology contracts.

## Boundary

This is not a RayJoin fix and not a native primitive. It is a small generic metadata helper that lets future work derive or validate caller-supplied owner-face columns without hiding dataset-specific policy inside RTDL's native engine.
