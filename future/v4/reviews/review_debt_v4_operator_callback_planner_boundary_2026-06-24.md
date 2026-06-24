# Review Debt: V4 Operator/Callback Planner Boundary

Date: 2026-06-24

Status: `external_review_blocked_continue_engineering_no_release_authorization`

## Scope

This records bounded review debt for:

- `future/v4/reviews/call_for_review_v4_operator_callback_planner_boundary_2026-06-24.md`
- `src/rtdsl/v4_operator_catalog.py`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/examples/operator_callback_planning.py`

## Review Attempts

Claude attempt:

- Tool: `C:\Users\Lestat\.local\bin\claude.exe`
- Output file: `future/v4/reviews/claude_v4_operator_callback_planner_boundary_review_2026-06-24.md`
- Result: blocked by session limit
- Captured message: `You've hit your session limit · resets 1:50pm (America/New_York)`

Antigravity attempt:

- Tool: `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`
- Output file: `future/v4/reviews/antigravity_v4_operator_callback_planner_boundary_review_2026-06-24.md`
- Result: exited 0 but produced no review content
- Captured review content: empty

## Engineering Evidence Available For Backfill

Local validation:

- `python -m unittest tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`
- Result: 14 tests passed.

Compile validation:

- `python -m py_compile src/rtdsl/v4_operator_catalog.py future/v4/examples/operator_callback_planning.py`
- Result: passed.

## Required Backfill Questions

An external reviewer should still answer:

1. Does the planner answer complex custom callback requests without pretending raw OptiX callbacks are supported?
2. Is the Tier-2/Tier-3/deferred classification strict enough?
3. Is scalar Numba callback handling correctly scoped as spike-only?
4. Does the planner over-authorize release, speedup, callback, or app-specific native-kernel claims?
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

