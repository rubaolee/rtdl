# Call For Review: V4 Goal4711 Custom Scored App Focused POD Result

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4711_fail_gate_pivot_required`
- `accept_with_required_amendments`
- `reject_result_rerun_required`

## Files To Review

- Completion report:
  `future/v4/v4_goal4711_custom_scored_app_focused_pod_2026-06-26.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.json`
- Evidence Markdown:
  `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.md`
- POD stdout log:
  `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.stdout.log`
- Result classifier:
  `src/rtdsl/v4_goal4711_custom_scored_app_result.py`
- POD runner:
  `scripts/v4_goal4711_custom_scored_app_pod.py`
- Tests:
  `tests/v4_goal4711_custom_scored_app_result_test.py`

## Review Questions

1. Is the corrected denominator valid for this focused target?
   - V2/V3 fallback materializes hit IDs on device and then evaluates callback
     plus reduction in a separate device kernel.
   - V4 gets callback-in-hit contribution generation.
2. Is the initial smoke-run mistake fully repaired?
   - The rejected mistake was giving fallback callback-in-hit execution.
3. Is the failure classification correct?
   - Primary custom-callback geomean is `1.029x`, below `1.20x` vs V3 and
     `1.50x` vs V2.
   - Per-callback minima are `1.014x`, `1.017x`, and `1.017x`, below the
     frozen `1.10x` floor.
4. Does this result forbid using Goal4711 as formal high-performance V4
   evidence?
5. Should the next step be pivot/reselect/redesign rather than all-app or
   release wording?
6. Are any public support claims accidentally authorized by the code, evidence,
   or prose?

## Non-Authorization

This review request does not authorize:

- V4 release;
- formal high-performance V4 wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support;
- all-app benchmark claims.

