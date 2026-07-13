# Call For Review: Goal4981 Reversed Side-Order Promotion No-Go

Date: 2026-07-04

## File Under Review

- `history/internal_docs/goal4981_reversed_side_order_promotion_no_go_2026-07-04.md`

## Requested Verdict

Please review with one of:

- `approve_goal4981_no_go_restore_diagnostic_only`
- `approve_with_required_amendments`
- `block_due_to_incomplete_control_runs`
- `block_due_to_wrong_rollback`

## Context

Goal4980 appeared to show that side order `1,0` reduced carrier construction from about `0.77s` to about `0.10s`.

Goal4981 attempted to promote `1,0` as the default for the writer-free binary descriptor route.

Control runs showed a different causal story:

- fresh `1,0` made side1 slow (`0.694s`)
- second `1,0` became fast
- later `0,1` also became fast

This indicates a first-large-call warmup/cache/page effect rather than a stable side-order win.

## Review Questions

1. Do the control runs justify rejecting `1,0` default promotion?
2. Is the interpretation correct that the slow cost follows the first large side-builder call, not side0 specifically?
3. Was it correct to restore default side order to `0,1` while keeping the diagnostic flag?
4. Does the report preserve structural correctness and distinguish performance-causality correction from correctness failure?
5. Is the proposed next direction correct: explicit carrier side-builder warmup / first-large-call isolation?
6. Does the report avoid paper-text ordering claims, author-performance headlines, RTDL core promotion, and RayJoin-specific native/core primitives?
7. Should Goal4981 close with `completed_reversed_side_order_promotion_no_go__restore_diagnostic_only`?

## Non-Authorization Boundary

This review should not authorize:

- `1,0` default promotion
- public high-performance claims
- paper byte-equality claims for the binary route
- RTDL core promotion
- RayJoin-specific native/core primitives
- Layer 4 traversal fusion

The only requested approval is that the promotion no-go and rollback are correct, and that the next target is explicit first-large-call warmup isolation.
