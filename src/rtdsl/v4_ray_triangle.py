from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .optix_runtime import _validate_closest_hit_grouped_argmin_device_output_columns
from .optix_runtime import _validate_primitive_grouped_i64_reduction_device_output_columns
from .optix_runtime import prepare_optix_primitive_grouped_i64_payload_3d
from .optix_runtime import prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene
from .optix_runtime import prepare_optix_static_triangle_scene_3d_device_triangles


V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE = (
    "v4_closest_hit_grouped_argmin_3d_device_arrays"
)
V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE = "v4_ray_triangle_any_hit_flags_2d_device_arrays"
V4_PRIMITIVE_GROUPED_I64_REDUCTION_DEVICE_ARRAY_SURFACE = (
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays"
)
V4_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_DEVICE_ARRAY_SURFACE = (
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"
)
V4_RAY_TRIANGLE_MEASURED_PARTNERS = ("torch",)
V4_RAY_TRIANGLE_DECLARED_UNMEASURED_PARTNERS = ("cupy",)
V4_RAY_TRIANGLE_ALLOWED_PARTNERS = (
    *V4_RAY_TRIANGLE_MEASURED_PARTNERS,
    *V4_RAY_TRIANGLE_DECLARED_UNMEASURED_PARTNERS,
)
V4_RAY_TRIANGLE_POD_CANDIDATE_PARTNERS = ("torch",)


def _require_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_RAY_TRIANGLE_ALLOWED_PARTNERS:
        allowed = ", ".join(V4_RAY_TRIANGLE_ALLOWED_PARTNERS)
        raise ValueError(f"partner must be one of: {allowed}")
    return partner


def _clear_public_true_zero_copy_authorizations(value):
    if isinstance(value, dict):
        cleared = {}
        for key, item in value.items():
            if key == "true_zero_copy" or key.endswith("true_zero_copy_authorized"):
                cleared[key] = False
            else:
                cleared[key] = _clear_public_true_zero_copy_authorizations(item)
        return cleared
    if isinstance(value, list):
        return [_clear_public_true_zero_copy_authorizations(item) for item in value]
    return value


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


def ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4(
    partner: str = "torch",
) -> dict[str, object]:
    """Return the V4 claim boundary for the ray/triangle any-hit flag surface."""

    partner = _require_partner(partner)
    measured = partner in V4_RAY_TRIANGLE_MEASURED_PARTNERS
    return {
        "v4_api_surface": V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE,
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


def primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4(
    partner: str = "torch",
) -> dict[str, object]:
    """Return the V4 claim boundary for the primitive grouped-i64 reduction surface."""

    partner = _require_partner(partner)
    measured = partner in V4_RAY_TRIANGLE_MEASURED_PARTNERS
    return {
        "v4_api_surface": V4_PRIMITIVE_GROUPED_I64_REDUCTION_DEVICE_ARRAY_SURFACE,
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": V4_RAY_TRIANGLE_MEASURED_PARTNERS,
        "partner_support_declared_unmeasured": tuple(
            item
            for item in V4_RAY_TRIANGLE_ALLOWED_PARTNERS
            if item not in V4_RAY_TRIANGLE_MEASURED_PARTNERS
        ),
        "partner_claim_status": (
            "measured_on_v4_goal4617_pod_optix8"
            if measured
            else "declared_unmeasured_not_performance_ready"
        ),
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "optix_9_1_validated": False,
        "python_ray_object_boundary_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "primitive_payload_prepare_is_hot_path": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
    }


def ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4(
    partner: str = "torch",
) -> dict[str, object]:
    """Return the V4 claim boundary for the any-hit weighted-sum surface."""

    partner = _require_partner(partner)
    measured = partner == "torch"
    return {
        "v4_api_surface": V4_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_DEVICE_ARRAY_SURFACE,
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": ("torch",),
        "pod_candidate_partners": (),
        "partner_support_declared_unmeasured": V4_RAY_TRIANGLE_DECLARED_UNMEASURED_PARTNERS,
        "partner_claim_status": (
            "measured_on_v4_goal4633_pod_optix8"
            if measured
            else "declared_unmeasured_not_performance_ready"
        ),
        "surface_status": "tier2_measured_v4_0_0_release_surface",
        "validated_optix_abi": "8.0" if measured else None,
        "validated_gpu_family": "RTX A5000 / Ampere" if measured else None,
        "validated_driver": "570.195.03" if measured else None,
        "validated_partner_scope": "torch 2.8.0+cu128" if measured else None,
        "optix_9_1_validated": False,
        "comparison_class": "same_operator_comparable_route",
        "comparable_route_ratio_range": "1.2011x-2.1459x" if measured else None,
        "comparable_route_geomean": 1.5457333064727565 if measured else None,
        "performance_caveat": (
            "largest_shape_barely_clears_1_20x_floor_not_large_speedup"
            if measured
            else None
        ),
        "scene_preparation_ownership": (
            "caller_initiated_v4_prepare_static_triangle_scene_from_device_triangle_columns"
        ),
        "scene_data_residency": "rtdl_owned_prepared_optix_scene_from_caller_device_triangle_columns",
        "output_scalar_primary_allocation": "rtdl_allocated_uint64_device_scalar",
        "output_scalar_caller_override_supported": True,
        "python_ray_object_boundary_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "host_scalar_read_before_consumer": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "true_zero_copy_authorized": False,
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


def allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4(
    ray_count: int,
    *,
    partner: str = "torch",
    device: object | None = None,
):
    """Allocate reusable device flag output columns for the V4 any-hit surface."""

    partner = _require_partner(partner)
    ray_count = int(ray_count)
    if ray_count < 0:
        raise ValueError("ray_count must be non-negative")
    if partner != "torch":
        raise RuntimeError("CuPy output allocation is declared but unmeasured for this V4 surface")
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch is required for the measured V4 any-hit flag surface") from exc
    if device is None:
        device = torch.device("cuda")
    return torch.zeros((ray_count,), dtype=torch.uint32, device=device)


def allocate_primitive_grouped_i64_reduction_3d_device_array_outputs_v4(
    group_count: int,
    *,
    partner: str = "torch",
    device: object | None = None,
) -> dict[str, object]:
    """Allocate reusable device output columns for the V4 grouped-i64 surface."""

    partner = _require_partner(partner)
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    if partner != "torch":
        raise RuntimeError("CuPy output allocation is declared but unmeasured for this V4 surface")
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch is required for the V4 grouped-i64 reduction surface") from exc
    if device is None:
        device = torch.device("cuda")
    return {
        "group_counts": torch.zeros((group_count,), dtype=torch.uint64, device=device),
        "group_sums": torch.zeros((group_count,), dtype=torch.uint64, device=device),
        "group_mins": torch.empty((group_count,), dtype=torch.uint64, device=device),
        "group_maxs": torch.zeros((group_count,), dtype=torch.uint64, device=device),
    }


def allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4(
    *,
    partner: str = "torch",
    device: object | None = None,
):
    """Allocate the primary V4 measured device scalar output for weighted sums."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy output allocation is declared but unmeasured for this V4 surface")
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch is required for the V4 weighted-sum measured surface") from exc
    if device is None:
        device = torch.device("cuda")
    return torch.zeros((1,), dtype=torch.uint64, device=device)


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
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
        if return_metadata:
            return {"columns": output_columns, "metadata": metadata}
        return output_columns


@dataclass
class V4RayTriangleAnyHitWeightedSum3DDeviceArraySession:
    """Prepared V4 measured ray/triangle any-hit weighted sum over device arrays."""

    prepared_scene: Any
    ray_batch: Any
    ray_weights: Any
    partner: str

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self._closed = False
        self._executor_cache_key = None
        self._executor_cache = None

    @property
    def claim_boundary(self) -> dict[str, object]:
        return ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4RayTriangleAnyHitWeightedSum3DDeviceArraySession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        handles = (self._executor_cache, self.ray_batch, self.prepared_scene)
        for handle in handles:
            close = getattr(handle, "close", None)
            if callable(close):
                close()
        self._executor_cache = None
        self._executor_cache_key = None
        self._closed = True

    def allocate_output_scalar(self):
        device = None
        owner = getattr(self.ray_batch, "_packed_rays_owner", None)
        rays = owner.get("rays") if isinstance(owner, dict) else None
        ids = rays.get("ids") if isinstance(rays, dict) else None
        column_owner = getattr(ids, "owner", None)
        if column_owner is not None and hasattr(column_owner, "device"):
            device = column_owner.device
        return allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4(
            partner=self.partner,
            device=device,
        )

    def _default_cuda_stream(self):
        try:
            import torch
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Torch is required to provide the default CUDA stream") from exc
        return torch.cuda.Stream()

    def _executor_for_output(self, output_scalar):
        key = (id(output_scalar), id(self.ray_weights))
        if key == self._executor_cache_key and self._executor_cache is not None:
            return self._executor_cache
        if self._executor_cache is not None:
            close = getattr(self._executor_cache, "close", None)
            if callable(close):
                close()
        self._executor_cache = self.prepared_scene.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor(
            self.ray_batch,
            self.ray_weights,
            output_scalar,
        )
        self._executor_cache_key = key
        return self._executor_cache

    def run(
        self,
        *,
        output_scalar=None,
        cuda_stream=None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 ray/triangle any-hit weighted-sum session is closed")
        if self.partner != "torch":
            raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
        output_scalar_allocation = "caller_supplied_override"
        if output_scalar is None:
            output_scalar = self.allocate_output_scalar()
            output_scalar_allocation = "rtdl_allocated_default"
        if cuda_stream is None:
            cuda_stream = self._default_cuda_stream()
        executor = self._executor_for_output(output_scalar)
        native_metadata = executor.launch(cuda_stream)
        executor_metadata = {}
        to_metadata = getattr(executor, "to_metadata", None)
        if callable(to_metadata):
            executor_metadata = dict(to_metadata())
        metadata = {
            **executor_metadata,
            **native_metadata,
            **self.claim_boundary,
            "adapter": V4_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_DEVICE_ARRAY_SURFACE,
            "generic_primitive": "RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D",
            "input_contract": f"caller_supplied_{self.partner}_device_ray_triangle_and_weight_columns",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_uint64_weighted_sum_scalar",
            "native_prepared_route": "prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor",
            "native_direct_device_output_scalar": True,
            "device_output_used": True,
            "output_scalar_allocation": output_scalar_allocation,
            "weighted_sum_downloaded_to_host_in_hot_path": False,
            "host_materialization_in_hot_path": False,
            "host_scalar_read_before_consumer": False,
        }
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
        if return_metadata:
            return {"columns": {"weighted_hit_sum": output_scalar}, "metadata": metadata}
        return {"weighted_hit_sum": output_scalar}


@dataclass
class V4RayTriangleAnyHitFlags2DDeviceArraySession:
    """Prepared V4 2-D ray/triangle any-hit flags over caller device arrays."""

    prepared_scene: Any
    partner: str

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4RayTriangleAnyHitFlags2DDeviceArraySession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self.prepared_scene, "close", None)
        if callable(close):
            close()
        self._closed = True

    def allocate_outputs(self, ray_count: int, *, device: object | None = None):
        return allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4(
            ray_count,
            partner=self.partner,
            device=device,
        )

    def run(
        self,
        ray_columns: dict[str, object],
        *,
        output_flags=None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 ray/triangle any-hit flag device-array session is closed")
        if self.partner != "torch":
            raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
        if "ids" not in ray_columns:
            raise ValueError("ray_columns must include 'ids'")
        if output_flags is None:
            device = None
            ids = ray_columns["ids"]
            if hasattr(ids, "device"):
                device = ids.device
            output_flags = self.allocate_outputs(int(ray_columns["ids"].shape[0]), device=device)
        native_result = self.prepared_scene.write_device_any_hit_flags(ray_columns, output_flags)
        metadata = {
            **native_result["metadata"],
            **self.claim_boundary,
            "adapter": V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE,
            "generic_primitive": "RAY_TRIANGLE_ANY_HIT_FLAGS_2D",
            "input_contract": f"caller_supplied_{self.partner}_device_ray_triangle_columns",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_any_hit_flag_column",
            "native_prepared_route": "write_device_any_hit_flags",
            "native_direct_device_output_columns": True,
            "ray_results_downloaded_to_host_in_hot_path": False,
        }
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
        if return_metadata:
            return {"columns": {"any_hit_flags": output_flags}, "metadata": metadata}
        return {"any_hit_flags": output_flags}


@dataclass
class V4PrimitiveGroupedI64Reduction3DDeviceArraySession:
    """Prepared V4 ray/triangle primitive grouped-i64 reduction over device arrays."""

    prepared_scene: Any
    ray_batch: Any
    primitive_payload: Any
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
        return primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4PrimitiveGroupedI64Reduction3DDeviceArraySession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        for handle in (self.primitive_payload, self.ray_batch, self.prepared_scene):
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
        return allocate_primitive_grouped_i64_reduction_3d_device_array_outputs_v4(
            self.group_count,
            partner=self.partner,
            device=device,
        )

    def _prevalidated_output_handoffs(self, output_columns: dict[str, object]) -> dict[str, object]:
        key = (
            id(output_columns.get("group_counts")),
            id(output_columns.get("group_sums")),
            id(output_columns.get("group_mins")),
            id(output_columns.get("group_maxs")),
        )
        if key == self._output_handoff_cache_key and self._output_handoff_cache is not None:
            return self._output_handoff_cache
        handoffs = _validate_primitive_grouped_i64_reduction_device_output_columns(
            output_columns,
            group_count=self.group_count,
        )
        self._output_handoff_cache_key = key
        self._output_handoff_cache = handoffs
        return handoffs

    def run(
        self,
        *,
        reduction: str = "sum",
        output_columns: dict[str, object] | None = None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 primitive grouped-i64 reduction device-array session is closed")
        if output_columns is None:
            output_columns = self.allocate_outputs()
        output_handoffs = self._prevalidated_output_handoffs(output_columns)
        native_result = self.prepared_scene.ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs(
            self.ray_batch,
            self.primitive_payload,
            output_columns,
            reduction=reduction,
            prevalidated_handoffs=output_handoffs,
        )
        metadata = {
            **native_result["metadata"],
            **self.claim_boundary,
            "adapter": V4_PRIMITIVE_GROUPED_I64_REDUCTION_DEVICE_ARRAY_SURFACE,
            "generic_primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "input_contract": f"caller_supplied_{self.partner}_device_ray_triangle_columns_prepared_primitive_payload",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_grouped_i64_columns",
            "native_prepared_route": "ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs",
            "native_direct_device_output_columns": True,
            "group_rows_downloaded_to_host_in_hot_path": False,
        }
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
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


def prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(
    triangle_columns: dict[str, object],
    triangle_aabbs,
    *,
    partner: str = "torch",
) -> V4RayTriangleAnyHitFlags2DDeviceArraySession:
    """Prepare the V4 ray/triangle any-hit flag surface over device arrays."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
    prepared_scene = prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        triangle_columns,
        triangle_aabbs,
    )
    return V4RayTriangleAnyHitFlags2DDeviceArraySession(
        prepared_scene=prepared_scene,
        partner=partner,
    )


def prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(
    triangle_columns: dict[str, object],
    ray_columns: dict[str, object],
    ray_weights,
    *,
    partner: str = "torch",
) -> V4RayTriangleAnyHitWeightedSum3DDeviceArraySession:
    """Prepare the V4 measured any-hit weighted-sum surface over device arrays."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
    prepared_scene = prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns)
    try:
        ray_batch = prepared_scene.prepare_ray_batch_device_columns(ray_columns)
    except Exception:
        prepared_scene.close()
        raise
    return V4RayTriangleAnyHitWeightedSum3DDeviceArraySession(
        prepared_scene=prepared_scene,
        ray_batch=ray_batch,
        ray_weights=ray_weights,
        partner=partner,
    )


def prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(
    triangle_columns: dict[str, object],
    ray_columns: dict[str, object],
    *,
    primitive_group_ids,
    primitive_values,
    group_count: int,
    partner: str = "torch",
) -> V4PrimitiveGroupedI64Reduction3DDeviceArraySession:
    """Prepare the V4 primitive grouped-i64 reduction surface over device arrays."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy is declared but unmeasured for this V4 surface")
    prepared_scene = prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns)
    try:
        ray_batch = prepared_scene.prepare_ray_batch_device_columns(ray_columns)
        primitive_payload = prepare_optix_primitive_grouped_i64_payload_3d(
            primitive_group_ids,
            primitive_values,
            primitive_count=int(prepared_scene.triangle_count),
            group_count=int(group_count),
        )
    except Exception:
        prepared_scene.close()
        raise
    return V4PrimitiveGroupedI64Reduction3DDeviceArraySession(
        prepared_scene=prepared_scene,
        ray_batch=ray_batch,
        primitive_payload=primitive_payload,
        partner=partner,
        group_count=int(group_count),
    )
