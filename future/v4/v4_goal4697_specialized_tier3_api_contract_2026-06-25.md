# V4 Goal4697: Specialized Tier-3 API Contract

Date: 2026-06-25
Status: `goal4697_constrained_specialized_tier3_api_contract_scaffold_not_public_support`

## Result

Goal4697 added a constrained API-contract scaffold for the specialized Tier-3
candidate selected by Goal4696.

Accepted internal candidate:

- surface: `module_specialized_direct_device_callback`
- supported shape: `pure_scalar_return_numba_cabi_device_function`
- wrapper strategy:
  `specialize_hit_program_module_and_call_callback_as_direct_device_function`
- accepted callback shapes:
  - `custom_scalar_reduce`
  - `custom_score`
  - `custom_threshold`
  - `custom_minmax`

The ordinary V4 planner remains closed for public Tier-3 support. The new
contract exists for internal productization work only.

Evidence:

- `future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.json`
- `future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.md`

## Negative Validation

Goal4697 rejects the important unsafe shapes before any compile path:

- arbitrary Python callback:
  `rejected_goal4697_arbitrary_python_callback`
- action or side-effect callback:
  `rejected_goal4697_action_or_side_effect_callback`
- external memory mutation callback:
  `rejected_goal4697_external_memory_mutation_callback`
- dynamic SBT direct-callable hot path:
  `rejected_goal4697_dynamic_sbt_direct_callable_hot_path`
- non-scalar signature:
  `rejected_goal4697_non_scalar_callback_signature`

## Verification

Local verification passed:

- `py scripts/v4_goal4697_specialized_tier3_api_contract.py --json-out future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.json --md-out future/v4/evidence/v4_goal4697_specialized_tier3_api_contract_2026-06-25.md`
- `py -m unittest tests.v4_goal4697_specialized_tier3_api_contract_test tests.v4_goal4696_tier3_productization_decision_test tests.v4_operator_catalog_test tests.v4_tier3_callback_spike_protocol_test`
  - result: `25 tests OK`
- `py -m py_compile src/rtdsl/v4_goal4697_specialized_tier3_api_contract.py scripts/v4_goal4697_specialized_tier3_api_contract.py src/rtdsl/v4.py src/rtdsl/v4_operator_catalog.py`

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- raw OptiX callback support
- app-level speedup claims
- V4 release or tag claims

Goal4698 should add compile/cache/error-reporting scaffold for the accepted
contract without opening the public support boundary.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. I avoided silently changing the public planner into a support claim.
   The new API contract is explicit and internal-only.

2. If yes, what action made it stupid?
   The stupid action would have been to reinterpret Goal4695 as broad custom
   callback support. The implementation keeps that false.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Keep public Tier-3 closed while productizing the one measured-safe
   specialized callback path behind a separate contract.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4698 can build compile/cache/error-reporting behavior against this
   explicit contract, then a later app-route validation can test user value.
