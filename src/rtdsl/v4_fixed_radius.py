from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .partner_adapters import allocate_fixed_radius_count_threshold_2d_partner_device_output_columns
from .partner_adapters import fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns
from .partner_adapters import prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene


V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE = "v4_fixed_radius_count_threshold_2d_device_arrays"
V4_FIXED_RADIUS_MEASURED_PARTNERS = ("torch",)
V4_FIXED_RADIUS_ALLOWED_PARTNERS = V4_FIXED_RADIUS_MEASURED_PARTNERS


def _require_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_FIXED_RADIUS_ALLOWED_PARTNERS:
        allowed = ", ".join(V4_FIXED_RADIUS_ALLOWED_PARTNERS)
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


def fixed_radius_count_threshold_2d_device_array_claim_boundary_v4(partner: str = "torch") -> dict[str, object]:
    """Return the V4 claim boundary for the fixed-radius device-array surface."""

    partner = _require_partner(partner)
    measured = partner in V4_FIXED_RADIUS_MEASURED_PARTNERS
    return {
        "v4_api_surface": V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE,
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": V4_FIXED_RADIUS_MEASURED_PARTNERS,
        "partner_support_declared_unmeasured": (),
        "partner_claim_status": "measured_on_v4_section8_pod" if measured else "declared_unmeasured_not_performance_ready",
        "python_point_object_boundary_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "second_primitive_work_authorized": False,
    }


def allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4(
    query_count: int,
    *,
    partner: str = "torch",
) -> dict[str, object]:
    """Allocate reusable device output columns for the V4 fixed-radius surface."""

    partner = _require_partner(partner)
    return allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
        query_count,
        partner=partner,
    )


@dataclass
class V4FixedRadiusCountThreshold2DDeviceArraySession:
    """Prepared V4 fixed-radius count-threshold session over caller device arrays."""

    prepared: Any
    partner: str
    max_radius: float

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self.max_radius = float(self.max_radius)
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return fixed_radius_count_threshold_2d_device_array_claim_boundary_v4(self.partner)

    def __enter__(self) -> "V4FixedRadiusCountThreshold2DDeviceArraySession":
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

    def allocate_outputs(self, query_count: int) -> dict[str, object]:
        return allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4(
            query_count,
            partner=self.partner,
        )

    def run(
        self,
        query_point_columns: dict[str, object],
        *,
        radius: float,
        threshold: int = 1,
        output_columns: dict[str, object] | None = None,
        return_metadata: bool = True,
    ):
        if self._closed:
            raise RuntimeError("V4 fixed-radius device-array session is closed")
        native_result = fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
            self.prepared,
            query_point_columns,
            radius=radius,
            threshold=threshold,
            partner=self.partner,
            output_columns=output_columns,
            return_metadata=True,
        )
        metadata = {
            **native_result["metadata"],
            **self.claim_boundary,
            "adapter": "v4_fixed_radius_count_threshold_2d_device_arrays",
            "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "input_contract": f"caller_supplied_{self.partner}_device_point_columns",
            "output_contract": f"caller_supplied_or_allocated_{self.partner}_device_output_columns",
            "native_prepared_route": "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
        }
        metadata = _clear_public_true_zero_copy_authorizations(metadata)
        if return_metadata:
            return {"columns": native_result["columns"], "metadata": metadata}
        return native_result["columns"]


def prepare_fixed_radius_count_threshold_2d_device_arrays_v4(
    search_point_columns: dict[str, object],
    *,
    max_radius: float,
    partner: str = "torch",
) -> V4FixedRadiusCountThreshold2DDeviceArraySession:
    """Prepare the V4 fixed-radius count-threshold surface over device arrays."""

    partner = _require_partner(partner)
    prepared = prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
        search_point_columns,
        max_radius=max_radius,
        partner=partner,
    )
    return V4FixedRadiusCountThreshold2DDeviceArraySession(
        prepared=prepared,
        partner=partner,
        max_radius=max_radius,
    )
