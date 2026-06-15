# Goal4398 V3.0 M6 Frontier/Vector Pilot Local Preparation

Date: 2026-06-15

Status: local M6 frontier/vector graph preparation complete. Full M6 measurement remains blocked on pod hardware evidence.

## Decision

M6 prepares a generic aggregate-frontier/vector-sum route without introducing an application-specific native engine or force-law ABI.

The local checkpoint builds two no-execution V3 graphs:

| Graph | Primitive route | Continuation route |
| --- | --- | --- |
| `aggregate_frontier_vector_pilot` | `primitive.aggregate_frontier_2d` | `continuation.vector_sum` |
| `generic_frontier_vector_pilot` | `primitive.generic_row_stream` | `continuation.vector_sum` |

Both graphs share:

- frontier contract: `aggregate_frontier_vector_contract_v1`;
- grouped frontier values: `frontier_group_ids`;
- vector components: `frontier_vector_x`, `frontier_vector_y`;
- summary outputs: `vector_sum_x`, `vector_sum_y`;
- fail-closed overflow policy.

## Implemented Files

- `src/rtdsl/v3_0_m6_aggregate_pilots.py`
- `tests/goal4398_v3_0_m6_frontier_vector_pilot_test.py`
- Updated public exports in `src/rtdsl/__init__.py`

## Local Validation

The tests validate:

- exactly two frontier/vector pilot graphs are produced;
- both graphs are no-execution `PreparedGraph` objects;
- neither graph uses PartnerNode or automatic partner selection;
- both graphs share `aggregate_frontier_vector_contract_v1`;
- both graphs reuse `continuation.vector_sum`;
- summary outputs are generic vector sums;
- public claim flags remain false;
- pod evidence is still required.

## Test Results

Focused V3 M1-M6 stack:

```text
40 tests OK
```

## Boundary

This checkpoint does not claim:

- backend performance;
- RT-core speedup;
- device-resident vector continuation;
- whole-application speedup;
- public V3.0 performance.

## Full M6 Requirements

Full M6 completion requires:

- OptiX and Embree same-contract measurements;
- M3-grade phase accounting;
- evidence records for stream ordering, residency, transfer/materialization, and backend timing;
- validation that `continuation.vector_sum` remains generic and reusable;
- fresh review before public wording.

## Conclusion

M6 local graph preparation is complete. Hardware evidence is still required for full M6.
