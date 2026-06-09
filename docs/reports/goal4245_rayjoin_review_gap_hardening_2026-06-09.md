# Goal4245 RayJoin Review Gap Hardening

Date: 2026-06-09

Status: internal review-followup hardening accepted with boundary

## Purpose

Goal4245 applies the two minor hardening findings from the Goal4241 Claude
review of the RayJoin long-repeat packet.

## Changes

| Finding | Action |
| --- | --- |
| Goal4239 report describes a 20+ second long-repeat run, but the test only required `wrapper_elapsed_sec > 10.0`. | `tests.goal4239_rayjoin_dedicated_long_repeat_profile_test` now requires `wrapper_elapsed_sec > 20.0`. |
| `rtdl_beats_rayjoin_claim_authorized` was guarded by JSON scan tests but not structurally represented in the target-map dataclass. | `CurrentMajorPerformanceTarget` now has a `rtdl_beats_rayjoin_claim_authorized` field, exports it in metadata, and rejects `True` values in `__post_init__`; `tests.goal4219_major_performance_target_map_test` asserts it stays false. |

## Validation

Focused validation passed:

```text
py -3 -m unittest \
  tests.goal4239_rayjoin_dedicated_long_repeat_profile_test \
  tests.goal4243_short_row_long_repeat_refresh_test \
  tests.goal4219_major_performance_target_map_test \
  tests.goal4235_current_head_rehearsal_after_measurement_closure_test \
  tests.goal4230_ten_app_measurement_adequacy_closure_test

Ran 19 tests ... OK
```

## Boundary

Goal4245 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RayJoin paper-reproduction wording,
RTDL-beats-RayJoin wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, or app-specific native-engine logic.
