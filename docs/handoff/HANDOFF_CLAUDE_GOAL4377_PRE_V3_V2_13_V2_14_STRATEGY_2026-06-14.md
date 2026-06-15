# Handoff To Claude: Goal4377 Pre-V3 Strategy Review

Date: 2026-06-14

Repository: `rubaolee/rtdl`

Primary document to review:

- `docs/reports/goal4377_pre_v3_v2_13_v2_14_strategy_2026-06-14.md`

## One-Sentence Reviewer Prompt

Please critically review the Goal4377 pre-V3 strategy: should RTDL treat v2.13
as an internal/corrective bridge after the RayJoin hot-path caveat, make v2.14
the formal cleanup-and-benchmark-boost release, and defer author-level hot-path
efficiency to a V3.0 planner/device-resident execution-graph target?

## Background

The latest RayJoin overlay work fixed a concrete RTDL OptiX-vs-Embree issue:
Block x Water is no longer Embree-faster under the current RTDL route.

Current measured rows:

| Row | Author RT process wall | Goal4376 RTDL OptiX | RTDL Embree CPU |
| --- | ---: | ---: | ---: |
| County x Zipcode | 5.614s | 5.767s | 9.954s |
| Block x Water | 28.088s | 28.471s | 34.905s |

But the cost structure is not equivalent. The author Block x Water process wall
includes large read/deserialization time, while RTDL spends substantial time in
runtime compute/prepare/materialization. We therefore cannot claim RTDL hot
compute matches the author C++/CUDA/OptiX implementation.

The proposed conclusion is:

- v2.13 should become an internal/corrective bridge or be explicitly superseded,
  depending on whether the existing v2.13 source-tree release/tag has already
  been published.
- v2.14 should be the formal cleanup release: current-head benchmark-app audit,
  best-known OptiX and Embree routes, fixed partners, phase explanations,
  current pod evidence, and public wording cleanup.
- V3.0 should target a generic planner/device-resident/fused primitive graph
  that can lower benchmark-app workloads into ray workloads closer to expert
  hand-written OptiX code, without making the native engine app-specific.

## Review Questions

1. Is the strategy honest about the RayJoin author-code comparison?
2. Is "near author process wall" clearly separated from "author hot-compute
   parity"?
3. Is it safe to describe v2.13 as an internal bridge given the existing v2.13
   release package, or should the document require "superseded by v2.14" wording
   instead?
4. Does the v2.14 gate list avoid overpromising with the phrase "boost all
   benchmark apps"?
5. Does the V3.0 target preserve the app-agnostic RTDL engine rule?
6. What release-blocking evidence should be added before v2.14?

## Expected Output

Write a review to:

- `docs/reviews/goal4377_claude_review_pre_v3_v2_13_v2_14_strategy_2026-06-14.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The review must not authorize a release, a tag move, broad RT-core speedup
wording, whole-application speedup wording, RTDL-beats-RayJoin wording,
RayJoin paper reproduction wording, automatic partner selection, Intel/AMD GPU
wording, or true zero-copy/device-residency wording.

