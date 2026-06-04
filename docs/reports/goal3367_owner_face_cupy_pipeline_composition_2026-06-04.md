# Goal3367: Owner-Face CuPy Pipeline Composition

Date: 2026-06-04

Status: internal v2.8 partner-device continuation. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3365 adds a CuPy device-column continuation for owner-face selection. Goal3362/3364 provide the CuPy continuation for the membership filter. Goal3367 composes those pieces into one optional helper:

- `run_closed_shape_owner_face_priority_membership_pipeline_cupy(...)`

This gives callers a single composed CuPy device-column pipeline for selection plus membership filter while preserving the generic owner-face contract.

## Contract

The composed helper:

- accepts generic incident point/face/count columns,
- accepts caller-supplied priority point/face/value columns,
- accepts generic candidate point/shape columns,
- accepts generic topology shape/left-face/right-face columns,
- runs CuPy owner-face selection first,
- passes selected owner point/face device columns directly into the CuPy membership filter,
- returns filtered membership columns plus selection diagnostic columns.

The helper returns:

- `point_id`, `shape_id`, `membership`, `owner_face_id`,
- `selection_point_id`, `selection_owner_face_id`,
- `selection_incident_face_count`, `selection_candidate_count`,
- `selection_status_code`, `selection_status_code_labels`.

The native engine still does not infer ownership policy. Priorities remain caller/data policy.

## Boundary

This is a composed CuPy device-column pipeline, not native RT traversal and not a native/device lowering of the full owner-face pipeline.

This does not authorize release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy claims.

pod evidence required before using this as evidence for any device-lowered path:

- CuPy availability,
- selection plus membership filter parity against the Python columnar reference,
- explicit unresolved-owner drop behavior,
- full owner-face family non-regression with CuPy available.

Still blocked:

- native/device lowering of the full owner-face pipeline,
- default selection of this composed helper,
- release or public performance wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

## Pod Evidence

Collected on 2026-06-04:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000`
- CuPy: `14.1.1`

Focused composed-pipeline command:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal3367_owner_face_cupy_pipeline_composition_test \
  tests.goal3365_owner_face_cupy_selection_continuation_test \
  tests.goal3364_owner_face_cupy_review_gap_closure_test \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3354_owner_face_columnar_selection_front_door_test \
  tests.goal3355_owner_face_columnar_filter_front_door_test
```

Focused result:

```text
Ran 30 tests in 0.830s
OK
```

Full owner-face family rerun with CuPy available:

```text
Ran 89 tests in 0.760s
OK
```

## Validation

Goal3367 tests cover:

- contract registration,
- composed CuPy output parity with Python columnar selection plus filter when CuPy is available,
- selection diagnostics staying visible,
- explicit drop behavior for unresolved owners,
- report boundary wording.
