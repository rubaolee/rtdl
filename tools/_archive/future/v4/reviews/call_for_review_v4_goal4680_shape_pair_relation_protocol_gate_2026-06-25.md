# Call For Review: V4 Goal4680 Shape-Pair Relation Protocol Gate

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4680_protocol_gate_continue_goal4681`
- `reject_goal4680_wrong_denominator_or_app_identity`
- `accept_with_required_amendments_before_goal4681`

## Review Target

- Report:
  `future/v4/v4_goal4680_shape_pair_relation_protocol_gate_2026-06-25.md`
- Evidence:
  `future/v4/evidence/v4_goal4680_shape_pair_relation_protocol_2026-06-25.json`
- Code:
  `src/rtdsl/v4_shape_pair_relation.py`
  `src/rtdsl/v4_goal4680_shape_pair_relation_protocol.py`
- Tests:
  `tests/v4_goal4680_shape_pair_relation_protocol_test.py`

## Questions

1. Does the V4 wrapper remain generic shape-pair relation/topology work rather
   than RayJoin/app-identity native work?
2. Is the V2.14 denominator strong enough?
3. Are the bars strict enough to prevent front-door migration from being called
   V4 speed?
4. Is it acceptable that the current measured/candidate catalog remains
   unchanged until POD evidence exists?
5. Should Goal4681 proceed to implement/run the focused POD benchmark, or
   should this path be killed/deferred?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release.
- public speedup wording.
- broad V4-over-V2/V3 claims.
- whole-app high-performance wording.
- app-identity native kernels.
- partner migration as speed evidence.
- Tier-3 callbacks or embedding/C ABI work.
