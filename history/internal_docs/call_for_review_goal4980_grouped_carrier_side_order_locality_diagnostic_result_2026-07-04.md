# Call For Review: Goal4980 Grouped Carrier Side-Order / Locality Diagnostic

Date: 2026-07-04

## File Under Review

- `history/internal_docs/goal4980_grouped_carrier_side_order_locality_diagnostic_result_2026-07-04.md`

## Requested Verdict

Please review with one of:

- `approve_goal4980_reverse_side_order_binary_route_win`
- `approve_with_required_amendments`
- `block_due_to_semantic_ordering_risk`
- `block_due_to_overclaim`

## Context

Goal4979 showed that side0 builder cost was not explained by simple work-unit counts. Goal4980 adds an app-owned diagnostic flag:

```text
--compiled-group-side-order 0,1
--compiled-group-side-order 1,0
```

It runs the same top4 writer-free binary descriptor route under both side orders.

## Review Questions

1. Does the evidence support that side0 slowness is order/locality/cache related rather than data-volume inherent?
2. Does reversing side order preserve the structural anchors relevant to the writer-free binary descriptor consumer?
3. Is it acceptable that grouped carrier row order changes, given that the current binary descriptor consumer aggregates descriptor pairs and does not claim paper-text ordering?
4. Is the report correct to limit this optimization candidate to the writer-free binary descriptor route, not the paper-text byte-equality route?
5. Does the report avoid RTDL core promotion, RayJoin-specific native primitive claims, and author-performance headlines?
6. Is the proposed next goal correct: promote reversed side order only for the binary descriptor route with explicit structural validation?
7. Should Goal4980 close with `completed_side_order_locality_diagnostic__reverse_order_wins`?

## Non-Authorization Boundary

This review should not authorize:

- public high-performance claims
- paper byte-equality claims for the reversed-order binary route
- RTDL core promotion
- RayJoin-specific native/core primitives
- Layer 4 traversal fusion

The only requested approval is that reversing side order is a valid app-owned binary-route optimization candidate and that Goal4981 may promote it with structural validation.
