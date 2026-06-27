# Review Debt: V4 Unified Python Front Door

Date: 2026-06-24

Status: `external_review_blocked_continue_engineering_no_release_authorization`

## Scope

This records bounded review debt for:

- `future/v4/reviews/call_for_review_v4_unified_frontdoor_2026-06-24.md`
- `src/rtdsl/v4.py`
- `future/v4/README.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `tests/v4_frontdoor_test.py`

## Review Attempts

Claude attempt:

- Tool: `C:\Users\Lestat\.local\bin\claude.exe`
- Output file: `future/v4/reviews/claude_v4_unified_frontdoor_review_2026-06-24.md`
- Result: blocked by session limit
- Captured message: `You've hit your session limit · resets 1:50pm (America/New_York)`

Antigravity attempt:

- Tool: `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`
- Output file: `future/v4/reviews/antigravity_v4_unified_frontdoor_review_2026-06-24.md`
- Result: exited 0 but produced no review content
- Captured review content: empty

## Engineering Evidence Available For Backfill

Local validation:

- `python -m unittest tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test`
- Result: 18 tests passed.

Compile validation:

- `python -m py_compile src/rtdsl/v4.py src/rtdsl/v4_operator_catalog.py future/v4/examples/v4_frontdoor_quickstart.py future/v4/examples/operator_callback_planning.py`
- Result: passed.

## Required Backfill Questions

An external reviewer should still answer:

1. Is `rtdsl.v4` an appropriate unified V4 development front door?
2. Does the front door preserve the development/non-release boundary?
3. Does it avoid over-authorizing Tier-3 callbacks, raw OptiX callbacks, or app-specific kernels?
4. Is the README clean enough as a V4 starting point without historical churn?
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

