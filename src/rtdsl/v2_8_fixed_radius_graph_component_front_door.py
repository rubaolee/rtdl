from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Any

from .partner_adapters import PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D
from .partner_adapters import PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D
from .partner_adapters import prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns
from .partner_adapters import radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
from .partner_adapters import radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns
from .v2_8_typed_result_stream import V28TypedResultStreamContract
from .v2_8_typed_result_stream import make_typed_result_stream_contract
from .v2_8_typed_result_stream import typed_result_column
from .v2_8_typed_result_stream import typed_result_status_columns
from .v2_8_typed_result_stream import validate_typed_result_stream_contract


V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION = (
    "rtdl.v2_8.fixed_radius_graph_component_front_door.v1"
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS = (
    "explicit_front_door_over_existing_grouped_stream_contract"
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION = "fixed_radius_graph_component_labels_3d"
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS = ("optix",)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS = ("cupy", "numba")
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES = ("grouped_stream",)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES = (
    "partition_convergence_hybrid",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES = (
    "direct_side_effect_default",
    "microcell_graph",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS = (
    "compressed_occupied_partition_key_structure",
    "bounded_near_partition_enumeration",
    "device_resident_partition_aabb_and_count_columns",
    "partition_point_ordinals_for_device_ambiguous_continuation",
    "no_dense_cell_pair_matrix",
    "safe_full_partition_pair_summary_without_pair_materialization",
    "ambiguous_boundary_pair_rt_traversal",
    "same_contract_parity_against_grouped_stream",
    "deterministic_component_root_policy",
    "readonly_root_find_default_preserved",
    "explicit_root_convergence_changes_only",
    "explicit_convergence_and_staleness_counters",
    "root_read_telemetry_reduction_required",
    "radius_x_0_125_partition_factor_evidence",
    "actual_benchmark_radius_pod_evidence",
    "compressed_partition_enumeration_accounting",
    "typed_partition_summary_stream_contract",
    "same_contract_validator_against_python_reference",
    "component_label_oracle_against_all_pairs",
    "complete_candidate_coverage_status_invariant",
    "edge_case_status_and_float_tolerance_tests",
    "cupy_preview_producer_same_contract_pod_execution",
    "cupy_device_bounded_pair_enumeration_same_contract_pod_execution",
    "cupy_device_ambiguous_partition_union_same_contract_pod_execution",
    "numba_preview_device_columns_same_contract_pod_execution",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PROMOTION_BLOCKERS = (
    "Goal4041_mixed_timing_not_universal_speed_win",
    "prepared_front_door_still_grouped_stream_only",
    "host_compact_label_materialization_breaks_resident_output",
    "separate_ambiguous_classifier_kernel_not_fused",
    "no_promoted_prepared_native_partition_handle",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS = (
    "Goal3999",
    "Goal4001",
    "Goal4002",
    "Goal4004",
    "Goal4007",
    "Goal4009",
    "Goal4011",
    "Goal4012",
    "Goal4014",
    "Goal4015",
    "Goal4016",
    "Goal4017",
    "Goal4019",
    "Goal4021",
    "Goal4023",
    "Goal4024",
    "Goal4027",
    "Goal4029",
    "Goal4032",
    "Goal4040",
    "Goal4041",
    "Goal4062",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE = MappingProxyType({
    "recommended_tested_cell_factor": "radius_x_0.125",
    "dense_cell_pair_matrix_allowed": False,
    "required_partition_pair_enumeration": (
        "compressed_occupied_partition_keys_with_bounded_near_offsets"
    ),
    "required_device_resident_columns": (
        "point_partition_ids",
        "partition_point_ordinals",
        "occupied_partition_keys",
        "partition_offsets",
        "partition_counts",
        "partition_aabbs",
    ),
    "required_status_counters": (
        "safe_full_partition_pairs",
        "safe_skip_partition_pairs",
        "ambiguous_partition_pairs",
        "root_find_invocations",
        "root_find_parent_link_steps",
        "component_root_convergence_iterations",
        "component_root_staleness_events",
    ),
    "default_root_policy": "readonly_root_find_until_explicit_convergence_policy_exists",
    "rejected_shortcuts": (
        "dense_all_cell_pair_matrix",
        "hidden_root_path_halving_inside_readonly_find",
        "app_specific_dbscan_or_clustering_native_abi",
        "incomplete_partition_pair_prefix_marked_complete",
    ),
    "required_validation_chain": (
        "typed_partition_summary_stream_contract",
        "same_contract_validator_against_python_reference",
        "component_label_oracle_against_all_pairs",
        "complete_candidate_coverage_status_invariant",
        "single_point_status_float_tolerance_edge_cases",
    ),
    "native_promotion_gate": (
        "candidate_device_producer_must_pass_goal4019_goal4021_goal4023_goal4024_before_timing"
    ),
    "executable_preview": (
        "cupy_device_bounded_pair_preview_and_numba_device_column_preview_pass_same_contract_but_are_not_final_fast_native_producers"
    ),
})
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY = (
    "The v2.8 fixed-radius graph component front door exposes an explicit "
    "user-selected OptiX+partner grouped-stream contract over an existing generic "
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
            "typed_result_stream": make_v2_8_fixed_radius_graph_component_typed_stream_contract(
                self.point_count,
                stream_id="fixed_radius_graph_component_labels_3d_plan",
                source_protocol="planned_cuda_device_columns",
            ).to_metadata(),
            "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
            "partner_reference_contract": f"generic_prepared_optix_{self.partner}_grouped_stream_component_labels_3d",
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
    lower_prepared: (
        PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D
        | PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D
    )
    plan: V28FixedRadiusGraphComponentPlan
    closed: bool = False

    def run(self, *, component_threshold: int, return_metadata: bool = False):
        if self.closed:
            raise RuntimeError("fixed-radius graph component front-door handle is closed")
        component_threshold = int(component_threshold)
        if component_threshold < 1:
            raise ValueError("component_threshold must be at least 1")
        if self.plan.partner == "cupy":
            lower_result = radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(
                self.lower_prepared,
                **{"min" + "_neighbors": component_threshold, "return_metadata": True},
            )
        elif self.plan.partner == "numba":
            lower_result = radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                self.lower_prepared,
                **{"min" + "_neighbors": component_threshold, "return_metadata": True},
            )
        else:  # pragma: no cover - plan validation should prevent this.
            raise ValueError(f"unsupported partner {self.plan.partner!r}")
        columns = lower_result["columns"]
        metadata = _front_door_metadata(
            self.plan,
            lower_metadata=lower_result["metadata"],
            component_threshold=component_threshold,
            columns=columns,
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
        "candidate_strategies": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES,
        "rejected_default_strategies": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES,
        "candidate_strategy_requirements": {
            "partition_convergence_hybrid": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS,
        },
        "candidate_strategy_evidence_goals": {
            "partition_convergence_hybrid": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS,
        },
        "candidate_strategy_partition_guidance": {
            "partition_convergence_hybrid": _hybrid_partition_guidance_metadata(),
        },
        "candidate_strategy_runtime_status": {
            "partition_convergence_hybrid": _hybrid_runtime_status_metadata(),
        },
        "user_selected_partner_required": True,
        "typed_result_stream_contract": make_v2_8_fixed_radius_graph_component_typed_stream_contract(
            1,
            stream_id="fixed_radius_graph_component_labels_3d_schema",
            source_protocol="schema_only",
        ).to_metadata(),
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
    if strategy in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES:
        point_count = int(point_count)
        radius = float(radius)
        component_threshold = int(component_threshold)
        if point_count <= 0:
            raise ValueError("point_count must be positive")
        if radius <= 0.0:
            raise ValueError("radius must be positive")
        if component_threshold < 1:
            raise ValueError("component_threshold must be at least 1")
        return {
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "status": "candidate_requires_native_implementation",
            "operation": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
            "point_count": point_count,
            "radius": radius,
            "component_threshold": component_threshold,
            "user_selected_backend": backend,
            "user_selected_partner": partner,
            "user_selected_strategy": strategy,
            "runtime_executable": False,
            "native_abi_added": False,
            "fallback_selected": False,
            "hidden_dispatch_allowed": False,
            "automatic_partner_selection_allowed": False,
            "app_specific_engine_logic_allowed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "producer_contract": "prepared_fixed_radius_graph_hit_stream_3d",
            "candidate_continuation_contract": (
                "device_resident_partition_convergence_grouped_union_component_labels_3d"
            ),
            "candidate_strategy_requirements": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS,
            "candidate_strategy_evidence_goals": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS,
            "candidate_strategy_partition_guidance": _hybrid_partition_guidance_metadata(),
            "candidate_strategy_runtime_status": _hybrid_runtime_status_metadata(),
            "rejected_default_strategies": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES,
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
        raise ValueError(str(metadata.get("unsupported_reason", metadata["status"])))
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
    if plan.partner == "cupy":
        lower_prepared = prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
            point_rows,
            radius=plan.radius,
            partner=plan.partner,
            grouped_union_query_block_size=plan.grouped_union_query_block_size,
            grouped_union_same_root_culling=plan.grouped_union_same_root_culling,
            grouped_union_direct_side_effect=plan.grouped_union_direct_side_effect,
        )
    elif plan.partner == "numba":
        lower_prepared = prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
            point_rows,
            radius=plan.radius,
            partner=plan.partner,
            grouped_union_query_block_size=plan.grouped_union_query_block_size,
            grouped_union_same_root_culling=plan.grouped_union_same_root_culling,
            grouped_union_direct_side_effect=plan.grouped_union_direct_side_effect,
        )
    else:  # pragma: no cover - plan validation should prevent this.
        raise ValueError(f"unsupported partner {plan.partner!r}")
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


def fixed_radius_graph_component_size_signature_3d_v2_8(
    prepared: V28PreparedFixedRadiusGraphComponentContinuation3D,
    *,
    component_threshold: int,
    return_metadata: bool = False,
):
    if prepared.closed:
        raise RuntimeError("fixed-radius graph component front-door handle is closed")
    component_threshold = int(component_threshold)
    if component_threshold < 1:
        raise ValueError("component_threshold must be at least 1")
    if prepared.plan.partner != "numba":
        raise ValueError("component-size signature front door currently requires partner='numba'")
    lower_result = radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns(
        prepared.lower_prepared,
        min_neighbors=component_threshold,
        return_metadata=True,
    )
    metadata = dict(lower_result["metadata"])
    metadata.update(
        {
            "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "front_door_status": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS,
            "operation": "fixed_radius_graph_component_size_signature_3d",
            "component_threshold": component_threshold,
            "user_selected_backend": prepared.plan.backend,
            "user_selected_partner": prepared.plan.partner,
            "user_selected_strategy": prepared.plan.strategy,
            "producer_contract": "prepared_fixed_radius_graph_hit_stream_3d",
            "continuation_contract": "grouped_stream_component_size_signature_3d",
            "result_columns": ("label_counts", "flag_true_count", "negative_label_count", "neighbor_counts"),
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
    if return_metadata:
        return {"columns": lower_result["columns"], "metadata": metadata}
    return lower_result["columns"]


def make_v2_8_fixed_radius_graph_component_typed_stream_contract(
    point_count: int,
    *,
    stream_id: str = "fixed_radius_graph_component_labels_3d",
    device_type: str = "cuda",
    device_id: int = 0,
    data_ptrs: dict[str, int] | None = None,
    source_protocol: str = "cuda_array_interface",
) -> V28TypedResultStreamContract:
    point_count = int(point_count)
    if point_count <= 0:
        raise ValueError("point_count must be positive")
    pointer_map = {str(key): int(value) for key, value in dict(data_ptrs or {}).items()}
    shape = (point_count,)
    columns = (
        typed_result_column(
            "point_ids",
            "item_id",
            "uint32",
            shape,
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get("point_ids"),
            source_protocol=source_protocol,
            lifetime="session_retained",
            mutability="immutable",
            capacity_elements=point_count,
        ),
        typed_result_column(
            "component_labels",
            "group_key",
            "int64",
            shape,
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get("component_labels"),
            source_protocol=source_protocol,
            lifetime="session_retained",
            mutability="mutable",
            capacity_elements=point_count,
        ),
        typed_result_column(
            "is_core",
            "mask",
            "uint32",
            shape,
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get("is_core"),
            source_protocol=source_protocol,
            lifetime="session_retained",
            mutability="mutable",
            capacity_elements=point_count,
        ),
        typed_result_column(
            "neighbor_counts",
            "payload",
            "uint32",
            shape,
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get("neighbor_counts"),
            source_protocol=source_protocol,
            lifetime="session_retained",
            mutability="mutable",
            capacity_elements=point_count,
        ),
    )
    status_columns = typed_result_status_columns(
        device_type=device_type,
        device_id=device_id,
        row_count_ptr=pointer_map.get("row_count"),
        capacity_ptr=pointer_map.get("capacity"),
        overflow_ptr=pointer_map.get("overflow"),
        complete_ptr=pointer_map.get("complete_candidate_coverage"),
        source_protocol=source_protocol,
    )
    return make_typed_result_stream_contract(
        stream_id=stream_id,
        stream_kind="adjacency_stream",
        producer_primitive=V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION,
        columns=columns,
        status_columns=status_columns,
        ordering="stable_row_order",
        page_capacity=point_count,
    )


def make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
    point_count: int,
    partition_count: int,
    pair_capacity: int,
    *,
    stream_id: str = "fixed_radius_partition_convergence_summary_3d",
    device_type: str = "cuda",
    device_id: int = 0,
    data_ptrs: dict[str, int] | None = None,
    source_protocol: str = "planned_cuda_device_columns",
) -> V28TypedResultStreamContract:
    point_count = int(point_count)
    partition_count = int(partition_count)
    pair_capacity = int(pair_capacity)
    if point_count <= 0:
        raise ValueError("point_count must be positive")
    if partition_count <= 0:
        raise ValueError("partition_count must be positive")
    if pair_capacity <= 0:
        raise ValueError("pair_capacity must be positive")
    pointer_map = {str(key): int(value) for key, value in dict(data_ptrs or {}).items()}

    def column(
        name: str,
        role: str,
        dtype: str,
        shape: tuple[int, ...],
        *,
        mutability: str = "immutable",
    ):
        return typed_result_column(
            name,
            role,
            dtype,
            shape,
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get(name),
            source_protocol=source_protocol,
            lifetime="session_retained",
            mutability=mutability,
            capacity_elements=shape[0],
        )

    partition_shape = (partition_count,)
    pair_shape = (pair_capacity,)
    columns = (
        column("point_partition_ids", "group_key", "uint32", (point_count,), mutability="mutable"),
        column("partition_point_ordinals", "item_id", "uint32", (point_count,)),
        column("occupied_partition_keys_x", "payload", "int32", partition_shape),
        column("occupied_partition_keys_y", "payload", "int32", partition_shape),
        column("occupied_partition_keys_z", "payload", "int32", partition_shape),
        column("partition_offsets", "row_offset", "uint32", (partition_count + 1,)),
        column("partition_counts", "payload", "uint32", partition_shape),
        column("partition_aabb_min_x", "payload", "float32", partition_shape),
        column("partition_aabb_min_y", "payload", "float32", partition_shape),
        column("partition_aabb_min_z", "payload", "float32", partition_shape),
        column("partition_aabb_max_x", "payload", "float32", partition_shape),
        column("partition_aabb_max_y", "payload", "float32", partition_shape),
        column("partition_aabb_max_z", "payload", "float32", partition_shape),
        column("near_pair_left_partition_ids", "group_key", "uint32", pair_shape),
        column("near_pair_right_partition_ids", "item_id", "uint32", pair_shape),
        column("near_pair_status", "mask", "uint32", pair_shape, mutability="mutable"),
    )
    status_columns = typed_result_status_columns(
        device_type=device_type,
        device_id=device_id,
        row_count_ptr=pointer_map.get("row_count"),
        capacity_ptr=pointer_map.get("capacity"),
        overflow_ptr=pointer_map.get("overflow"),
        complete_ptr=pointer_map.get("complete_candidate_coverage"),
        source_protocol=source_protocol,
    )
    return make_typed_result_stream_contract(
        stream_id=stream_id,
        stream_kind="candidate_stream",
        producer_primitive="fixed_radius_partition_convergence_summary_3d",
        columns=columns,
        status_columns=status_columns,
        ordering="group_ordered",
        page_capacity=pair_capacity,
    )


def build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
) -> dict[str, Any]:
    points = tuple(_point_xyz(row) for row in point_rows)
    if not points:
        raise ValueError("point_rows must contain at least one point")
    radius = float(radius)
    cell_factor = float(cell_factor)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if cell_factor <= 0.0:
        raise ValueError("cell_factor must be positive")
    cell_size = radius * cell_factor
    radius_sq = radius * radius

    cells: dict[tuple[int, int, int], dict[str, Any]] = {}
    point_partition_keys = []
    for ordinal, (x, y, z) in enumerate(points):
        key = _partition_key_3d(x, y, z, cell_size)
        point_partition_keys.append(key)
        entry = cells.get(key)
        if entry is None:
            cells[key] = {
                "indices": [ordinal],
                "min_x": x,
                "min_y": y,
                "min_z": z,
                "max_x": x,
                "max_y": y,
                "max_z": z,
            }
        else:
            entry["indices"].append(ordinal)
            entry["min_x"] = min(entry["min_x"], x)
            entry["min_y"] = min(entry["min_y"], y)
            entry["min_z"] = min(entry["min_z"], z)
            entry["max_x"] = max(entry["max_x"], x)
            entry["max_y"] = max(entry["max_y"], y)
            entry["max_z"] = max(entry["max_z"], z)

    ordered_keys = tuple(sorted(cells))
    partition_ordinals = {key: ordinal for ordinal, key in enumerate(ordered_keys)}
    point_partition_ids = tuple(partition_ordinals[key] for key in point_partition_keys)
    partition_counts = tuple(len(cells[key]["indices"]) for key in ordered_keys)
    partition_point_ordinals = tuple(
        ordinal for key in ordered_keys for ordinal in cells[key]["indices"]
    )
    offsets = [0]
    for count in partition_counts:
        offsets.append(offsets[-1] + count)

    pair_rows: list[tuple[int, int, int]] = []
    max_offset = int(math.ceil(radius / cell_size)) + 1
    for left_ordinal, left_key in enumerate(ordered_keys):
        lx, ly, lz = left_key
        left = cells[left_key]
        for dx in range(-max_offset, max_offset + 1):
            for dy in range(-max_offset, max_offset + 1):
                for dz in range(-max_offset, max_offset + 1):
                    right_key = (lx + dx, ly + dy, lz + dz)
                    right_ordinal = partition_ordinals.get(right_key)
                    if right_ordinal is None or right_ordinal < left_ordinal:
                        continue
                    right = cells[right_key]
                    if _partition_aabb_max_distance_sq(left, right) <= radius_sq:
                        status = 1
                    elif _partition_aabb_min_distance_sq(left, right) > radius_sq:
                        status = 0
                    else:
                        status = 2
                    pair_rows.append((left_ordinal, right_ordinal, status))

    requested_capacity = len(pair_rows) if pair_capacity is None else int(pair_capacity)
    if requested_capacity <= 0:
        raise ValueError("pair_capacity must be positive when provided")
    overflow = len(pair_rows) > requested_capacity
    visible_pairs = tuple(pair_rows[:requested_capacity])
    status_counts = {
        "safe_skip_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 0),
        "safe_full_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 1),
        "ambiguous_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 2),
    }
    contract = make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
        len(points),
        len(ordered_keys),
        max(1, requested_capacity),
        stream_id="fixed_radius_partition_convergence_summary_3d_reference",
        device_type="cpu",
        source_protocol="python_reference",
    )
    return {
        "columns": {
            "point_partition_ids": point_partition_ids,
            "partition_point_ordinals": partition_point_ordinals,
            "occupied_partition_keys_x": tuple(key[0] for key in ordered_keys),
            "occupied_partition_keys_y": tuple(key[1] for key in ordered_keys),
            "occupied_partition_keys_z": tuple(key[2] for key in ordered_keys),
            "partition_offsets": tuple(offsets),
            "partition_counts": partition_counts,
            "partition_aabb_min_x": tuple(cells[key]["min_x"] for key in ordered_keys),
            "partition_aabb_min_y": tuple(cells[key]["min_y"] for key in ordered_keys),
            "partition_aabb_min_z": tuple(cells[key]["min_z"] for key in ordered_keys),
            "partition_aabb_max_x": tuple(cells[key]["max_x"] for key in ordered_keys),
            "partition_aabb_max_y": tuple(cells[key]["max_y"] for key in ordered_keys),
            "partition_aabb_max_z": tuple(cells[key]["max_z"] for key in ordered_keys),
            "near_pair_left_partition_ids": tuple(left for left, _, _ in visible_pairs),
            "near_pair_right_partition_ids": tuple(right for _, right, _ in visible_pairs),
            "near_pair_status": tuple(status for _, _, status in visible_pairs),
        },
        "metadata": {
            "reference": "fixed_radius_partition_convergence_summary_3d_python_reference",
            "point_count": len(points),
            "partition_count": len(ordered_keys),
            "cell_factor": cell_factor,
            "cell_size": cell_size,
            "max_neighbor_offset": max_offset,
            "pair_count": len(pair_rows),
            "visible_pair_count": len(visible_pairs),
            "pair_capacity": requested_capacity,
            "overflow": overflow,
            "complete_candidate_coverage": not overflow,
            "status_column_values": {
                "row_count": len(visible_pairs),
                "capacity": requested_capacity,
                "overflow": overflow,
                "complete_candidate_coverage": not overflow,
            },
            "status_counts": status_counts,
            "typed_result_stream": contract.to_metadata(),
            "native_abi_added": False,
            "runtime_executable": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_engine_logic_allowed": False,
            "automatic_partner_selection_allowed": False,
            "hidden_dispatch_allowed": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        },
    }


def validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
    point_rows,
    *,
    radius: float,
    candidate: dict[str, Any],
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
    float_abs_tol: float = 1.0e-6,
) -> dict[str, Any]:
    """Validate a candidate partition-summary producer against the reference."""

    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dict with columns and metadata")
    candidate_columns = dict(candidate.get("columns", {}))
    candidate_metadata = dict(candidate.get("metadata", {}))
    if pair_capacity is None:
        pair_capacity = candidate_metadata.get("pair_capacity")
    reference = build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
        point_rows,
        radius=radius,
        cell_factor=cell_factor,
        pair_capacity=None if pair_capacity is None else int(pair_capacity),
    )
    reference_columns = reference["columns"]
    reference_metadata = reference["metadata"]
    float_abs_tol = float(float_abs_tol)
    if float_abs_tol < 0.0:
        raise ValueError("float_abs_tol must be non-negative")

    errors: list[str] = []
    mismatch_columns: list[str] = []
    required_columns = tuple(reference_columns.keys())
    float_columns = {
        "partition_aabb_min_x",
        "partition_aabb_min_y",
        "partition_aabb_min_z",
        "partition_aabb_max_x",
        "partition_aabb_max_y",
        "partition_aabb_max_z",
    }
    for name in required_columns:
        if name not in candidate_columns:
            errors.append(f"missing candidate column: {name}")
            mismatch_columns.append(name)
            continue
        expected = _column_tuple(reference_columns[name])
        actual = _column_tuple(candidate_columns[name])
        if name in float_columns:
            if len(expected) != len(actual) or any(
                abs(float(left) - float(right)) > float_abs_tol
                for left, right in zip(expected, actual)
            ):
                errors.append(f"candidate column mismatch: {name}")
                mismatch_columns.append(name)
        elif expected != actual:
            errors.append(f"candidate column mismatch: {name}")
            mismatch_columns.append(name)

    candidate_pair_count = candidate_metadata.get("pair_count")
    if candidate_pair_count is not None and int(candidate_pair_count) != int(reference_metadata["pair_count"]):
        errors.append("candidate pair_count mismatch")
    candidate_visible_pair_count = candidate_metadata.get("visible_pair_count")
    if (
        candidate_visible_pair_count is not None
        and int(candidate_visible_pair_count) != int(reference_metadata["visible_pair_count"])
    ):
        errors.append("candidate visible_pair_count mismatch")
    candidate_partition_count = candidate_metadata.get("partition_count")
    if (
        candidate_partition_count is not None
        and int(candidate_partition_count) != int(reference_metadata["partition_count"])
    ):
        errors.append("candidate partition_count mismatch")
    if candidate_metadata.get("overflow") is not None and bool(candidate_metadata["overflow"]) != bool(
        reference_metadata["overflow"]
    ):
        errors.append("candidate overflow mismatch")
    candidate_complete_coverage = candidate_metadata.get("complete_candidate_coverage")
    if candidate_complete_coverage is not None and bool(candidate_complete_coverage) != bool(
        reference_metadata["complete_candidate_coverage"]
    ):
        errors.append("candidate complete_candidate_coverage mismatch")
    if bool(candidate_metadata.get("overflow", False)) and bool(candidate_metadata.get("complete_candidate_coverage", False)):
        errors.append("candidate overflow cannot claim complete_candidate_coverage")

    expected_status_counts = reference_metadata["status_counts"]
    candidate_status_counts = candidate_metadata.get("status_counts")
    if candidate_status_counts is not None and dict(candidate_status_counts) != dict(expected_status_counts):
        errors.append("candidate status_counts mismatch")
    candidate_status_values = candidate_metadata.get("status_column_values")
    if candidate_status_values is not None and dict(candidate_status_values) != dict(reference_metadata["status_column_values"]):
        errors.append("candidate status_column_values mismatch")

    typed_stream = candidate_metadata.get("typed_result_stream")
    if typed_stream is not None:
        typed_validation = validate_typed_result_stream_contract(typed_stream)
        if typed_validation["status"] != "accept":
            errors.append("candidate typed_result_stream rejected")
    else:
        typed_validation = {"status": "not_provided", "errors": ()}

    for flag in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "app_specific_engine_logic_allowed",
        "automatic_partner_selection_allowed",
        "hidden_dispatch_allowed",
    ):
        if candidate_metadata.get(flag, False) is not False:
            errors.append(f"candidate metadata must not authorize {flag}")

    return {
        "status": "accept" if not errors else "reject",
        "reference": reference_metadata["reference"],
        "candidate_reference_contract": "fixed_radius_partition_convergence_summary_3d_same_contract",
        "errors": tuple(errors),
        "mismatch_columns": tuple(dict.fromkeys(mismatch_columns)),
        "point_count": reference_metadata["point_count"],
        "partition_count": reference_metadata["partition_count"],
        "pair_count": reference_metadata["pair_count"],
        "visible_pair_count": reference_metadata["visible_pair_count"],
        "pair_capacity": reference_metadata["pair_capacity"],
        "overflow": reference_metadata["overflow"],
        "complete_candidate_coverage": reference_metadata["complete_candidate_coverage"],
        "status_column_values": dict(reference_metadata["status_column_values"]),
        "status_counts": dict(expected_status_counts),
        "typed_result_stream_validation": typed_validation,
        "native_abi_added": False,
        "runtime_executable": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
    }


def build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    partition_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reference component labels from a partition-convergence summary."""

    raw_rows = tuple(point_rows)
    points = tuple(_point_xyz(row) for row in raw_rows)
    if not points:
        raise ValueError("point_rows must contain at least one point")
    radius = float(radius)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if partition_summary is None:
        partition_summary = build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
        )
    summary_validation = validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
        raw_rows,
        radius=radius,
        candidate=partition_summary,
        cell_factor=cell_factor,
    )
    base_metadata = {
        "reference": "fixed_radius_partition_convergence_component_labels_3d_python_reference",
        "partition_summary_validation": summary_validation,
        "native_abi_added": False,
        "runtime_executable": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "hidden_dispatch_allowed": False,
        "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
    }
    if summary_validation["status"] != "accept":
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_mismatch",
                "errors": summary_validation["errors"],
            },
        }
    if bool(partition_summary["metadata"].get("overflow", False)):
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_overflow",
                "overflow": True,
                "complete_candidate_coverage": False,
                "errors": ("partition summary overflow prevents complete component labels",),
            },
        }

    summary_columns = dict(partition_summary["columns"])
    point_partition_ids = tuple(int(value) for value in _column_tuple(summary_columns["point_partition_ids"]))
    partition_count = int(summary_validation["partition_count"])
    partitions: list[list[int]] = [[] for _ in range(partition_count)]
    errors: list[str] = []
    for ordinal, partition_id in enumerate(point_partition_ids):
        if partition_id < 0 or partition_id >= partition_count:
            errors.append("point_partition_ids contains an out-of-range partition id")
            continue
        partitions[partition_id].append(ordinal)
    parents = list(range(len(points)))
    radius_sq = radius * radius
    for left, right, status in zip(
        _column_tuple(summary_columns["near_pair_left_partition_ids"]),
        _column_tuple(summary_columns["near_pair_right_partition_ids"]),
        _column_tuple(summary_columns["near_pair_status"]),
    ):
        left_id = int(left)
        right_id = int(right)
        status_id = int(status)
        if left_id < 0 or right_id < 0 or left_id >= partition_count or right_id >= partition_count:
            errors.append("near partition pair contains an out-of-range partition id")
            continue
        left_members = partitions[left_id]
        right_members = partitions[right_id]
        if status_id == 0:
            continue
        if status_id == 1:
            combined = tuple(left_members) + tuple(right_members)
            if combined:
                root = combined[0]
                for member in combined[1:]:
                    _union_parent(parents, root, member)
            continue
        if status_id != 2:
            errors.append("near_pair_status must be 0, 1, or 2")
            continue
        for left_point in left_members:
            for right_point in right_members:
                if left_id == right_id and right_point <= left_point:
                    continue
                if _distance_sq_3d(points[left_point], points[right_point]) <= radius_sq:
                    _union_parent(parents, left_point, right_point)

    if errors:
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_consumer_error",
                "errors": tuple(errors),
            },
        }

    labels = _compact_component_labels(parents)
    all_pairs_labels = _fixed_radius_component_labels_all_pairs_3d(points, radius)
    same_contract = labels == all_pairs_labels
    point_ids = tuple(_point_id(row, ordinal) for ordinal, row in enumerate(raw_rows))
    return {
        "columns": {
            "point_ids": point_ids,
            "component_labels": labels,
        },
        "metadata": {
            **base_metadata,
            "status": "accept" if same_contract else "reject_all_pairs_mismatch",
            "point_count": len(points),
            "component_count": len(set(labels)),
            "same_contract_against_all_pairs": same_contract,
            "complete_candidate_coverage": True,
            "all_pairs_component_labels": all_pairs_labels,
            "partition_pair_status_counts": dict(summary_validation["status_counts"]),
        },
    }


def build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
    pair_enumeration: str = "host",
) -> dict[str, Any]:
    """Executable CuPy preview for partition-summary columns."""

    import cupy

    points = tuple(_point_xyz(row) for row in point_rows)
    if not points:
        raise ValueError("point_rows must contain at least one point")
    radius = float(radius)
    cell_factor = float(cell_factor)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if cell_factor <= 0.0:
        raise ValueError("cell_factor must be positive")
    pair_enumeration = str(pair_enumeration)
    if pair_enumeration not in {"host", "device_bounded_offsets"}:
        raise ValueError("pair_enumeration must be 'host' or 'device_bounded_offsets'")
    cell_size = radius * cell_factor
    radius_sq = radius * radius

    point_count = len(points)
    x = cupy.asarray([point[0] for point in points], dtype=cupy.float64)
    y = cupy.asarray([point[1] for point in points], dtype=cupy.float64)
    z = cupy.asarray([point[2] for point in points], dtype=cupy.float64)
    kx = cupy.floor(x / cell_size).astype(cupy.int64, copy=False)
    ky = cupy.floor(y / cell_size).astype(cupy.int64, copy=False)
    kz = cupy.floor(z / cell_size).astype(cupy.int64, copy=False)
    min_kx = int(cupy.min(kx).item())
    min_ky = int(cupy.min(ky).item())
    min_kz = int(cupy.min(kz).item())
    local_kx = kx - min_kx
    local_ky = ky - min_ky
    local_kz = kz - min_kz
    dim_y = int(cupy.max(local_ky).item()) + 1
    dim_z = int(cupy.max(local_kz).item()) + 1
    cell_ids = (local_kx * dim_y * dim_z + local_ky * dim_z + local_kz).astype(cupy.int64)
    order = cupy.argsort(cell_ids).astype(cupy.int32, copy=False)
    sorted_cell_ids = cell_ids[order]
    unique_cells, starts, counts = cupy.unique(
        sorted_cell_ids,
        return_index=True,
        return_counts=True,
    )
    partition_count = int(unique_cells.size)
    point_partition_ids = cupy.searchsorted(unique_cells, cell_ids).astype(cupy.uint32, copy=False)
    counts_u32 = counts.astype(cupy.uint32, copy=False)
    offsets = cupy.concatenate((
        cupy.zeros((1,), dtype=cupy.uint32),
        cupy.cumsum(counts_u32, dtype=cupy.uint32),
    ))
    aabb_min_x64 = cupy.full((partition_count,), cupy.inf, dtype=cupy.float64)
    aabb_min_y64 = cupy.full((partition_count,), cupy.inf, dtype=cupy.float64)
    aabb_min_z64 = cupy.full((partition_count,), cupy.inf, dtype=cupy.float64)
    aabb_max_x64 = cupy.full((partition_count,), -cupy.inf, dtype=cupy.float64)
    aabb_max_y64 = cupy.full((partition_count,), -cupy.inf, dtype=cupy.float64)
    aabb_max_z64 = cupy.full((partition_count,), -cupy.inf, dtype=cupy.float64)
    cupy.minimum.at(aabb_min_x64, point_partition_ids, x)
    cupy.minimum.at(aabb_min_y64, point_partition_ids, y)
    cupy.minimum.at(aabb_min_z64, point_partition_ids, z)
    cupy.maximum.at(aabb_max_x64, point_partition_ids, x)
    cupy.maximum.at(aabb_max_y64, point_partition_ids, y)
    cupy.maximum.at(aabb_max_z64, point_partition_ids, z)
    aabb_min_x = aabb_min_x64.astype(cupy.float32, copy=False)
    aabb_min_y = aabb_min_y64.astype(cupy.float32, copy=False)
    aabb_min_z = aabb_min_z64.astype(cupy.float32, copy=False)
    aabb_max_x = aabb_max_x64.astype(cupy.float32, copy=False)
    aabb_max_y = aabb_max_y64.astype(cupy.float32, copy=False)
    aabb_max_z = aabb_max_z64.astype(cupy.float32, copy=False)

    unique_host = tuple(int(value) for value in cupy.asnumpy(unique_cells).tolist())
    key_rows = []
    for encoded in unique_host:
        local_x = encoded // (dim_y * dim_z)
        rem = encoded % (dim_y * dim_z)
        local_y = rem // dim_z
        local_z = rem % dim_z
        key_rows.append((local_x + min_kx, local_y + min_ky, local_z + min_kz))
    key_to_ordinal = {key: ordinal for ordinal, key in enumerate(key_rows)}
    aabbs = [
        {
            "min_x": math.inf,
            "min_y": math.inf,
            "min_z": math.inf,
            "max_x": -math.inf,
            "max_y": -math.inf,
            "max_z": -math.inf,
        }
        for index in range(partition_count)
    ]
    for ordinal, partition_id in enumerate(cupy.asnumpy(point_partition_ids).tolist()):
        partition = aabbs[int(partition_id)]
        px, py, pz = points[ordinal]
        partition["min_x"] = min(partition["min_x"], px)
        partition["min_y"] = min(partition["min_y"], py)
        partition["min_z"] = min(partition["min_z"], pz)
        partition["max_x"] = max(partition["max_x"], px)
        partition["max_y"] = max(partition["max_y"], py)
        partition["max_z"] = max(partition["max_z"], pz)
    max_offset = int(math.ceil(radius / cell_size)) + 1
    classification_tol = 1.0e-5 * max(1.0, radius_sq)
    if pair_enumeration == "host":
        pair_rows: list[tuple[int, int, int]] = []
        for left_ordinal, left_key in enumerate(key_rows):
            lx, ly, lz = left_key
            left = aabbs[left_ordinal]
            for dx in range(-max_offset, max_offset + 1):
                for dy in range(-max_offset, max_offset + 1):
                    for dz in range(-max_offset, max_offset + 1):
                        right_key = (lx + dx, ly + dy, lz + dz)
                        right_ordinal = key_to_ordinal.get(right_key)
                        if right_ordinal is None or right_ordinal < left_ordinal:
                            continue
                        right = aabbs[right_ordinal]
                        if _partition_aabb_max_distance_sq(left, right) <= radius_sq + classification_tol:
                            status = 1
                        elif _partition_aabb_min_distance_sq(left, right) > radius_sq + classification_tol:
                            status = 0
                        else:
                            status = 2
                        pair_rows.append((left_ordinal, right_ordinal, status))

        requested_capacity = len(pair_rows) if pair_capacity is None else int(pair_capacity)
        if requested_capacity <= 0:
            raise ValueError("pair_capacity must be positive when provided")
        overflow = len(pair_rows) > requested_capacity
        visible_pairs = tuple(pair_rows[:requested_capacity])
        left_ids = cupy.asarray([row[0] for row in visible_pairs], dtype=cupy.uint32)
        right_ids = cupy.asarray([row[1] for row in visible_pairs], dtype=cupy.uint32)
        statuses = cupy.asarray([row[2] for row in visible_pairs], dtype=cupy.uint32)
        pair_count = len(pair_rows)
        visible_pair_count = len(visible_pairs)
        status_counts = {
            "safe_skip_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 0),
            "safe_full_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 1),
            "ambiguous_partition_pairs": sum(1 for _, _, status in visible_pairs if status == 2),
        }
    else:
        if pair_capacity is None:
            requested_capacity = int(partition_count) * int((2 * max_offset + 1) ** 3)
        else:
            requested_capacity = int(pair_capacity)
        if requested_capacity <= 0:
            raise ValueError("pair_capacity must be positive when provided")
        left_ids, right_ids, statuses, pair_count, visible_pair_count, overflow = (
            _cupy_partition_pair_status_device_bounded_offsets(
                cupy,
                key_rows=key_rows,
                unique_cells=unique_cells,
                min_kx=min_kx,
                min_ky=min_ky,
                min_kz=min_kz,
                dim_y=dim_y,
                dim_z=dim_z,
                aabb_min_x64=aabb_min_x64,
                aabb_min_y64=aabb_min_y64,
                aabb_min_z64=aabb_min_z64,
                aabb_max_x64=aabb_max_x64,
                aabb_max_y64=aabb_max_y64,
                aabb_max_z64=aabb_max_z64,
                max_offset=max_offset,
                radius_sq=radius_sq,
                classification_tol=classification_tol,
                pair_capacity=requested_capacity,
            )
        )
        status_counts = {
            "safe_skip_partition_pairs": int(cupy.sum(statuses == 0).item()),
            "safe_full_partition_pairs": int(cupy.sum(statuses == 1).item()),
            "ambiguous_partition_pairs": int(cupy.sum(statuses == 2).item()),
        }
    columns = {
        "point_partition_ids": point_partition_ids,
        "partition_point_ordinals": order.astype(cupy.uint32, copy=False),
        "occupied_partition_keys_x": cupy.asarray([key[0] for key in key_rows], dtype=cupy.int32),
        "occupied_partition_keys_y": cupy.asarray([key[1] for key in key_rows], dtype=cupy.int32),
        "occupied_partition_keys_z": cupy.asarray([key[2] for key in key_rows], dtype=cupy.int32),
        "partition_offsets": offsets,
        "partition_counts": counts_u32,
        "partition_aabb_min_x": aabb_min_x,
        "partition_aabb_min_y": aabb_min_y,
        "partition_aabb_min_z": aabb_min_z,
        "partition_aabb_max_x": aabb_max_x,
        "partition_aabb_max_y": aabb_max_y,
        "partition_aabb_max_z": aabb_max_z,
        "near_pair_left_partition_ids": left_ids,
        "near_pair_right_partition_ids": right_ids,
        "near_pair_status": statuses,
    }
    contract = make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
        point_count,
        partition_count,
        max(1, requested_capacity),
        stream_id="fixed_radius_partition_convergence_summary_3d_cupy_preview",
        data_ptrs=_column_data_ptrs(columns),
        source_protocol="cupy_cuda_array_interface",
    )
    return {
        "columns": columns,
        "metadata": {
            "adapter": "fixed_radius_partition_convergence_summary_cupy_preview_3d",
            "reference": "fixed_radius_partition_convergence_summary_3d_cupy_preview",
            "point_count": point_count,
            "partition_count": partition_count,
            "cell_factor": cell_factor,
            "cell_size": cell_size,
            "max_neighbor_offset": max_offset,
            "pair_count": pair_count,
            "visible_pair_count": visible_pair_count,
            "pair_capacity": requested_capacity,
            "overflow": overflow,
            "complete_candidate_coverage": not overflow,
            "status_column_values": {
                "row_count": visible_pair_count,
                "capacity": requested_capacity,
                "overflow": overflow,
                "complete_candidate_coverage": not overflow,
            },
            "status_counts": status_counts,
            "typed_result_stream": contract.to_metadata(),
            "device_partition_columns_used": True,
            "host_pair_enumeration_used": pair_enumeration == "host",
            "device_pair_enumeration_used": pair_enumeration == "device_bounded_offsets",
            "pair_enumeration": pair_enumeration,
            "pair_capacity_source": (
                "caller_provided"
                if pair_capacity is not None
                else "device_upper_bound"
                if pair_enumeration == "device_bounded_offsets"
                else "host_exact_pair_count"
            ),
            "native_abi_added": False,
            "runtime_executable": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_engine_logic_allowed": False,
            "automatic_partner_selection_allowed": False,
            "hidden_dispatch_allowed": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        },
    }


def _skipped_partition_summary_prepare_validation(summary: dict[str, Any]) -> dict[str, Any]:
    summary_metadata = summary["metadata"]
    return {
        "status": "accept",
        "reference": "fixed_radius_partition_convergence_summary_3d_prepare_trusted_preview",
        "candidate_reference_contract": (
            "fixed_radius_partition_convergence_summary_3d_same_contract_skipped_for_prepared_timing"
        ),
        "errors": (),
        "point_count": int(summary_metadata["point_count"]),
        "partition_count": int(summary_metadata["partition_count"]),
        "pair_count": int(summary_metadata["pair_count"]),
        "visible_pair_count": int(summary_metadata["visible_pair_count"]),
        "pair_capacity": int(summary_metadata["pair_capacity"]),
        "overflow": bool(summary_metadata["overflow"]),
        "complete_candidate_coverage": bool(summary_metadata["complete_candidate_coverage"]),
        "status_column_values": dict(summary_metadata["status_column_values"]),
        "status_counts": dict(summary_metadata["status_counts"]),
        "summary_same_contract_validation_skipped_for_prepared_timing": True,
    }


def _partition_summary_digest(summary: dict[str, Any]) -> dict[str, Any]:
    metadata = summary["metadata"]
    return {
        "adapter": metadata["adapter"],
        "reference": metadata["reference"],
        "point_count": int(metadata["point_count"]),
        "partition_count": int(metadata["partition_count"]),
        "pair_count": int(metadata["pair_count"]),
        "visible_pair_count": int(metadata["visible_pair_count"]),
        "pair_capacity": int(metadata["pair_capacity"]),
        "overflow": bool(metadata["overflow"]),
        "complete_candidate_coverage": bool(metadata["complete_candidate_coverage"]),
        "status_counts": dict(metadata["status_counts"]),
        "pair_enumeration": metadata["pair_enumeration"],
        "pair_capacity_source": metadata["pair_capacity_source"],
        "device_partition_columns_used": bool(metadata["device_partition_columns_used"]),
        "device_pair_enumeration_used": bool(metadata["device_pair_enumeration_used"]),
    }


@dataclass
class V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D:
    point_rows: tuple[Any, ...]
    radius: float
    cell_factor: float
    pair_capacity: int | None
    pair_enumeration: str
    partition_summary: dict[str, Any]
    prepare_validation: dict[str, Any]
    closed: bool = False
    component_label_runs: int = 0
    component_signature_runs: int = 0

    def _ensure_open(self) -> None:
        if self.closed:
            raise RuntimeError("prepared partition-convergence summary handle is closed")

    def to_metadata(self) -> dict[str, Any]:
        summary_digest = _partition_summary_digest(self.partition_summary)
        return {
            "version": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION,
            "status": "explicit_cupy_prepared_partition_summary_preview",
            "operation": "fixed_radius_partition_convergence_summary_3d",
            "prepared_partition_summary_handle": True,
            "prepared_partition_summary_handle_status": "explicit_cupy_preview_not_promoted",
            "prepared_partition_summary_partner": "cupy",
            "prepared_partition_summary_runtime_executable": True,
            "point_count": summary_digest["point_count"],
            "radius": self.radius,
            "cell_factor": self.cell_factor,
            "pair_enumeration": self.pair_enumeration,
            "pair_capacity": summary_digest["pair_capacity"],
            "partition_summary_digest": summary_digest,
            "prepare_validation": dict(self.prepare_validation),
            "component_label_runs": self.component_label_runs,
            "component_signature_runs": self.component_signature_runs,
            "closed": self.closed,
            "native_abi_added": False,
            "runtime_executable": True,
            "default_route_promoted": False,
            "partition_convergence_hybrid_promoted": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_engine_logic_allowed": False,
            "automatic_partner_selection_allowed": False,
            "hidden_dispatch_allowed": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }

    def run_component_labels(
        self,
        *,
        partition_union_execution: str = "cupy_safe_full",
        ambiguous_union_execution: str = "cupy_partition_points",
        validate_summary_same_contract: bool = False,
        validate_against_all_pairs: bool = False,
    ) -> dict[str, Any]:
        self._ensure_open()
        self.component_label_runs += 1
        result = build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
            self.point_rows,
            radius=self.radius,
            cell_factor=self.cell_factor,
            partition_summary=self.partition_summary,
            partition_union_execution=partition_union_execution,
            ambiguous_union_execution=ambiguous_union_execution,
            validate_summary_same_contract=validate_summary_same_contract,
            validate_against_all_pairs=validate_against_all_pairs,
        )
        return _decorate_prepared_partition_summary_result(
            result,
            prepared=self,
            operation="fixed_radius_partition_convergence_component_labels_3d",
            run_index=self.component_label_runs,
        )

    def run_component_signature(
        self,
        *,
        ambiguous_union_execution: str = "cupy_partition_points",
        validate_summary_same_contract: bool = False,
        validate_against_component_labels: bool = False,
    ) -> dict[str, Any]:
        self._ensure_open()
        self.component_signature_runs += 1
        result = build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            self.point_rows,
            radius=self.radius,
            cell_factor=self.cell_factor,
            partition_summary=self.partition_summary,
            ambiguous_union_execution=ambiguous_union_execution,
            validate_summary_same_contract=validate_summary_same_contract,
            validate_against_component_labels=validate_against_component_labels,
        )
        return _decorate_prepared_partition_summary_result(
            result,
            prepared=self,
            operation="fixed_radius_partition_convergence_component_signature_3d",
            run_index=self.component_signature_runs,
        )

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> "V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _decorate_prepared_partition_summary_result(
    result: dict[str, Any],
    *,
    prepared: V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D,
    operation: str,
    run_index: int,
) -> dict[str, Any]:
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "prepared_partition_summary_handle": True,
            "prepared_partition_summary_handle_status": "explicit_cupy_preview_not_promoted",
            "prepared_partition_summary_partner": "cupy",
            "prepared_partition_summary_reused": True,
            "prepared_partition_summary_operation": operation,
            "prepared_partition_summary_run_index": int(run_index),
            "prepared_partition_summary_digest": _partition_summary_digest(prepared.partition_summary),
            "prepared_partition_summary_prepare_validation": dict(prepared.prepare_validation),
            "prepared_partition_summary_default_route_promoted": False,
            "partition_convergence_hybrid_promoted": False,
            "native_abi_added": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_engine_logic_allowed": False,
            "automatic_partner_selection_allowed": False,
            "hidden_dispatch_allowed": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }
    )
    return {"columns": result["columns"], "metadata": metadata}


def prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
    pair_enumeration: str = "device_bounded_offsets",
    validate_summary_same_contract: bool = False,
) -> V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D:
    """Build a reusable explicit CuPy preview handle for partition-summary columns."""

    raw_rows = tuple(point_rows)
    summary = build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
        raw_rows,
        radius=radius,
        cell_factor=cell_factor,
        pair_capacity=pair_capacity,
        pair_enumeration=pair_enumeration,
    )
    if validate_summary_same_contract:
        prepare_validation = validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            candidate=summary,
            float_abs_tol=1.0e-5,
        )
        if prepare_validation["status"] != "accept":
            raise ValueError(f"partition summary validation failed: {prepare_validation['errors']}")
    else:
        prepare_validation = _skipped_partition_summary_prepare_validation(summary)
    return V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D(
        point_rows=raw_rows,
        radius=float(radius),
        cell_factor=float(cell_factor),
        pair_capacity=pair_capacity,
        pair_enumeration=str(pair_enumeration),
        partition_summary=summary,
        prepare_validation=prepare_validation,
    )


def run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d(
    prepared: V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D,
    *,
    partition_union_execution: str = "cupy_safe_full",
    ambiguous_union_execution: str = "cupy_partition_points",
    validate_summary_same_contract: bool = False,
    validate_against_all_pairs: bool = False,
) -> dict[str, Any]:
    return prepared.run_component_labels(
        partition_union_execution=partition_union_execution,
        ambiguous_union_execution=ambiguous_union_execution,
        validate_summary_same_contract=validate_summary_same_contract,
        validate_against_all_pairs=validate_against_all_pairs,
    )


def run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(
    prepared: V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D,
    *,
    ambiguous_union_execution: str = "cupy_partition_points",
    validate_summary_same_contract: bool = False,
    validate_against_component_labels: bool = False,
) -> dict[str, Any]:
    return prepared.run_component_signature(
        ambiguous_union_execution=ambiguous_union_execution,
        validate_summary_same_contract=validate_summary_same_contract,
        validate_against_component_labels=validate_against_component_labels,
    )


def build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
) -> dict[str, Any]:
    """Executable Numba device-column preview for partition-summary columns."""

    import numpy as np
    from numba import cuda

    reference = build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
        point_rows,
        radius=radius,
        cell_factor=cell_factor,
        pair_capacity=pair_capacity,
    )
    dtype_map = {
        "point_partition_ids": np.uint32,
        "partition_point_ordinals": np.uint32,
        "occupied_partition_keys_x": np.int32,
        "occupied_partition_keys_y": np.int32,
        "occupied_partition_keys_z": np.int32,
        "partition_offsets": np.uint32,
        "partition_counts": np.uint32,
        "partition_aabb_min_x": np.float32,
        "partition_aabb_min_y": np.float32,
        "partition_aabb_min_z": np.float32,
        "partition_aabb_max_x": np.float32,
        "partition_aabb_max_y": np.float32,
        "partition_aabb_max_z": np.float32,
        "near_pair_left_partition_ids": np.uint32,
        "near_pair_right_partition_ids": np.uint32,
        "near_pair_status": np.uint32,
    }
    columns = {
        name: cuda.to_device(np.asarray(values, dtype=dtype_map[name]))
        for name, values in reference["columns"].items()
    }
    metadata = dict(reference["metadata"])
    metadata.update(
        {
            "adapter": "fixed_radius_partition_convergence_summary_numba_preview_3d",
            "reference": "fixed_radius_partition_convergence_summary_3d_numba_preview",
            "typed_result_stream": make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
                int(metadata["point_count"]),
                int(metadata["partition_count"]),
                max(1, int(metadata["pair_capacity"])),
                stream_id="fixed_radius_partition_convergence_summary_3d_numba_preview",
                data_ptrs=_column_data_ptrs(columns),
                source_protocol="numba_cuda_array_interface",
            ).to_metadata(),
            "device_partition_columns_used": True,
            "host_partition_summary_used": True,
            "native_abi_added": False,
            "runtime_executable": True,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_engine_logic_allowed": False,
            "automatic_partner_selection_allowed": False,
            "hidden_dispatch_allowed": False,
            "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
        }
    )
    return {"columns": columns, "metadata": metadata}


def build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
    pair_enumeration: str = "device_bounded_offsets",
    partition_summary: dict[str, Any] | None = None,
    partition_union_execution: str = "host",
    ambiguous_union_execution: str = "host",
    validate_summary_same_contract: bool = True,
    validate_against_all_pairs: bool = False,
) -> dict[str, Any]:
    """Executable CuPy preview for partition-level component labels."""

    raw_rows = tuple(point_rows)
    points = tuple(_point_xyz(row) for row in raw_rows)
    if not points:
        raise ValueError("point_rows must contain at least one point")
    radius = float(radius)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    partition_union_execution = str(partition_union_execution)
    if partition_union_execution not in {"host", "cupy_safe_full"}:
        raise ValueError("partition_union_execution must be 'host' or 'cupy_safe_full'")
    ambiguous_union_execution = str(ambiguous_union_execution)
    if ambiguous_union_execution not in {"host", "cupy_partition_points"}:
        raise ValueError("ambiguous_union_execution must be 'host' or 'cupy_partition_points'")
    if ambiguous_union_execution == "cupy_partition_points" and partition_union_execution != "cupy_safe_full":
        raise ValueError("cupy_partition_points ambiguous union requires cupy_safe_full partition union")
    if partition_summary is None:
        summary = build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            pair_capacity=pair_capacity,
            pair_enumeration=pair_enumeration,
        )
        partition_summary_reused = False
    else:
        summary = partition_summary
        partition_summary_reused = True
    if validate_summary_same_contract:
        summary_validation = validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            candidate=summary,
            float_abs_tol=1.0e-5,
        )
    else:
        summary_metadata = summary["metadata"]
        summary_validation = {
            "status": "accept",
            "reference": "fixed_radius_partition_convergence_summary_3d_timing_trusted_preview",
            "candidate_reference_contract": "fixed_radius_partition_convergence_summary_3d_same_contract_skipped_for_timing",
            "errors": (),
            "point_count": int(summary_metadata["point_count"]),
            "partition_count": int(summary_metadata["partition_count"]),
            "pair_count": int(summary_metadata["pair_count"]),
            "visible_pair_count": int(summary_metadata["visible_pair_count"]),
            "pair_capacity": int(summary_metadata["pair_capacity"]),
            "overflow": bool(summary_metadata["overflow"]),
            "complete_candidate_coverage": bool(summary_metadata["complete_candidate_coverage"]),
            "status_column_values": dict(summary_metadata["status_column_values"]),
            "status_counts": dict(summary_metadata["status_counts"]),
            "summary_same_contract_validation_skipped_for_timing": True,
        }
    base_metadata = {
        "reference": "fixed_radius_partition_convergence_component_labels_3d_cupy_preview",
        "partition_summary_validation": summary_validation,
        "summary_same_contract_validation_enabled": validate_summary_same_contract,
        "partition_summary_reused": partition_summary_reused,
        "partition_summary_pair_enumeration": summary["metadata"]["pair_enumeration"],
        "partition_summary_pair_capacity_source": summary["metadata"]["pair_capacity_source"],
        "partition_union_execution": partition_union_execution,
        "ambiguous_union_execution": ambiguous_union_execution,
        "native_abi_added": False,
        "runtime_executable": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "hidden_dispatch_allowed": False,
        "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
    }
    if summary_validation["status"] != "accept":
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_mismatch",
                "errors": summary_validation["errors"],
            },
        }
    if bool(summary["metadata"].get("overflow", False)):
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_overflow",
                "overflow": True,
                "complete_candidate_coverage": False,
                "errors": ("partition summary overflow prevents complete component labels",),
            },
        }

    summary_columns = dict(summary["columns"])
    point_partition_ids = tuple(int(value) for value in _column_tuple(summary_columns["point_partition_ids"]))
    partition_count = int(summary_validation["partition_count"])
    partitions: list[list[int]] = [[] for _ in range(partition_count)]
    errors: list[str] = []
    for ordinal, partition_id in enumerate(point_partition_ids):
        if partition_id < 0 or partition_id >= partition_count:
            errors.append("point_partition_ids contains an out-of-range partition id")
            continue
        partitions[partition_id].append(ordinal)

    summary_left = summary_columns["near_pair_left_partition_ids"]
    summary_right = summary_columns["near_pair_right_partition_ids"]
    summary_status = summary_columns["near_pair_status"]
    ambiguous_union_skipped_reason = None
    if partition_union_execution == "cupy_safe_full" and ambiguous_union_execution == "cupy_partition_points":
        import cupy

        status_counts = dict(summary["metadata"]["status_counts"])
        safe_skip_pairs = int(status_counts["safe_skip_partition_pairs"])
        safe_full_pairs = int(status_counts["safe_full_partition_pairs"])
        ambiguous_pairs = int(status_counts["ambiguous_partition_pairs"])
        if ambiguous_pairs == 0:
            partition_parents, union_iterations = _cupy_union_safe_full_partition_pairs(
                cupy,
                partition_count=partition_count,
                left_ids=summary_left,
                right_ids=summary_right,
                statuses=summary_status,
            )
            ambiguous_point_comparisons = 0
            ambiguous_positive_edges = 0
            ambiguous_union_skipped_reason = "no_ambiguous_partition_pairs"
        else:
            x_dev = cupy.asarray([point[0] for point in points], dtype=cupy.float64)
            y_dev = cupy.asarray([point[1] for point in points], dtype=cupy.float64)
            z_dev = cupy.asarray([point[2] for point in points], dtype=cupy.float64)
            (
                partition_parents_device,
                union_iterations,
                ambiguous_point_comparisons,
                ambiguous_positive_edges,
            ) = _cupy_union_partition_pairs_with_ambiguous_points(
                cupy,
                partition_count=partition_count,
                left_ids=summary_left,
                right_ids=summary_right,
                statuses=summary_status,
                partition_offsets=summary_columns["partition_offsets"],
                partition_point_ordinals=summary_columns["partition_point_ordinals"],
                x=x_dev,
                y=y_dev,
                z=z_dev,
                radius_sq=radius * radius,
            )
            partition_parents = [int(value) for value in cupy.asnumpy(partition_parents_device).tolist()]
        ambiguous_left_values = ()
        ambiguous_right_values = ()
        ambiguous_status_values = ()
    elif partition_union_execution == "cupy_safe_full":
        import cupy

        partition_parents, union_iterations = _cupy_union_safe_full_partition_pairs(
            cupy,
            partition_count=partition_count,
            left_ids=summary_left,
            right_ids=summary_right,
            statuses=summary_status,
        )
        safe_skip_pairs = int(summary["metadata"]["status_counts"]["safe_skip_partition_pairs"])
        safe_full_pairs = int(summary["metadata"]["status_counts"]["safe_full_partition_pairs"])
        ambiguous_indices = cupy.where(summary_status == 2)[0]
        ambiguous_left_values = tuple(int(value) for value in cupy.asnumpy(summary_left[ambiguous_indices]).tolist())
        ambiguous_right_values = tuple(int(value) for value in cupy.asnumpy(summary_right[ambiguous_indices]).tolist())
        ambiguous_status_values = (2,) * len(ambiguous_left_values)
    else:
        partition_parents = list(range(partition_count))
        union_iterations = 0
        ambiguous_left_values = tuple(int(value) for value in _column_tuple(summary_left))
        ambiguous_right_values = tuple(int(value) for value in _column_tuple(summary_right))
        ambiguous_status_values = tuple(int(value) for value in _column_tuple(summary_status))
    radius_sq = radius * radius
    safe_skip_pairs = int(safe_skip_pairs) if partition_union_execution == "cupy_safe_full" else 0
    safe_full_pairs = int(safe_full_pairs) if partition_union_execution == "cupy_safe_full" else 0
    if not (partition_union_execution == "cupy_safe_full" and ambiguous_union_execution == "cupy_partition_points"):
        ambiguous_pairs = 0
        ambiguous_point_comparisons = 0
        ambiguous_positive_edges = 0
    for left, right, status in zip(
        ambiguous_left_values,
        ambiguous_right_values,
        ambiguous_status_values,
    ):
        left_id = int(left)
        right_id = int(right)
        status_id = int(status)
        if left_id < 0 or right_id < 0 or left_id >= partition_count or right_id >= partition_count:
            errors.append("near partition pair contains an out-of-range partition id")
            continue
        if status_id == 0:
            safe_skip_pairs += 1
            continue
        if status_id == 1:
            safe_full_pairs += 1
            _union_parent(partition_parents, left_id, right_id)
            continue
        if status_id != 2:
            errors.append("near_pair_status must be 0, 1, or 2")
            continue
        ambiguous_pairs += 1
        left_members = partitions[left_id]
        right_members = partitions[right_id]
        connected = False
        for left_point in left_members:
            for right_point in right_members:
                if left_id == right_id and right_point <= left_point:
                    continue
                ambiguous_point_comparisons += 1
                if _distance_sq_3d(points[left_point], points[right_point]) <= radius_sq:
                    connected = True
                    ambiguous_positive_edges += 1
                    break
            if connected:
                break
        if connected:
            _union_parent(partition_parents, left_id, right_id)

    if errors:
        return {
            "columns": {"point_ids": (), "component_labels": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_consumer_error",
                "errors": tuple(errors),
            },
        }

    partition_labels = _compact_component_labels(partition_parents)
    point_labels = tuple(partition_labels[partition_id] for partition_id in point_partition_ids)
    point_ids = tuple(_point_id(row, ordinal) for ordinal, row in enumerate(raw_rows))
    all_pairs_labels = None
    same_contract = None
    if validate_against_all_pairs:
        all_pairs_labels = _fixed_radius_component_labels_all_pairs_3d(points, radius)
        same_contract = point_labels == all_pairs_labels
    return {
        "columns": {
            "point_ids": point_ids,
            "component_labels": point_labels,
        },
        "metadata": {
            **base_metadata,
            "status": (
                "accept"
                if same_contract is None or same_contract
                else "reject_all_pairs_mismatch"
            ),
            "point_count": len(points),
            "partition_count": partition_count,
            "component_count": len(set(point_labels)),
            "same_contract_against_all_pairs": same_contract,
            "complete_candidate_coverage": True,
            "safe_skip_partition_pairs": safe_skip_pairs,
            "safe_full_partition_pairs": safe_full_pairs,
            "ambiguous_partition_pairs": ambiguous_pairs,
            "ambiguous_point_comparisons": ambiguous_point_comparisons,
            "ambiguous_positive_edges": ambiguous_positive_edges,
            "safe_full_partition_union_iterations": union_iterations,
            "device_ambiguous_union_used": (
                ambiguous_union_execution == "cupy_partition_points"
                and ambiguous_union_skipped_reason is None
            ),
            "ambiguous_union_skipped_reason": ambiguous_union_skipped_reason,
            "all_pairs_component_labels": all_pairs_labels,
        },
    }


def build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
    point_rows,
    *,
    radius: float,
    cell_factor: float = 0.125,
    pair_capacity: int | None = None,
    pair_enumeration: str = "device_bounded_offsets",
    partition_summary: dict[str, Any] | None = None,
    ambiguous_union_execution: str = "cupy_partition_points",
    validate_summary_same_contract: bool = True,
    validate_against_component_labels: bool = False,
) -> dict[str, Any]:
    """Executable CuPy preview for component-size signatures without host labels."""

    raw_rows = tuple(point_rows)
    points = tuple(_point_xyz(row) for row in raw_rows)
    if not points:
        raise ValueError("point_rows must contain at least one point")
    radius = float(radius)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    ambiguous_union_execution = str(ambiguous_union_execution)
    if ambiguous_union_execution != "cupy_partition_points":
        raise ValueError("component signature preview currently requires cupy_partition_points")
    if partition_summary is None:
        summary = build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            pair_capacity=pair_capacity,
            pair_enumeration=pair_enumeration,
        )
        partition_summary_reused = False
    else:
        summary = partition_summary
        partition_summary_reused = True
    if validate_summary_same_contract:
        summary_validation = validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            candidate=summary,
            float_abs_tol=1.0e-5,
        )
    else:
        summary_metadata = summary["metadata"]
        summary_validation = {
            "status": "accept",
            "reference": "fixed_radius_partition_convergence_summary_3d_timing_trusted_preview",
            "candidate_reference_contract": "fixed_radius_partition_convergence_summary_3d_same_contract_skipped_for_timing",
            "errors": (),
            "point_count": int(summary_metadata["point_count"]),
            "partition_count": int(summary_metadata["partition_count"]),
            "pair_count": int(summary_metadata["pair_count"]),
            "visible_pair_count": int(summary_metadata["visible_pair_count"]),
            "pair_capacity": int(summary_metadata["pair_capacity"]),
            "overflow": bool(summary_metadata["overflow"]),
            "complete_candidate_coverage": bool(summary_metadata["complete_candidate_coverage"]),
            "status_column_values": dict(summary_metadata["status_column_values"]),
            "status_counts": dict(summary_metadata["status_counts"]),
            "summary_same_contract_validation_skipped_for_timing": True,
        }
    base_metadata = {
        "reference": "fixed_radius_partition_convergence_component_signature_3d_cupy_preview",
        "partition_summary_validation": summary_validation,
        "summary_same_contract_validation_enabled": validate_summary_same_contract,
        "partition_summary_reused": partition_summary_reused,
        "partition_summary_pair_enumeration": summary["metadata"]["pair_enumeration"],
        "partition_summary_pair_capacity_source": summary["metadata"]["pair_capacity_source"],
        "partition_union_execution": "cupy_safe_full",
        "ambiguous_union_execution": ambiguous_union_execution,
        "label_materialization": "component_size_signature_only",
        "native_abi_added": False,
        "runtime_executable": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_engine_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "hidden_dispatch_allowed": False,
        "claim_boundary": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY,
    }
    if summary_validation["status"] != "accept":
        return {
            "columns": {"component_size_signature": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_mismatch",
                "errors": summary_validation["errors"],
            },
        }
    if bool(summary["metadata"].get("overflow", False)):
        return {
            "columns": {"component_size_signature": ()},
            "metadata": {
                **base_metadata,
                "status": "reject_partition_summary_overflow",
                "overflow": True,
                "complete_candidate_coverage": False,
                "errors": ("partition summary overflow prevents complete component signature",),
            },
        }

    import cupy

    summary_columns = dict(summary["columns"])
    partition_count = int(summary_validation["partition_count"])
    status_counts = dict(summary["metadata"]["status_counts"])
    ambiguous_pairs = int(status_counts["ambiguous_partition_pairs"])
    safe_skip_pairs = int(status_counts["safe_skip_partition_pairs"])
    safe_full_pairs = int(status_counts["safe_full_partition_pairs"])
    ambiguous_union_skipped_reason = None
    if ambiguous_pairs == 0:
        partition_parents_device, union_iterations = _cupy_union_safe_full_partition_pairs(
            cupy,
            partition_count=partition_count,
            left_ids=summary_columns["near_pair_left_partition_ids"],
            right_ids=summary_columns["near_pair_right_partition_ids"],
            statuses=summary_columns["near_pair_status"],
            return_device=True,
        )
        ambiguous_point_comparisons = 0
        ambiguous_positive_edges = 0
        ambiguous_union_skipped_reason = "no_ambiguous_partition_pairs"
    else:
        x_dev = cupy.asarray([point[0] for point in points], dtype=cupy.float64)
        y_dev = cupy.asarray([point[1] for point in points], dtype=cupy.float64)
        z_dev = cupy.asarray([point[2] for point in points], dtype=cupy.float64)
        (
            partition_parents_device,
            union_iterations,
            ambiguous_point_comparisons,
            ambiguous_positive_edges,
        ) = _cupy_union_partition_pairs_with_ambiguous_points(
            cupy,
            partition_count=partition_count,
            left_ids=summary_columns["near_pair_left_partition_ids"],
            right_ids=summary_columns["near_pair_right_partition_ids"],
            statuses=summary_columns["near_pair_status"],
            partition_offsets=summary_columns["partition_offsets"],
            partition_point_ordinals=summary_columns["partition_point_ordinals"],
            x=x_dev,
            y=y_dev,
            z=z_dev,
            radius_sq=radius * radius,
        )
    point_partition_ids = cupy.asarray(summary_columns["point_partition_ids"], dtype=cupy.uint32)
    component_roots = partition_parents_device[point_partition_ids]
    _, component_counts = cupy.unique(component_roots, return_counts=True)
    signature = tuple(
        int(value)
        for value in cupy.asnumpy(cupy.sort(component_counts.astype(cupy.uint32, copy=False))).tolist()
    )
    same_contract = None
    if validate_against_component_labels:
        labels = build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
            raw_rows,
            radius=radius,
            cell_factor=cell_factor,
            partition_summary=summary,
            partition_union_execution="cupy_safe_full",
            ambiguous_union_execution=ambiguous_union_execution,
            validate_summary_same_contract=False,
        )
        label_values = tuple(int(value) for value in labels["columns"]["component_labels"])
        expected = tuple(sorted(label_values.count(label) for label in set(label_values)))
        same_contract = signature == expected
    return {
        "columns": {
            "component_size_signature": signature,
        },
        "metadata": {
            **base_metadata,
            "status": (
                "accept"
                if same_contract is None or same_contract
                else "reject_component_label_signature_mismatch"
            ),
            "point_count": len(points),
            "partition_count": partition_count,
            "component_count": len(signature),
            "same_contract_against_component_labels": same_contract,
            "complete_candidate_coverage": True,
            "safe_skip_partition_pairs": safe_skip_pairs,
            "safe_full_partition_pairs": safe_full_pairs,
            "ambiguous_partition_pairs": ambiguous_pairs,
            "ambiguous_point_comparisons": ambiguous_point_comparisons,
            "ambiguous_positive_edges": ambiguous_positive_edges,
            "safe_full_partition_union_iterations": union_iterations,
            "device_ambiguous_union_used": ambiguous_union_skipped_reason is None,
            "ambiguous_union_skipped_reason": ambiguous_union_skipped_reason,
        },
    }


def _cupy_union_partition_pairs_with_ambiguous_points(
    cupy,
    *,
    partition_count: int,
    left_ids,
    right_ids,
    statuses,
    partition_offsets,
    partition_point_ordinals,
    x,
    y,
    z,
    radius_sq: float,
    max_iterations: int = 64,
):
    classify_kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void classify_ambiguous_partition_pairs_kernel(
            const unsigned int* left_ids,
            const unsigned int* right_ids,
            const unsigned int* statuses,
            unsigned int pair_count,
            const unsigned int* partition_offsets,
            const unsigned int* partition_point_ordinals,
            const double* x,
            const double* y,
            const double* z,
            double radius_sq,
            unsigned int* ambiguous_connected,
            unsigned int* comparison_count,
            unsigned int* positive_count)
        {
            unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx >= pair_count || statuses[idx] != 2u) return;
            unsigned int left = left_ids[idx];
            unsigned int right = right_ids[idx];
            unsigned int left_begin = partition_offsets[left];
            unsigned int left_end = partition_offsets[left + 1u];
            unsigned int right_begin = partition_offsets[right];
            unsigned int right_end = partition_offsets[right + 1u];
            unsigned int connected = 0u;
            for (unsigned int li = left_begin; li < left_end && connected == 0u; ++li) {
                unsigned int left_point = partition_point_ordinals[li];
                for (unsigned int ri = right_begin; ri < right_end; ++ri) {
                    unsigned int right_point = partition_point_ordinals[ri];
                    if (left == right && right_point <= left_point) continue;
                    atomicAdd(comparison_count, 1u);
                    double dx = x[left_point] - x[right_point];
                    double dy = y[left_point] - y[right_point];
                    double dz = z[left_point] - z[right_point];
                    double dist = dx * dx + dy * dy + dz * dz;
                    if (dist <= radius_sq) {
                        connected = 1u;
                        break;
                    }
                }
            }
            if (connected != 0u) {
                ambiguous_connected[idx] = 1u;
                atomicAdd(positive_count, 1u);
            }
        }
        ''',
        "classify_ambiguous_partition_pairs_kernel",
    )
    union_kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void union_partition_pairs_kernel(
            const unsigned int* left_ids,
            const unsigned int* right_ids,
            const unsigned int* statuses,
            const unsigned int* ambiguous_connected,
            unsigned int pair_count,
            unsigned int* parents,
            unsigned int* changed)
        {
            unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx >= pair_count) return;
            unsigned int status = statuses[idx];
            if (status != 1u && !(status == 2u && ambiguous_connected[idx] != 0u)) return;
            unsigned int left_root = left_ids[idx];
            unsigned int right_root = right_ids[idx];
            while (parents[left_root] != left_root) left_root = parents[left_root];
            while (parents[right_root] != right_root) right_root = parents[right_root];
            while (left_root != right_root) {
                unsigned int low = left_root < right_root ? left_root : right_root;
                unsigned int high = left_root < right_root ? right_root : left_root;
                unsigned int old = atomicMin(&parents[high], low);
                if (old == high) {
                    *changed = 1u;
                    break;
                }
                left_root = low;
                right_root = old;
                while (parents[left_root] != left_root) left_root = parents[left_root];
                while (parents[right_root] != right_root) right_root = parents[right_root];
            }
        }
        ''',
        "union_partition_pairs_kernel",
    )
    compress_kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void compress_partition_parents_kernel(unsigned int* parents, unsigned int partition_count)
        {
            unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx >= partition_count) return;
            unsigned int root = idx;
            while (parents[root] != root) root = parents[root];
            parents[idx] = root;
        }
        ''',
        "compress_partition_parents_kernel",
    )
    partition_count = int(partition_count)
    pair_count = int(statuses.size)
    parents = cupy.arange(partition_count, dtype=cupy.uint32)
    ambiguous_connected = cupy.zeros((pair_count,), dtype=cupy.uint32)
    comparison_count = cupy.zeros((1,), dtype=cupy.uint32)
    positive_count = cupy.zeros((1,), dtype=cupy.uint32)
    changed = cupy.zeros((1,), dtype=cupy.uint32)
    threads = 256
    pair_blocks = (max(1, (pair_count + threads - 1) // threads),)
    parent_blocks = (max(1, (partition_count + threads - 1) // threads),)
    classify_kernel(
        pair_blocks,
        (threads,),
        (
            left_ids,
            right_ids,
            statuses,
            cupy.uint32(pair_count),
            partition_offsets,
            partition_point_ordinals,
            x,
            y,
            z,
            float(radius_sq),
            ambiguous_connected,
            comparison_count,
            positive_count,
        ),
    )
    iterations = 0
    for iteration in range(int(max_iterations)):
        changed.fill(0)
        union_kernel(
            pair_blocks,
            (threads,),
            (
                left_ids,
                right_ids,
                statuses,
                ambiguous_connected,
                cupy.uint32(pair_count),
                parents,
                changed,
            ),
        )
        compress_kernel(parent_blocks, (threads,), (parents, cupy.uint32(partition_count)))
        cupy.cuda.get_current_stream().synchronize()
        iterations = iteration + 1
        if int(changed[0].item()) == 0:
            break
    else:
        raise RuntimeError("partition union did not converge")
    return (
        parents,
        iterations,
        int(comparison_count[0].item()),
        int(positive_count[0].item()),
    )


def _cupy_union_safe_full_partition_pairs(
    cupy,
    *,
    partition_count: int,
    left_ids,
    right_ids,
    statuses,
    max_iterations: int = 64,
    return_device: bool = False,
):
    kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void safe_full_union_kernel(
            const unsigned int* left_ids,
            const unsigned int* right_ids,
            const unsigned int* statuses,
            unsigned int pair_count,
            unsigned int* parents,
            unsigned int* changed)
        {
            unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx >= pair_count || statuses[idx] != 1u) return;
            unsigned int left = left_ids[idx];
            unsigned int right = right_ids[idx];
            unsigned int left_root = left;
            while (parents[left_root] != left_root) left_root = parents[left_root];
            unsigned int right_root = right;
            while (parents[right_root] != right_root) right_root = parents[right_root];
            while (left_root != right_root) {
                unsigned int low = left_root < right_root ? left_root : right_root;
                unsigned int high = left_root < right_root ? right_root : left_root;
                unsigned int old = atomicMin(&parents[high], low);
                if (old == high) {
                    *changed = 1u;
                    break;
                }
                left_root = low;
                right_root = old;
                while (parents[left_root] != left_root) left_root = parents[left_root];
                while (parents[right_root] != right_root) right_root = parents[right_root];
            }
        }
        ''',
        "safe_full_union_kernel",
    )
    compress_kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void compress_partition_parents_kernel(unsigned int* parents, unsigned int partition_count)
        {
            unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx >= partition_count) return;
            unsigned int root = idx;
            while (parents[root] != root) root = parents[root];
            parents[idx] = root;
        }
        ''',
        "compress_partition_parents_kernel",
    )
    partition_count = int(partition_count)
    if partition_count <= 0:
        raise ValueError("partition_count must be positive")
    pair_count = int(statuses.size)
    parents = cupy.arange(partition_count, dtype=cupy.uint32)
    changed = cupy.zeros((1,), dtype=cupy.uint32)
    threads = 256
    pair_blocks = (max(1, (pair_count + threads - 1) // threads),)
    parent_blocks = (max(1, (partition_count + threads - 1) // threads),)
    iterations = 0
    for iteration in range(int(max_iterations)):
        changed.fill(0)
        kernel(
            pair_blocks,
            (threads,),
            (
                left_ids,
                right_ids,
                statuses,
                cupy.uint32(pair_count),
                parents,
                changed,
            ),
        )
        compress_kernel(parent_blocks, (threads,), (parents, cupy.uint32(partition_count)))
        cupy.cuda.get_current_stream().synchronize()
        iterations = iteration + 1
        if int(changed[0].item()) == 0:
            break
    else:
        raise RuntimeError("safe-full partition union did not converge")
    if return_device:
        return parents, iterations
    return [int(value) for value in cupy.asnumpy(parents).tolist()], iterations


def _cupy_partition_pair_status_device_bounded_offsets(
    cupy,
    *,
    key_rows: list[tuple[int, int, int]],
    unique_cells,
    min_kx: int,
    min_ky: int,
    min_kz: int,
    dim_y: int,
    dim_z: int,
    aabb_min_x64,
    aabb_min_y64,
    aabb_min_z64,
    aabb_max_x64,
    aabb_max_y64,
    aabb_max_z64,
    max_offset: int,
    radius_sq: float,
    classification_tol: float,
    pair_capacity: int,
):
    kernel = cupy.RawKernel(
        r'''
        extern "C" __global__
        void partition_pair_status_kernel(
            const int* key_x,
            const int* key_y,
            const int* key_z,
            const long long* unique_cells,
            const double* min_x,
            const double* min_y,
            const double* min_z,
            const double* max_x,
            const double* max_y,
            const double* max_z,
            unsigned int partition_count,
            int min_kx,
            int min_ky,
            int min_kz,
            int dim_y,
            int dim_z,
            int max_offset,
            double radius_sq,
            double classification_tol,
            unsigned int capacity,
            unsigned int* left_out,
            unsigned int* right_out,
            unsigned int* status_out,
            unsigned int* row_count,
            unsigned int* overflow)
        {
            const unsigned long long offset_count =
                (unsigned long long)(2 * max_offset + 1)
                * (unsigned long long)(2 * max_offset + 1)
                * (unsigned long long)(2 * max_offset + 1);
            const unsigned long long total =
                (unsigned long long)partition_count * offset_count;
            unsigned long long linear =
                (unsigned long long)blockIdx.x * (unsigned long long)blockDim.x
                + (unsigned long long)threadIdx.x;
            if (linear >= total) return;
            const unsigned int left = (unsigned int)(linear / offset_count);
            unsigned long long rem = linear - (unsigned long long)left * offset_count;
            const int span = 2 * max_offset + 1;
            const int dx = (int)(rem / (unsigned long long)(span * span)) - max_offset;
            rem = rem % (unsigned long long)(span * span);
            const int dy = (int)(rem / (unsigned long long)span) - max_offset;
            const int dz = (int)(rem % (unsigned long long)span) - max_offset;
            const int tx = key_x[left] + dx;
            const int ty = key_y[left] + dy;
            const int tz = key_z[left] + dz;
            const long long lx = (long long)tx - (long long)min_kx;
            const long long ly = (long long)ty - (long long)min_ky;
            const long long lz = (long long)tz - (long long)min_kz;
            if (lx < 0 || ly < 0 || lz < 0 || ly >= dim_y || lz >= dim_z) return;
            const long long target = (lx * (long long)dim_y + ly) * (long long)dim_z + lz;
            int lo = 0;
            int hi = (int)partition_count;
            while (lo < hi) {
                const int mid = lo + ((hi - lo) >> 1);
                if (unique_cells[mid] < target) lo = mid + 1;
                else hi = mid;
            }
            if (lo >= (int)partition_count || unique_cells[lo] != target) return;
            const unsigned int right = (unsigned int)lo;
            if (right < left) return;
            double min_dist = 0.0;
            double delta = 0.0;
            if (max_x[left] < min_x[right]) delta = min_x[right] - max_x[left];
            else if (max_x[right] < min_x[left]) delta = min_x[left] - max_x[right];
            min_dist += delta * delta;
            delta = 0.0;
            if (max_y[left] < min_y[right]) delta = min_y[right] - max_y[left];
            else if (max_y[right] < min_y[left]) delta = min_y[left] - max_y[right];
            min_dist += delta * delta;
            delta = 0.0;
            if (max_z[left] < min_z[right]) delta = min_z[right] - max_z[left];
            else if (max_z[right] < min_z[left]) delta = min_z[left] - max_z[right];
            min_dist += delta * delta;
            double mdx1 = max_x[left] - min_x[right];
            if (mdx1 < 0.0) mdx1 = -mdx1;
            double mdx2 = max_x[right] - min_x[left];
            if (mdx2 < 0.0) mdx2 = -mdx2;
            double mdy1 = max_y[left] - min_y[right];
            if (mdy1 < 0.0) mdy1 = -mdy1;
            double mdy2 = max_y[right] - min_y[left];
            if (mdy2 < 0.0) mdy2 = -mdy2;
            double mdz1 = max_z[left] - min_z[right];
            if (mdz1 < 0.0) mdz1 = -mdz1;
            double mdz2 = max_z[right] - min_z[left];
            if (mdz2 < 0.0) mdz2 = -mdz2;
            const double max_dx = mdx1 > mdx2 ? mdx1 : mdx2;
            const double max_dy = mdy1 > mdy2 ? mdy1 : mdy2;
            const double max_dz = mdz1 > mdz2 ? mdz1 : mdz2;
            const double max_dist = max_dx * max_dx + max_dy * max_dy + max_dz * max_dz;
            unsigned int status = 2u;
            if (max_dist <= radius_sq - classification_tol) status = 1u;
            else if (min_dist > radius_sq + classification_tol) status = 0u;
            const unsigned int row = atomicAdd(row_count, 1u);
            if (row < capacity) {
                left_out[row] = left;
                right_out[row] = right;
                status_out[row] = status;
            } else {
                *overflow = 1u;
            }
        }
        ''',
        "partition_pair_status_kernel",
    )
    partition_count = len(key_rows)
    key_x = cupy.asarray([key[0] for key in key_rows], dtype=cupy.int32)
    key_y = cupy.asarray([key[1] for key in key_rows], dtype=cupy.int32)
    key_z = cupy.asarray([key[2] for key in key_rows], dtype=cupy.int32)
    left_out = cupy.zeros((pair_capacity,), dtype=cupy.uint32)
    right_out = cupy.zeros((pair_capacity,), dtype=cupy.uint32)
    status_out = cupy.zeros((pair_capacity,), dtype=cupy.uint32)
    row_count = cupy.zeros((1,), dtype=cupy.uint32)
    overflow = cupy.zeros((1,), dtype=cupy.uint32)
    offset_count = (2 * int(max_offset) + 1) ** 3
    total = max(1, int(partition_count) * int(offset_count))
    threads = 256
    blocks = ((total + threads - 1) // threads,)
    kernel(
        blocks,
        (threads,),
        (
            key_x,
            key_y,
            key_z,
            unique_cells,
            aabb_min_x64,
            aabb_min_y64,
            aabb_min_z64,
            aabb_max_x64,
            aabb_max_y64,
            aabb_max_z64,
            cupy.uint32(partition_count),
            int(min_kx),
            int(min_ky),
            int(min_kz),
            int(dim_y),
            int(dim_z),
            int(max_offset),
            float(radius_sq),
            float(classification_tol),
            cupy.uint32(pair_capacity),
            left_out,
            right_out,
            status_out,
            row_count,
            overflow,
        ),
    )
    cupy.cuda.get_current_stream().synchronize()
    attempted = int(row_count[0].item())
    visible = min(attempted, int(pair_capacity))
    left = left_out[:visible]
    right = right_out[:visible]
    status = status_out[:visible]
    if visible > 0:
        sort_key = left.astype(cupy.uint64) * cupy.uint64(max(1, partition_count)) + right.astype(cupy.uint64)
        order = cupy.argsort(sort_key)
        left = left[order]
        right = right[order]
        status = status[order]
    return left, right, status, attempted, visible, bool(int(overflow[0].item()))


def _unsupported_reason(*, backend: str, partner: str, strategy: str) -> str:
    if backend not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS:
        return f"unsupported backend {backend!r}; supported backends are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_BACKENDS}"
    if partner not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS:
        return f"unsupported partner {partner!r}; supported partners are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_PARTNERS}"
    if (
        strategy not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES
        and strategy not in V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES
    ):
        return f"unsupported strategy {strategy!r}; supported strategies are {V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES}"
    return ""


def _point_xyz(row) -> tuple[float, float, float]:
    if hasattr(row, "x") and hasattr(row, "y") and hasattr(row, "z"):
        return float(row.x), float(row.y), float(row.z)
    if isinstance(row, dict):
        return float(row["x"]), float(row["y"]), float(row["z"])
    values = tuple(row)
    if len(values) == 3:
        return float(values[0]), float(values[1]), float(values[2])
    if len(values) >= 4:
        return float(values[1]), float(values[2]), float(values[3])
    raise TypeError("point row must expose x/y/z fields or a 3/4-item sequence")


def _point_id(row, ordinal: int) -> int:
    if hasattr(row, "id"):
        return int(row.id)
    if isinstance(row, dict) and "id" in row:
        return int(row["id"])
    try:
        values = tuple(row)
    except TypeError:
        return int(ordinal)
    if len(values) >= 4:
        return int(values[0])
    return int(ordinal)


def _column_tuple(values) -> tuple[Any, ...]:
    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, list):
        return tuple(values)
    if isinstance(values, tuple):
        return values
    return tuple(values)


def _find_parent(parents: list[int], index: int) -> int:
    while parents[index] != index:
        index = parents[index]
    return index


def _union_parent(parents: list[int], left: int, right: int) -> None:
    left_root = _find_parent(parents, left)
    right_root = _find_parent(parents, right)
    if left_root == right_root:
        return
    if right_root < left_root:
        left_root, right_root = right_root, left_root
    parents[right_root] = left_root


def _compact_component_labels(parents: list[int]) -> tuple[int, ...]:
    root_to_label: dict[int, int] = {}
    labels: list[int] = []
    for ordinal in range(len(parents)):
        root = _find_parent(parents, ordinal)
        label = root_to_label.get(root)
        if label is None:
            label = len(root_to_label)
            root_to_label[root] = label
        labels.append(label)
    return tuple(labels)


def _fixed_radius_component_labels_all_pairs_3d(
    points: tuple[tuple[float, float, float], ...],
    radius: float,
) -> tuple[int, ...]:
    parents = list(range(len(points)))
    radius_sq = radius * radius
    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            if _distance_sq_3d(points[left], points[right]) <= radius_sq:
                _union_parent(parents, left, right)
    return _compact_component_labels(parents)


def _distance_sq_3d(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    dx = left[0] - right[0]
    dy = left[1] - right[1]
    dz = left[2] - right[2]
    return dx * dx + dy * dy + dz * dz


def _partition_key_3d(x: float, y: float, z: float, cell_size: float) -> tuple[int, int, int]:
    return (
        math.floor(x / cell_size),
        math.floor(y / cell_size),
        math.floor(z / cell_size),
    )


def _partition_aabb_min_distance_sq(left: dict[str, Any], right: dict[str, Any]) -> float:
    total = 0.0
    for min_left, max_left, min_right, max_right in (
        (left["min_x"], left["max_x"], right["min_x"], right["max_x"]),
        (left["min_y"], left["max_y"], right["min_y"], right["max_y"]),
        (left["min_z"], left["max_z"], right["min_z"], right["max_z"]),
    ):
        if max_left < min_right:
            delta = min_right - max_left
        elif max_right < min_left:
            delta = min_left - max_right
        else:
            delta = 0.0
        total += delta * delta
    return total


def _partition_aabb_max_distance_sq(left: dict[str, Any], right: dict[str, Any]) -> float:
    dx = max(abs(left["max_x"] - right["min_x"]), abs(right["max_x"] - left["min_x"]))
    dy = max(abs(left["max_y"] - right["min_y"]), abs(right["max_y"] - left["min_y"]))
    dz = max(abs(left["max_z"] - right["min_z"]), abs(right["max_z"] - left["min_z"]))
    return dx * dx + dy * dy + dz * dz


def _hybrid_partition_guidance_metadata() -> dict[str, Any]:
    return dict(V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE)


def _hybrid_runtime_status_metadata() -> dict[str, Any]:
    return {
        "planner_status": "candidate_requires_native_implementation",
        "planner_status_meaning": (
            "No promoted prepared/native/default route exists for partition_convergence_hybrid. "
            "Executable CuPy and Numba previews exist separately, and the CuPy prepared-summary "
            "preview remains candidate evidence only."
        ),
        "executable_preview_available": True,
        "prepared_front_door_runtime_executable": True,
        "prepared_front_door_runtime_status": "explicit_cupy_preview_not_promoted",
        "default_route_promoted": False,
        "partition_convergence_hybrid_promoted": False,
        "latest_preview_evidence_goals": ("Goal4040", "Goal4041", "Goal4062"),
        "promotion_blockers": V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PROMOTION_BLOCKERS,
        "next_engineering_target": (
            "fused resident component-label continuation or promoted native partition handle"
        ),
    }


def _front_door_metadata(
    plan: V28FixedRadiusGraphComponentPlan,
    *,
    lower_metadata: dict[str, Any],
    component_threshold: int,
    columns: dict[str, Any],
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
            "typed_result_stream": make_v2_8_fixed_radius_graph_component_typed_stream_contract(
                int(plan.point_count),
                stream_id="fixed_radius_graph_component_labels_3d_runtime",
                data_ptrs=_column_data_ptrs(columns),
                source_protocol=f"{plan.partner}_cuda_array_interface",
            ).to_metadata(),
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


def _column_data_ptrs(columns: dict[str, Any]) -> dict[str, int]:
    pointers: dict[str, int] = {}
    for name, column in columns.items():
        data = getattr(column, "data", None)
        ptr = getattr(data, "ptr", None)
        if ptr is not None:
            pointers[str(name)] = int(ptr)
            continue
        device_ptr = getattr(column, "device_ctypes_pointer", None)
        value = getattr(device_ptr, "value", None)
        if value is not None:
            pointers[str(name)] = int(value)
            continue
        data_ptr = getattr(column, "data_ptr", None)
        if data_ptr is not None:
            pointers[str(name)] = int(data_ptr)
    return pointers


__all__ = [
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CANDIDATE_STRATEGIES",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_STATUS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_FRONT_DOOR_VERSION",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PROMOTION_BLOCKERS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES",
    "V28FixedRadiusGraphComponentPlan",
    "V28PreparedFixedRadiusGraphComponentContinuation3D",
    "V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D",
    "build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d",
    "build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d",
    "build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d",
    "build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
    "build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d",
    "build_v2_8_fixed_radius_partition_convergence_summary_reference_3d",
    "describe_v2_8_fixed_radius_graph_component_front_door",
    "fixed_radius_graph_component_labels_3d_v2_8",
    "fixed_radius_graph_component_size_signature_3d_v2_8",
    "make_v2_8_fixed_radius_graph_component_typed_stream_contract",
    "make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract",
    "plan_v2_8_fixed_radius_graph_component_continuation",
    "prepare_v2_8_fixed_radius_graph_component_continuation_3d",
    "prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
    "run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d",
    "run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d",
    "validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d",
]
