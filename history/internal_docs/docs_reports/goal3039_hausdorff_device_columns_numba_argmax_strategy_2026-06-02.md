# Goal3039 - Hausdorff Device Columns plus Numba Argmax Strategy

Date: 2026-06-02

## Purpose

Goal3037 proved the generic composition:

`OptiX point-group nearest-witness device columns -> Numba global_argmax_u32_f64`

Goal3039 wires that composition into the Hausdorff benchmark application as a
selectable exact method:

`rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness`

This is app-level code only. The native engine remains app-agnostic and exposes
only generic point/group and reduction contracts.

## What Changed

The Hausdorff benchmark now has a directed helper that:

1. Packs source points and target point groups.
2. Uses `write_device_nearest_witness_columns` to write:
   - `query_ids:uint32`
   - `neighbor_ids:uint32`
   - `distances:float64`
   into CuPy-owned device buffers.
3. Uses `global_argmax_u32_f64_partner_columns(..., partner="numba")` to select
   the max-distance witness on the Numba partner path.
4. Copies only the selected scalar/witness back for the final Python result.

The user-facing function is:

`hausdorff_distance_2d_rt_grouped_device_columns_numba_argmax_nearest_witness`

and the CLI method is:

`--method rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness`

## Boundary

This goal does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- app-specific native-engine behavior

It is a benchmark-app strategy wiring step. The next goal must run it on a pod
against the current CuPy grouped-grid reference under the same exact Hausdorff
contract before any performance conclusion is drawn.
