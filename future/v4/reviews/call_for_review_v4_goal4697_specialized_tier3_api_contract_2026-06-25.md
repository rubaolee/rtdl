# Call For Review: V4 Goal4697 Specialized Tier-3 API Contract

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4697_continue_goal4698`
- `reject_goal4697_contract_overclaims`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4697_specialized_tier3_api_contract_2026-06-25.md`
- Machine evidence:
  `future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.json`
- Evidence summary:
  `future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.md`
- Contract implementation:
  `src/rtdsl/v4_goal4697_specialized_tier3_api_contract.py`
- Tests:
  `tests/v4_goal4697_specialized_tier3_api_contract_test.py`
- Existing public planner:
  `src/rtdsl/v4_operator_catalog.py`

## Review Questions

1. Does Goal4697 keep the ordinary V4 public planner closed for Tier-3 support?
2. Is the explicit specialized contract narrow enough for internal
   productization work?
3. Are arbitrary Python, action/side-effect, external memory mutation, dynamic
   SBT direct callable, and non-scalar signatures rejected early enough?
4. Is Goal4698 the right next step, or should another negative validation case
   be added first?
5. Does the report preserve all non-authorization boundaries?

## Non-Authorization

This review request does not authorize:

- final V4 release
- public Tier-3 callback support
- arbitrary callback support
- raw OptiX callback support
- app-level benchmark claims
- V4 tag wording
