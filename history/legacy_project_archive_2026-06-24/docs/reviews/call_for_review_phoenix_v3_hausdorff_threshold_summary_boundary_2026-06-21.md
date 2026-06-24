# Call For Review: Phoenix V3 Hausdorff Threshold-Summary Boundary

Reviewer: Claude or Gemini.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only boundary packet:

```text
docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.json
tutorials/current/13_hausdorff_threshold_summary.md
```

## Intended Decision

Hausdorff threshold-summary may be taught as a scoped V3 rebuild lesson, but it
must not be promoted to M7 or full Hausdorff speedup wording.

Key table:

| Copies | Query OptiX / Embree | Wall OptiX / Embree |
| ---: | ---: | ---: |
| 16,384 | 2.000x | 0.657x |
| 65,536 | 1.595x | 0.965x |
| 262,144 | 1.864x | 1.258x |

## Questions For The Reviewer

1. Is threshold-only scope clear enough?
2. Does the packet prevent full exact Hausdorff witness overclaims?
3. Does it make mixed wall timing clear enough?
4. Are the M7 blockers sufficient?
5. Would you approve this as a rebuild boundary, not M7?
