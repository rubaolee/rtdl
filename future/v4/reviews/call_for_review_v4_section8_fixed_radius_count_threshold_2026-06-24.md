# Call For Review: V4 Section 8 Fixed-Radius Count-Threshold Validation

Date: 2026-06-24
Requested verdict labels: `accept_strict_fail_revise_architecture`, `accept_pass_promote_tier2`, `reject_measurement_invalid`, or `needs_rerun`

## Review Materials

- Design: `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`
- Protocol: `future/v4/rtdl_v4_0_section8_fixed_radius_count_threshold_validation_protocol_2026-06-24.md`
- Report: `future/v4/evidence/v4_section8_fixed_radius_validation_report_2026-06-24.md`
- Raw JSON: `future/v4/evidence/v4_section8_fixed_radius_result_2026-06-24.json`
- Phase profile JSON: `future/v4/evidence/v4_section8_summary_route_phase_profile_2026-06-24.json`
- Harness: `scripts/v4_section8_fixed_radius_count_threshold_validation.py`
- Phase profile harness: `scripts/v4_section8_summary_route_phase_profile.py`
- App route: `examples/current/apps/ml/rtdl_outlier_detection_app.py`
- Test: `tests/v4_section8_fixed_radius_count_threshold_validation_test.py`

## What Changed

The app route was corrected so the full rows baseline no longer times an O(N^2) brute-force oracle. The fixture has an exact tiled oracle, now used for all output modes. A test prevents regression to the quadratic oracle. The harness also gained `--progress` stderr logging for route-level auditability.

## Measured Outcome

Strict Section 8 status is `fail`.

Scalar fused route passed the 2.0x gate on all serious sizes in the final rerun:

- 8192 copies: 2.100x
- 32768 copies: 2.157x
- 131072 copies: 2.434x

Summary fused route did not pass the 1.5x gate on two serious sizes in the final rerun:

- 8192 copies: 1.415x
- 32768 copies: 1.394x
- 131072 copies: 1.497x

Correctness passed on all sizes.

Phase-profile follow-up shows summary no-prepare medians beat rows total medians by more than 2x at all sizes, while the written Section 8 harness includes prepare/setup inside every app-route repeat. Please review whether this justifies a protocol revision to prepared-session hot-path timing, or whether the whole-call strict fail should stand for V4.0.

## Questions For Reviewer

1. Is the oracle-boundary fix valid, or does this require a rerun with a different correctness strategy?
2. Is the measurement valid enough to accept the strict gate outcome as `fail`?
3. Should V4.0 stop the broad Tier-2 performance-release path under the written protocol?
4. Is it valid to preserve a narrower scalar fused primitive track while revising the summary-route claim?
5. What next experiment should be required before adding more Tier-2 primitives?
6. Does the phase profile justify a revised prepared-session hot-path protocol, or must the current whole-call route gate remain controlling?
7. Confirm no V4 release claim, broad speedup wording, near-handwritten OptiX claim, Tier-3 callback claim, or app-specific native engine claim is authorized.

## Non-Authorization

This packet does not authorize V4 release, broad V4 performance claims, public speedup wording, Tier-3 callback claims, C ABI/embedding claims, or near-handwritten OptiX wording.
