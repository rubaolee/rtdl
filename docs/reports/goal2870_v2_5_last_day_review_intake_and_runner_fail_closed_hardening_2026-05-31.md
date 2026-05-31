# Goal2870 v2.5 Last-Day Review Intake And Runner Fail-Closed Hardening

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2868 requested critical external review of the v2.5 work from the Goal2773
Claude review intake through the Goal2867 app-facing front-door bypass audit.
Claude and Gemini both returned `accept-with-boundary` reviews. This goal
indexes those reviews into the internal readiness packet and hardens the
canonical packet-runner metadata checks in response to Gemini's compact-output
finding.

## Review Intake

Indexed external reviews:

- `docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`
- `docs/reviews/goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`

Shared accepted boundary:

- the last-day v2.5 engineering packet is coherent for internal work;
- final release remains blocked;
- public speedup, broad RT-core speedup, whole-app speedup, true-zero-copy,
  package-install, automatic Triton selection, and app-specific native-engine
  claims remain unauthorized.

Key release-review blockers preserved from the reviews:

- remove or fully seam-route the legacy torch carrier before release review;
- prove per-op partner conformance and kernel-level determinism/tie-breaks;
- do not read 7/7 canonical harness pass as Tier A/B parity;
- handle Triton preview performance gaps with explicit fallback/default policy
  until a preview wins same-contract timing.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test.py`
- `docs/reports/goal2870_goal2868_last_day_review_intake_consensus_2026-05-31.md`

The internal readiness packet now requires the two Goal2868 review files and the
Goal2870 reports. It also exposes and validates compact packet-runner status
fields:

- `returncode_ok`
- `artifact_status_ok`
- `source_commit_consistent`

This directly addresses Gemini's compact-child-output concern: compact output is
acceptable only when the summary records clean child return codes, artifact
statuses, source consistency, dirty-artifact checks, and claim-boundary checks.

## Boundary

This is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not a true-zero-copy claim,
and not package-install wording.

The Goal2868 reviews are internal-packet reviews. They are not v2.5 release
consensus and do not replace a future user-requested fresh 3-AI release review.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test \
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test \
  tests.goal2865_current_head_packet_after_front_doors_test \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 26 tests in 0.764s
OK
```

Expanded local readiness slice:

```text
py -3 -m unittest \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test \
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test \
  tests.goal2865_current_head_packet_after_front_doors_test \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2861_v2_5_generic_partner_front_door_completion_test \
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 47 tests in 1.283s
OK (skipped=1)
```

## Codex Verdict

`accept-with-boundary`
