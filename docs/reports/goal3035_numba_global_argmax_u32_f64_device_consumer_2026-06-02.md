# Goal3035 - Generic Numba Global Argmax Device Consumer

Date: 2026-06-02

## Purpose

Goal3033/3034 added a generic OptiX producer that writes point-group
nearest-witness data into caller-owned CUDA columns. The next missing piece was
a generic device-side consumer that can reduce such columns without pulling a
full row table back to Python.

Goal3035 adds:

- `run_numba_global_argmax_u32_f64(item_ids, scores, ...)`
- `global_argmax_u32_f64_partner_columns({"item_ids": ..., "scores": ...}, partner="numba")`

The operation selects the row with the highest `float64` score, then uses the
lowest `uint32` item id and lowest row index as deterministic tie-breakers. It
also skips an explicit invalid item-id sentinel, defaulting to `0xffffffff`.

## Why This Is Generic

The primitive knows only:

- `item_ids:uint32`
- `scores:float64`
- an optional invalid item-id sentinel

It does not mention Hausdorff, X-HD, nearest neighbors, point sets, RayJoin, or
any benchmark app. Hausdorff can use it by passing query ids as `item_ids` and
nearest-witness distances as `scores`, while other apps can use the same
contract for any global winner row over device columns.

## Boundary

The new front door validates the v2.6 neutral partner handoff before running
Numba. CuPy columns are accepted as explicit user-selected device columns for a
Numba consumer through the CUDA array interface, without a torch carrier.

This work does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true-zero-copy wording
- app-specific native-engine behavior

It is a generic partner continuation over device arrays. It does not replace RT
traversal and does not add app logic to the native engine.

## Next Work

Use `global_argmax_u32_f64_partner_columns` after the Goal3033 OptiX device
column producer inside the Hausdorff benchmark path, then validate on the L4 pod
that the reduced device-column result matches the raw row-view result.
