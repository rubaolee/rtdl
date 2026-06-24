# Goal3368: Owner-Face CuPy Selection Review Gap Closure

Date: 2026-06-04

Status: internal v2.8 review-gap closure. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3366 Claude review accepted Goal3365 with boundary and identified selector-promotion gaps. Goal3368 closes the selector-specific gaps that were not already closed by Goal3367.

## Closure Map

| Goal3366 finding | Closure |
| --- | --- |
| `selection_status_code` differs from Python `selection_status` and must be documented. | Goal3368 updates the CuPy selector docstring and contract `promotion_requirements`; the validator now requires `selection_status_code` translation language. |
| `ambiguity_policy="drop"` parity was untested. | Goal3368 adds a CuPy/Python columnar parity test where unresolved tied owner faces are dropped while a unique-max point is preserved. |
| End-to-end selection to filter pipeline test was missing. | Goal3367 closed this with `run_closed_shape_owner_face_priority_membership_pipeline_cupy(...)` and pod evidence. |
| Missing-priority and ambiguous-priority emitted rows were not parity-tested against the Python reference. | Goal3368 adds explicit CuPy/Python parity tests for both emitted status paths. |

## Boundary

The CuPy selector and composed pipeline remain optional partner-device continuations. They are not native RT traversal, not default device-lowered paths, and not release/performance artifacts.

Still blocked:

- native/device lowering of the full owner-face pipeline,
- default selection of the CuPy selector or composed helper,
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

Focused review-gap closure command:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal3368_owner_face_cupy_selection_review_gap_closure_test \
  tests.goal3367_owner_face_cupy_pipeline_composition_test \
  tests.goal3365_owner_face_cupy_selection_continuation_test \
  tests.goal3364_owner_face_cupy_review_gap_closure_test \
  tests.goal3362_owner_face_cupy_filter_continuation_test
```

Focused result:

```text
Ran 24 tests in 0.850s
OK
```

Full owner-face family rerun with CuPy available:

```text
Ran 94 tests in 0.832s
OK
```

## Validation

Goal3368 tests cover:

- contract documentation and validator enforcement for status-code translation,
- `ambiguity_policy="drop"` parity,
- missing-priority emitted-row parity,
- ambiguous-priority emitted-row parity,
- report linkage to the Goal3366 Claude review.

Pod evidence is still required for the CuPy-specific parity tests before citing this closure as GPU-executed evidence.
