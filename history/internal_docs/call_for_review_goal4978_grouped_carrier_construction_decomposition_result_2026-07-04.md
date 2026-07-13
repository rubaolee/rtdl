# Call For Review: Goal4978 Grouped Carrier Construction Decomposition

Date: 2026-07-04

## File Under Review

- `history/internal_docs/goal4978_grouped_carrier_construction_decomposition_result_2026-07-04.md`

## Requested Verdict

Please review with one of:

- `approve_goal4978_carrier_construction_side_builder_dominated`
- `approve_with_required_amendments`
- `block_due_to_missing_subphase_evidence`
- `block_due_to_genericity_or_overclaim`

## Context

Goal4977 removed the midpoint scaled-point host pack floor. The largest remaining downstream component became:

```text
grouped_compiled_columnar_carrier_construction_sec ~= 0.664s
```

Goal4978 instruments the compiled carrier builder to split this phase into:

- input coercion/allocation
- side0/side1 Numba builder loops
- slice copies
- concatenate
- group-offset cumsum
- stats packaging

## Review Questions

1. Does the evidence show that carrier construction is dominated by the side-builder Numba loops?
2. Is the side0 dominance (`0.576s` of `0.655s`) correctly interpreted as the next real carrier target?
3. Does the report correctly rule out concat/cumsum/slice-copy micro-optimization as the next meaningful target?
4. Did Goal4978 preserve structural consistency with Goal4977?
5. Does the report maintain the generic-system boundary and avoid promoting app-owned overlay assembly into RTDL core?
6. Is the proposed next direction correct: audit side-builder work units before optimizing the carrier algorithm?
7. Should Goal4978 close with `completed_carrier_construction_side_builder_dominated`?

## Non-Authorization Boundary

This review should not authorize:

- author-performance claims
- public high-performance claims
- RTDL core promotion of the grouped carrier
- RayJoin-specific native/core primitives
- Layer 4 traversal fusion

The only requested approval is that Goal4978 correctly decomposes the carrier floor and identifies the side-builder loop as the next carrier target.
