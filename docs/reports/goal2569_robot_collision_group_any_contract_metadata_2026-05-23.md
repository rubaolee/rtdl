# Goal2569: Robot-Collision Group-Any Contract Metadata

Date: 2026-05-23

## Scope

Goal2569 applies the shared grouped-reduction contract to the robot-collision
app adapter. The adapter already used a generic partner-side group-any
reduction over native ray any-hit flags; this change records that operation in
standard metadata.

## Change

`robot_collision_pose_flags_optix_prepared_partner_device_columns` now records:

- `grouped_reduction_contract` from `GroupedReductionSpec`
- `grouped_reduction_capacity_status` from `GroupedReductionCapacityStatus`

The operation is `group_any` over app-owned `pose_index` groups. The native
engine row contract remains `generic_ray_primitive_any_hit_flags`.

## Boundary

This is app-adapter metadata only. It does not move robot semantics into native
engines, does not add native symbols, and does not authorize public speedup,
whole-app, or robot-solver claims.

Boundary phrase: does not move robot semantics into native engines.

## Validation

Added `tests/goal2569_robot_collision_group_any_contract_metadata_test.py`,
covering:

- shared grouped-reduction metadata in the app adapter;
- preserved native row-contract boundary;
- this report.

No pod was used.
