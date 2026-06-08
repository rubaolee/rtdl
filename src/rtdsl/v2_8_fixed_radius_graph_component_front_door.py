from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .partner_adapters import PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D
from .partner_adapters import PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D
from .partner_adapters import prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
from .partner_adapters import radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns
from .partner_adapters import radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
from .v2_8_typed_result_stream import V28TypedResultStreamContract
from .v2_8_typed_result_stream import make_typed_result_stream_contract
from .v2_8_typed_result_stream import typed_result_column
from .v2_8_typed_result_stream import typed_result_status_columns


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
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS = (
    "Goal3999",
    "Goal4001",
    "Goal4002",
    "Goal4004",
    "Goal4007",
    "Goal4009",
    "Goal4011",
)
V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE = MappingProxyType({
    "recommended_tested_cell_factor": "radius_x_0.125",
    "dense_cell_pair_matrix_allowed": False,
    "required_partition_pair_enumeration": (
        "compressed_occupied_partition_keys_with_bounded_near_offsets"
    ),
    "required_device_resident_columns": (
        "point_partition_ids",
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


def _hybrid_partition_guidance_metadata() -> dict[str, Any]:
    return dict(V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE)


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
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_OPERATION",
    "V2_8_FIXED_RADIUS_GRAPH_COMPONENT_REJECTED_DEFAULT_STRATEGIES",
    "V28FixedRadiusGraphComponentPlan",
    "V28PreparedFixedRadiusGraphComponentContinuation3D",
    "describe_v2_8_fixed_radius_graph_component_front_door",
    "fixed_radius_graph_component_labels_3d_v2_8",
    "make_v2_8_fixed_radius_graph_component_typed_stream_contract",
    "make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract",
    "plan_v2_8_fixed_radius_graph_component_continuation",
    "prepare_v2_8_fixed_radius_graph_component_continuation_3d",
]
