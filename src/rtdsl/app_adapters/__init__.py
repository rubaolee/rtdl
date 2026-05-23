"""Application-scoped RTDL adapter helpers.

Shared primitives stay in `rtdsl.partner_adapters`; app-specific compositions
belong in this package or in benchmark/example modules.
"""

from .robot_collision import allocate_robot_collision_pose_partner_device_output_columns
from .robot_collision import robot_collision_pose_flags_optix_prepared_partner_device_columns


__all__ = [
    "allocate_robot_collision_pose_partner_device_output_columns",
    "robot_collision_pose_flags_optix_prepared_partner_device_columns",
]
