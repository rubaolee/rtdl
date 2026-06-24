# V4.0 Release Candidate Packet

Status: engineering release candidate packet, not a release authorization

Date: 2026-06-24

## Candidate Definition

V4.0 is the Python GPU-array RT-core lane for measured Tier-2 fused generic
operators. The current candidate includes one unified Python front door, three
measured Torch CUDA device-array surfaces, an operator/callback planner, and
machine gates that keep V4.x work out of the V4.0 claim surface.

Release authorization remains `false` until external review and a release
decision record are obtained.

## Included V4.0 Surfaces

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`

## Included Capabilities

- unified Python front door: `import rtdsl.v4 as rtdl_v4`
- Torch CUDA device-array input
- Torch CUDA device-array output
- Tier-2 fused generic RT operators
- conservative operator/callback planner

## Deferred To V4.x

- Tier-3 Numba/PTX callback support
- raw OptiX callback public API
- wrapper/direct-callable ABI for custom scalar callbacks
- CuPy measured performance claims
- embedding/C-ABI
- non-Python host bindings
- app-specific native engine kernels

## Final GPU Validation

Fresh POD worktree:

- worktree: `/root/rtdl_v4_section8/worktrees/v4_final_validation_20260624_1340`
- validated code commit: `ae22afd90dbde1fde0d923e830e3ad0aa532f2ed`
- native build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-dev`
- native library: `build/librtdl_optix.so`
- required grouped-argmin symbol: present

Validation evidence:

- scope gate: `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- final GPU catalog gate, serious size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`
- final GPU catalog gate, smoke size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json`
- local V4 full test sweep: `future/v4/evidence/v4_local_full_test_sweep_2026-06-24.md`

The final GPU validation is tied to the runtime-code commit above. Later
candidate-packet edits are documentation/evidence wording updates only and are
covered by the local V4 full test sweep.

Final GPU catalog gate result:

- status: `passed`
- mode: `gpu`
- serious validation size: fixed-radius `copies=32768` / `262144` points; ray/triangle examples `32768` rays and triangles
- release authorized: `false`
- measured Tier-2 examples: 3/3 passed
- operator/callback planner examples: passed
- complex action-shaped callback: rejected/deferred

## Tier-3 Callback Boundary

Tier-3 remains spike-only and outside V4.0:

- Numba scalar device callback PTX generation: passed
- direct `optixModuleCreate` on bare helper PTX: blocked
- blocked reason: `No functions with semantic types found`
- interpretation: a future Tier-3 path requires wrapper/direct-callable ABI work

Evidence:

- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`

## User-Facing Entry Points

- `future/v4/README.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `future/v4/examples/fixed_radius_torch_device_arrays.py`
- `future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py`
- `future/v4/examples/ray_triangle_any_hit_flags_torch_device_arrays.py`
- `future/v4/examples/operator_callback_planning.py`

## Release Blockers

- external release review not obtained
- release decision record not obtained
- open V4 review debt exists

## Non-Authorization

This packet does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
