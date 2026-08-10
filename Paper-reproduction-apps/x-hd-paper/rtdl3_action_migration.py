"""App-owned X-HD semantic adapter for the private RTDL 3.0 Action study."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import rtdsl as rt
from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_event_columns,
    bind_action_producer,
    compile_action_source,
    compile_bound_action_for_target,
    detect_action_target_profile,
    validate_bound_action_event_columns,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_composition import ActionConsumerCompositionKind
from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase
from rtdsl.action_prepared import (
    PreparedCertifiedNearestGridPayload3D,
    prepare_action_execution,
)
from rtdsl.action_ir import (
    F64,
    U32,
    ActionField,
    ActionRecordType,
    ActionScalarLiteral,
    ActionStateSpec,
    DeliveryEnforcement,
    LogicalEventContract,
    NumericContract,
    PhysicalDelivery,
    StateScope,
    TerminationProofKind,
    TerminationProofSpec,
)
from rtdsl.action_numba_continuation import (
    execute_numba_certified_query_min_state,
    prepare_numba_certified_query_min_columns,
    reduce_numba_certified_query_min_global_max_witness,
)


APP_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = APP_DIR / "data" / "fixtures"
RESULTS_DIR = APP_DIR / "results"

# Both algorithms are supported, but the paper application selects which one
# it requests.  Canonical resolution never chooses between them.
CANONICAL_ALGORITHM_BINDINGS = {
    "certified_nearest_state_exact_witness": (
        "nearest_state.frontier_seeded_exact.v1",
        "nvidia.optix_traversal.v1",
    ),
    "cell_mbr_exact_witness": (
        "nearest_state.cell_mbr_exact_witness.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("cell_mbr_exact_witness",)
SUPPORTED_ALTERNATIVE_PAPER_ALGORITHMS = (
    "certified_nearest_state_exact_witness",
)


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
    distance = event.distance
    candidate = event.candidate_id
    best = read_state("best_distance")
    improves = distance < best
    require(improves)
    write_state("best_distance", distance)
    write_state("best_id", candidate)
    terminate("done")
"""


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "nearest_event",
        (
            ActionField("query_id", U32),
            ActionField("candidate_id", U32),
            ActionField("distance", F64),
        ),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=ActionRecordType("parameters", ()),
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
                name="done",
                kind=TerminationProofKind.MONOTONE_BOUND,
                certificate="query-local-lower-bound-certificate-v1",
                state_name="best_distance",
                order_independent=True,
                unseen_cannot_improve=True,
            ),
        ),
        numeric_contract=NumericContract(allow_infinity=True),
    )


def _load_points(path: Path) -> tuple[tuple[float, float], ...]:
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        value = line.strip()
        if not value:
            continue
        if not value.startswith("POINT (") or not value.endswith(")"):
            raise ValueError(f"bounded Action adapter expects POINT WKT: {value!r}")
        coordinates = value[len("POINT (") : -1].split()
        if len(coordinates) != 2:
            raise ValueError(f"bounded Action adapter expects 2-D points: {value!r}")
        rows.append((float(coordinates[0]), float(coordinates[1])))
    return tuple(rows)


def event_columns() -> dict[str, np.ndarray]:
    sources = _load_points(FIXTURE_DIR / "directed2d_asymmetric_a.wkt")
    targets = _load_points(FIXTURE_DIR / "directed2d_asymmetric_b.wkt")
    return event_columns_from_points(sources, targets)


def event_columns_from_points(sources, targets) -> dict[str, np.ndarray]:
    sources = tuple(tuple(float(value) for value in point) for point in sources)
    targets = tuple(tuple(float(value) for value in point) for point in targets)
    if not sources or not targets:
        raise ValueError("X-HD source and target point sets must be nonempty")
    dimensions = len(sources[0])
    if dimensions not in {2, 3}:
        raise ValueError("X-HD V3 point rows must be 2-D or 3-D")
    if any(len(point) != dimensions for point in (*sources, *targets)):
        raise ValueError("X-HD source and target rows must share one dimension")
    rows = []
    for query_id, source in enumerate(sources):
        for candidate_id, target in enumerate(targets):
            distance_sq = np.float64(0.0)
            for dimension in range(dimensions):
                delta = np.float64(source[dimension] - target[dimension])
                distance_sq = np.float64(distance_sq + np.float64(delta * delta))
            distance = np.float64(np.sqrt(distance_sq))
            rows.append((query_id, candidate_id, distance))
    rows.sort(key=lambda row: (row[0], float(row[2]), row[1]))
    return {
        "query_id": np.asarray([row[0] for row in rows], dtype=np.uint32),
        "candidate_id": np.asarray([row[1] for row in rows], dtype=np.uint32),
        "distance": np.asarray([row[2] for row in rows], dtype=np.float64),
    }


