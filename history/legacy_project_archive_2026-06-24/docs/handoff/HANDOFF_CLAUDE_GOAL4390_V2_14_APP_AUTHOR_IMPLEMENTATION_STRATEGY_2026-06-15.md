# Handoff To Claude: Goal4390 v2.14 App-Author Implementation Strategy

Date: 2026-06-15

Repository: `rubaolee/rtdl`

Primary document to review:

- `docs/learn/v2_14_app_author_implementation_strategy.md`

Supporting context:

- `docs/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- `docs/release_reports/v2_14/public_wording_boundaries.md`
- `docs/release_reports/v2_14/promoted_benchmark_inventory.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal4389_rtdbscan_partner_dual_implementation_2026-06-15.md`

## One-Sentence Reviewer Prompt

Please critically review whether the new v2.14 app-author implementation
strategy correctly tells users how to choose RTDL primitives, OptiX/Embree
backends, explicit partners, and complex app orchestration without overclaiming
raw OptiX callback support or violating RTDL's app-agnostic native-engine
boundary.

## Required Review Focus

1. Does the document give a usable decision process for a real app author?
2. Does it correctly prioritize primitive-first implementation before partner
   continuation?
3. Does it explain when to choose Numba, CuPy, Torch, CPU oracles, and
   specialized C++/CUDA/OptiX without implying automatic partner selection?
4. Does it preserve same-contract OptiX-vs-Embree comparison discipline?
5. Is the raw OptiX callback boundary technically honest: internal primitive
   implementation yes, arbitrary user callback API no?
6. Does the guidance handle complex multi-stage apps without encouraging
   app-specific native engine semantics?
7. Does it accurately reflect v2.14 benchmark lessons, including RTDBSCAN
   Goal4389 and RayJoin overlay's available 2/8 exact-subset boundary?
8. What wording should be changed before this becomes part of the v2.14 public
   release packet?

## Expected Output

Write a review to:

- `docs/reviews/goal4390_claude_review_v2_14_app_author_implementation_strategy_2026-06-15.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The review must not authorize:

- broad whole-app speedup claims;
- RT cores accelerate every app claims;
- RTDL beats handwritten C++/CUDA/OptiX claims;
- automatic partner selection;
- arbitrary raw OptiX callback exposure as the v2.14 user API;
- app-specific native engine semantics;
- full 8/8 RayJoin Section 5.7 reproduction wording.

## Suggested Review Shape

```text
# Claude Review: Goal4390 v2.14 App-Author Implementation Strategy

Verdict: <accept | accept-with-boundary | needs-more-evidence | reject>

## Findings

## Required Fixes Before Public Release

## Suggestions

## Residual Risks
```

## Single-Command Prompt

Please read `docs/handoff/HANDOFF_CLAUDE_GOAL4390_V2_14_APP_AUTHOR_IMPLEMENTATION_STRATEGY_2026-06-15.md` and write a critical review to `docs/reviews/goal4390_claude_review_v2_14_app_author_implementation_strategy_2026-06-15.md`, using one of the required verdicts and focusing on whether the v2.14 app-author strategy preserves primitive-first design, explicit partner selection, same-contract OptiX-vs-Embree comparisons, and the no-arbitrary-OptiX-callback user API boundary.
