# Goal2272: Prepared Segment-Pair Count 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers:

- Goal2269 implementation of `rtdl_optix_count_prepared_segment_pair_intersection`
  and `PreparedOptixSegmentPairIntersection.count(...)`.
- Goal2270 pod evidence comparing exact scalar count against raw witness-row
  return on synthetic crossing grids.
- Gemini review Goal2271.

## Evidence

Codex implemented the generic count-only API and ran clean pushed-commit pod
validation on commit `dffabc1317f382dcb19cd3ea30087692a0b69e48`. The pod
artifact is:

`docs/reports/goal2270_prepared_segment_pair_count_probe_pod_2026-05-17.json`

The evidence shows parity for all tested sizes:

| Intersections | Raw Rows Median Sec | Scalar Count Median Sec | Rows / Count |
| ---: | ---: | ---: | ---: |
| 65,536 | 0.006880 | 0.006627 | 1.038x |
| 262,144 | 0.026872 | 0.026943 | 0.997x |
| 589,824 | 0.076856 | 0.054059 | 1.422x |
| 1,048,576 | 0.129207 | 0.106134 | 1.217x |
| 2,359,296 | 0.266754 | 0.211288 | 1.263x |
| 4,194,304 | 0.492979 | 0.373820 | 1.319x |

## External Review

Gemini reviewed Goals2269/2270 in:

`docs/reviews/goal2271_gemini_review_goal2269_2270_segment_pair_count_2026-05-17.md`

Gemini verdict: `accept-with-boundary`.

Gemini confirmed:

- the new API is generic, not RayJoin/LSI-specific,
- the count path preserves exactness through the same candidate collection,
  host exact refinement, and duplicate-pair suppression,
- Goal2270 supports only the narrow scalar-count parity and larger-scale
  row-return-avoidance claim,
- the reports do not overclaim whole-app speedup, RayJoin paper reproduction,
  broad RT-core speedup, true zero-copy, or pure device-resident continuation.

## Consensus Verdict

Codex + Gemini consensus: `accept-with-boundary`.

Allowed claim:

On the recorded RTX A5000 pod, the generic prepared OptiX segment-pair exact
scalar-count API preserves parity with raw witness-row return and becomes faster
than raw witness-row return once synthetic crossing-grid witness output is large
enough.

Still not allowed from this evidence:

- whole RayJoin application speedup,
- RayJoin paper dataset reproduction,
- broad RT-core speedup,
- true zero-copy,
- pure device-resident continuation.

## Design Lesson

This closes another count-only public surface in the v2.0 direction, but the
scale results still show the same future optimization boundary: candidate
download plus host exact refinement remains the dominant cost after witness-row
materialization is reduced. Device-resident prepared-scene output streams and
partner continuation remain v2.5+ work, not a v2.0 release claim.