def _expected_from_columns(columns: dict[str, np.ndarray], *, query_count: int):
    rows = rt.PartnerCandidateRows(
        query_ids=np.asarray(columns["query_id"], dtype=np.int64),
        primitive_ids=np.asarray(columns["candidate_id"], dtype=np.int64),
        values=np.asarray(columns["distance"], dtype=np.float64),
    )
    nearest = rt.nearest_witness_numpy_columns(
        rows,
        np.arange(query_count, dtype=np.int64),
        group_count=query_count,
        return_metadata=True,
    )
    return rt.max_nearest_distance_witness_numpy_columns(
        nearest["columns"],
        group_ids=np.arange(query_count, dtype=np.int64),
        return_metadata=True,
    )


def run_reference_points(sources, targets) -> dict[str, object]:
    sources = tuple(sources)
    columns = event_columns_from_points(sources, targets)
    compiled, bound = _compiled_and_bound()
    states = bound.execute_reference(_events(columns), {}).states
    actual = _directed_witness(states)
    expected = _expected_from_columns(columns, query_count=len(sources))
    return {
        "backend": "action_cpu_plus_generic_max_nearest",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "source_count": len(sources),
        "target_count": len(tuple(targets)),
        "compiled_metadata": compiled.to_metadata(),
    }


def run_numba_resident_points(
    sources,
    targets,
    *,
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
) -> dict[str, object]:
    trace = (
        ActionPhaseTrace(app="x_hd", route="resident_min_state_global_max_witness")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="freeze_source_target_points"):
        sources = tuple(sources)
        targets = tuple(targets)
    with action_phase(trace, "event_producer", label="cartesian_distance_columns"):
        columns = event_columns_from_points(sources, targets)
    with action_phase(
        trace, "action_compile_or_cache_hit", label="compile_action_source"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(
        trace, "binding_certificate", label="typed_column_digest_duplicate_and_order_binding"
    ):
        bound = bind_action_event_columns(
            compiled,
            columns,
            producer_kind=ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS,
            ordering_fields=("query_id", "distance", "candidate_id"),
        )
    with action_phase(trace, "physical_plan", label="target_probe_plan_and_lower"):
        lowered = compile_bound_action_for_target(
            bound,
            detect_action_target_profile(cpu_reference_available=False),
            extents={"query_count": len(sources)},
            parameters={},
        ).lowered
    with action_phase(trace, "backend_prepare", label="prepare_numba_min_state"):
        validate_bound_action_event_columns(lowered, columns)
        prepared = prepare_numba_certified_query_min_columns(
            lowered.program, columns, query_count=len(sources)
        )
    if trace is not None:
        trace.fold_device_operation(
            name="distance_columns_upload",
            kind="host_to_device_transfer",
            folded_into="backend_prepare",
            reason="Numba prepare uploads Cartesian columns without an independent transfer timer",
        )
    with action_phase(trace, "execute", label="numba_query_min_state_kernel"):
        state_result = execute_numba_certified_query_min_state(prepared)
    reduced = None
    try:
        with action_phase(trace, "execute", label="numba_global_max_witness_kernel"):
            reduced = reduce_numba_certified_query_min_global_max_witness(state_result)
    finally:
        with action_phase(trace, "backend_prepare", label="release_numba_min_state"):
            state_result.close()
            prepared.close()
    try:
        with action_phase(trace, "projection", label="device_witness_to_host"):
            actual = reduced.to_host_witness()
            composition_metadata = reduced.to_metadata()
    finally:
        with action_phase(trace, "backend_prepare", label="release_global_reducer"):
            reduced.close()
    if trace is not None:
        trace.fold_device_operation(
            name="global_witness_download",
            kind="device_to_host_transfer",
            folded_into="projection",
            reason="to_host_witness performs the device download without an independent timer",
        )
        trace.fold_device_operation(
            name="global_witness_ready_wait",
            kind="device_synchronization_wait",
            folded_into="projection",
            reason="to_host_witness waits for device completion before returning host values",
        )
    if validate_against_reference:
        with action_phase(trace, "app_validation", label="exact_nearest_reference"):
            expected = _expected_from_columns(columns, query_count=len(sources))
    else:
        expected = None
        if trace is not None:
            trace.mark_not_applicable(
                "app_validation", reason="validate_against_reference is false"
            )
    phase_trace = trace.finish() if trace is not None else None
    return {
        "backend": "resident_action_state_plus_device_global_reducer",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected) if expected is not None else None,
        "reference_validation_performed": bool(validate_against_reference),
        "source_count": len(sources),
        "target_count": len(targets),
        "lowering_metadata": lowered.to_metadata(),
        "composition_metadata": composition_metadata,
        "phase_trace": phase_trace,
    }


