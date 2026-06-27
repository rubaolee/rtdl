# Call For Review: V4 Goal4715 Custom Predicate Early-Exit Timing POD

Date: 2026-06-26

Requested verdict:

`accept_goal4715_focused_timing_gate_passed_continue_productization`

or reject/amend with concrete reasons.

## Review Target

Please critically review Goal4715:

- completion report:
  `future/v4/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`
- JSON evidence:
  `future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json`
- markdown evidence:
  `future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`
- result classifier:
  `src/rtdsl/v4_goal4715_custom_predicate_early_exit_timing_result.py`
- POD script:
  `scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py`
- tests:
  `tests/v4_goal4715_custom_predicate_early_exit_timing_result_test.py`

## Questions

1. Is the selected denominator fair for V2.14/V3.0.2 for this new capability?
   It uses the same OptiX geometry, materializes all hit layers to device, then
   evaluates the predicate and reduces accepted flags in separate device
   kernels. It does not receive V4 any-hit predicate early termination.
2. Does the evidence prove the route changed the cost model, not just moved
   work around?
3. Do the frozen numeric bars pass without post-hoc reinterpretation?
4. Are the controls sufficient to show correctness and no obvious regression?
5. Is the next step correctly limited to productization and broader app-level
   validation, with no release/high-performance wording yet?
6. Are any public claims still overbroad?

## Key Result

Classification:

`pass_focused_timing_gate_not_release`

Primary speed:

- V4/V3 primary geomean: `3.608025018751732x`
- V4/V2 primary geomean: `3.608025018751732x`
- minimum primary V4/V3 row: `1.9761904761904763x`

Primary rows:

- `dense_early_accept_k8`: `1.976x` and `1.987x`
- `dense_early_accept_k32`: `6.701x` and `8.131x`
- `sparse_early_accept_k32`: `2.769x` and `3.724x`

Correctness passed for all rows.

## Non-Authorization To Preserve

This review must not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

The review may only authorize the next engineering step if accepted:

`Productize custom predicate early-exit as a measured V4 route and broaden app-level validation.`
