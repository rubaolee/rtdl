from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .optix_runtime import prepare_optix_point_group_nearest_witness_2d


V4_POINT_GROUP_NEAREST_WITNESS_DEVICE_ARRAY_SURFACE = (
    "v4_point_group_nearest_witness_2d_device_arrays"
)
V4_POINT_GROUP_ALLOWED_PARTNERS = ("torch", "cupy")
V4_POINT_GROUP_MEASURED_PARTNERS = ("torch",)
V4_POINT_GROUP_DECLARED_UNMEASURED_PARTNERS = ("cupy",)


def _require_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_POINT_GROUP_ALLOWED_PARTNERS:
        allowed = ", ".join(V4_POINT_GROUP_ALLOWED_PARTNERS)
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


def point_group_nearest_witness_2d_device_array_claim_boundary_v4(
    partner: str = "torch",
) -> dict[str, object]:
    """Return the V4 claim boundary for the point-group nearest-witness surface."""

    partner = _require_partner(partner)
    measured = partner in V4_POINT_GROUP_MEASURED_PARTNERS
    return {
        "v4_api_surface": V4_POINT_GROUP_NEAREST_WITNESS_DEVICE_ARRAY_SURFACE,
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": V4_POINT_GROUP_MEASURED_PARTNERS,
        "partner_support_declared_unmeasured": V4_POINT_GROUP_DECLARED_UNMEASURED_PARTNERS,
        "partner_claim_status": (
            "measured_on_v4_goal4618_pod_optix8"
            if measured
            else "declared_unmeasured_not_performance_ready"
        ),
        "generic_primitive": "POINT_GROUP_NEAREST_WITNESS_2D",
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "distance_precision": "float32_computed_float64_output",
        "optix_9_1_validated": False,
        "native_prepared_search_groups_owned_by_rtdl": True,
        "query_point_columns_partner_owned": True,
        "output_columns_partner_owned": True,
        "python_point_object_boundary_in_hot_path": False,
        "host_query_upload_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "true_zero_copy_authorized": False,
    }


def allocate_point_group_nearest_witness_2d_device_array_outputs_v4(
    query_count: int,
    *,
    partner: str = "torch",
    device: object | None = None,
) -> dict[str, object]:
    """Allocate Torch CUDA output columns for the nearest-witness surface."""

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy output allocation is declared but unmeasured for this V4 candidate")
    count = int(query_count)
    if count < 0:
        raise ValueError("query_count must be non-negative")
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch is required for the V4 point-group nearest-witness surface") from exc
    if device is None:
        device = torch.device("cuda")
    return {
        "query_ids": torch.empty((count,), dtype=torch.uint32, device=device),
        "neighbor_ids": torch.empty((count,), dtype=torch.uint32, device=device),
        "distances": torch.empty((count,), dtype=torch.float64, device=device),
    }


def _query_count_from_columns(query_point_columns: dict[str, object]) -> int:
    ids = query_point_columns.get("ids")
    if ids is None:
        raise ValueError("query_point_columns must include ids")
    try:
        return int(ids.shape[0])
    except Exception as exc:
        raise ValueError("query_point_columns['ids'] must expose a one-dimensional shape") from exc


def _device_from_query_columns(query_point_columns: dict[str, object]) -> object | None:
    ids = query_point_columns.get("ids")
    return getattr(ids, "device", None)


@dataclass
class V4PointGroupNearestWitness2DDeviceArraySession:
    """Prepared V4 point-group nearest-witness surface over device query columns."""

    prepared: Any
    partner: str
    max_radius: float

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self.max_radius = float(self.max_radius)
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return point_group_nearest_witness_2d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4PointGroupNearestWitness2DDeviceArraySession":
        enter = getattr(self.prepared, "__enter__", None)
        if callable(enter):
            enter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        exit_method = getattr(self.prepared, "__exit__", None)
        if callable(exit_method):
            exit_method(exc_type, exc, tb)
        else:
            self.close()
        self._closed = True

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self.prepared, "close", None)
        if callable(close):
            close()
        self._closed = True

    def allocate_outputs(self, query_point_columns: dict[str, object]) -> dict[str, object]:
        return allocate_point_group_nearest_witness_2d_device_array_outputs_v4(
            _query_count_from_columns(query_point_columns),
            partner=self.partner,
            device=_device_from_query_columns(query_point_columns),
        )

    def run(
        self,
        query_point_columns: dict[str, object],
        *,
        radius: float,
        output_columns: dict[str, object] | None = None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 point-group nearest-witness device-array session is closed")
        if output_columns is None:
            output_columns = self.allocate_outputs(query_point_columns)
        native_result = self.prepared.write_device_nearest_witness_columns_from_device_query_columns(
            query_point_columns,
            radius=radius,
            query_ids_out=output_columns["query_ids"],
            neighbor_ids_out=output_columns["neighbor_ids"],
            distances_out=output_columns["distances"],
        )
        metadata = {
            **native_result["metadata"],
            **self.claim_boundary,
            "adapter": V4_POINT_GROUP_NEAREST_WITNESS_DEVICE_ARRAY_SURFACE,
            "generic_primitive": "POINT_GROUP_NEAREST_WITNESS_2D",
            "input_contract": f"native_prepared_point_groups_plus_{self.partner}_device_query_columns",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_nearest_witness_columns",
            "native_prepared_route": "write_device_nearest_witness_columns_from_device_query_columns",
            "native_direct_device_output_columns": True,
            "host_query_upload_in_hot_path": False,
            "rows_materialized": False,
            "neighbor_rows_downloaded_to_host_in_hot_path": False,
        }
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
        if return_metadata:
            return {"columns": output_columns, "metadata": metadata}
        return output_columns


def prepare_point_group_nearest_witness_2d_device_arrays_v4(
    search_points,
    point_groups,
    *,
    max_radius: float,
    partner: str = "torch",
) -> V4PointGroupNearestWitness2DDeviceArraySession:
    """Prepare the point-group nearest-witness measured surface.

    Search points and group bounds are prepared into an RTDL-owned native scene.
    Query points and output witness columns are caller-owned device arrays in the
    hot run. This is intentionally narrower than a full input zero-copy claim.
    """

    partner = _require_partner(partner)
    if partner != "torch":
        raise RuntimeError("CuPy is declared but unmeasured for this V4 candidate")
    prepared = prepare_optix_point_group_nearest_witness_2d(
        search_points,
        point_groups,
        max_radius=max_radius,
    )
    return V4PointGroupNearestWitness2DDeviceArraySession(
        prepared=prepared,
        partner=partner,
        max_radius=max_radius,
    )
