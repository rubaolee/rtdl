# Gemini Review Request - Goal2796 RayDB Scalar Reduction Selection Guidance

Please perform an independent read-only review of Goal2796 and write your
review to:

`docs/reviews/goal2796_gemini_review_raydb_scalar_reduction_selection_guidance_2026-05-31.md`

## Context

Goal2796 ran a fresh RTX A5000 pod probe for the current v2.5 RayDB Triton
public-front-door scalar reductions. The Triton front door is correct, but Torch
CUDA is much faster on the measured shapes. The implementation records this as
negative partner-selection guidance, not as a failure and not as a public claim.

## Files To Inspect

- `docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json`
- `docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2796_raydb_scalar_reduction_selection_guidance_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`

## Questions

1. Does the artifact support the claim that Triton is correct but slower than
   Torch CUDA for RayDB-style scalar grouped reductions?
2. Are the four guidance rows for `segmented_count_i64`, `segmented_sum_f64`,
   `segmented_min_f64`, and `segmented_max_f64` accurate and scoped correctly?
3. Does the RayDB app migration plan remain primitive-first rather than forcing
   Triton?
4. Do the tests prevent accidental auto-selection or performance promotion from
   this negative evidence?
5. Does the report avoid public speedup, release, broad Triton, and whole-app
   overclaims?

## Required Output Shape

Please include:

- verdict: one of `accept`, `accept-with-boundary`, `needs-more-evidence`, or
  `reject`;
- findings, if any, with file/line references;
- explicit statement that this is an independent Gemini review distinct from
  Codex authoring.

Do not mutate source files other than writing the requested review document.