def run_scalable_compiler_points(
    sources,
    targets,
    *,
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
    grid_shape=(32, 32, 32),
) -> dict[str, object]:
    """Run the exact O(query)-state physical producer without Cartesian rows."""

    trace = (
        ActionPhaseTrace(app="x_hd", route="certified_nearest_state_global_max_witness")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="contiguous_source_target_matrices"):
        source_matrix = np.ascontiguousarray(np.asarray(sources, dtype=np.float64))
        target_matrix = np.ascontiguousarray(np.asarray(targets, dtype=np.float64))
        if source_matrix.ndim != 2 or target_matrix.ndim != 2:
            raise ValueError("X-HD scalable V3 input must be two point matrices")
        if source_matrix.shape[1:] != (3,) or target_matrix.shape[1:] != (3,):
            raise ValueError("X-HD scalable V3 producer requires 3-D points")
        if source_matrix.shape[0] == 0 or target_matrix.shape[0] == 0:
            raise ValueError("X-HD source and target point sets must be nonempty")
    with action_phase(trace, "action_compile_or_cache_hit", label="compile_action_source"):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(trace, "binding_certificate", label="bind_certified_nearest_state_producer"):
        bound = bind_action_producer(
            compiled,
            ActionProducerKind.CERTIFIED_NEAREST_STATE_3D,
        )
    with action_phase(trace, "physical_plan", label="target_probe_plan_and_lower"):
        target = detect_action_target_profile(
            producer_kind=ActionProducerKind.CERTIFIED_NEAREST_STATE_3D,
            cpu_reference_available=True,
        )
        planned = compile_bound_action_for_target(
            bound,
            target,
            extents={
                "query_count": int(source_matrix.shape[0]),
                "primitive_count": int(target_matrix.shape[0]),
            },
            parameters={},
            consumer_composition=(
                ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
            ),
            **_canonical_authority_kwargs(target, "cell_mbr_exact_witness"),
        )
    prepared = None
    query_result = None
    with action_phase(trace, "backend_prepare", label="prepare_resident_target_grid"):
        prepared_payload = PreparedCertifiedNearestGridPayload3D(
            target_points=target_matrix,
            grid_shape=tuple(int(value) for value in grid_shape),
            # Formal performance workers use the pinned external comparator.
            # Keep the CPU sample comparator (and its bounded projection) out of
            # the primary timer in that regime.
            independent_validation_sample_count=(
                64 if validate_against_reference else 0
            ),
        )
        prepared = prepare_action_execution(
            planned,
            extents={"query_count": int(source_matrix.shape[0])},
            parameters={},
            prepared_input=prepared_payload,
        )
    try:
        with action_phase(
            trace,
            "event_producer",
            label="resident_grid_branch_bound_state_to_global_witness",
        ):
            query_result = prepared.execute_queries(
                source_matrix,
                extents={"query_count": int(source_matrix.shape[0])},
                parameters={},
            )
        physical = query_result.payload
    finally:
        if prepared is not None:
            with action_phase(trace, "backend_prepare", label="release_resident_target_grid"):
                prepared.close()
    prepared_metadata = prepared.to_metadata()
    if trace is not None:
        validation_projection_rows = int(
            physical["metadata"]["bounded_validation_sample_rows"]
        )
        trace.fold_phase(
            "execute",
            folded_into="event_producer",
            reason="exact nearest-state and resident global reduction are reported by the closed producer execution",
        )
        trace.fold_phase(
            "projection",
            folded_into="event_producer",
            reason=(
                "producer execution projects one witness and "
                f"{validation_projection_rows} independent-validation rows"
            ),
        )
        if physical["metadata"]["physical_placement"] == "device_continuation":
            trace.fold_device_operation(
                name="prepared_target_grid_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="compiler-owned prepare uploads targets once and constructs the resident grid",
            )
            trace.fold_device_operation(
                name="query_batch_upload",
                kind="host_to_device_transfer",
                folded_into="event_producer",
                reason="each execution uploads only its immutable query batch",
            )
            trace.fold_device_operation(
                name=(
                    "bounded_witness_and_validation_download"
                    if validation_projection_rows
                    else "bounded_witness_only_download"
                ),
                kind="device_to_host_transfer",
                folded_into="event_producer",
                reason=(
                    "the resident reducer projects one witness and exactly "
                    f"{validation_projection_rows} independent-validation rows"
                ),
            )
            trace.fold_device_operation(
                name="prepared_default_stream_completion_wait",
                kind="device_synchronization_wait",
                folded_into="event_producer",
                reason="the closed ABI synchronizes the default stream before bounded projection returns",
            )
        else:
            trace.mark_not_applicable(
                "host_to_device_transfer", reason="compiler selected CPU reference fallback"
            )
            trace.mark_not_applicable(
                "device_to_host_transfer", reason="compiler selected CPU reference fallback"
            )
            trace.mark_not_applicable(
                "device_synchronization_wait", reason="compiler selected CPU reference fallback"
            )
    actual = physical["actual"]
    if validate_against_reference:
        pair_count = int(source_matrix.shape[0]) * int(target_matrix.shape[0])
        if pair_count > 1_000_000:
            raise ValueError(
                "Cartesian reference validation is bounded to one million pairs; "
                "large inputs require a pinned external comparator"
            )
        with action_phase(trace, "app_validation", label="bounded_exact_cartesian_reference"):
            expected_columns = event_columns_from_points(source_matrix, target_matrix)
            expected = _expected_from_columns(
                expected_columns,
                query_count=int(source_matrix.shape[0]),
            )
    else:
        expected = None
        if trace is not None:
            trace.mark_not_applicable(
                "app_validation",
                reason="large-input validation is delegated to the pinned Goal5263 comparator",
            )
    phase_trace = trace.finish() if trace is not None else None
    return {
        "backend": "compiler_selected_certified_nearest_state_plus_global_max_witness",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected) if expected is not None else None,
        "reference_validation_performed": bool(validate_against_reference),
        "source_count": int(source_matrix.shape[0]),
        "target_count": int(target_matrix.shape[0]),
        "planned_lowering_metadata": planned.to_metadata(),
        "prepared_action_metadata": prepared_metadata,
        "physical_execution_metadata": physical["metadata"],
        "complete_cartesian_relation_materialized": False,
        "materialized_candidate_row_count": 0,
        "phase_trace": phase_trace,
    }


