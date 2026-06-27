# Call For Review: V4 Goal4726 Robot Collision Partial/No-Go Row

Please review:

- `future/v4/v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.md`
- `future/v4/evidence/v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.json`
- `tests/v4_goal4726_robot_collision_partial_no_go_row_test.py`

Context:

- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25/summary.json`
- `src/rtdsl/v4_goal4636_grouped_any_hit_decision.py`
- `src/rtdsl/v4_goal4636_grouped_any_hit_target.py`
- `future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json`

## Questions For Reviewer

1. Is it correct to close robot_collision as partial/no-go for the current V4
   high-performance path given the wrapper-wall floor failure?
2. Does the row correctly preserve the distinction between real native traversal
   speed and failed app/wrapper-wall promotion?
3. Does it correctly account for the V2.14 denominator already having the
   grouped-segment any-hit primitive?
4. Does it avoid authorizing robot_collision speedup wording, measured catalog
   promotion, final tag, POD spend, broad V4 speed claims, or app-specific
   native kernels?

## Requested Verdict Labels

- `accept_goal4726_robot_collision_partial_no_go_row`
- `accept_with_required_amendments`
- `reject_goal4726_row_overclaims_or_should_reopen`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims,
robot-collision speedup wording, whole-app high-performance claims,
all-benchmark speedups, POD spend, arbitrary callback support, raw OptiX
callbacks, app-specific native kernels, or hidden V2/V3 fallbacks.

