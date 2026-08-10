"""Private RTDL 3.0 research consumer; excluded from public v2 release artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import itertools

import numpy as np

from rtdsl.action_api import (
    ActionProducerKind,
    ActionTargetProfile,
    CompiledAction,
    bind_action_event_columns,
    bind_action_producer,
    compile_action_source,
    compile_bound_action_for_target,
    lower_action,
    prepare_bound_numba_action_columns,
)
from rtdsl.action_prepared import prepare_action_execution
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_embree_lowering import (
    prepare_embree_action_aabb_filter_bounded_emit_2d,
)
from rtdsl.action_ir import (
    F32,
    U32,
    ActionEmitSpec,
    ActionField,
    ActionRecordType,
    CapacityParam,
    DeliveryEnforcement,
    DuplicatePolicy,
    LogicalEventContract,
    OrderKey,
    OrderKeyRole,
    OutputOrderKind,
    PhysicalDelivery,
)
from rtdsl.action_numba_continuation import (
    execute_numba_action_continuation,
)
from rtdsl.action_optix_lowering import prepare_optix_action_aabb_filter_bounded_emit_2d


ACTION_SOURCE = """
def action(event, params):
    probe = event.probe_id
    item = event.object_id
    area = event.overlap_area
    threshold = params.minimum_overlap
    eligible = area > threshold
    require(eligible)
    emit("rows", probe, item)
"""

@dataclass(frozen=True)
class Box2D:
    id: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float


INDEXED_BOXES = (
    Box2D(10, 0.0, 0.0, 2.0, 2.0),
    Box2D(20, 3.0, 0.0, 4.0, 1.0),
)
QUERY_BOXES = (
    Box2D(100, 1.0, 1.0, 2.5, 2.5),
    Box2D(101, 2.0, 0.0, 3.0, 1.0),
    Box2D(102, 3.2, 0.2, 3.8, 0.8),
)
SECOND_QUERY_BOXES = (
    Box2D(200, 0.25, 0.25, 1.25, 1.25),
    Box2D(201, 4.5, 4.5, 5.0, 5.0),
    Box2D(202, 3.1, 0.1, 3.9, 0.9),
)
EXPECTED_ROWS = ((100, 10), (102, 20))
SECOND_EXPECTED_ROWS = ((200, 10), (202, 20))


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "box_pair_event",
        (
            ActionField("probe_id", U32),
            ActionField("object_id", U32),
            ActionField("overlap_area", F32),
        ),
    )
    parameter_type = ActionRecordType(
        "parameters",
        (
            ActionField("minimum_overlap", F32),
            ActionField("row_capacity", U32, nonnegative=True),
        ),
    )
    output = ActionRecordType(
        "pair_row",
        (ActionField("probe_id", U32), ActionField("object_id", U32)),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=parameter_type,
        logical_event=LogicalEventContract(
            key_fields=("probe_id", "object_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "rows",
                output,
                CapacityParam("row_capacity"),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("probe_id"),
                    OrderKey("object_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
            ),
        ),
    )


def compile_contact_action() -> CompiledAction:
    return compile_action_source(ACTION_SOURCE, action_contract())


def events():
    rows = []
    for query, indexed in itertools.product(QUERY_BOXES, INDEXED_BOXES):
        overlap_x = max(
            0.0,
            min(query.max_x, indexed.max_x) - max(query.min_x, indexed.min_x),
        )
        overlap_y = max(
            0.0,
            min(query.max_y, indexed.max_y) - max(query.min_y, indexed.min_y),
        )
        rows.append(
            {
                "probe_id": query.id,
                "object_id": indexed.id,
                "overlap_area": np.float32(overlap_x * overlap_y).item(),
            }
        )
    return tuple(rows)


def parameters() -> dict[str, object]:
    return {"minimum_overlap": np.float32(0.0).item(), "row_capacity": 2}


def event_columns(rows=None) -> dict[str, np.ndarray]:
    resolved = events() if rows is None else tuple(rows)
    return {
        field: np.asarray([row[field] for row in resolved], dtype=dtype)
        for field, dtype in (
            ("probe_id", np.uint32),
            ("object_id", np.uint32),
            ("overlap_area", np.float32),
        )
    }


def run_reference() -> tuple[tuple[int, int], ...]:
    relation = compile_contact_action().execute_reference(events(), parameters()).emitted_relations[0]
    return relation.rows  # type: ignore[return-value]


def run_numba() -> tuple[tuple[int, int], ...]:
    compiled = compile_contact_action()
    rows = events()
    columns = event_columns(rows)
    lowered = lower_action(
        bind_action_event_columns(
            compiled,
            columns,
            ordering_fields=("probe_id", "object_id"),
        ),
        backend="numba",
    )
    prepared = prepare_bound_numba_action_columns(lowered, columns, parameters())
    result = execute_numba_action_continuation(prepared, extents={})
    try:
        return result.to_host_relation().rows  # type: ignore[return-value]
    finally:
        result.close()
        prepared.close()


def run_optix() -> tuple[tuple[int, int], ...]:
    lowered = lower_action(
        bind_action_producer(
            compile_contact_action(),
            ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D,
        ),
        backend="optix",
    )
    with prepare_optix_action_aabb_filter_bounded_emit_2d(
        lowered.program,
        INDEXED_BOXES,
    ) as prepared:
        return prepared.run(QUERY_BOXES, parameters())["rows"]


def run_embree() -> tuple[tuple[int, int], ...]:
    lowered = lower_action(
        bind_action_producer(
            compile_contact_action(),
            ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D,
        ),
        backend="embree",
    )
    with prepare_embree_action_aabb_filter_bounded_emit_2d(
        lowered.program,
        INDEXED_BOXES,
        max_candidate_rows=len(INDEXED_BOXES) * len(QUERY_BOXES),
    ) as prepared:
        return prepared.run(QUERY_BOXES, parameters())["rows"]


def run_prepared_facility_batches() -> dict[str, object]:
    """Exercise two distinct demand batches over one compiler-owned box index."""

    bound = bind_action_producer(
        compile_contact_action(),
        ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D,
    )
    planned = compile_bound_action_for_target(
        bound,
        ActionTargetProfile(optix_available=True, cpu_reference_available=False),
        extents={},
        parameters={"row_capacity": 2},
    )
    with prepare_action_execution(
        planned,
        extents={},
        parameters=parameters(),
        prepared_input=INDEXED_BOXES,
    ) as prepared:
        first = prepared.execute_queries(
            QUERY_BOXES,
            extents={},
            parameters=parameters(),
        )
        repeated = prepared.execute_queries(
            SECOND_QUERY_BOXES,
            extents={},
            parameters=parameters(),
        )
        first_rows = tuple(first.payload["rows"])
        repeated_rows = tuple(repeated.payload["rows"])
        return {
            "first_rows": first_rows,
            "repeated_rows": repeated_rows,
            "first_matched": first_rows == EXPECTED_ROWS,
            "repeated_matched": repeated_rows == SECOND_EXPECTED_ROWS,
            "prepared_metadata": prepared.to_metadata(),
            "first_query_metadata": first.to_metadata(),
            "repeated_query_metadata": repeated.to_metadata(),
        }
