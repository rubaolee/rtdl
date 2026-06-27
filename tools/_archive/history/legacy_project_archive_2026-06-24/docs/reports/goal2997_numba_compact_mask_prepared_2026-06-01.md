# Goal2997: Numba Compact Mask Prepared

Date: 2026-06-01

Status: prepared for pod validation.

## Purpose

After Goal2995 closed the RayDB-style grouped scalar reductions for
user-selected Numba, the next useful v2.6 primitive is `compact_mask_i64`.

This primitive supports benchmark-app continuations that need to turn a
device-resident boolean mask into selected row indices, including RayJoin-style
and triangle-counting-style paths. It remains a generic continuation primitive,
not an app-specific native engine feature.

## Implementation

The Numba continuation layer now exposes:

- `describe_numba_compact_mask_i64`
- `run_numba_compact_mask_i64`
- `run_numba_mask_indices_i64`

The public adapter front door now supports:

- `partner_mask_indices(mask, partner="numba")`

The adapter validates the mask through the v2.6 neutral partner handoff before
launching Numba. Host NumPy masks are rejected before CUDA execution.

## Determinism

The implementation deliberately avoids a nondeterministic global-atomic scatter.
It uses:

1. per-block counts,
2. a host prefix sum over block counts,
3. per-block stable scatter.

This is correctness-first and stable-input-order preserving. It is not yet a performance claim.

## Boundaries

This goal does not authorize:

- v2.6 release
- public speedup claims
- whole-app speedup claims
- broad RT-core speedup claims
- true zero-copy claims
- automatic partner selection claims

CUDA pod evidence is still required before this can be treated as runtime
conformance evidence.
