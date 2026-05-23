from __future__ import annotations

from ..partner_adapters import _column_length
from ..partner_adapters import _partner_module
from ..partner_adapters import partner_group_any_by_key


def allocate_robot_collision_pose_partner_device_output_columns(
    pose_count: int,
    ray_count: int,
    *,
    partner: str = "torch",
) -> dict[str, object]:
    """Allocate reusable partner-owned ray and pose flag buffers."""
    pose_count = int(pose_count)
    ray_count = int(ray_count)
    if pose_count < 0:
        raise ValueError("pose_count must be non-negative")
    if ray_count < 0:
        raise ValueError("ray_count must be non-negative")
    runtime = _partner_module(partner)
    return {
        "ray_any_hit_flags": runtime["zeros"]((ray_count,), runtime["uint32"], runtime["device"]),
        "pose_collision_flags": runtime["zeros"]((pose_count,), runtime["uint32"], runtime["device"]),
    }


def _require_robot_collision_output_column_lengths(
    output_columns: dict[str, object],
    *,
    pose_count: int,
    ray_count: int,
) -> None:
    for name, expected in (("ray_any_hit_flags", ray_count), ("pose_collision_flags", pose_count)):
        if name not in output_columns:
            raise ValueError(f"output_columns must include {name!r}")
        if _column_length(output_columns, name) != expected:
            raise ValueError(f"output_columns[{name!r}] length must match {expected}")


def _scatter_ray_flags_to_pose_flags(runtime: dict, ray_flags, pose_indices, pose_flags) -> None:
    if runtime["name"] == "torch":
        pose_flags.copy_(
            partner_group_any_by_key(
                pose_indices,
                ray_flags,
                _column_length({"pose_flags": pose_flags}, "pose_flags"),
                partner=runtime["name"],
            )
        )
        return
    if runtime["name"] == "cupy":
        pose_flags[...] = partner_group_any_by_key(
            pose_indices,
            ray_flags,
            _column_length({"pose_flags": pose_flags}, "pose_flags"),
            partner=runtime["name"],
        )
        return
    raise ValueError("partner must be 'torch' or 'cupy'")


def robot_collision_pose_flags_optix_prepared_partner_device_columns(
    prepared_scene,
    ray_columns: dict[str, object],
    pose_indices,
    *,
    pose_count: int,
    partner: str = "torch",
    output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return robot collision pose flags through generic ray/triangle any-hit flags.

    The native engine writes one generic any-hit flag per ray. This app-layer
    adapter reduces ray flags to one collision flag per pose with Torch/CuPy.
    """
    pose_count = int(pose_count)
    if pose_count < 0:
        raise ValueError("pose_count must be non-negative")
    ray_count = _column_length(ray_columns, "ids")
    if _column_length({"pose_indices": pose_indices}, "pose_indices") != ray_count:
        raise ValueError("pose_indices length must match ray count")
    runtime = _partner_module(partner)
    output_reuse_authorized = output_columns is not None
    if output_columns is None:
        output_columns = allocate_robot_collision_pose_partner_device_output_columns(
            pose_count,
            ray_count,
            partner=partner,
        )
    _require_robot_collision_output_column_lengths(
        output_columns,
        pose_count=pose_count,
        ray_count=ray_count,
    )
    ray_flags = output_columns["ray_any_hit_flags"]
    pose_flags = output_columns["pose_collision_flags"]
    native_result = prepared_scene.write_device_any_hit_flags(ray_columns, ray_flags)
    _scatter_ray_flags_to_pose_flags(runtime, ray_flags, pose_indices, pose_flags)
    runtime["sync"]()
    columns = {
        "ray_any_hit_flags": ray_flags,
        "pose_collision_flags": pose_flags,
    }
    metadata = dict(native_result["metadata"])
    metadata.update(
        {
            "adapter": "robot_collision_pose_flags_optix_prepared_partner_device_columns",
            "app": "robot_collision_screening",
            "partner": runtime["name"],
            "pose_count": pose_count,
            "ray_count": ray_count,
            "output_columns_reused": output_reuse_authorized,
            "input_contract": "caller_supplied_partner_device_ray_columns_and_pose_indices",
            "native_engine_row_contract": "generic_ray_primitive_any_hit_flags",
            "app_flag_materialization": "partner_gpu_pose_flags_from_native_any_hit_ray_flags",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns
