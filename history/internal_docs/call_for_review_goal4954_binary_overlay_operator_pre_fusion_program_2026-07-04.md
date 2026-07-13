# Call For Review: Goal4954 Binary Overlay Operator Pre-Fusion Program

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md`
- `history/internal_docs/goal4953_rayjoin_binary_overlay_operator_contract_2026-07-04.md`
- `history/internal_docs/claude_review_goal4953_binary_overlay_operator_contract_2026-07-04.md`

Requested verdict:

`approve_goal4954_binary_overlay_pre_fusion_program`

or:

`block_goal4954_program_until_amended`

## Context

The owner approved the following boundary:

> Do everything practical before Layer 4 fusion. Do not do Layer 4 yet.

This means the next program should target:

- binary/columnar overlay operator contract;
- writer-free measurement;
- columnar/device-resident reprojection and sort where possible;
- binary row construction;
- downstream consumer;
- final pre-fusion gap classification.

It must exclude:

- raw OptiX callbacks;
- traversal-side fusion;
- Numba PTX injection into traversal;
- hidden RayJoin kernels in RTDL core.

It must also preserve the owner invariant:

> RTDL is a general spatial dataflow system. RayJoin is an app/stress test on
> top of it.

Any RTDL-core feature proposed by Goal4954 must be generic and must have a
non-RayJoin proof before promotion. RayJoin-specific adaptation, paper text
formatting, AuthorOfficial comparison, and CDB/paper conventions must stay in
the RayJoin paper-reproduction app layer.

## Review Questions

1. Does Goal4954 correctly express the owner boundary:
   "all practical Layer 1/2/3 binary overlay work, but no Layer 4 fusion"?

2. Does it preserve the split between:
   - paper reproduction text-output line as correctness anchor;
   - binary operator line as performance/value benchmark?

3. Does it correctly incorporate Claude's Goal4953 AM1:
   removing writer isolates the compute gap but does not close it?

4. Does the subgoal sequence make sense:
   - 4954-A contract/measurement plan;
   - 4954-B writer-free baseline;
   - 4954-C columnar reprojection/sort;
   - 4954-D binary rows + downstream consumer;
   - 4954-E pre-fusion decision?

5. Are the non-goals strong enough to prevent accidental Layer 4 work or
   RayJoin-specific RTDL core logic?

6. Does the new System Invariant section make the generic-system boundary
   enforceable rather than rhetorical?

7. Does the promotion gate correctly require:
   - generic name/schema;
   - non-RayJoin consumer or test;
   - no paper text or AuthorOfficial semantics in RTDL core;
   - RayJoin-specific adaptation confined to the app layer?

8. If a future 4954 subgoal needs RayJoin-specific fields or output-chain
   semantics, should that be classified as app-owned rather than RTDL-core
   progress?

9. Are success/failure criteria decision-forcing and honest?

10. Should this program be approved with:

   `approve_goal4954_binary_overlay_pre_fusion_program`

## Non-Authorization Boundary

Approval authorizes only the Goal4954 program structure and opening Goal4954-A.

It does not authorize:

- immediate implementation of all subgoals;
- raw callback support;
- traversal-side fusion;
- public API exposure;
- app-specific RayJoin kernels in RTDL core;
- performance claims before measurement;
- weakening of the paper-reproduction correctness anchor.
