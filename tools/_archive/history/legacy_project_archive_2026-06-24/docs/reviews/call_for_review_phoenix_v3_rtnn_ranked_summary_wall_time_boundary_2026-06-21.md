# Call For Review: Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary

Reviewer: Claude or Gemini.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only tutorial-boundary packet:

```text
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.json
tutorials/current/11_rtnn_ranked_summary_boundary.md
```

Underlying reviewed intake:

```text
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json
docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md
```

## Intended Decision

RTNN may be taught as a V3 rebuild wall-time boundary lesson, but it must not
be promoted to M7 or public RTNN acceleration wording.

The teaching row must show hot and wall ratios together:

| Distribution | Hot OptiX / Embree | Wall OptiX / Embree |
| --- | ---: | ---: |
| clustered | 3.333x | 0.625x |
| shell | 1.182x | 0.316x |
| uniform | 1.084x | 0.303x |

## Questions For The Reviewer

1. Is it fair to teach this as a `ranked_summary` boundary lesson?
2. Does the tutorial make wall ratios below 1.0 clear enough?
3. Does it prevent readers from treating 3.333x as end-to-end speedup?
4. Does it prevent universal RTNN and paper-equivalent overclaims?
5. Would you approve this as a rebuild tutorial boundary, not as M7?

## Required Review Style

Please be strict. Reject if the packet or tutorial makes the clustered hot
metric too easy to misread as public RTNN performance.
