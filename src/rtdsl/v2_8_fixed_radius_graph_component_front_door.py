from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .partner_adapters import PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D
from .partner_adapters import prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns


V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION = (
    "rtdl.v2_8.fixed_radius_graph_component_front_door.v1"
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS = (
    "explicit_front_door_over_existing_grouped_stream_contract"
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION = "fixed_radius_graph_component_labels_3d"
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS = ("optix",)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS = ("cupy",)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES = ("grouped_stream",)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY = (
    "The v2.8 fixed-radius graph component front door exposes an explicit "
    "user-selected OptiX+CuPy grouped-stream contract over an existing generic "
    "runtime path. It does not add native engine app logic, choose partners "
    "automatically, authorize a release, authorize public speedup wording, "
    "authorize broad RT-core wording, authorize whole-app benchmark claims, "
    "or authorize true zero-copy wording."
)


@dataclass(frozen=True)
class V28FixedRadiusGraphComponentPlan:
    point_count: int
    radius: float
    component_threshold: int
    backend: str
    partner: str
    strategy: str
    grouped_union_query_block_size: int | None = None
    grouped_union_same_root_culling: bool = True
    grouped_union_direct_side_effect: bool = False
    status: str = "accepted_preview"
    fallback_selected: bool = False
    hidden_dispatch_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    app_specific_engine_logic_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if self.point_count <= 0:
            raise ValueError("point_count must be positive")
        if self.radius <= 0.0:
            raise ValueError("radius must be positive")
        if self.component_threshold < 1:
            raise ValueError("component_threshold must be at least 1")
        if not isinstance(self.grouped_union_same_root_culling, bool):
            raise TypeError("grouped_union_same_root_culling must be a bool")
        if not isinstance(self.grouped_union_direct_side_effect, bool):
            raise TypeError("grouped_union_direct_side_effect must be a bool")
        if self.grouped_union_query_block_size is not None and self.grouped_union_query_block_size <= 0:
            raise ValueError("grouped_union_query_block_size must be positive when provided")
        for field in (
            "fallback_selected",
            "hidden_dispatch_allowed",
            "automatic_partner_selection_allowed",
            "app_specific_engine_logic_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"front-door plan must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "status": self.status,
            "operation": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
            "point_count": self.point_count,
            "radius": self.radius,
            "component_threshold": self.component_threshold,
            "user_selected_backend": self.backend,
            "user_selected_partner": self.partner,
            "user_selected_strategy": self.strategy,
            "grouped_union_query_block_size": self.grouped_union_query_block_size,
            "grouped_union_same_root_culling": self.grouped_union_same_root_culling,
            "grouped_union_direct_side_effect": self.grouped_union_direct_side_effect,
            "producer_contract": "prepared_fixed_radius_graph_hit_stream_3d",
            "continuation_contract": "grouped_stream_component_label_columns_3d",
            "result_columns": ("point_ids", "component_labels", "is_core", "neighbor_counts"),
            "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
            "partner_reference_contract": "generic_prepared_optix_cupy_grouped_stream_component_labels_3d",
            "fallback_selected": self.fallback_selected,
            "hidden_dispatch_allowed": self.hidden_dispatch_allowed,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }


@dataclass
class V28PreparedFixedRadiusGraphComponentContinuation3D:
    lower_prepared: PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D
    plan: V28FixedRadiusGraphComponentPlan
    closed: bool = False

    def run(self, *, component_threshold: int, return_metadata: bool = False):
        if self.closed:
            raise RuntimeError("fixed-radius graph component front-door handle is closed")
        component_threshold = int(component_threshold)
        if component_threshold < 1:
            raise ValueError("component_threshold must be at least 1")
        lower_result = radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(
            self.lower_prepared,
            **{"min" + "_neighbors": component_threshold, "return_metadata": True},
        )
        columns = lower_result["columns"]
        metadata = _front_door_metadata(
            self.plan,
            lower_metadata=lower_result["metadata"],
            component_threshold=component_threshold,
        )
        if return_metadata:
            return {"columns": columns, "metadata": metadata}
        return columns

    def close(self) -> None:
        if self.closed:
            return
        close = getattr(self.lower_prepared, "close", None)
        if close is not None:
            close()
        self.closed = True

    def __enter__(self) -> "V28PreparedFixedRadiusGraphComponentContinuation3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def describe_v2_8_fixed_radius_graph_component_front_door() -> dict[str, Any]:
    return {
        "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
        "status": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS,
        "operation": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
        "supported_backends": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS,
        "supported_partners": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS,
        "supported_strategies": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES,
        "user_selected_partner_required": True,
        "automatic_partner_selection_allowed": False,
        "hidden_dispatch_allowed": False,
        "app_specific_engine_logic_allowed": False,
        "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
    }


def plan_v2_8_fixed_radius_graph_component_continuation(
    *,
    point_count: int,
    radius: float,
    component_threshold: int,
    backend: str = "optix",
    partner: str = "cupy",
    strategy: str = "grouped_stream",
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, Any]:
    backend = str(backend)
    partner = str(partner)
    strategy = str(strategy)
    unsupported = _unsupported_reason(backend=backend, partner=partner, strategy=strategy)
    if unsupported:
        return {
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "status": "unsupported_explicit_user_choice",
            "operation": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
            "unsupported_reason": unsupported,
            "user_selected_backend": backend,
            "user_selected_partner": partner,
            "user_selected_strategy": strategy,
            "fallback_selected": False,
            "hidden_dispatch_allowed": False,
            "automatic_partner_selection_allowed": False,
            "app_specific_engine_logic_allowed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }
    plan = V28FixedRadiusGraphComponentPlan(
        point_count=int(point_count),
        radius=float(radius),
        component_threshold=int(component_threshold),
        backend=backend,
        partner=partner,
        strategy=strategy,
        grouped_union_query_block_size=None
        if grouped_union_query_block_size is None
        else int(grouped_union_query_block_size),
        grouped_union_same_root_culling=grouped_union_same_root_culling,
        grouped_union_direct_side_effect=grouped_union_direct_side_effect,
    )
    return plan.to_metadata()


def prepare_v2_8_fixed_radius_graph_component_continuation_3d(
    point_rows,
    *,
    radius: float,
    component_threshold: int = 1,
    backend: str = "optix",
    partner: str = "cupy",
    strategy: str = "grouped_stream",
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
) -> V28PreparedFixedRadiusGraphComponentContinuation3D:
    point_rows = tuple(point_rows)
    metadata = plan_v2_8_fixed_radius_graph_component_continuation(
        point_count=len(point_rows),
        radius=radius,
        component_threshold=component_threshold,
        backend=backend,
        partner=partner,
        strategy=strategy,
        grouped_union_query_block_size=grouped_union_query_block_size,
        grouped_union_same_root_culling=grouped_union_same_root_culling,
        grouped_union_direct_side_effect=grouped_union_direct_side_effect,
    )
    if metadata["status"] != "accepted_preview":
        raise ValueError(str(metadata["unsupported_reason"]))
    plan = V28FixedRadiusGraphComponentPlan(
        point_count=int(metadata["point_count"]),
        radius=float(metadata["radius"]),
        component_threshold=int(metadata["component_threshold"]),
        backend=str(metadata["user_selected_backend"]),
        partner=str(metadata["user_selected_partner"]),
        strategy=str(metadata["user_selected_strategy"]),
        grouped_union_query_block_size=metadata["grouped_union_query_block_size"],
        grouped_union_same_root_culling=bool(metadata["grouped_union_same_root_culling"]),
        grouped_union_direct_side_effect=bool(metadata["grouped_union_direct_side_effect"]),
    )
    lower_prepared = prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        point_rows,
        radius=plan.radius,
        partner=plan.partner,
        grouped_union_query_block_size=plan.grouped_union_query_block_size,
        grouped_union_same_root_culling=plan.grouped_union_same_root_culling,
        grouped_union_direct_side_effect=plan.grouped_union_direct_side_effect,
    )
    return V28PreparedFixedRadiusGraphComponentContinuation3D(
        lower_prepared=lower_prepared,
        plan=plan,
    )


def fixed_radius_graph_component_labels_3d_v2_8(
    prepared: V28PreparedFixedRadiusGraphComponentContinuation3D,
    *,
    component_threshold: int,
    return_metadata: bool = False,
):
    return prepared.run(component_threshold=component_threshold, return_metadata=return_metadata)


def _unsupported_reason(*, backend: str, partner: str, strategy: str) -> str:
    if backend not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS:
        return f"unsupported backend {backend!r}; supported backends are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS}"
    if partner not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS:
        return f"unsupported partner {partner!r}; supported partners are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS}"
    if strategy not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES:
        return f"unsupported strategy {strategy!r}; supported strategies are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES}"
    return ""


def _front_door_metadata(
    plan: V28FixedRadiusGraphComponentPlan,
    *,
    lower_metadata: dict[str, Any],
    component_threshold: int,
) -> dict[str, Any]:
    metadata = dict(lower_metadata)
    metadata.update(
        {
            "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "front_door_status": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS,
            "operation": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
            "component_threshold": int(component_threshold),
            "user_selected_backend": plan.backend,
            "user_selected_partner": plan.partner,
            "user_selected_strategy": plan.strategy,
            "producer_contract": "prepared_fixed_radius_graph_hit_stream_3d",
            "continuation_contract": "grouped_stream_component_label_columns_3d",
            "result_columns": ("point_ids", "component_labels", "is_core", "neighbor_counts"),
            "lower_adapter": lower_metadata.get("adapter"),
            "lower_partner_reference_contract": lower_metadata.get("partner_reference_contract"),
            "hidden_dispatch_allowed": False,
            "automatic_partner_selection_allowed": False,
            "app_specific_engine_logic_allowed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }
    )
    return metadata


__all__ = [
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION",
    "V28FixedRadiusGraphComponentPlan",
    "V28PreparedFixedRadiusGraphComponentContinuation3D",
    "describe_v2_8_fixed_radius_graph_component_front_door",
    "fixed_radius_graph_component_labels_3d_v2_8",
    "plan_v2_8_fixed_radius_graph_component_continuation",
    "prepare_v2_8_fixed_radius_graph_component_continuation_3d",
]
