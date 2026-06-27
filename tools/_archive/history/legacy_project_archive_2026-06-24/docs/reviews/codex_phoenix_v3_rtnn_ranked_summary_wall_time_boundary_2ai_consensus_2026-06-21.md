# Codex Consensus - Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary

Status: Claude + Codex consensus complete; no M7 promotion.

Date: 2026-06-21.

## Inputs

```text
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.json
tutorials/current/11_rtnn_ranked_summary_boundary.md
docs/reviews/claude_phoenix_v3_rtnn_ranked_summary_wall_time_boundary_review_2026-06-21.md
```

## Decision

Codex accepts Claude's verdict.

RTNN remains a rebuild tutorial boundary and is not M7-qualified:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
universal_rtnn_acceleration_claim_authorized: false
paper_reproduction_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## Fixes Applied

- The tutorial now makes wall-ratio inversion explicit:
  `0.316x` means OptiX takes about `3.16x` as long as Embree wall-to-wall.
- The tutorial adds a mechanistic hot-vs-wall sentence.
- The tutorial explains that materialized summary rows prevent treating the hot
  metric as an in-device or zero-copy baseline.
- The tutorial repeats the paper-equivalent non-claim.

## Goal-Level Decision Audit

Decision: close the RTNN wall-time boundary external-review gap as reviewed
boundary evidence only, with no M7 promotion.

1. Was I foolish?

   No. This keeps the hot `3.333x` signal visible while making the wall-time
   regression impossible to miss.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be using the clustered hot metric
   as RTNN performance wording while hiding `0.625x`, `0.316x`, and `0.303x`
   wall ratios.

3. Was there another path?

   Yes. Rerun RTNN immediately. That may be future optimization work, but it
   does not fix the current documentation/release-boundary risk.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep RTNN out of M7, record the review, and require a future M7 packet
   to solve wall timing, variance, and external baseline gaps.
