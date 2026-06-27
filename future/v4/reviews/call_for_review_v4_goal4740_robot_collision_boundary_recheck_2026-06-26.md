# Call For Review: V4 Goal4740 Robot Collision Boundary Recheck

Date: 2026-06-26

Reviewer requested: Claude and Antigravity when available.

Status: `external_review_requested_debt_allowed`

## Files To Review

- Report:
  `future/v4/v4_goal4740_robot_collision_boundary_recheck_2026-06-26.md`
- Evidence:
  `future/v4/evidence/v4_goal4740_robot_collision_boundary_recheck_2026-06-26.json`
- POD raw evidence:
  `future/v4/evidence/v4_goal4740_robot_boundary_20260626/`
- Prior no-go:
  `future/v4/v4_goal4726_robot_collision_partial_no_go_row_2026-06-26.md`
- V2.14 primitive audit:
  `future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json`

## Questions

1. Does Goal4740 correctly identify that the old wrapper-wall failure was a
   coarse timing-boundary problem?
2. Does the clean-boundary POD evidence support the internal statement that the
   grouped any-hit primitive is fast under the proper hot-path boundary?
3. Is the no-speed-credit conclusion versus V2.14 correct, given V2.14 already
   had device-buffer and count-only grouped any-hit primitives?
4. Is it correct to keep `robot_collision` out of formal high-performance V4
   candidate rows?
5. Are all non-authorization boundaries preserved?

## Requested Verdict Labels

- `accept_goal4740_keep_robot_no_go_with_boundary_correction`
- `accept_with_required_amendments`
- `reject_robot_reclassification_or_overclaim`

## Non-Authorization

This review must not authorize final V4 tag, Robot speedup wording versus
V2.14, all-benchmark speedup claims, broad V4-over-V2.14 claims, app-specific
native kernels, arbitrary callbacks, raw OptiX callbacks, or true-zero-copy
wording.
