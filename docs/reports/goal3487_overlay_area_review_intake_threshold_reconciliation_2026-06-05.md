# Goal3487 - Overlay-Area Review Intake: Row Threshold Reconciliation

## Status

Implemented locally.

Goal3487 responds to the Goal3485 Claude review of Goals3482-3484.

Claude accepted the pre-kernel/payload/tiled chain with boundary, but flagged a
medium issue: the scalar evaluators used the clipping arithmetic epsilon
(`1e-12`) as the positive-row threshold, while Goal3482 defines the row
absolute tolerance as `1e-10`.

## What Changed

Updated module:

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`

Both scalar evaluators now separate two concepts:

- `eps`: geometric clipping arithmetic tolerance;
- `row_positive_threshold`: row classification threshold.

If `row_positive_threshold` is omitted, both evaluators use:

- `V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE = 1e-10`

This means rows with tiny positive area below the policy threshold are not
counted as positive oracle rows by default, matching the pre-kernel policy.

## Test Additions

Updated tests:

- `tests/goal3483_overlay_area_prepared_payload_test.py`
- `tests/goal3484_overlay_area_tiled_scalar_evaluator_test.py`

New coverage:

- tiny-overlap fixture with area between `1e-12` and `1e-10`;
- default positive-row count is `0`;
- explicit low threshold can still count it as positive;
- multi-component, multi-row prepared-pair fixture.

## Boundary

This goal does not authorize release packaging, public speedup wording,
RT-core speedup wording, true-zero-copy wording, paper reproduction claims,
hidden dispatch, automatic partner selection, full overlay completion claims,
or app-specific native engine behavior.

It only reconciles pre-kernel policy with CPU prototype classification before
the future device continuation is expanded.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3483_overlay_area_prepared_payload_test`
- `py -3 -m unittest tests.goal3484_overlay_area_tiled_scalar_evaluator_test`
- `py -3 -m unittest tests.goal3486_overlay_area_cupy_tiled_prototype_test`

