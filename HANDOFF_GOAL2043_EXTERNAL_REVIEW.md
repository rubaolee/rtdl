# Handoff: Goal2043 v2.0 Clean, Powerful, Traceable Plan Review

Please review `docs/reports/goal2043_v2_0_clean_powerful_traceable_plan_2026-05-14.md`.

Context:

- v2.0 is the Python+partner+RTDL release target.
- The RTDL native engines must remain absolutely app-agnostic.
- Goal2041 repaired several Embree weak rows for decision/summary contracts, but left richer requirements unsolved:
  - exact K=3 facility fallback ranking at large scale;
  - exact ANN ranking / recall optimization;
  - exact Hausdorff distance with witness extraction;
  - broad general polygon overlay.
- These requirements also affect OptiX/RT because RT acceleration can produce candidates but does not itself define partner-side ranking, witness reductions, or topology assembly.

Review questions:

1. Does Goal2043 correctly identify the real design gap as generic partner continuation/reduction contracts rather than app-specific engine customization?
2. Are the proposed contracts clean and app-agnostic: candidate rows, segmented reductions, group top-K, threshold decisions, witness extraction, polygon topology split, and user-defined partner kernels?
3. Does the plan preserve a consistent Embree/OptiX story while respecting that Embree uses host-memory partners and OptiX uses device-memory partners?
4. Are the traceability and performance evidence rules strong enough for v2.0 release preparation?
5. Is the recommended Goal2044 next step reasonable, or should another primitive come first?

Please write the review to:

`docs/reviews/goal2043_gemini_review_v2_0_clean_powerful_traceable_plan_2026-05-14.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