def _events(columns: dict[str, np.ndarray]) -> tuple[dict[str, object], ...]:
    return tuple(
        {name: values[index].item() for name, values in columns.items()}
        for index in range(len(columns["query_id"]))
    )


def _directed_witness(states) -> dict[str, object]:
    rows_by_state = {state.name: state.rows for state in states}
    distance_rows = rows_by_state["best_distance"]
    candidate_rows = rows_by_state["best_id"]
    distance_by_query = {int(key[0]): float(value) for key, value in distance_rows}
    candidate_by_query = {int(key[0]): int(value) for key, value in candidate_rows}
    query_ids = tuple(sorted(distance_by_query))
    nearest = {
        "source_ids": np.asarray(query_ids, dtype=np.int64),
        "nearest_item_ids": np.asarray(
            [candidate_by_query[query_id] for query_id in query_ids], dtype=np.int64
        ),
        "nearest_distances": np.asarray(
            [distance_by_query[query_id] for query_id in query_ids], dtype=np.float64
        ),
    }
    return rt.max_nearest_distance_witness_numpy_columns(
        nearest,
        group_ids=np.asarray(query_ids, dtype=np.int64),
        return_metadata=True,
    )


def _expected() -> dict[str, object]:
    payload = json.loads(
        (RESULTS_DIR / "directed2d_asymmetric_rtdl_route_gate_summary.json").read_text(
            encoding="utf-8"
        )
    )
    directed = payload["rtdl_route"]["directed_a_to_b"]
    return {
        "source_id": int(directed["source_id"]),
        "item_id": int(directed["target_id"]),
        "value": float(directed["distance"]),
    }


