# Call For Review: Goal4951 Compiled Generic Path-Split Materializer

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md`

## Context

Goals 4939 and 4940 already proved a generic host-columnar path-split prototype and showed that app-adapter wiring was byte-equal but too slow.

Goal4950 closed Layer 1/2 as capability success but RayJoin performance no-go.

The proposed next goal is to test a compiled/native generic path-split materializer. It must not place RayJoin output format or overlay semantics into RTDL core.

## Requested Verdict Label

Use one of:

- `approve_goal4951_compiled_generic_path_split_spike`
- `approve_with_required_amendments`
- `reject_goal4951_as_not_generic_or_not_worth_it`

## Review Questions

1. Does Goal4951 correctly follow from Goal4938/4939/4940/4949/4950?
2. Is the proposed target the measured structural bottleneck rather than another small Layer 2 tweak?
3. Are the genericity red lines strong enough to prevent RayJoin-specific output logic from entering RTDL core?
4. Is the non-RayJoin synthetic gate required before RayJoin adapter wiring?
5. Are the correctness and performance gates strict enough?
6. Should implementation start if this review passes?
7. If implementation starts, should the first implementation be a minimal compiled/internal spike rather than public API productization?
