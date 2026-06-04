# Goal3343: Priority Owner-Face Selector Catalog Wiring

Date: 2026-06-04

Status: metadata/catalog wiring. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3342 added an explicit-priority owner-face selector. Goal3343 updates primitive discovery so the closed-shape topology candidate points to the latest selector report.

Updated primitive:

- `candidate.closed_shape_topology_membership_count_2d`

Changes:

- Summary names the explicit-priority tie-break helper.
- Intent phrases include breaking incident topology ties only with caller-supplied face priorities.
- `reference_path` now points to `docs/reports/goal3342_priority_owner_face_selector_reference_2026-06-04.md`.

## Boundary

The candidate remains unpromoted. Caller priorities are explicit app/data policy; the native engine must not infer CDB or RayJoin ownership semantics.
