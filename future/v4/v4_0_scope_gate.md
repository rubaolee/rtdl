# V4.0 Scope Gate

Status: V4 development scope, not a release announcement

V4.0 currently means the Python GPU-array front door over measured Tier-2 fused
generic RT operators. It does not mean raw OptiX callbacks, arbitrary user
device code, CuPy performance, embedding/C-ABI, or app-specific native kernels.

## Included In V4.0 Development Scope

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`

Included capabilities:

- unified `import rtdsl.v4 as rtdl_v4` front door
- Torch CUDA device-array input
- Torch CUDA device-array output
- Tier-2 fused generic RT operators
- conservative operator/callback planner

## Deferred To V4.x

- Tier-3 Numba/PTX/OptiX callback support
- raw OptiX callback public API
- CuPy measured performance claims
- embedding/C-ABI
- non-Python host bindings
- app-specific native engine kernels

## Machine Gate

Run:

```bash
python scripts/v4_scope_gate.py \
  --json-out future/v4/evidence/v4_scope_gate_2026-06-24.json \
  --md-out future/v4/evidence/v4_scope_gate_2026-06-24.md
```

The gate must keep `release_authorized: false` until external release review and
a release decision record exist.

## Non-Claims

This page does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
- embedding/C-ABI claims

