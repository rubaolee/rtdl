# Call For Review: Goal4954-C Measured Pre-Fusion Bottleneck Prototype Plan

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md`
- `history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`
- `history/internal_docs/antigravity_review_goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`

Requested verdict:

`approve_goal4954c_grouped_carrier_prototype`

or:

`block_goal4954c_plan_until_amended`

## Review Questions

1. Is it correct to target binary grouped row construction first, given it is
   the largest measured pre-fusion bottleneck?

2. Is the grouped columnar carrier generic enough:
   - group offsets/lengths;
   - group-level labels/descriptors;
   - point-level coordinate columns?

3. Does the plan avoid RTDL core/runtime edits and public API exposure?

4. Does it preserve the RTDL-generic/RayJoin-app invariant?

5. Is it correct to hold LSI, reprojection, sort, PIP, midpoint generation, and
   input data constant for C1, so the effect is isolated?

6. Is the descriptor-pair consumer over group-level labels and `group_length`
   a fair replacement for the flat repeated-label consumer?

7. Are success/failure labels decision-forcing?

8. Should Goal4954-C C1 open with:

   `approve_goal4954c_grouped_carrier_prototype`

## Non-Authorization Boundary

Approval does not authorize:

- Layer 4 fusion;
- raw callbacks;
- RTDL core/runtime edits;
- public API exposure;
- promotion of app-owned RayJoin prototype code into RTDL core;
- performance claims beyond the measured public sample.
