"""Paper contract versus frozen Goal5752 V4 physical ABI admission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


FAILURE_CODE = (
    "unsupported_physical_geometry_family__triangle_mesh_required__"
    "frozen_v4_sphere_only"
)


@dataclass(frozen=True)
class FrozenPhysicalCapability:
    geometry_family: str
    primitive_columns: tuple[str, ...]
    hit_channels: tuple[str, ...]
    query_columns: tuple[str, ...]
    output_columns: tuple[str, ...]
    prepare_symbol: str
    execute_symbol: str


FROZEN_GOAL5752_CAPABILITY = FrozenPhysicalCapability(
    geometry_family="custom_analytic_sphere_aabb_gas",
    primitive_columns=("center_f32x3", "radius_f32", "item_id_u32"),
    hit_channels=("analytic_attribute_0_as_item_id",),
    query_columns=("query_x_f32", "query_y_f32", "query_z_f32", "query_tmax_f32"),
    output_columns=("item_id_u32", "distance_f32", "status", "counters"),
    prepare_symbol="rtdl_optix_v4_prepare_formal_callback_v1",
    execute_symbol="rtdl_optix_v4_execute_prepared_formal_callback_device_v1",
)


class PhysicalAdmissionError(RuntimeError):
    def __init__(self, code: str, missing: Mapping[str, Sequence[str] | str]):
        super().__init__(code)
        self.code = code
        self.missing = dict(missing)


def admit_required_physical_capabilities(
    required: Mapping[str, Sequence[str] | str],
    available: FrozenPhysicalCapability = FROZEN_GOAL5752_CAPABILITY,
) -> FrozenPhysicalCapability:
    """Return authority only when every exact physical requirement is present."""

    missing: dict[str, Sequence[str] | str] = {}
    if required["geometry_family"] != available.geometry_family:
        missing["geometry_family"] = str(required["geometry_family"])
    for field in ("primitive_columns", "hit_channels", "query_columns", "output_columns"):
        wanted = tuple(str(value) for value in required[field])
        present = set(getattr(available, field))
        absent = tuple(value for value in wanted if value not in present)
        if absent:
            missing[field] = absent
    if missing:
        raise PhysicalAdmissionError(FAILURE_CODE, missing)
    return available
