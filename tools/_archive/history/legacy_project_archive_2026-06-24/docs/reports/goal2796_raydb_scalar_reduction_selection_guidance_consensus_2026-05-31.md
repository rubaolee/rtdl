# Goal2796 Consensus - RayDB Scalar Reduction Selection Guidance

Date: 2026-05-31

## Inputs

- Codex implementation/report:
  `docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md`
- Pod artifact:
  `docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json`
- Independent Gemini review:
  `docs/reviews/goal2796_gemini_review_raydb_scalar_reduction_selection_guidance_2026-05-31.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Triton scalar reductions are correct but slower than Torch CUDA on measured RayDB-style scalar grouped reductions; guidance blocks auto-selection. |
| Gemini | `accept-with-boundary` | Artifact supports correctness plus slowdown; guidance rows, RayDB primitive-first plan, tests, and claim boundary are scoped correctly. |

## Consensus

`accept-with-boundary`

Goal2796 is accepted as negative partner-selection guidance for RayDB-style
scalar grouped reductions. The generic Triton front door remains a correct v2.5
preview operation, but it must not be auto-selected or promoted as the
performance path for this measured workload shape.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- release readiness;
- broad Triton-performance claims;
- treating the RayDB Triton front door as the default performance path.
