# Review Debt: V4 Goal4717 Custom Predicate Early-Exit Serious-Scale Validation

Date: 2026-06-26

Status: `open_review_debt_continue_engineering`

Goal:

`Goal4717 custom predicate early-exit serious-scale validation`

## Why This Is Debt

The project rule requires 3-AI consensus for goal completion or explicit review
debt when external reviewers are unavailable. Claude is known to be unavailable
until the recorded weekly-limit reset window, and the user has explicitly
authorized continuing engineering while recording review debt.

Do not loop on Claude availability for this goal. Do not create internal fake
reviewers to fill the consensus seat.

## Files To Review Later

- `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`
- `future/v4/reviews/call_for_review_v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`
- `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json`
- `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.md`
- `src/rtdsl/v4_custom_predicate_early_exit.py`
- `src/rtdsl/v4_operator_catalog.py`

## Current Internal Classification

`complete_pending_3ai_review_debt`

The measured result passes the serious-scale focused gate:

- primary V4/V3.0.2 geomean: `4.632757911153888x`
- minimum primary V4/V3.0.2 row: `2.054686620906942x`
- correctness all passed
- denominator discovery complete

## Non-Authorization

This debt record does not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI claims.

Engineering may continue to Goal4718 while this debt remains open.
