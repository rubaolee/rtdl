# Goal2871 Hit-Stream Torch Carrier Seam Authority Guard

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

The Goal2868 Claude review accepted the v2.5 packet with a release-boundary
finding: the legacy torch carrier is bounded, but release review should not rely
on prose alone to prove that transfer/copy/lifetime metadata comes only from the
neutral buffer seam.

Goal2871 adds that executable guard. Torch may remain a Triton launch carrier,
but it is not the source of transfer status, copy status, lifetime state,
ownership state, zero-copy authorization, or native-output promotion authority.

## Implementation

Updated:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2871_hit_stream_torch_carrier_seam_authority_guard_test.py`

New public validator:

- `validate_v2_5_hit_stream_neutral_seam_authority(...)`

The validator checks that:

- the reconciliation contract names `neutral_buffer_seam` as the
  transfer/copy/lifetime authority;
- the torch carrier adapter does not contain forbidden authority fields such as
  `transfer_status`, `copy_status`, `lifetime_state`, `owner_state`,
  `zero_copy_claim_authorized`, or `native_device_output_promotion_ready`;
- neutral seam metadata does contain the required authority fields;
- torch remains Triton-only and is not promoted to a neutral protocol;
- true-zero-copy and public-speedup claims remain false.

## Boundary

This closes the metadata-authority part of the Goal2868 torch-carrier finding.
It does not remove the torch launch carrier, does not promote Triton, and is not a v2.5 release authorization.
It is not true zero-copy, not a public speedup
claim, and not package-install wording.

Before any future release review, the remaining release question is whether the
torch launch carrier should be physically removed or kept as a bounded
Triton-only runtime bridge after the neutral-seam authority guard.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 23 tests in 0.188s
OK
```

Expanded local readiness slice:

```text
py -3 -m unittest \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test \
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test \
  tests.goal2865_current_head_packet_after_front_doors_test \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2861_v2_5_generic_partner_front_door_completion_test \
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2806_v2_5_internal_readiness_packet_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test

Ran 61 tests in 1.290s
OK (skipped=1)
```

## Codex Verdict

`accept-with-boundary`
