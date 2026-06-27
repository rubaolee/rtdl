# Review Debt: V4 Third Tier-2 Any-Hit Flags Surface And Operator Catalog

Date: 2026-06-24

Status: `external_review_blocked_continue_engineering_no_release_authorization`

## Scope

This records bounded review debt for:

- `future/v4/reviews/call_for_review_v4_third_tier2_any_hit_flags_and_catalog_2026-06-24.md`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`
- `future/v4/tier2_operator_catalog.md`

The engineering work has local and POD validation, but does not yet have a
completed external review from Claude, Antigravity, or a third AI seat.

## Review Attempts

Claude attempt:

- Tool: `C:\Users\Lestat\.local\bin\claude.exe`
- Output file: `future/v4/reviews/claude_v4_third_tier2_any_hit_flags_and_catalog_review_2026-06-24.md`
- Result: blocked by session limit
- Captured message: `You've hit your session limit · resets 1:50pm (America/New_York)`

Antigravity attempt:

- Tool: `C:\Users\Lestat\AppData\Local\agy\bin\agy.exe`
- Output file: `future/v4/reviews/antigravity_v4_third_tier2_any_hit_flags_and_catalog_review_2026-06-24.md`
- Result: timed out after the bounded 120 second attempt
- Captured review content: empty

## Engineering Evidence Available For Backfill

Local validation:

- `python -m unittest tests.v4_ray_triangle_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_section8_any_hit_flags_device_frontdoor_validation_test tests.v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation_test tests.v4_fixed_radius_device_array_api_test tests.v4_section8_device_array_frontdoor_validation_test`
- Result: 22 tests passed.

POD validation:

- `python -m unittest tests.v4_ray_triangle_device_array_api_test tests.v4_fixed_radius_docs_and_example_test tests.v4_section8_any_hit_flags_device_frontdoor_validation_test`
- Result: 14 tests passed.

POD measurement:

- Evidence: `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json`
- Result: correctness passed for 8,192 / 32,768 / 131,072 rays and triangles.
- 8,192-row fixture-analytic Torch reference ratio: 9.379x.
- Boundary: the Torch reference is not a handwritten OptiX ceiling and not a broad V4 speedup basis.

## Required Backfill Questions

An external reviewer should still answer:

1. Is this a legitimate V4 Tier-2 generic operator surface, not an app-specific kernel?
2. Does it preserve the V4 boundary: Python GPU arrays in, RTDL generic RT operator, GPU arrays out?
3. Are the claim boundaries strict enough?
4. Should the 8K Torch reference ratio be retained, softened, or removed?
5. Is the operator catalog honest, or does it overstate V4 readiness?
6. What amendments are required before the next V4 engineering goal is considered clean?

## Non-Authorization

This debt record does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- CuPy performance claims
- embedding/C-ABI work
- app-specific native engine kernels