def _matched(actual: dict[str, object], expected: dict[str, object]) -> bool:
    return (
        int(actual["source_id"]) == int(expected["source_id"])
        and int(actual["item_id"]) == int(expected["item_id"])
        and math.isclose(
            float(actual["value"]),
            float(expected["value"]),
            rel_tol=0.0,
            abs_tol=1e-6,
        )
    )


def _compiled_and_bound():
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    return compiled, bind_action_producer(
        compiled, ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS
    )


def _compiled_and_column_bound(columns):
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    return compiled, bind_action_event_columns(
        compiled,
        columns,
        producer_kind=ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS,
        ordering_fields=("query_id", "distance", "candidate_id"),
    )


def run_local_semantic_pair() -> dict[str, object]:
    compiled, bound = _compiled_and_bound()
    columns = event_columns()
    states = bound.execute_reference(_events(columns), {}).states
    actual = _directed_witness(states)
    expected = _expected()
    return {
        "schema": "rtdl.research.action.paper_app_pair.xhd.v1",
        "app": "x_hd",
        "backend": "cpu_reference_plus_generic_numpy_argmax",
        "action_pattern": "certified_query_min_state",
        "pipeline": [
            "restricted_action_certified_query_min",
            "generic_max_nearest_distance_witness",
        ],
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "compiled_metadata": compiled.to_metadata(),
        "one_action_covers_whole_pipeline": False,
        "cross_query_reduction_device_resident": False,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_numba_semantic_pair() -> dict[str, object]:
    columns = event_columns()
    compiled, bound = _compiled_and_column_bound(columns)
    lowered = compile_bound_action_for_target(
        bound,
        detect_action_target_profile(cpu_reference_available=False),
        extents={"query_count": 2},
        parameters={},
    ).lowered
    validate_bound_action_event_columns(lowered, columns)
    prepared = prepare_numba_certified_query_min_columns(
        lowered.program, columns, query_count=2
    )
    result = execute_numba_certified_query_min_state(prepared)
    try:
        states = result.to_host_states()
        state_metadata = result.to_metadata()
    finally:
        result.close()
        prepared.close()
    actual = _directed_witness(states)
    expected = _expected()
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.xhd.v1",
        "app": "x_hd",
        "backend": "numba_action_plus_host_numpy_argmax",
        "action_pattern": "certified_query_min_state",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "lowering_metadata": lowered.to_metadata(),
        "state_metadata": state_metadata,
        "one_action_covers_whole_pipeline": False,
        "cross_query_reduction_device_resident": False,
        "explicit_host_projection_used": True,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_numba_resident_composition_pair() -> dict[str, object]:
    columns = event_columns()
    compiled, bound = _compiled_and_column_bound(columns)
    lowered = compile_bound_action_for_target(
        bound,
        detect_action_target_profile(cpu_reference_available=False),
        extents={"query_count": 2},
        parameters={},
    ).lowered
    validate_bound_action_event_columns(lowered, columns)
    prepared = prepare_numba_certified_query_min_columns(
        lowered.program, columns, query_count=2
    )
    state_result = execute_numba_certified_query_min_state(prepared)
    reduced = None
    try:
        reduced = reduce_numba_certified_query_min_global_max_witness(state_result)
    finally:
        state_result.close()
        prepared.close()
    try:
        actual = reduced.to_host_witness()
        composition_metadata = reduced.to_metadata()
    finally:
        reduced.close()
    expected = _expected()
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.xhd_resident_composition.v1",
        "app": "x_hd",
        "backend": "numba_action_state_to_numba_global_max",
        "action_pattern": "certified_query_min_state",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "lowering_metadata": lowered.to_metadata(),
        "composition_metadata": composition_metadata,
        "one_action_covers_whole_pipeline": False,
        "cross_query_reduction_device_resident": True,
        "full_state_host_projection_used": False,
        "bounded_witness_host_projection_used": True,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "SUPPORTED_ALTERNATIVE_PAPER_ALGORITHMS",
    "action_contract",
    "event_columns_from_points",
    "run_local_semantic_pair",
    "run_numba_resident_composition_pair",
    "run_numba_resident_points",
    "run_numba_semantic_pair",
    "run_reference_points",
    "run_scalable_compiler_points",
)
