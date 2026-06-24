# Handoff: Gemini Review Request for Goal2797

Please review Goal2797 as an independent Gemini reviewer, distinct from Codex.

## Files to Inspect

- `scripts/goal2797_triangle_counting_v25_canonical_harness.py`
- `tests/goal2797_triangle_counting_v25_canonical_harness_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md`
- `docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json`

## Review Questions

1. Does the new harness genuinely make Triangle Counting rerunnable as a v2.5 canonical harness for both RT-2A1 and RT-1A2 generic lowerings?
2. Does the harness preserve the primitive-first design instead of forcing or relabeling a Triton continuation?
3. Does the pod artifact support the narrow claim that the OptiX rows match the oracle on the measured disjoint-triangle scales?
4. Does the manifest update close the previous `needs_single_rerunnable_harness` gap without overclaiming release readiness or paper reproduction?
5. Do the tests guard the generator, local CPU path, manifest status, pod artifact, and claim boundary?

## Required Output

Write your review to:

`docs/reviews/goal2797_gemini_review_triangle_counting_canonical_harness_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Expected boundary if accepted: Goal2797 is harness/correctness evidence only. It must not authorize public speedup, whole-app speedup, Triton speedup, true zero-copy, paper reproduction, or v2.5 release claims.
