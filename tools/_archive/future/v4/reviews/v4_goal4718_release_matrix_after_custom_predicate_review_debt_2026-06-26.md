# Review Debt: V4 Goal4718 Release Matrix After Custom Predicate Early-Exit

Date: 2026-06-26

Status: `open_review_debt_continue_engineering`

Goal:

`Goal4718 release matrix after custom predicate early-exit`

## Why This Is Debt

The project rule requires 3-AI consensus for goal completion or explicit review
debt when external reviewers are unavailable. Claude is known unavailable until
the recorded weekly-limit reset window, and the user authorized continuing
engineering while recording review debt.

Do not loop on Claude availability. Do not create internal fake reviewers.

## Files To Review Later

- `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- `future/v4/reviews/call_for_review_v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json`
- `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- `src/rtdsl/v4_goal4718_release_matrix_after_custom_predicate.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_scope.py`

## Current Internal Classification

`complete_pending_3ai_review_debt`

Goal4718 validates:

- measured surface count: `10`;
- V4 Python eDSL/operator-pushdown release candidate supported: `true`;
- operator-pushdown workflow high-performance supported: `true`;
- legacy all-app high-performance supported: `false`;
- broad all-benchmark speedup supported: `false`.

## Non-Authorization

This debt record does not authorize:

- public tag;
- final V4 release wording;
- broad all-app speedup;
- "all benchmark apps are faster";
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI;
- app-specific native kernels.

Engineering may continue to Goal4719 while this debt remains open.
