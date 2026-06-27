# Call For Review: V4 Section 8 Prepared Hot-Path Validation

Date: 2026-06-24
Requested verdict labels: `accept_prepared_hot_path_credit_no_release`, `reject_protocol_revision`, `reject_measurement_invalid`, or `needs_rerun`

## Review Materials

- Original design: `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`
- Original protocol and report:
  - `future/v4/rtdl_v4_0_section8_fixed_radius_count_threshold_validation_protocol_2026-06-24.md`
  - `future/v4/evidence/v4_section8_fixed_radius_validation_report_2026-06-24.md`
- Claude backfill review:
  - `future/v4/reviews/claude_v4_section8_fixed_radius_count_threshold_backfill_review_2026-06-24.md`
- Revised protocol and result:
  - `future/v4/rtdl_v4_0_section8_prepared_hot_path_protocol_2026-06-24.md`
  - `future/v4/evidence/v4_section8_prepared_hot_path_validation_report_2026-06-24.md`
  - `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`
- Harness/code:
  - `scripts/v4_section8_prepared_hot_path_validation.py`
  - `examples/current/apps/ml/rtdl_outlier_detection_app.py`
  - `tests/v4_section8_fixed_radius_count_threshold_validation_test.py`

## Measured Outcome

The original whole-call route gate failed and remains failed.

The revised prepared hot-path gate passed:

- 8192 copies: 1.655x
- 32768 copies: 1.772x
- 131072 copies: 1.970x

Correctness passed on all sizes.

## Questions For Reviewer

1. Was the protocol revision legitimate, given Claude's prior review and the existing prepared-session model?
2. Is the timing boundary valid and matched across baseline/candidate?
3. Is the result valid enough to grant prepared-session summary hot-path credit?
4. What claim wording, if any, is authorized?
5. What remains required before adding another Tier-2 primitive?
6. Confirm no V4 release claim, broad V4 speedup claim, near-handwritten OptiX claim, Tier-3 callback claim, or app-specific native engine claim is authorized.

## Non-Authorization

This packet does not authorize V4 release, broad V4 performance claims, near-handwritten OptiX wording, Tier-3 callback claims, C ABI/embedding claims, or app-specific native engine claims.

