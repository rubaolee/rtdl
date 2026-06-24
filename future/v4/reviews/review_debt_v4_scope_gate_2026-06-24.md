# Review Debt: V4.0 Scope Gate

Date: 2026-06-24

Status: `external_review_not_retried_continue_engineering_no_release_authorization`

## Scope

This records bounded review debt for:

- `future/v4/reviews/call_for_review_v4_scope_gate_2026-06-24.md`
- `src/rtdsl/v4_scope.py`
- `scripts/v4_scope_gate.py`
- `future/v4/v4_0_scope_gate.md`
- `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- `future/v4/evidence/v4_scope_gate_2026-06-24.md`

## Why External Review Was Not Retried For This Gate

In the same work session, two immediately preceding V4 review attempts already
established the available external-review state:

- Claude: blocked by session limit with `You've hit your session limit · resets 1:50pm (America/New_York)`.
- Antigravity: exited 0 but produced empty review content.

This scope gate records debt instead of repeatedly calling the same unavailable
reviewers and converting tool churn into fake progress.

## Engineering Evidence Available For Backfill

Local validation:

- `python -m unittest tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`
- Result: 23 tests passed.

Compile validation:

- `python -m py_compile src/rtdsl/v4.py src/rtdsl/v4_scope.py scripts/v4_scope_gate.py`
- Result: passed.

Generated evidence:

- `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- `future/v4/evidence/v4_scope_gate_2026-06-24.md`

## Required Backfill Questions

An external reviewer should still answer:

1. Does this correctly define V4.0 scope without smuggling V4.x work into V4.0?
2. Is it correct to keep Tier-3 callback support deferred while keeping the planner in V4.0?
3. Are the release-blocking reasons clear and strict enough?
4. Does the gate avoid over-authorizing broad speedup, callback, embedding, or app-specific kernel claims?
5. What amendments are required before continuing V4 engineering?

## Non-Authorization

This debt record does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
- embedding/C-ABI work

