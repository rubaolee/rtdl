# Goal3008: Numba Group-Argmin Then Global-Argmax Front Door

## Purpose

Goal3007 proved the two generic Numba grouped reducers independently on an L4
pod. Goal3008 wires those reducers into the existing user-facing witness
adapter:

`group_argmin_then_global_argmax_partner_columns(..., partner="numba")`

This is the generic continuation shape needed by Hausdorff-style and
nearest-witness benchmark apps:

1. reduce candidate score rows to the lowest-score item per group;
2. reduce those per-group minima to the highest directed witness;
3. preserve deterministic tie-breaks.

## Semantics

| Stage | Operation | Tie-break |
| --- | --- | --- |
| Per group | `grouped_argmin_f64` | lowest score, then lowest `item_id` |
| Global | `grouped_argmax_f64` | highest score, then lowest group id |

The adapter accepts caller-supplied Numba CUDA arrays for `group_ids`,
`item_ids`, and `scores`. It returns generic columns:

- `group_ids`;
- `argmin_item_ids`;
- `argmin_scores`;

and metadata including `winner_group_id`, `winner_item_id`, and `winner_score`.

## Boundary

The front door is generic partner continuation only. It does not call RT
traversal, does not compute app-specific distances, and does not add native
engine logic.

This does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Use this adapter in a benchmark app wrapper, starting with Hausdorff or RTNN,
then collect pod evidence for the app-level wrapper.
