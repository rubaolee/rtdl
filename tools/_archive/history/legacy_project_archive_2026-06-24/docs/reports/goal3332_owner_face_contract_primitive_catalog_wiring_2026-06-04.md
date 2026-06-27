# Goal3332: Owner-Face Contract Primitive Catalog Wiring

Date: 2026-06-04

Status: metadata/catalog wiring. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3330 added an executable Python reference contract for owner-face closed-shape membership filtering. Goal3332 wires that contract into the primitive hierarchy so discovery points to the executable reference, not only the earlier Goal3324 candidate sketch.

Updated primitive:

- `candidate.closed_shape_topology_membership_count_2d`

Key metadata changes:

- Summary now states the primitive direction has an owner-face Python reference contract plus future native/device lowering.
- Outputs now include `owner_face_id`.
- Boundary now says owner-face ids are caller supplied and that CDB/RayJoin/map semantics remain app code.
- Intent phrases include filtering by caller-supplied owner face ids.
- `reference_path` now points to `docs/reports/goal3330_owner_face_closed_shape_membership_reference_contract_2026-06-04.md`.

## Validation

Local validation:

```text
Ran 26 tests in 0.077s
OK
primitive catalog up to date
```

Validated tests:

- `tests.goal3330_owner_face_closed_shape_membership_reference_contract_test`
- `tests.goal3324_closed_shape_topology_membership_candidate_test`
- `tests.goal3073_v2_7_generated_primitive_catalog_test`
- `tests.goal3090_v2_7_discovery_metadata_backfill_test`
- `tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test`

## Boundary

This is still a candidate/native-lowering direction, not a finished native primitive. The Python reference contract gives future device work a same-contract target while preserving the app-agnostic ownership split.
