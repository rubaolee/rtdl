# Call For Review: Goal4979 Grouped Carrier Side-Builder Work-Unit Audit

Date: 2026-07-04

## File Under Review

- `history/internal_docs/goal4979_grouped_carrier_side_builder_work_unit_audit_result_2026-07-04.md`

## Requested Verdict

Please review with one of:

- `approve_goal4979_side_builder_mixed_no_single_target`
- `approve_with_required_amendments`
- `block_due_to_missing_work_unit_evidence`
- `block_due_to_overclaim_or_wrong_next_step`

## Context

Goal4978 showed grouped carrier construction is dominated by the Numba side-builder loop. Goal4979 adds work-unit metrics to determine whether side0 is slower because of more original points, more intersections, more groups, more dedupe calls, or another effect.

## Review Questions

1. Does the work-unit evidence show that side0 is not simply slower because it scans more original points?
2. Does the evidence show that side0 and side1 process the same intersection row count and similar group counts?
3. Is it correct to reject concat/cumsum/slice-copy as the next meaningful optimization target?
4. Is the report right to classify the outcome as mixed/no single scalar target rather than chain-scan/intersection-run dominated?
5. Is the recommended next diagnostic correct: side-order/locality/first-large-call test before algorithm rewrite?
6. Does the report preserve the generic-system boundary and avoid promoting app-owned overlay assembly into RTDL core?
7. Should Goal4979 close with `completed_side_builder_mixed_no_single_target`?

## Non-Authorization Boundary

This review should not authorize:

- author-performance claims
- public high-performance claims
- RTDL core promotion of grouped carrier
- RayJoin-specific core/native primitives
- Layer 4 traversal fusion

The only requested approval is that Goal4979 correctly interprets the side-builder work-unit audit and chooses the next diagnostic rather than jumping to premature optimization.
