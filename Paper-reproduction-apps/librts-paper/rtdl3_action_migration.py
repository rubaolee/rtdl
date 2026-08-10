"""App-owned LibRTS semantic adapter for the private RTDL 3.0 Action study."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_producer,
    compile_action_source,
    compile_bound_action_for_target,
    detect_action_target_profile,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase
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
from rtdsl.action_prepared import prepare_action_execution

from librts_reproduction import load_boxes


APP_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = APP_DIR / "data" / "fixtures"

CANONICAL_ALGORITHM_BINDINGS = {
    "aabb_overlap_filter": (
        "aabb_overlap.filter_bounded_emit_2d.v1",
        "nvidia.optix_traversal.v1",
    ),
    "prepared_aabb_query": (
        "aabb_index.prepared_query_2d.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("aabb_overlap_filter", "prepared_aabb_query")


def _canonical_authority_kwargs(target, algorithm: str) -> dict[str, str]:
    if target.production_selection_policy != "compiler_owned_default":
        return {}
    statement, backend = CANONICAL_ALGORITHM_BINDINGS[algorithm]
    return {
        "semantic_statement_stable_id": statement,
        "backend_contract_id": backend,
    }

ACTION_SOURCE = """
def action(event, params):
    query = event.query_id
    indexed = event.indexed_id
    overlap = event.overlap_area
    minimum = params.minimum_overlap
    eligible = overlap >= minimum
    require(eligible)
    emit("rows", query, indexed)
