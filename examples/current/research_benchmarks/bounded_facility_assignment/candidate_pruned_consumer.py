"""Non-paper consumer of generic exact bounded top-K point selection."""

from __future__ import annotations

import numpy as np

from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_producer,
    compile_action_source,
    detect_action_target_profile,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_ir import (
    F32,
    U32,
    ActionEmitSpec,
    ActionField,
    ActionRecordType,
    BoundedSelectionSpec,
    CapacityExtent,
    CapacityMul,
    CapacityParam,
    DeliveryEnforcement,
    DuplicatePolicy,
    ExtentKind,
    LogicalEventContract,
    OrderKey,
    OrderKeyRole,
    OutputOrderKind,
    PhysicalDelivery,
)
from rtdsl.action_physical_registry import (
    plan_registered_point_bounded_selection,
)
from rtdsl.action_prepared import prepare_action_execution
from rtdsl.direct_optix_physical import (
    prepare_direct_optix_bounded_selection_3d,
)
from rtdsl.optix_runtime import pack_points


ACTION_SOURCE = """
def action(event, params):
    demand = event.demand_id
    facility = event.facility_id
    distance = event.distance
    eligible = distance > params.minimum and distance < params.maximum
    require(eligible)
    emit("assignments", demand, facility, distance)
"""


def action_contract() -> RestrictedActionFrontendContract:
    return RestrictedActionFrontendContract(
        event_type=ActionRecordType(
            "facility_candidate",
            (
                ActionField("demand_id", U32),
                ActionField("facility_id", U32),
                ActionField("distance", F32),
            ),
        ),
        parameter_type=ActionRecordType(
            "facility_policy",
            (
                ActionField("limit", U32, nonnegative=True),
                ActionField("minimum", F32),
                ActionField("maximum", F32),
            ),
        ),
        logical_event=LogicalEventContract(
            key_fields=("demand_id", "facility_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "assignments",
                ActionRecordType(
                    "facility_assignment",
                    (
                        ActionField("demand_id", U32),
                        ActionField("facility_id", U32),
                        ActionField("distance", F32),
                    ),
                ),
                CapacityMul(
                    CapacityExtent(ExtentKind.QUERY_COUNT),
                    CapacityParam("limit"),
                ),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("demand_id"),
                    OrderKey("distance"),
                    OrderKey("facility_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
                selection=BoundedSelectionSpec(
                    scope_key_fields=("demand_id",),
                    scope_extent=ExtentKind.QUERY_COUNT,
                    limit=CapacityParam("limit"),
                    order_keys=(
                        OrderKey("distance"),
                        OrderKey(
                            "facility_id",
                            role=OrderKeyRole.ITEM_ID,
                        ),
                    ),
                ),
            ),
        ),
    )


def _pack(points: np.ndarray):
    values = np.ascontiguousarray(points, dtype=np.float64)
    if values.ndim != 2 or values.shape[1:] != (3,):
        raise ValueError("facility/demand points must be Nx3")
    return pack_points(
        ids=np.arange(values.shape[0], dtype=np.uint32),
        x=values[:, 0],
        y=values[:, 1],
        z=values[:, 2],
        dimension=3,
    )


def run_candidate_pruned_facility_assignment(
    facilities,
    demands,
    *,
    limit: int,
    minimum: float,
    maximum: float,
) -> dict[str, object]:
    packed_facilities = _pack(np.asarray(facilities))
    packed_demands = _pack(np.asarray(demands))
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_producer(
        compiled,
        ActionProducerKind.PREPARED_POINT_CANDIDATES_3D,
    )
    parameters = {
        "limit": int(limit),
        "minimum": float(minimum),
        "maximum": float(maximum),
    }
    planned = plan_registered_point_bounded_selection(
        bound,
        detect_action_target_profile(
            producer_kind=ActionProducerKind.PREPARED_POINT_CANDIDATES_3D,
            cpu_reference_available=False,
        ),
        prepared_search_points=packed_facilities,
        query_points=packed_demands,
        extents={ExtentKind.QUERY_COUNT: packed_demands.count},
        parameters=parameters,
    )
    prepared = prepare_action_execution(
        planned,
        extents={ExtentKind.QUERY_COUNT: packed_demands.count},
        parameters=parameters,
        prepared_input=packed_facilities,
        max_distance_bound=float(maximum),
    )
    try:
        result = prepared.execute_queries(
            packed_demands,
            extents={ExtentKind.QUERY_COUNT: packed_demands.count},
            parameters=parameters,
        )
    finally:
        prepared.close()
    columns = result.payload["columns"]
    rows = tuple(
        (
            int(demand_id),
            int(facility_id),
            float(np.float32(distance)),
        )
        for demand_id, facility_id, distance in zip(
            columns["demand_id"],
            columns["facility_id"],
            columns["distance"],
            strict=True,
        )
    )
    return {
        "rows": rows,
        "metadata": result.payload["metadata"],
        "selected_backend": planned.plan.selected_backend,
        "selected_template": planned.lowered.template_kind,
    }


def _reference_facility_rows(
    facilities: np.ndarray,
    demands: np.ndarray,
    *,
    limit: int,
    minimum: float,
    maximum: float,
) -> tuple[tuple[int, int, float], ...]:
    rows: list[tuple[int, int, float]] = []
    for demand_id, demand in enumerate(demands):
        candidates: list[tuple[float, int]] = []
        for facility_id, facility in enumerate(facilities):
            delta = np.asarray(facility, dtype=np.float32) - np.asarray(
                demand, dtype=np.float32
            )
            distance_sq = np.float32(
                np.float32(delta[0] * delta[0])
                + np.float32(delta[1] * delta[1])
                + np.float32(delta[2] * delta[2])
            )
            distance = float(np.float32(np.sqrt(distance_sq)))
            if float(minimum) < distance < float(maximum):
                candidates.append((distance, facility_id))
        for distance, facility_id in sorted(candidates)[: int(limit)]:
            rows.append((demand_id, facility_id, distance))
    return tuple(rows)


def run_direct_true_optix_facility_assignment(
    facilities,
    demands,
    *,
    limit: int,
    minimum: float,
    maximum: float,
) -> dict[str, object]:
    """Distinct non-paper consumer of the generic direct physical owner."""

    facility_values = np.ascontiguousarray(facilities, dtype=np.float32)
    demand_values = np.ascontiguousarray(demands, dtype=np.float32)
    packed_facilities = _pack(facility_values)
    packed_demands = _pack(demand_values)
    with prepare_direct_optix_bounded_selection_3d(
        packed_facilities,
        max_distance_bound=float(maximum),
    ) as prepared:
        physical = prepared.run(
            packed_demands,
            minimum_distance=float(minimum),
            maximum_distance=float(maximum),
            k=int(limit),
            minimum_boundary="open",
            maximum_boundary="open",
        )
    rows = tuple(
        (int(demand_id), int(facility_id), float(np.float32(distance)))
        for demand_id, facility_id, distance in physical["rows"]
    )
    expected = _reference_facility_rows(
        facility_values,
        demand_values,
        limit=int(limit),
        minimum=float(minimum),
        maximum=float(maximum),
    )
    return {
        "rows": rows,
        "expected_rows": expected,
        "matched": rows == expected,
        "metadata": physical["metadata"],
        "physical_family": "action_bounded_selection_3d",
        "consumer_contract": "bounded_facility_candidate_assignment.v1",
        "paper_or_application_identity_used_for_core_dispatch": False,
    }


__all__ = (
    "ACTION_SOURCE",
    "action_contract",
    "run_candidate_pruned_facility_assignment",
    "run_direct_true_optix_facility_assignment",
)
