# Goal3365: Owner-Face CuPy Selection Continuation

Date: 2026-06-04

Status: internal v2.8 partner-device continuation. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goals3353-3355 built the owner-face priority pipeline as a Python/columnar reference. Goal3362 moved the final membership filter into an optional CuPy device-column continuation, and Goal3364 closed the Claude review gaps for that filter.

Goal3365 adds the matching CuPy continuation for the selection stage:

- `select_owner_faces_from_incident_candidate_columns_with_priority_cupy(...)`

This keeps the owner-face pipeline moving toward device-resident columnar continuation while preserving the app-agnostic rule: RTDL consumes generic point/face/count/priority columns, and the caller supplies priority policy.

## Contract

Inputs mirror the Python columnar selector:

- incident point id column,
- incident face id column,
- incident face count column,
- priority point id column,
- priority face id column,
- priority value column.

The helper:

- groups incident candidates by point on device,
- selects a unique maximum incident count when one exists,
- breaks count ties only with explicit caller-supplied priority values,
- fails closed on missing or tied priorities by default,
- can emit ambiguous rows when `ambiguity_policy="emit_ambiguous"`,
- rejects duplicate incident or priority `(point_id, face_id)` pairs by default,
- returns CuPy arrays for selected point ids, owner face ids, incident counts, candidate counts, and numeric selection_status_code values.

The device continuation returns `selection_status_code` instead of Python status strings. The status-code label map is returned as metadata:

- `unique_max_incident_face = 1`
- `priority_tie_break = 2`
- `missing_priority = 3`
- `ambiguous_priority_tie = 4`

## Boundary

This is partner-device continuation work. It is not an OptiX native implementation, not native RT traversal, and not a release/performance claim.

This helper does not infer owner-face priorities. It only applies caller-supplied priority columns.

pod evidence required before using this as evidence for any device-lowered path:

- CuPy availability,
- same-contract parity against the Python columnar selector,
- fail-closed missing-priority behavior,
- fail-closed duplicate incident/priority pair behavior,
- ambiguous-status emission behavior.

Still blocked:

- native/device lowering of the full owner-face pipeline,
- default selection of this helper,
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

Focused command:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal3365_owner_face_cupy_selection_continuation_test \
  tests.goal3364_owner_face_cupy_review_gap_closure_test \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3354_owner_face_columnar_selection_front_door_test \
  tests.goal3355_owner_face_columnar_filter_front_door_test
```

Focused result:

```text
Ran 26 tests in 1.230s
OK
```

Full owner-face family rerun with CuPy available:

```text
Ran 85 tests in 0.687s
OK
```

## Validation

Goal3365 tests cover:

- contract registration,
- CuPy output parity with the Python columnar selector when CuPy is available,
- numeric status codes for unique-max and priority-tie-break outcomes,
- fail-closed missing-priority behavior,
- fail-closed duplicate incident and priority pair behavior,
- ambiguous-priority status emission,
- report boundary wording.
