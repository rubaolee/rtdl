# Goal4636 Threshold-Summary Target Protocol Review Record

Date: 2026-06-25

Status: `target_protocol_approved_with_required_amendments_pod_may_proceed_after_runner_floor_patch_not_release`

## Review Inputs

- `future/v4/reviews/call_for_review_v4_goal4636_threshold_summary_target_protocol_2026-06-25.md`
- `future/v4/v4_goal4636_threshold_summary_operator_target_protocol_2026-06-25.md`
- `src/rtdsl/v4_goal4636_threshold_summary_target.py`
- `tests/v4_goal4636_threshold_summary_target_test.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`

## Claude Review

Raw review:

- `future/v4/reviews/claude_v4_goal4636_threshold_summary_target_protocol_review_2026-06-25.raw.md`

Verdict:

- `approve_with_required_amendments`

Summary:

- `fixed_radius_threshold_summary_2d` is accepted as a marginal but valid
  generic continuation target.
- The distinction from existing count-threshold is real because this target is
  a scalar threshold-summary workflow, not a per-query flag column.
- `rtdl_native_prepared_runner` scope is honest, but cannot be blindly inserted
  into the existing framework-partner catalog schema.
- The 1.20x Embree floors are material, but the runner originally failed to
  enforce them in `failed_checks`.
- POD may proceed after patching the runner floor check.

Required amendments:

1. Before catalog promotion, define native prepared-runner scope separately
   from framework partners or make it a first-class catalog scope.
2. Before or alongside POD execution, hard-check the declared Embree material
   floors in the runner.

Amendment 2 status:

- applied before POD;
- `runner_below_embree_phase_total_material_floor` and
  `runner_below_embree_wrapper_wall_material_floor` are now emitted by the
  runner when floors are missed;
- regression test added.

Amendment 1 status:

- open until post-POD promotion decision;
- blocks catalog promotion if the POD gate passes and the catalog scope is not
  resolved.

## Antigravity Review

Raw files:

- `future/v4/reviews/antigravity_v4_goal4636_threshold_summary_target_protocol_review_2026-06-25.raw.md`
- `future/v4/reviews/antigravity_v4_goal4636_threshold_summary_target_protocol_review_2026-06-25.stderr.txt`

Result:

- command exited `0`;
- stdout and stderr were empty;
- recorded as review debt, not a substantive review.

## Local Verification After Amendment 2

- `py -m unittest tests.v4_goal4636_threshold_summary_target_test`
  - `Ran 5 tests`
  - `OK`
- `py -m unittest tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test`
  - `Ran 8 tests`
  - `OK`
- `$env:PYTHONPATH='src;.'; py -m unittest tests.v3_phoenix_prepared_execution_session_runner_test`
  - `Ran 42 tests`
  - `OK`

## Decision

The Goal4636 POD gate may proceed under the patched runner.

This is not a release decision and not a measured catalog promotion. If the POD
gate passes, promotion still requires a separate decision that resolves
`rtdl_native_prepared_runner` catalog representation.

## Non-Authorization

This record does not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-Hausdorff speedup;
- all-benchmark speedup;
- measured catalog promotion;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- Hausdorff-native or other app-specific kernels.
