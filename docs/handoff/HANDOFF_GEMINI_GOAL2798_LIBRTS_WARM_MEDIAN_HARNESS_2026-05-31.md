# Handoff: Gemini Review Request for Goal2798

Please review Goal2798 as an independent Gemini reviewer, distinct from Codex.

## Files to Inspect

- `scripts/goal2798_librts_v25_warm_median_harness.py`
- `tests/goal2798_librts_v25_warm_median_harness_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2798_librts_v2_5_warm_median_harness_2026-05-31.md`
- `docs/reports/goal2798_pod_artifacts/librts_v25_warm_median_optix_4096_2048.json`

## Review Questions

1. Does the new harness genuinely measure the prepared OptiX `AABB_INDEX_QUERY_2D` path with warm/repeat timing rather than cold one-shot CLI timing?
2. Does it keep LibRTS in the correct Tier C no-regression lane instead of forcing Triton or partner parity?
3. Does the pod artifact support the narrow claim that all three AABB operations match the CPU oracle on the measured 4096-box / 2048-query fixture?
4. Does the manifest update close the previous `needs_warm_median_harness` gap without overclaiming paper reproduction or release readiness?
5. Do the tests guard the prepared-query usage, manifest status, pod artifact, and claim boundary?

## Required Output

Write your review to:

`docs/reviews/goal2798_gemini_review_librts_warm_median_harness_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Expected boundary if accepted: Goal2798 is Tier C no-regression harness/correctness evidence only. It must not authorize public speedup, whole-app speedup, Triton speedup, true zero-copy, paper reproduction, or v2.5 release claims.
