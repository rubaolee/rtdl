# Handoff To Gemini: Goal4377 Pre-V3 Strategy Review

Date: 2026-06-14

Repository: `rubaolee/rtdl`

Primary document to review:

- `docs/reports/goal4377_pre_v3_v2_13_v2_14_strategy_2026-06-14.md`

## One-Sentence Reviewer Prompt

Please review whether Goal4377 draws the right line between v2.13 internal
cleanup, a v2.14 formal benchmark-app cleanup/boost release, and a later V3.0
planner/device-residency effort aimed at approaching expert C++/CUDA/OptiX hot
paths without adding app-specific native engine logic.

## Why This Review Is Needed

RayJoin Section 5.7 exposed a subtle but important risk. RTDL OptiX is now near
the author RT process wall time on the available County x Zipcode and Block x
Water rows, and faster than RTDL Embree CPU on those rows. However, the author
process wall includes large map read/deserialization time, while RTDL's wall
time reflects runtime compute/prepare/materialization. Therefore the same table
must not be used as evidence that RTDL's generic hot path is as efficient as the
author's specialized C++/CUDA/OptiX hot path.

The proposed roadmap is:

1. Use v2.13 as an internal/corrective bridge or explicitly supersede the
   existing v2.13 source-tree release package after review.
2. Make v2.14 the formal cleanup release, with every promoted benchmark app
   audited for current best routes, same-contract comparison, partner choice,
   phase explanation, and public wording.
3. Start V3.0 only after v2.14, with a focus on generic primitive planning,
   device-resident streams, fused continuations, backend-specific lowering, and
   profiler-grade phase accounting.

## Specific Points To Audit

- Does the document avoid treating "RTDL OptiX near author process wall" as
  "RTDL hot compute matches author code"?
- Does it handle the existing v2.13 release package and version marker safely?
- Does "boost all benchmark apps" mean disciplined optimization and explanation
  rather than guaranteed RT-core wins?
- Are the v2.14 gates sufficient for a serious public release packet?
- Is V3.0 correctly defined as a generic planner/device-resident execution
  system rather than a RayJoin-specific native rewrite?
- Are any necessary release blockers missing?

## Expected Output

Write a review to:

- `docs/reviews/goal4377_gemini_review_pre_v3_v2_13_v2_14_strategy_2026-06-14.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The review must not authorize a release, a tag move, broad RT-core speedup
wording, whole-application speedup wording, RTDL-beats-RayJoin wording,
RayJoin paper reproduction wording, automatic partner selection, Intel/AMD GPU
wording, or true zero-copy/device-residency wording.

