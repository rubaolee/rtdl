# Goal1011 RTX Public Wording Matrix

Date: 2026-04-26

## Problem

The public docs correctly separated two facts for `robot_collision_screening`:

- the prepared ray/triangle any-hit scalar pose-count path is a real RT-core path;
- public RTX speedup wording is blocked because Goal1008 larger repeats stayed below the 100 ms public-review timing floor.

The machine-readable source did not expose that distinction. The existing
`optix_app_benchmark_readiness_matrix()` and `rt_core_app_maturity_matrix()`
could say the app was technically ready, but there was no separate API for
public wording status.

## Change

Added `rtdsl.rtx_public_wording_matrix()` and
`rtdsl.rtx_public_wording_status(app)`.

The new statuses are:

- `public_wording_reviewed`
- `public_wording_blocked`
- `public_wording_not_reviewed`
- `not_nvidia_public_wording_target`

Goal1009's exact reviewed set is machine-readable as seven rows:

- `service_coverage_gaps`
- `outlier_detection`
- `dbscan_clustering`
- `facility_knn_assignment`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `ann_candidate_search`

`robot_collision_screening` remains `ready_for_rtx_claim_review` and
`rt_core_ready`, but is now explicitly `public_wording_blocked`.

## Tests

Added `tests/goal1011_rtx_public_wording_matrix_test.py`.

The test verifies:

- every public app has a public wording row;
- the reviewed public wording set is exactly seven apps;
- reviewed wording is bounded to named sub-paths and same-semantics baselines;
- robot remains technically RT-core ready while public wording is blocked;
- Apple RT and HIPRT demo apps are excluded from NVIDIA public wording.

## Documentation

Updated:

- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`

The docs now list `rtdsl.rtx_public_wording_matrix()` as a source of truth.

## Boundary

This goal does not authorize any new public speedup claim. It records the
existing Goal1009 reviewed wording and prevents implementation readiness from
being confused with public marketing wording.
