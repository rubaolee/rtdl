"""Independent non-paper consumer for exact worst-served facility evidence.

This application-owned front door deliberately does not import X-HD.  It
expresses the generic per-demand nearest-facility state that RTDL composes with
the compiler-owned global maximum/witness reducer.
"""

from __future__ import annotations

import numpy as np

from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_producer,
    compile_action_source,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_ir import (
    ActionField,
    ActionRecordType,
    ActionScalarLiteral,
    ActionStateSpec,
    DeliveryEnforcement,
    F64,
    LogicalEventContract,
    NumericContract,
    PhysicalDelivery,
    StateScope,
    TerminationProofKind,
    TerminationProofSpec,
    U32,
)


CONSUMER_IDENTITY = "bounded_facility_assignment.worst_served_facility.v1"

ACTION_SOURCE = """
def action(event, params):
    service_distance = event.distance
    facility = event.candidate_id
    current_service_distance = read_state("best_distance")
    closer_facility = service_distance < current_service_distance
    require(closer_facility)
    write_state("best_distance", service_distance)
    write_state("best_id", facility)
    terminate("facility_nearest_fixed")
"""


def action_contract() -> RestrictedActionFrontendContract:
    return RestrictedActionFrontendContract(
        event_type=ActionRecordType(
            "facility_service_candidate",
            (
                ActionField("query_id", U32),
                ActionField("candidate_id", U32),
                ActionField("distance", F64),
            ),
        ),
        parameter_type=ActionRecordType("facility_parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("query_id", "candidate_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        states=(
            ActionStateSpec(
                "best_distance",
                F64,
                StateScope.PER_QUERY,
                ActionScalarLiteral.from_python(F64, float("inf")),
                ("query_id",),
            ),
            ActionStateSpec(
                "best_id",
                U32,
                StateScope.PER_QUERY,
                ActionScalarLiteral.from_python(U32, (1 << 32) - 1),
                ("query_id",),
            ),
        ),
        termination_proofs=(
            TerminationProofSpec(
                name="facility_nearest_fixed",
                kind=TerminationProofKind.MONOTONE_BOUND,
                certificate="query-local-lower-bound-certificate-v1",
                state_name="best_distance",
                order_independent=True,
                unseen_cannot_improve=True,
            ),
        ),
        numeric_contract=NumericContract(allow_infinity=True),
    )


def compile_bound_worst_served_facility():
    """Compile and bind this consumer's own Action to the generic producer."""

    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_producer(
        compiled,
        ActionProducerKind.CERTIFIED_NEAREST_STATE_3D,
    )
    return compiled, bound


def functional_fixture() -> dict[str, np.ndarray]:
    """Return an authored demand/facility slice with non-row logical IDs."""

    return {
        "demand_points": np.asarray(
            [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [6.0, 0.0, 0.0]],
            dtype=np.float64,
        ),
        "demand_ids": np.asarray([101, 105, 109], dtype=np.int64),
        "facility_points": np.asarray(
            [[0.0, 0.0, 0.0], [4.0, 0.0, 0.0]],
            dtype=np.float64,
        ),
        "facility_ids": np.asarray([200, 201], dtype=np.int64),
    }


def project_witness(
    witness: dict[str, object],
    demand_ids: np.ndarray,
) -> dict[str, object]:
    """Project RTDL's dense query-row witness to application demand identity."""

    source_row = int(witness["source_id"])
    if source_row < 0 or source_row >= int(demand_ids.shape[0]):
        raise ValueError("facility witness source row is outside demand IDs")
    return {
        "demand_id": int(demand_ids[source_row]),
        "facility_id": int(witness["item_id"]),
        "service_distance": float(witness["value"]),
    }


__all__ = (
    "ACTION_SOURCE",
    "CONSUMER_IDENTITY",
    "action_contract",
    "compile_bound_worst_served_facility",
    "functional_fixture",
    "project_witness",
)
