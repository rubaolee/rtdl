# Goal3006: Numba Grouped Argmin/Argmax Preview

## Purpose

v2.6 needs a Numba first-class path for benchmark apps whose RT traversal returns
generic score rows and then needs a best witness per group. RTNN, Hausdorff, and RMQ-style workloads all pressure this shape.

Goal3006 adds preview support for:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

The contract is generic:

| Field | Meaning |
| --- | --- |
| `group_ids:int64` | group/key for each score row |
| `item_ids:int64` | candidate/witness id for each row |
| `scores:float64` | score to reduce |

No app vocabulary is added to the native engine or the Numba primitive.

## Semantics

| Operation | Tie-break |
| --- | --- |
| `grouped_argmin_f64` | lowest score, then lowest `item_id` |
| `grouped_argmax_f64` | highest score, then lowest `item_id` |

Outputs mirror the existing v2.5 grouped reducer shape:

- compact `group_ids`, `item_ids`, and `scores` for present groups;
- `missing_group_ids`;
- dense `dense_item_ids`, `dense_scores`, and `present_counts`.

## Implementation Boundary

The first Numba implementation uses CUDA device arrays and a generic two-pass
score/item reduction. It also uses host-observed present-group compaction, just
as the current `compact_mask_i64` preview uses a host prefix sum.

That means Goal3006 is a correctness and API-coverage step, not a performance
or zero-copy claim.

## Public Adapter

`grouped_argmin_f64_partner_columns(..., partner="numba")` and
`grouped_argmax_f64_partner_columns(..., partner="numba")` now route through the
v2.6 neutral Numba handoff and reject non-Numba CUDA arrays.

## Claim Boundary

Goal3006 does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Run an L4 pod conformance artifact with equal-score tie cases, missing groups,
and the public adapter front door before using this primitive in a benchmark app
wrapper.
