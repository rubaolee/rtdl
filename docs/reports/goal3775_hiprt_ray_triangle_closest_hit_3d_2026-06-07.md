# Goal3775 HIPRT Ray/Triangle Closest-Hit 3D

## Purpose

Goal3775 makes the HIPRT `ray_triangle_closest_hit_3d` feature-matrix entry
executable instead of merely planned. This is a generic primitive: the native
engine sees only 3-D rays and 3-D triangles, then emits same-contract rows with
`ray_id`, `triangle_id`, and `t`.

This work is a prerequisite for the v2.10 contact-manifold AMD/HIPRT lane, but
it does not add contact-manifold-specific native logic.

## Implementation

- Adds `RtdlRayClosestHitRow` to the HIPRT C ABI.
- Adds `rtdl_hiprt_run_ray_closest_hit_3d`.
- Adds `RtdlRayClosestHit3DKernel`, which traverses HIPRT triangle geometry and
  compacts hit rows.
- Passes caller triangle ids through a device-side `triangle_ids` array so the
  output matches the established Embree/OptiX contract.
- Adds `ray_triangle_closest_hit_hiprt(...)` to the Python runtime and wires
  compiled `ray_triangle_closest_hit` kernels through `run_hiprt(...)`.
- Allows `run_generic_ray_triangle_closest_hit(..., backend="hiprt")` for this
  specific v2.10 primitive while leaving other frozen HIPRT generic wrappers
  unchanged.

## Current v2.10 Position

The v2.10 AMD/HIPRT parity map remains:

- 6 apps ready for AMD functional pod validation:
  `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`,
  `librts_spatial_index`, and `rtnn`.
- 2 apps still needing generic HIPRT extensions:
  `contact_manifold` and `barnes_hut`.
- 2 apps still compatibility-only for AMD performance:
  `raydb_style` and `triangle_counting`.

For `contact_manifold`, Goal3775 closes the closest-hit primitive gap. The
remaining blocker is a generic bounded contact-witness output contract.

## Boundary

This goal does not authorize AMD performance claims, HIPRT release claims,
whole-app acceleration claims, broad RT-core claims, paper-reproduction claims,
or app-specific native-engine logic.

NVIDIA CUDA/Orochi HIPRT pod evidence, when present, is functional
implementation evidence only. It is not AMD hardware evidence.
