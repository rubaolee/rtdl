# Call For Review: V4 Goal4717 Custom Predicate Early-Exit Serious-Scale Validation

Date: 2026-06-26

Requested verdict:

`accept_goal4717_serious_scale_validation_continue_app_matrix`

or reject/amend with concrete reasons.

## Review Target

Please review:

- completion report:
  `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`
- evidence:
  `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json`
- evidence summary:
  `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.md`
- product surface:
  `src/rtdsl/v4_custom_predicate_early_exit.py`
- catalog:
  `src/rtdsl/v4_operator_catalog.py`

## Questions

1. Does Goal4717 legitimately broaden Goal4715 beyond toy scale?
2. Is the denominator fair: same OptiX geometry, materialized all-hit device
   fallback for V2.14/V3.0.2 after discovering no custom predicate early-exit
   route in those tag roots?
3. Are the primary speed rows correctly interpreted as operator-pushdown early
   termination wins rather than arbitrary callback or all-app wins?
4. Does correctness parity pass on all primary and control rows?
5. Are the control rows correctly kept out of the primary speed claim?
6. Is the continuation correctly limited to Goal4718 app-level matrix/release
   mapping rather than direct public release?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI claims.

The only accepted continuation should be:

`Goal4718: map the measured custom predicate early-exit surface into the V4 app-level benchmark/release matrix and decide what public V4 claim it can support.`
