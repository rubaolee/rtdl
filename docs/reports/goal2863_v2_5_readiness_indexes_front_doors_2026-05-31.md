# Goal2863: v2.5 Readiness Indexes Generic Front Doors

Status: metadata-only readiness hardening.

Date: 2026-05-31

## Purpose

Goal2861 completed the promoted v2.5 benchmark operation set at the generic
partner-adapter front door: `v2_5_triton_front_door_coverage()` now reports
10/10 promoted benchmark apps as `adapter_front_door_ready`.

This goal indexes that state in the internal readiness packet so future edits
cannot silently regress from generic front-door APIs back to dispatcher-only
access.

## What Changed

`src/rtdsl/v2_5_internal_readiness.py` now:

- imports and records `front_door_coverage`;
- requires the Goal2861 implementation report;
- requires the Goal2862 consensus report;
- requires the independent Gemini review for Goal2861;
- validates that `front_door_coverage` still covers exactly 10 benchmark apps;
- validates that all 10 apps have `adapter_front_door_ready` status;
- fails closed if any app has dispatcher-only or missing front-door operations.

## Boundary

This is metadata-only readiness indexing. It is not a release authorization, not
a speedup claim, not package-install evidence, and not a public v2.5 launch
decision. It only makes the internal packet aware that the user-facing generic
partner front doors have been completed for the promoted benchmark operation
set.

## Validation

Focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2857_v2_5_readiness_indexes_packet_runner_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test
```

Expected result: all tests pass.
