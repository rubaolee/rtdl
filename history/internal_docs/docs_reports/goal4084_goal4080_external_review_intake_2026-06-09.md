# Goal4084 Goal4080 External Review Intake

Date: 2026-06-09

## Status

Implemented, local tests pass.

## Reviews

Goal4080 was reviewed by two distinct external systems:

- Claude: `docs/reviews/goal4081_claude_review_goal4080_grouped_union_work_reduction_plan_2026-06-09.md`
- Gemini: `docs/reviews/goal4082_gemini_review_goal4080_grouped_union_work_reduction_plan_2026-06-09.md`

Claude verdict: `accept-with-boundary`.

Gemini verdict: `accept`.

## Consensus

Both reviewers agree that the next serious RT-DBSCAN direction is a generic
fixed-radius grouped-union work-reduction primitive rather than more wrapper
tuning. Both reviewers also confirm that the plan preserves the app-agnostic
native boundary and explicit user partner choice.

The consensus is therefore:

`accept-with-boundary`

## Boundary Conditions Added

Claude identified three missing acceptance details. Goal4084 updates Goal4080 to
include them before implementation:

1. **Minimum work-reduction threshold:** the candidate must show at least 50%
   lower candidate hits or root calls than Goal4079 on rows it claims to
   improve.
2. **ngsim_dense regression guard:** the candidate must record
   `ngsim_dense_65536`; a material regression blocks promotion.
3. **Partition-build overhead:** the candidate must record
   `partition_summary_build_sec` and include that overhead in net production
   timing.

## Next Step

Proceed to Goal4081 native/API feasibility with those gates in force. The
feasibility pass should inspect integration points, partition-pair counts,
partition-build timing needs, and whether the existing OptiX grouped-union path
can consume partition-aware work without app vocabulary.

## Boundary

This intake does not authorize implementation promotion, release, public speedup
wording, broad RT-core wording, whole-app acceleration wording, paper
reproduction wording, automatic partner/backend selection, true-zero-copy
claims, or app-specific native-engine logic.