"""


class PreparedLibrtsAabbSession:
    """App-owned row projection around a compiler-owned prepared AABB session."""

    def __init__(self, prepared, planned, parameters, *, phase_trace=None) -> None:
        self._prepared = prepared
        self._planned = planned
        self._parameters = dict(parameters)
        self._phase_trace = phase_trace

    @property
    def query_count(self) -> int:
        return self._prepared.query_count

    def execute_boxes(self, query_boxes) -> dict[str, object]:
        ordinal = self._prepared.query_count
        with action_phase(
            self._phase_trace,
            "execute",
            label=f"prepared_aabb_filter_emit_batch_{ordinal}",
        ):
            query_result = self._prepared.execute_queries(
                tuple(query_boxes),
                extents={},
                parameters=self._parameters,
            )
        if self._phase_trace is not None and self._planned.lowered.backend == "optix":
            suffix = f"batch_{ordinal}"
            self._phase_trace.fold_device_operation(
                name=f"query_boxes_upload_{suffix}",
                kind="host_to_device_transfer",
                folded_into="execute",
                reason="prepared Action query owns query-box upload without an independent timer",
            )
            self._phase_trace.fold_device_operation(
                name=f"emitted_rows_download_{suffix}",
                kind="device_to_host_transfer",
                folded_into="execute",
                reason="prepared Action query returns host rows without an independent download timer",
            )
            self._phase_trace.fold_device_operation(
                name=f"emitted_rows_ready_wait_{suffix}",
                kind="device_synchronization_wait",
                folded_into="execute",
                reason="prepared Action query synchronizes before exposing emitted rows",
            )
        payload = query_result.payload
        return {
            "rows": tuple(payload["rows"]),
            "runtime_metadata": payload["metadata"],
            "query_metadata": query_result.to_metadata(),
        }

    def close(self) -> None:
        with action_phase(
            self._phase_trace,
            "backend_prepare",
            label="release_prepared_aabb_index",
        ):
            self._prepared.close()

    def to_metadata(self) -> dict[str, object]:
        return {
            "prepared_action": self._prepared.to_metadata(),
            "lowering": self._planned.lowered.to_metadata(),
            "application_selected_backend": False,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_compiler_boxes(
    indexed_boxes,
    *,
    minimum_overlap: float,
    row_capacity: int,
    phase_trace=None,
) -> PreparedLibrtsAabbSession:
    indexed_boxes = tuple(indexed_boxes)
    if not indexed_boxes:
        raise ValueError("at least one indexed box is required")
    if not isinstance(row_capacity, int) or isinstance(row_capacity, bool) or row_capacity < 0:
        raise ValueError("row_capacity must be a nonnegative integer")
    parameters = {
        "minimum_overlap": float(minimum_overlap),
        "row_capacity": row_capacity,
    }
    with action_phase(
        phase_trace, "action_compile_or_cache_hit", label="compile_action_source"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(
        phase_trace, "binding_certificate", label="bind_prepared_aabb_producer"
    ):
        bound = bind_action_producer(
            compiled, ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D
        )
    with action_phase(phase_trace, "physical_plan", label="target_probe_plan_and_lower"):
        target = detect_action_target_profile(cpu_reference_available=False)
        planned = compile_bound_action_for_target(
            bound,
            target,
            extents={},
            parameters={"row_capacity": row_capacity},
            **_canonical_authority_kwargs(target, "aabb_overlap_filter"),
        )
    with action_phase(phase_trace, "backend_prepare", label="prepare_aabb_index"):
        prepared = prepare_action_execution(
            planned,
            extents={},
            parameters=parameters,
            prepared_input=indexed_boxes,
            max_candidate_rows=row_capacity,
        )
    if phase_trace is not None:
        if planned.lowered.backend == "optix":
            phase_trace.fold_device_operation(
                name="indexed_boxes_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="prepared Action construction owns indexed-box upload without an independent timer",
            )
        else:
            for phase in (
                "host_to_device_transfer",
                "device_to_host_transfer",
                "device_synchronization_wait",
            ):
                phase_trace.mark_not_applicable(phase, reason="compiler selected a host backend")
    return PreparedLibrtsAabbSession(
        prepared,
        planned,
        parameters,
        phase_trace=phase_trace,
    )


@dataclass(frozen=True)
class IdentifiedBox2D:
    id: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "box_pair_event",
        (
            ActionField("query_id", U32),
            ActionField("indexed_id", U32),
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
    output_type = ActionRecordType(
        "pair_row",
        (ActionField("query_id", U32), ActionField("indexed_id", U32)),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=parameter_type,
        logical_event=LogicalEventContract(
            key_fields=("query_id", "indexed_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "rows",
                output_type,
                CapacityParam("row_capacity"),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("query_id"),
                    OrderKey("indexed_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
            ),
        ),
    )


def fixture_events() -> tuple[dict[str, object], ...]:
    boxes = load_boxes(FIXTURE_DIR / "tiny_boxes.wkt")
    queries = load_boxes(FIXTURE_DIR / "tiny_range_queries.wkt")
    return events_from_boxes(boxes, queries)


def events_from_boxes(boxes, queries) -> tuple[dict[str, object], ...]:
    boxes = tuple(boxes)
    queries = tuple(queries)
    if not boxes or not queries:
        raise ValueError("LibRTS indexed and query box sets must be nonempty")
    rows = []
    for query_id, indexed_id in itertools.product(range(len(queries)), range(len(boxes))):
        query = queries[query_id]
        indexed = boxes[indexed_id]
        intersects_inclusively = (
            query.min_x <= indexed.max_x
            and indexed.min_x <= query.max_x
            and query.min_y <= indexed.max_y
            and indexed.min_y <= query.max_y
        )
        if not intersects_inclusively:
            continue
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
                "query_id": query_id,
                "indexed_id": indexed_id,
                "overlap_area": float(np.float32(overlap_x * overlap_y)),
            }
        )
    return tuple(rows)


def _expected_rows_for_boxes(boxes, queries, *, minimum_overlap: float):
    rows = []
    for query_id, indexed_id in itertools.product(range(len(queries)), range(len(boxes))):
        query = queries[query_id]
        indexed = boxes[indexed_id]
        intersects = (
            query.min_x <= indexed.max_x
            and indexed.min_x <= query.max_x
            and query.min_y <= indexed.max_y
            and indexed.min_y <= query.max_y
        )
        if not intersects:
            continue
        overlap_x = max(0.0, min(query.max_x, indexed.max_x) - max(query.min_x, indexed.min_x))
        overlap_y = max(0.0, min(query.max_y, indexed.max_y) - max(query.min_y, indexed.min_y))
        overlap = float(np.float32(overlap_x * overlap_y))
        if overlap >= float(np.float32(minimum_overlap)):
            rows.append((query_id, indexed_id))
    return tuple(sorted(rows))


def _identified_box_rows(boxes) -> tuple[IdentifiedBox2D, ...]:
    return tuple(
        IdentifiedBox2D(index, box.min_x, box.min_y, box.max_x, box.max_y)
        for index, box in enumerate(boxes)
    )


def run_reference_boxes(boxes, queries, *, minimum_overlap: float = 0.0):
    boxes = tuple(boxes)
    queries = tuple(queries)
    events = events_from_boxes(boxes, queries)
    expected = _expected_rows_for_boxes(
        boxes, queries, minimum_overlap=minimum_overlap
    )
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    result = compiled.execute_reference(
        events,
        {"minimum_overlap": float(minimum_overlap), "row_capacity": len(boxes) * len(queries)},
    )
    actual = tuple(
        sorted((int(query), int(indexed)) for query, indexed in result.emitted_relations[0].rows)
    )
    return {
        "backend": "action_cpu_reference",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "indexed_count": len(boxes),
        "query_count": len(queries),
        "compiled_metadata": compiled.to_metadata(),
    }


def run_optix_boxes(
    boxes,
    queries,
    *,
    minimum_overlap: float = 0.0,
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
):
    trace = (
        ActionPhaseTrace(app="librts", route="prepared_aabb_filter_bounded_emit")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="identified_aabb_rows"):
        boxes = tuple(boxes)
        queries = tuple(queries)
        if not boxes or not queries:
            raise ValueError("LibRTS indexed and query box sets must be nonempty")
        indexed_box_rows = _identified_box_rows(boxes)
        query_box_rows = _identified_box_rows(queries)
    if trace is not None:
        trace.fold_phase(
            "event_producer",
            folded_into="execute",
            reason="AABB candidate traversal and Action filtering are fused in the selected backend",
        )
    session = prepare_compiler_boxes(
        indexed_box_rows,
        minimum_overlap=minimum_overlap,
        row_capacity=len(boxes) * len(queries),
        phase_trace=trace,
    )
    try:
        batch = session.execute_boxes(query_box_rows)
    finally:
        session.close()
    with action_phase(trace, "projection", label="canonical_aabb_relation_rows"):
        actual = tuple(
            sorted((int(query), int(indexed)) for query, indexed in batch["rows"])
        )
    if validate_against_reference:
        with action_phase(trace, "app_validation", label="reference_aabb_comparator"):
            expected = _expected_rows_for_boxes(
                boxes, queries, minimum_overlap=minimum_overlap
            )
    else:
        expected = None
        if trace is not None:
            trace.mark_not_applicable(
                "app_validation", reason="validate_against_reference is false"
            )
    phase_trace = trace.finish() if trace is not None else None
    session_metadata = session.to_metadata()
    return {
        "backend": f"action_{session_metadata['lowering']['backend']}_closed_boundary",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected if expected is not None else None,
        "reference_validation_performed": bool(validate_against_reference),
        "indexed_count": len(boxes),
        "query_count": len(queries),
        "lowering_metadata": session_metadata["lowering"],
        "runtime_metadata": batch["runtime_metadata"],
        "prepared_execution_metadata": session_metadata["prepared_action"],
        "prepared_query_metadata": batch["query_metadata"],
        "phase_trace": phase_trace,
    }


def run_local_semantic_pair() -> dict[str, object]:
    expected_payload = json.loads(
        (FIXTURE_DIR / "tiny_range_intersects_expected.json").read_text(
            encoding="utf-8"
        )
    )
    expected = tuple(tuple(int(value) for value in row) for row in expected_payload["candidate_id_rows"])
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    result = compiled.execute_reference(
        fixture_events(),
        {"minimum_overlap": 0.0, "row_capacity": len(expected)},
    )
    query_indexed_rows = result.emitted_relations[0].rows
    actual = tuple(
        sorted((int(query), int(indexed)) for query, indexed in query_indexed_rows)
    )
    boundary = boundary_touch_discriminator()
    boundary_result = compiled.execute_reference(
        ({"query_id": 0, "indexed_id": 0, "overlap_area": 0.0},),
        {"minimum_overlap": 0.0, "row_capacity": 1},
    )
    boundary_actual = tuple(boundary_result.emitted_relations[0].rows)
    boundary_matched = boundary_actual == boundary["inclusive_v2_expected_rows"]
    return {
        "schema": "rtdl.research.action.paper_app_pair.librts.v1",
        "app": "librts",
        "cohort": "cohort_2_seven_app_paired_migration",
        "v2_semantic_baseline": "goal5456_tiny_range_intersects_and_goal5525_strongest_closeout",
        "semantic_scope": "inclusive_range_intersects_with_closed_overlap_threshold",
        "action_pattern": "aabb_filter_bounded_emit",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "fixture_has_zero_area_boundary_discriminator": True,
        "boundary_touch_rows": boundary_actual,
        "boundary_touch_matched": boundary_matched,
        "full_inclusive_boundary_semantics_claimed": boundary_matched,
        "compiled_metadata": compiled.to_metadata(),
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def _identified_boxes(path: Path) -> tuple[IdentifiedBox2D, ...]:
    return tuple(
        IdentifiedBox2D(index, box.min_x, box.min_y, box.max_x, box.max_y)
        for index, box in enumerate(load_boxes(path))
    )


def boundary_touch_discriminator() -> dict[str, object]:
    indexed = (IdentifiedBox2D(0, 0.0, 0.0, 1.0, 1.0),)
    queries = (IdentifiedBox2D(0, 1.0, 0.0, 2.0, 1.0),)
    return {
        "indexed_boxes": indexed,
        "query_boxes": queries,
        "inclusive_v2_expected_rows": ((0, 0),),
        "closed_boundary_action_expected_rows": ((0, 0),),
        "distinguishes_inclusive_from_strict_overlap": True,
    }


def run_optix_semantic_pair() -> dict[str, object]:
    expected_payload = json.loads(
        (FIXTURE_DIR / "tiny_range_intersects_expected.json").read_text(
            encoding="utf-8"
        )
    )
    expected = tuple(
        tuple(int(value) for value in row)
        for row in expected_payload["candidate_id_rows"]
    )
    session = prepare_compiler_boxes(
        _identified_boxes(FIXTURE_DIR / "tiny_boxes.wkt"),
        minimum_overlap=0.0,
        row_capacity=len(expected),
    )
    try:
        batch = session.execute_boxes(
            _identified_boxes(FIXTURE_DIR / "tiny_range_queries.wkt")
        )
    finally:
        session.close()
    actual = tuple(sorted((int(query), int(indexed)) for query, indexed in batch["rows"]))
    session_metadata = session.to_metadata()

    discriminator = boundary_touch_discriminator()
    boundary_session = prepare_compiler_boxes(
        discriminator["indexed_boxes"],
        minimum_overlap=0.0,
        row_capacity=1,
    )
    try:
        boundary_batch = boundary_session.execute_boxes(discriminator["query_boxes"])
    finally:
        boundary_session.close()
    boundary_actual = tuple(boundary_batch["rows"])
    boundary_matched = boundary_actual == discriminator["inclusive_v2_expected_rows"]
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.librts.v1",
        "app": "librts",
        "backend": "optix",
        "action_pattern": "aabb_filter_bounded_emit",
        "semantic_scope": "inclusive_range_intersects_with_closed_overlap_threshold",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "boundary_discriminator": {
            "inclusive_v2_expected_rows": discriminator["inclusive_v2_expected_rows"],
            "closed_action_actual_rows": boundary_actual,
            "boundary_matched": boundary_matched,
        },
        "full_inclusive_boundary_semantics_claimed": boundary_matched,
        "generic_capability": "aabb_overlap_boundary_policy",
        "lowering_metadata": session_metadata["lowering"],
        "runtime_metadata": batch["runtime_metadata"],
        "prepared_execution_metadata": session_metadata["prepared_action"],
        "prepared_query_metadata": batch["query_metadata"],
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "IdentifiedBox2D",
    "PreparedLibrtsAabbSession",
    "action_contract",
    "events_from_boxes",
    "prepare_compiler_boxes",
    "run_local_semantic_pair",
    "run_optix_boxes",
    "run_optix_semantic_pair",
    "run_reference_boxes",
)
