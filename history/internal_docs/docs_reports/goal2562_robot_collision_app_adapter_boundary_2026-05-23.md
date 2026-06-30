# Goal2562: Robot Collision App Adapter Boundary

Date: 2026-05-23

## Scope

Goal2551 consensus identified
`robot_collision_pose_flags_optix_prepared_partner_device_columns` as an
app-specific adapter living in the shared `rtdsl.partner_adapters` module.
Goal2562 moves that composition into an application-scoped adapter namespace.

## Change

- Added `src/rtdsl/app_adapters/robot_collision.py`.
- Moved the robot collision pose-flag partner adapter and its output-buffer
  allocator into that module.
- Removed the robot-collision-specific functions from
  `src/rtdsl/partner_adapters.py`.
- Kept top-level `rtdsl` exports intact by importing the moved functions from
  `rtdsl.app_adapters`.

## Boundary

The shared partner adapter module no longer carries robot-collision-specific
functions. Generic partner primitives, including `partner_group_any_by_key`,
remain in `rtdsl.partner_adapters`; the robot adapter composes those primitives
in the app-adapter layer.

The top-level `rtdsl` exports remain for compatibility. Direct imports from
`rtdsl.partner_adapters` for the old robot-specific functions are intentionally
not preserved because the cleanup goal is to remove those app-specific symbols
from the shared module.

## Validation

- Updated `tests/goal1927_robot_collision_partner_pose_flags_adapter_test.py`.
- Added `tests/goal2562_robot_collision_app_adapter_boundary_test.py`.
- The tests verify the moved location, absence from shared partner adapters, and
  preserved top-level `rtdsl` exports.

No pod was used. This is local Python module-boundary cleanup.
