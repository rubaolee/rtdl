# Call For Review: V4 Goal4716 Custom Predicate Early-Exit Productization

Date: 2026-06-26

Requested verdict:

`accept_goal4716_productization_continue_broader_validation`

or reject/amend with concrete reasons.

## Review Target

Please review:

- completion report:
  `future/v4/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.md`
- evidence:
  `future/v4/evidence/v4_goal4716_custom_predicate_early_exit_productization_2026-06-26.json`
- product module:
  `src/rtdsl/v4_custom_predicate_early_exit.py`
- catalog changes:
  `src/rtdsl/v4_operator_catalog.py`
- front door:
  `src/rtdsl/v4.py`
- tests:
  `tests/v4_goal4716_custom_predicate_early_exit_productization_test.py`

## Questions

1. Does Goal4716 correctly productize Goal4715 as a bounded V4 operator-pushdown
   surface rather than overclaiming arbitrary callback support?
2. Are the accepted callback shapes narrow enough for V4.0?
3. Are unsafe callbacks and unmeasured partners fail-closed correctly?
4. Is the measured catalog update legitimate and traceable to Goal4715
   evidence?
5. Does the API surface keep RTDL as the eDSL/runtime boundary instead of
   exposing raw OptiX?
6. Is the next step correctly limited to broader app/app-like validation rather
   than release?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

The only accepted continuation should be:

`Goal4717: broaden custom predicate early-exit validation into serious app/app-like benchmark coverage.`
