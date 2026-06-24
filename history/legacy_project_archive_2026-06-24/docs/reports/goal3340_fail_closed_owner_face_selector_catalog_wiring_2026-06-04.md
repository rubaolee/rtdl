# Goal3340: Fail-Closed Owner-Face Selector Catalog Wiring

Date: 2026-06-04

Status: metadata/catalog wiring. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3339 added a fail-closed incident owner-face selector. Goal3340 updates primitive discovery so `candidate.closed_shape_topology_membership_count_2d` points to the latest executable selector report instead of the earlier owner-face filter report.

Updated metadata:

- Summary names the fail-closed incident-face selector.
- Intent phrases include deriving an owner face only when incident topology has a unique maximum.
- `reference_path` points to `docs/reports/goal3339_fail_closed_incident_owner_face_selector_2026-06-04.md`.

## Boundary

The primitive remains `candidate_behavior` in the candidate/experimental layer. The selector is a conservative Python reference helper, not a promoted native primitive and not a RayJoin-specific fix.
