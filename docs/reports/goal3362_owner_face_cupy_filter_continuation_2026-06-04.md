# Goal3362: Owner-Face CuPy Filter Continuation

Date: 2026-06-04

Status: internal v2.8 partner-device continuation. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goals3353-3355 produced a complete Python reference columnar owner-face pipeline. Goal3362 adds the first device-column continuation for the final membership filter stage:

- `filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(...)`

This is a CuPy device-column continuation over explicit generic columns. It is not native RT traversal and it does not infer app ownership.

## Contract

Inputs mirror the Python columnar filter:

- candidate point/shape id columns,
- topology shape/left-face/right-face columns,
- optional topology face-presence columns,
- owner point/face columns.

The helper:

- sorts owner point ids and topology shape ids on device,
- uses device `searchsorted` to locate owner faces and topology rows,
- drops missing-topology candidates,
- fails closed on missing owner rows by default,
- requires unique owner point ids by default,
- returns CuPy arrays for `point_id`, `shape_id`, `membership`, and `owner_face_id`.

## Boundary

This is partner-device continuation work. It is not an OptiX native implementation, not native RT traversal, and not a release/performance claim.

pod evidence required before using this as evidence for any device-lowered path:

- CuPy availability,
- same-contract parity against the Python columnar reference,
- missing-topology and topology face-presence behavior,
- fail-closed missing/duplicate owner behavior.

## Pod Evidence

Collected on 2026-06-04:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000`
- Driver: `580.126.09`
- CuPy: `14.1.1`
- Repo commit basis: `04bd3c01` plus Goal3362 working files copied into the pod checkout before commit.

Command scope:

```text
python3 -m unittest \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3361_owner_face_filter_policy_validator_hardening_test \
  tests.goal3359_owner_face_review_gap_closure_test \
  tests.goal3358_owner_face_columnar_known_mismatch_fixture_test
```

Result:

```text
Ran 15 tests in 8.593s
OK
```

## Validation

Goal3362 tests cover:

- contract registration,
- CuPy output parity with the Python columnar reference when CuPy is available,
- missing-topology drop behavior,
- optional topology face-presence gating,
- missing-owner and duplicate-owner fail-closed behavior,
- report boundary wording.
