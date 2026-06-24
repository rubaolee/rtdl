from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .optix_runtime import _validate_closest_hit_grouped_argmin_device_output_columns
from .optix_runtime import prepare_optix_static_triangle_scene_3d_device_triangles


V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE = (
    "v4_closest_hit_grouped_argmin_3d_device_arrays"
)
V4_RAY_TRIANGLE_MEASURED_PARTNERS = ("torch",)
V4_RAY_TRIANGLE_DECLARED_UNMEASURED_PARTNERS = ("cupy",)
V4_RAY_TRIANGLE_ALLOWED_PARTNERS = (
    *V4_RAY_TRIANGLE_MEASURED_PARTNERS,
    *V4_RAY_TRIANGLE_DECLARED_UNMEASURED_PARTNERS,
)


def _require_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_RAY_TRIANGLE_ALLOWED_PARTNERS:
        allowed = ", ".join(V4_RAY_TRIANGLE_ALLOWED_PARTNERS)
        raise ValueError(f"partner must be one of: {allowed}")
    return partner


def closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4(
    partner: str = "torch",
) -> dict[str, object]:
    """Return the V4 claim boundary for the closest-hit grouped-argmin surface."""

    partner = _require_partner(partner)
    measured = partner in V4_RAY_TRIANGLE_MEASURED_PARTNERS
    return {
        "v4_api_surface": V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE,
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": V4_RAY_TRIANGLE_MEASURED_PARTNERS,
        "partner_support_declared_unmeasured": tuple(
            item
            for item in V4_RAY_TRIANGLE_ALLOWED_PARTNERS
            if item not in V4_RAY_TRIANGLE_MEASURED_PARTNERS
        ),
        "partner_claim_status": (
            "measured_on_v4_section8_pod"
            if measured
            else "declared_unmeasured_not_performance_ready"
        ),
        "python_ray_object_boundary_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
    }


def allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4(
    group_count: int,
    *,
    partner: str = "torch",
    device: object | None = None,
) -> dict[str, object]:
    """Allocate reusable device output columns for the V4 grouped-argmin surface."""

    partner = _require_partner(partner)
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    if partner != "torch":
        raise RuntimeError("CuPy output allocation is declared but unmeasured for this V4 surface")
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch is required for the measured V4 grouped-argmin surface") from exc
    if device is None:
        device = torch.device("cuda")
    return {
        "group_has_value": torch.zeros((group_count,), dtype=torch.uint8, device=device),
        "group_index": torch.empty((group_count,), dtype=torch.uint32, device=device),
        "group_value": torch.empty((group_count,), dtype=torch.float64, device=device),
    }


@dataclass
class V4ClosestHitGroupedArgmin3DDeviceArraySession:
    """Prepared V4 ray/triangle closest-hit grouped-argmin over device arrays."""

    prepared_scene: Any
    ray_batch: Any
    grouped_inputs: Any
    partner: str
    group_count: int

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self.group_count = int(self.group_count)
        if self.group_count < 0:
            raise ValueError("group_count must be non-negative")
        self._closed = False
        self._output_handoff_cache_key = None
        self._output_handoff_cache = None

    @property
    def claim_boundary(self) -> dict[str, object]:
        return closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4ClosestHitGroupedArgmin3DDeviceArraySession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        for handle in (self.grouped_inputs, self.ray_batch, self.prepared_scene):
            close = getattr(handle, "close", None)
            if callable(close):
                close()
        self._closed = True

    def allocate_outputs(self) -> dict[str, object]:
        device = None
        owner = getattr(self.ray_batch, "_packed_rays_owner", None)
        rays = owner.get("rays") if isinstance(owner, dict) else None
        ids = rays.get("ids") if isinstance(rays, dict) else None
        column_owner = getattr(ids, "owner", None)
        if column_owner is not None and hasattr(column_owner, "device"):
            device = column_owner.device
        return allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4(
            self.group_count,
            partner=self.partner,
            device=device,
        )

    def _prevalidated_output_handoffs(self, output_columns: dict[str, object]) -> dict[str, object]:
        key = (
            id(output_columns.get("group_has_value")),
            id(output_columns.get("group_index")),
            id(output_columns.get("group_value")),
        )
        if key == self._output_handoff_cache_key and self._output_handoff_cache is not None:
            return self._output_handoff_cache
        handoffs = _validate_closest_hit_grouped_argmin_device_output_columns(
            output_columns,
            group_count=self.group_count,
        )
        self._output_handoff_cache_key = key
        self._output_handoff_cache = handoffs
        return handoffs

    def run(
        self,
        *,
        output_columns: dict[str, object] | None = None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 closest-hit grouped-argmin device-array session is closed")
        if output_columns is None:
            output_columns = self.allocate_outputs()
        output_handoffs = self._prevalidated_output_handoffs(output_columns)
        native_result = self.prepared_scene.ray_closest_hit_prepared_grouped_argmin_device_outputs(
            self.ray_batch,
            self.grouped_inputs,
            output_columns,
            prevalidated_handoffs=output_handoffs,
        )
        metadata = {
            **native_result["metadata"],
            **self.claim_boundary,
            "adapter": V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE,
            "generic_primitive": "CLOSEST_HIT_GROUPED_ARGMIN_3D",
            "input_contract": f"caller_supplied_{self.partner}_device_ray_triangle_and_group_columns",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_grouped_argmin_columns",
            "native_prepared_route": "ray_closest_hit_prepared_grouped_argmin_device_outputs",
            "native_direct_device_output_columns": True,
            "grouped_result_device_to_device_export": False,
            "grouped_results_downloaded_to_host_in_hot_path": False,
        }
        if return_metadata:
            return {"columns": output_columns, "metadata": metadata}
        return output_columns


def prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(
    triangle_columns: dict[str, object],
    ray_columns: dict[str, object],
    *,
    per_ray_group_ids,
    candidate_values,
    candidate_indices,
    group_count: int,
    partner: str = "torch",
) -> V4ClosestHitGroupedArgmin3DDeviceArraySession:
    """Prepare the V4 closest-hit grouped-argmin surface over device arrays."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
    prepared_scene = prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns)
    try:
        ray_batch = prepared_scene.prepare_ray_batch_device_columns(ray_columns)
        grouped_inputs = prepared_scene.prepare_closest_hit_device_per_ray_grouped_argmin_inputs(
            per_ray_group_ids=per_ray_group_ids,
            candidate_values=candidate_values,
            candidate_indices=candidate_indices,
            group_count=int(group_count),
        )
    except Exception:
        prepared_scene.close()
        raise
    return V4ClosestHitGroupedArgmin3DDeviceArraySession(
        prepared_scene=prepared_scene,
        ray_batch=ray_batch,
        grouped_inputs=grouped_inputs,
        partner=partner,
        group_count=int(group_count),
    )
