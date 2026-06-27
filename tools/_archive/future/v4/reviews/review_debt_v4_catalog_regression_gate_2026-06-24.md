# Review Debt: V4 Catalog Regression Gate

Date: 2026-06-24

Status: `external_review_not_retried_continue_engineering_no_release_authorization`

## Scope

This records bounded review debt for:

- `future/v4/reviews/call_for_review_v4_catalog_regression_gate_2026-06-24.md`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.json`

## Why External Review Was Not Retried For This Gate

In the same work session, immediately preceding V4 review attempts established:

- Claude is blocked by session limit.
- Antigravity exits without review content.

The gate has real local and POD evidence, so this debt record preserves the
review requirement without spending more time on empty review attempts.

## Engineering Evidence Available For Backfill

Local validation:

- `python -m unittest tests.v4_catalog_regression_gate_test tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_fixed_radius_docs_and_example_test`
- Result: 18 tests passed.

Compile validation:

- `python -m py_compile scripts/v4_catalog_regression_gate.py`
- Result: passed.

Dry-run evidence:

- `future/v4/evidence/v4_catalog_regression_gate_dry_run_2026-06-24.json`
- status: `passed`

POD GPU evidence:

- `future/v4/evidence/v4_catalog_regression_gate_gpu_2026-06-24.json`
- status: `passed`
- GPU examples measured and correctness passed.

## Required Backfill Questions

An external reviewer should still answer:

1. Is this an adequate regression gate for the current V4 catalog examples?
2. Does the GPU evidence prove the examples run correctly without overstating performance?
3. Are the non-authorization flags strict enough?
4. Is it acceptable that this gate validates examples, not a broad all-app benchmark?
5. What amendments are required before the next V4 engineering gate?

## Non-Authorization

This debt record does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
- embedding/C-ABI work

