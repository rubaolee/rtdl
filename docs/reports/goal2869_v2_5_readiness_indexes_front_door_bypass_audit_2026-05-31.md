# Goal2869 v2.5 Readiness Indexes Front-Door Bypass Audit

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2867 added a static audit proving that app-facing v2.5 code does not bypass
the promoted generic partner front doors by calling raw `run_triton_*` preview
helpers. Goal2868 then opened a broad external review request for the last-day
v2.5 work burst after Claude's status review.

This goal makes the Goal2867 audit part of the internal readiness packet instead
of leaving it as a standalone report. If that bypass audit report disappears,
`validate_v2_5_internal_readiness_packet(...)` now fails closed.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test.py`

The readiness packet now requires:

- `docs/reports/goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md`
- `docs/reports/goal2869_v2_5_readiness_indexes_front_door_bypass_audit_2026-05-31.md`

The allowed next actions now explicitly include:

- keep the Goal2867 front-door bypass audit green;
- triage the Goal2868 last-day external review before any future release packet;
- request fresh 3-AI release review only if the user asks for release.

## Boundary

This is a metadata and readiness-indexing update. It is not a v2.5 release authorization,
not a public speedup claim, not a broad RT-core claim, not a
whole-app speedup claim, not a true-zero-copy claim, and not package-install
wording.

Goal2868 is a call for review, not release consensus. A future release packet
still requires an explicit user request and fresh 3-AI release review.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test \
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test \
  tests.goal2865_current_head_packet_after_front_doors_test \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 22 tests in 0.684s
OK
```

## Codex Verdict

`accept-with-boundary`
