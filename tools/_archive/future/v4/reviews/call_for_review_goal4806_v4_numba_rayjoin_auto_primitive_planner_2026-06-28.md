# Call For Review - Goal4806 V4 + Numba RayJoin Auto-Primitive Planner

Please review:

`tools/_archive/future/v4/goals/goal4806_v4_numba_rayjoin_section57_auto_primitive_planner_2026-06-28.md`

## Requested Verdict Labels

Choose one:

- `approve_execute_goal4806`
- `approve_with_required_amendments`
- `reject_goal4806_unclear_or_unsafe`
- `block_goal4806_overclaims_or_wrong_scope`

## Context

The desired goal is a serious V4+Numba RayJoin paper-reproduction effort for Section 5.7 Polygon Overlay.

The key product requirement is that the user should express workload semantics and choose `partner="numba"`; the runtime should automatically enumerate valid primitive combinations, validate correctness, measure them on NVIDIA GPU, and select the fastest valid plan. The user should not need to know or hand-select primitive names.

A full paper-reproduction claim also requires correctness and performance
comparison against the RayJoin author implementation. If the author code or
author binaries cannot be run under the same Section 5.7 contract, the result
must be labeled `blocked_missing_author_baseline` and cannot be treated as a
complete paper reproduction.

## Required Review Questions

1. Is the goal clear and executable?
2. Does it correctly require user-level semantics instead of primitive-name hand selection?
3. Is the automatic primitive-plan selection requirement strong enough?
4. Is Numba partner work defined in a way that is meaningful and not just wrapper theater?
5. Are the correctness and performance bars fair and not toy-level?
6. Are the no-go and bounded-claim outcomes explicit enough?
7. Does anything in this plan accidentally pull V4.1 arbitrary callback work into V4.0?
8. Does the goal require author-code correctness and performance comparison strongly enough?
9. What amendments are required before implementation?

## Non-Authorization Reminder

Do not authorize a public high-performance claim or full Section 5.7 paper-reproduction claim from this plan alone. The review is only for whether the goal is valid to execute.
