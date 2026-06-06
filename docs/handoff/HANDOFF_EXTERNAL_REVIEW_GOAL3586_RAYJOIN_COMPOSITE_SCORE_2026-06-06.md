# External Review Handoff: Goal3586 RayJoin Composite Score

Date: 2026-06-06

Please perform an independent review of Goal3586.

## Scope

Goal3586 converts the reviewed Goal3583 per-contract RayJoin hot prepared-route
measurements into a single app-level RayJoin-style score.

Files to inspect:

- `docs/reports/goal3586_rayjoin_composite_score_from_hot_promoted_routes_2026-06-06.md`
- `tests/goal3586_rayjoin_composite_score_from_hot_promoted_routes_test.py`
- `docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json`
- `docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json`
- `docs/reviews/goal3584_claude_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`
- `docs/reviews/goal3585_gemini_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`

## Reported Scores

Primary app-packet score: summed wall-time ratio across PIP, LSI, and overlay
active-count contracts.

- Standard: 0.373467754 sec Embree / 0.002575233 sec OptiX = 145.023x
- Stress: 5.447204675 sec Embree / 0.007194325 sec OptiX = 757.153x

Secondary route-balanced score: geometric mean of the three per-contract
speedups.

- Standard: 85.956x
- Stress: 159.830x

## Reviewer Questions

1. Is summed wall-time ratio a reasonable primary single app-packet score for
   this fixed RayJoin-style benchmark packet?
2. Is the geometric mean a reasonable secondary route-balanced score, and does it
   properly reduce overlay dominance?
3. Are all scores recomputed correctly from the Goal3583 artifacts?
4. Are the caveats strong enough that no one reads the composite score as full
   RayJoin paper reproduction, paper-scale performance, full polygon overlay
   materialization, a true zero-copy claim, or release authorization?
5. What should the next RayJoin work be after composite scoring: external
   same-contract CUDA/OptiX baseline, full-overlay continuation, or another
   target?

## Required Output

Write one review file:

- Claude: `docs/reviews/goal3587_claude_review_goal3586_rayjoin_composite_score_2026-06-06.md`
- Gemini: `docs/reviews/goal3588_gemini_review_goal3586_rayjoin_composite_score_2026-06-06.md`

Use verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
