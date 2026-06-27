# Call For Review: V4 Goal4699 Specialized Tier-3 App-Route Protocol

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4699_authorize_goal4700_pod`
- `reject_goal4699_protocol_wrong_target_or_wrong_denominator`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.md`
- Machine evidence:
  `future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.json`
- Evidence summary:
  `future/v4/evidence/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.md`
- Protocol implementation:
  `src/rtdsl/v4_goal4699_specialized_tier3_app_route_protocol.py`
- Tests:
  `tests/v4_goal4699_specialized_tier3_app_route_protocol_test.py`
- Existing weighted-sum route:
  `scripts/v4_ray_triangle_weighted_sum_device_output_validation.py`
  `src/rtdsl/v4_ray_triangle.py`

## Review Questions

1. Is `ray_triangle_any_hit_weighted_sum_scalar_reduce` an honest app-route
   validation target for the specialized callback candidate?
2. Is the existing Tier-2 built-in weighted-sum fused route the correct primary
   denominator?
3. Are the frozen bars strict enough to prevent a fake win against only a slow
   host/materialized route?
4. Does the protocol preserve public-support=false and release=false?
5. Should Goal4700 be allowed to run the POD implementation under this
   protocol?

## Non-Authorization

This review request does not authorize:

- final V4 release
- public Tier-3 callback support
- arbitrary callback support
- raw OptiX callback support
- app-level benchmark claims
- V4 tag wording
