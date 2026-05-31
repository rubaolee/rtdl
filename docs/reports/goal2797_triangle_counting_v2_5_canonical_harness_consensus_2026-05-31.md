# Goal2797 Consensus - Triangle Counting v2.5 Canonical Harness

Date: 2026-05-31

## Inputs

- Codex implementation/report:
  `docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md`
- Pod artifact:
  `docs/reports/goal2797_pod_artifacts/triangle_counting_v25_canonical_harness_5000_optix.json`
- Independent Gemini review:
  `docs/reviews/goal2797_gemini_review_triangle_counting_canonical_harness_2026-05-31.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Triangle Counting now has a rerunnable v2.5 canonical OptiX harness for RT-2A1 and RT-1A2 primitive-first scalar-summary rows. |
| Gemini | `accept-with-boundary` | Harness is rerunnable, primitive-first design is preserved, pod artifact supports oracle matching, manifest gap is closed, and tests guard the boundary. |

## Consensus

`accept-with-boundary`

Goal2797 is accepted as harness and correctness evidence. It closes the
Triangle Counting `needs_single_rerunnable_harness` manifest gap by adding a
canonical runner and current RTX A5000 OptiX evidence for both generic
RT-Graph-style lowerings.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- Triton speedup claims;
- true zero-copy claims;
- paper-reproduction claims;
- v2.5 release readiness claims.

The accepted claim is narrow: the measured OptiX rows match the oracle through
the new rerunnable harness, and the app remains primitive-first rather than
being forced into a Triton continuation.
