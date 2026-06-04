# Goal3364: Owner-Face CuPy Review Gap Closure

Date: 2026-06-04

Status: internal v2.8 device-continuation hardening. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3363 Claude review accepted the Goal3362 CuPy owner-face filter continuation with boundary. The review identified four divergences that had to be resolved before the helper could be promoted beyond its current optional device-continuation role:

- duplicate candidate pairs were not deduplicated like the Python reference,
- negative topology face ids were not explicitly excluded,
- multiple owner faces per point were not supported by the device lookup,
- left/right face tie handling used a left-first expression instead of a minimum matched-face expression.

Goal3364 closes these findings by hardening the helper and documenting the remaining intended boundary.

## Code Closure

`filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(...)` now:

- rejects duplicate `(point_id, shape_id)` candidate pairs by default using a device-side lexicographic duplicate check,
- rejects duplicate owner point ids even when the legacy `require_unique_owner_point=False` opt-out is passed, because multi-owner-per-point semantics need a richer device join,
- excludes negative left/right topology face ids before matching owner faces,
- computes the returned owner face with a minimum matched-face expression instead of a left-first `where`.

The owner-face priority pipeline contract now records these device-helper limits in `filter_policy`:

- `device_cupy_filter_candidate_duplicates = fail_closed_by_default`
- `device_cupy_filter_face_ids = non_negative_matches_only`
- `device_cupy_filter_owner_multiplicity = single_owner_face_per_point_only`

The validator enforces those policy strings so this boundary cannot silently disappear.

## Boundary

The CuPy helper remains an optional columnar pipeline helper. It is not native RT traversal and it is not selected as a default device-lowered path.

The only remaining semantic restriction is intentional: this helper is single-owner-face-per-point. Callers that need multiple owner faces per point must use the Python/columnar reference path or a future richer device join.

Still blocked:

- native/device lowering of the full owner-face pipeline,
- default selection of this helper,
- release or public performance wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

## Pod Evidence

Collected on 2026-06-04 after the Goal3364 hardening patch:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000`
- CuPy: `14.1.1`

Command:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal3364_owner_face_cupy_review_gap_closure_test \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3361_owner_face_filter_policy_validator_hardening_test \
  tests.goal3359_owner_face_review_gap_closure_test \
  tests.goal3358_owner_face_columnar_known_mismatch_fixture_test
```

Result:

```text
Ran 20 tests in 0.743s
OK
```

Full owner-face family rerun with CuPy available:

```text
Ran 80 tests in 0.766s
OK
```

## Validation

Goal3364 tests cover:

- contract documentation and validator enforcement for the CuPy helper boundaries,
- duplicate candidate-pair fail-closed behavior,
- duplicate owner-point fail-closed behavior when the opt-out is passed,
- negative face-id exclusion parity with the Python columnar reference,
- report linkage to the Goal3363 Claude review.
