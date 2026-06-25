# V4.0 Development-State Decision Packet

Status: development-state decision packet, not a release authorization

Date: 2026-06-24

## Decision

V4.0 is not release-authorized by this packet.

Current recommended outcome for `goal4623` review:

- `development_state_documentation_disclosure_not_release`

This means the current V4 front door can be documented as a development surface
with measured/candidate status clearly labeled, but it must not be presented as
a V4 release, release candidate, broad speedup result, or whole-application
benchmark result until a later release decision explicitly authorizes that.

## Current V4 Definition

V4 is the Python GPU-array RT-core lane for generic fused Tier-2 operators.
It accepts caller-owned Torch CUDA arrays for measured surfaces, runs RTDL
generic fused operators, and writes to device outputs without Python row objects
in the hot path.

This V4 packet is not the old C ABI / embedding / multi-language host plan.
Those items remain deferred.

## Measured V4 Tier-2 Surfaces

Measured Torch CUDA surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`

Measured scope:

- partner: Torch CUDA
- validated GPU family: RTX A5000 / Ampere for the newer measured surfaces
- maximum validated OptiX ABI for the newer measured surfaces: `8.0`
- release authorization: `false`

Not authorized:

- CuPy performance claims
- OptiX 9.1 claims for grouped-i64 or point-group
- broad V4 speedup wording
- whole-application speedup wording
- public true-zero-copy wording

## Current Tier-2 Candidate

Candidate surface:

- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

Candidate status:

- `tier2_candidate_goal4620_not_measured`

This candidate has a candidate POD gate and completion consensus, but it is not
a measured V4 release surface. It must remain labeled as candidate until a
separate promotion decision authorizes otherwise.

## Tier-3 Callback Boundary

Tier-3 callbacks are protocol-only, not supported:

- protocol: `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- scalar callback planner status:
  `tier3_spike_only_not_v4_0_release_surface`
- protocol status:
  `tier3_protocol_goal4622_spike_only_not_support`
- action-shaped callback status:
  `rejected_action_shaped_callback_deferred`

The previous evidence remains narrow:

- Numba scalar device callback PTX generation: passed in a limited toolchain
- direct `optixModuleCreate` on bare helper PTX: blocked
- blocked reason: `No functions with semantic types found`

This packet does not authorize Tier-3 callback support or raw OptiX callback
support.

## Current Gates

Scope gate:

- `future/v4/v4_0_scope_gate.md`
- `future/v4/evidence/v4_goal4623_scope_gate_current_2026-06-24.json`
- status: `passed`
- included measured surfaces: `5`
- candidate surfaces: `1`

Final `goal4623` GPU catalog gate:

- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.md`
- status: `passed`
- mode: `gpu`
- measured surfaces: `5/5` passed
- candidate surfaces: `1/1` passed as candidate only
- release authorization: `false`

The catalog gate includes:

- all five measured surfaces
- the one candidate surface labeled as candidate
- operator/callback planner examples
- release authorization false
- claim flags false

## User-Facing Entry Points

- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_0_scope_gate.md`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `future/v4/examples/fixed_radius_torch_device_arrays.py`
- `future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py`
- `future/v4/examples/ray_triangle_any_hit_flags_torch_device_arrays.py`
- `future/v4/examples/primitive_grouped_i64_reduction_torch_device_arrays.py`
- `future/v4/examples/point_group_nearest_witness_torch_device_arrays.py`
- `future/v4/examples/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py`
- `future/v4/examples/operator_callback_planning.py`

## Release Blockers

- no release decision record authorizes V4 release
- Antigravity review debt remains open for recent goals
- no all-application benchmark protocol authorizes whole-app speedup wording
- weighted-sum remains candidate, not measured
- Tier-3 remains protocol-only

## Non-Authorization

This packet does not authorize:

- V4 release
- V4 release candidate
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- public true-zero-copy wording
- CuPy performance claims
- embedding/C-ABI claims
- non-Python host binding claims
- app-specific native engine kernels
