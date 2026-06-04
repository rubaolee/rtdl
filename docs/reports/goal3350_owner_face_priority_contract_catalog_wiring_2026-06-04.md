# Goal3350: Owner-Face Priority Contract Catalog Wiring

Date: 2026-06-04

Status: internal v2.8 discovery update. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3349 created the formal explicit-priority owner-face pipeline contract. Goal3350 updates primitive discovery so `candidate.closed_shape_topology_membership_count_2d` points at that contract report instead of the older Goal3345 reference-pipeline note.

This is not a promotion. The node remains:

- `layer = candidate_experimental`
- `status = candidate_behavior`

## Change

Updated `src/rtdsl/primitive_hierarchy.py`:

- reference path changed to `docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md`,
- summary now mentions the formal priority pipeline contract,
- intent phrases include discovery text for the explicit priority owner-face pipeline contract.

Regenerated `docs/rtdl_primitive_catalog.md` from the hierarchy source of truth.

## Boundary

The discovery surface now points users and future implementers at the stricter Goal3349 contract, but the primitive is still not accepted as a default native/device primitive.

Still blocked before promotion:

- deterministic priority derivation contract or explicit caller priority columns,
- same-contract tests against Python reference semantics,
- native/device implementation evidence if lowered,
- pod evidence for any selected OptiX path,
- external review before any public performance or paper-reproduction wording.

The native engine must continue to consume explicit generic columns only. It must not infer CDB, RayJoin, map/entity, or paper-system ownership policy.
