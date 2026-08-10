"""App-owned RTNN semantic adapter for the private RTDL 3.0 Action study."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import time

import numpy as np

from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_producer,
    compile_action_source,
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
    canonical_float32_key,
)
from rtdsl.action_physical_registry import plan_registered_point_bounded_selection
from rtdsl.action_physical_registry import (
    plan_registered_point_bounded_selection_candidate_for_functional_validation,
)
from rtdsl.action_prepared import prepare_action_execution
from rtdsl.direct_optix_physical import (
    prepare_direct_optix_bounded_selection_3d,
)
from rtdsl.optix_runtime import pack_points


APP_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = APP_DIR / "data" / "fixtures" / "goal5531_exact_knn"

# The application owns this algorithm choice.  The compiler may verify and
# lower it, but it may not substitute a different paper algorithm.
CANONICAL_ALGORITHM_BINDINGS = {
    "ranked_distance_window": (
        "point_selection.spatial_bounded.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("ranked_distance_window",)


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
    candidate = event.candidate_id
    distance = event.distance
    minimum = params.min_distance
    maximum = params.max_distance
    above_minimum = distance > minimum
    below_maximum = distance < maximum
    eligible = above_minimum and below_maximum
    require(eligible)
    emit("rows", query, candidate, distance)
"""


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "candidate_event",
        (
            ActionField("query_id", U32),
            ActionField("candidate_id", U32),
            ActionField("distance", F32),
        ),
    )
    parameter_type = ActionRecordType(
        "parameters",
        (
            ActionField("k", U32, nonnegative=True),
            ActionField("min_distance", F32),
            ActionField("max_distance", F32),
        ),
    )
    output_type = ActionRecordType(
        "ranked_row",
        (
            ActionField("query_id", U32),
            ActionField("candidate_id", U32),
            ActionField("distance", F32),
        ),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=parameter_type,
        logical_event=LogicalEventContract(
            key_fields=("query_id", "candidate_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "rows",
                output_type,
                CapacityMul(
                    CapacityExtent(ExtentKind.QUERY_COUNT), CapacityParam("k")
                ),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("query_id"),
                    OrderKey("distance"),
                    OrderKey("candidate_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
                selection=BoundedSelectionSpec(
                    scope_key_fields=("query_id",),
                    scope_extent=ExtentKind.QUERY_COUNT,
                    limit=CapacityParam("k"),
                    order_keys=(
                        OrderKey("distance"),
                        OrderKey("candidate_id", role=OrderKeyRole.ITEM_ID),
                    ),
                ),
            ),
        ),
    )


def _load_xyz(path: Path) -> tuple[tuple[float, float, float], ...]:
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        if not line.strip():
            continue
        values = tuple(float(value) for value in line.split(","))
        if len(values) != 3:
            raise ValueError(f"expected three coordinates in {path}")
        rows.append(values)
    return tuple(rows)


def _distance_f32(left, right) -> float:
    dx = np.float32(left[0] - right[0])
    dy = np.float32(left[1] - right[1])
    dz = np.float32(left[2] - right[2])
    distance_sq = np.float32(
        np.float32(dx * dx) + np.float32(dy * dy) + np.float32(dz * dz)
    )
    return float(np.float32(np.sqrt(distance_sq)))


def fixture_events() -> tuple[dict[str, object], ...]:
    search = _load_xyz(FIXTURE_DIR / "search.xyz")
    queries = _load_xyz(FIXTURE_DIR / "queries.xyz")
    return tuple(
        {
            "query_id": query_id,
            "candidate_id": candidate_id,
            "distance": _distance_f32(query, candidate),
        }
        for query_id, query in enumerate(queries)
        for candidate_id, candidate in enumerate(search)
    )


def events_from_points(search_points, query_points) -> tuple[dict[str, object], ...]:
    search = tuple(tuple(float(value) for value in point) for point in search_points)
    queries = tuple(tuple(float(value) for value in point) for point in query_points)
    if not search or not queries:
        raise ValueError("RTNN search and query point sets must be nonempty")
    if any(len(point) != 3 for point in (*search, *queries)):
        raise ValueError("RTNN V3 point inputs must be 3-D")
    return tuple(
        {
            "query_id": query_id,
            "candidate_id": candidate_id,
            "distance": _distance_f32(query, candidate),
        }
        for query_id, query in enumerate(queries)
        for candidate_id, candidate in enumerate(search)
    )


def _expected_for_points(search_points, query_points, *, k, min_distance, max_distance):
    rows = []
    for query_id, query in enumerate(query_points):
        candidates = []
        for candidate_id, candidate in enumerate(search_points):
            distance = _distance_f32(query, candidate)
            if float(min_distance) < distance < float(max_distance):
                candidates.append((distance, candidate_id))
        for rank, (distance, candidate_id) in enumerate(
            sorted(candidates, key=lambda row: (row[0], row[1]))[: int(k)], start=1
        ):
            rows.append(
                (
                    query_id,
                    candidate_id,
                    rank,
                    float(np.float32(np.float32(distance) * np.float32(distance))),
                )
            )
    return tuple(rows)


def _pack_point_rows(points):
    values = np.asarray(points, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] != 3:
        raise ValueError("RTNN V3 point inputs must be nonempty Nx3 rows")
    return pack_points(
        ids=np.arange(values.shape[0], dtype=np.uint32),
        x=values[:, 0],
        y=values[:, 1],
        z=values[:, 2],
        dimension=3,
    )


def _canonicalize_relation_rows(rows) -> tuple[tuple[int, int, float], ...]:
    normalized = tuple(rows)
    return tuple(
        sorted(
            normalized,
            key=lambda row: (
                row[0],
                canonical_float32_key(row[2]),
                row[1],
            ),
        )
    )


def _relation_rows_from_columns(columns) -> tuple[tuple[int, int, float], ...]:
    query_ids = np.asarray(columns["query_id"])
    candidate_ids = np.asarray(columns["candidate_id"])
    distances = np.asarray(columns["distance"])
    expected_dtypes = {
        "query_id": np.dtype(np.uint32),
        "candidate_id": np.dtype(np.uint32),
        "distance": np.dtype(np.float32),
    }
    actual_dtypes = {
        "query_id": query_ids.dtype,
        "candidate_id": candidate_ids.dtype,
        "distance": distances.dtype,
    }
    for name, expected_dtype in expected_dtypes.items():
        if actual_dtypes[name] != expected_dtype:
            raise TypeError(
                f"compiler result {name} must have exact dtype {expected_dtype}; "
                f"got {actual_dtypes[name]}"
            )
    if not (
        query_ids.ndim == candidate_ids.ndim == distances.ndim == 1
        and query_ids.shape == candidate_ids.shape == distances.shape
    ):
        raise ValueError("compiler result columns must be equal-length 1-D arrays")
    rows = tuple(
        (int(query_id), int(candidate_id), float(distance))
        for query_id, candidate_id, distance in zip(
            query_ids, candidate_ids, distances, strict=True
        )
    )
    return _canonicalize_relation_rows(rows)


def _relation_rows_from_rows(rows) -> tuple[tuple[int, int, float], ...]:
    normalized: list[tuple[int, int, float]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise TypeError(f"compiler result row {index} must be a three-field row")
        query_id, candidate_id, distance = row
        for name, value in (
            ("query_id", query_id),
            ("candidate_id", candidate_id),
        ):
            if isinstance(value, np.uint32):
                continue
            if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
                raise TypeError(
                    f"compiler result row {index} {name} must be uint32-valued "
                    "without coercion"
                )
        if isinstance(distance, np.float32):
            normalized_distance = float(distance)
        elif type(distance) is float:
            normalized_distance = float(distance)
            if float(np.float32(normalized_distance)) != normalized_distance:
                raise TypeError(
                    f"compiler result row {index} distance must be exactly float32"
                )
        else:
            raise TypeError(
                f"compiler result row {index} distance must be float32 without coercion"
            )
        normalized.append((int(query_id), int(candidate_id), normalized_distance))
    return _canonicalize_relation_rows(normalized)


def _canonical_rows_from_columns(columns) -> tuple[tuple[int, int, int, float], ...]:
    return _canonical_rows(_relation_rows_from_columns(columns))


def run_reference_points(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float,
    max_distance: float,
) -> dict[str, object]:
    search = tuple(search_points)
    queries = tuple(query_points)
    events = events_from_points(search, queries)
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    result = compiled.execute_reference(
        events,
        {"k": int(k), "min_distance": float(min_distance), "max_distance": float(max_distance)},
        extents={ExtentKind.QUERY_COUNT: len(queries)},
    )
    actual = _canonical_rows(result.emitted_relations[0].rows)
    expected = _expected_for_points(
        search, queries, k=k, min_distance=min_distance, max_distance=max_distance
    )
    return {
        "backend": "action_cpu_reference",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "search_count": len(search),
        "query_count": len(queries),
        "compiled_metadata": compiled.to_metadata(),
    }


def run_compiler_points(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float,
    max_distance: float,
    collect_phase_trace: bool = False,
    validate_reference: bool = True,
) -> dict[str, object]:
    trace = (
        ActionPhaseTrace(app="rtnn", route="prepared_point_bounded_selection")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="pack_search_and_query_points"):
        search = np.asarray(search_points, dtype=np.float32)
        queries = np.asarray(query_points, dtype=np.float32)
        if search.ndim != 2 or search.shape[1:] != (3,) or search.shape[0] == 0:
            raise ValueError("RTNN search points must be a nonempty Nx3 matrix")
        if queries.ndim != 2 or queries.shape[1:] != (3,) or queries.shape[0] == 0:
            raise ValueError("RTNN query points must be a nonempty Nx3 matrix")
        packed_search = _pack_point_rows(search)
        packed_queries = _pack_point_rows(queries)
    with action_phase(trace, "event_producer", label="logical_candidate_rows"):
        logical_event_count_upper_bound = int(search.shape[0]) * int(queries.shape[0])
    with action_phase(
        trace, "action_compile_or_cache_hit", label="compile_action_source"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(trace, "binding_certificate", label="bind_prepared_point_producer"):
        bound = bind_action_producer(
            compiled, ActionProducerKind.PREPARED_POINT_CANDIDATES_3D
        )
    with action_phase(trace, "physical_plan", label="target_probe_plan_and_lower"):
        target = detect_action_target_profile(
            producer_kind=ActionProducerKind.PREPARED_POINT_CANDIDATES_3D,
            cpu_reference_available=False,
        )
        planned = plan_registered_point_bounded_selection(
            bound,
            target,
            prepared_search_points=packed_search,
            query_points=packed_queries,
            extents={ExtentKind.QUERY_COUNT: int(queries.shape[0])},
            parameters={
                "k": int(k),
                "min_distance": float(min_distance),
                "max_distance": float(max_distance),
            },
            **_canonical_authority_kwargs(target, "ranked_distance_window"),
        )
    parameters = {
        "k": int(k),
        "min_distance": float(min_distance),
        "max_distance": float(max_distance),
    }
    with action_phase(trace, "backend_prepare", label="prepare_compiler_selected_point_index"):
        prepared = prepare_action_execution(
            planned,
            extents={ExtentKind.QUERY_COUNT: int(queries.shape[0])},
            parameters=parameters,
            prepared_input=packed_search,
            max_distance_bound=float(max_distance),
        )
    if trace is not None:
        trace.fold_device_operation(
            name="search_points_upload",
            kind="host_to_device_transfer",
            folded_into="backend_prepare",
            reason="OptiX prepare owns the indexed-point upload without an independent timer",
        )
    try:
        with action_phase(trace, "execute", label="compiler_query_and_bounded_selection"):
            query_result = prepared.execute_queries(
                packed_queries,
                parameters=parameters,
                extents={ExtentKind.QUERY_COUNT: int(queries.shape[0])},
            )
    finally:
        with action_phase(trace, "backend_prepare", label="release_compiler_selected_point_index"):
            prepared.close()
    if trace is not None:
        trace.fold_device_operation(
            name="query_points_upload",
            kind="host_to_device_transfer",
            folded_into="execute",
            reason="prepared execution owns the query upload without an independent timer",
        )
        trace.fold_device_operation(
            name="bounded_rows_download",
            kind="device_to_host_transfer",
            folded_into="execute",
            reason="prepared execution returns copied host columns without an independent download timer",
        )
        trace.fold_device_operation(
            name="bounded_rows_ready_wait",
            kind="device_synchronization_wait",
            folded_into="execute",
            reason="prepared execution synchronizes before returning copied host columns",
        )
    with action_phase(trace, "projection", label="canonical_neighbor_rows"):
        payload = query_result.payload
        if "columns" in payload:
            actual_relation_rows = _relation_rows_from_columns(payload["columns"])
        else:
            actual_relation_rows = _relation_rows_from_rows(payload["rows"])
        actual = _canonical_rows(actual_relation_rows)
    with action_phase(trace, "app_validation", label="exact_knn_reference_comparator"):
        expected = (
            _expected_for_points(
                search,
                queries,
                k=k,
                min_distance=min_distance,
                max_distance=max_distance,
            )
            if validate_reference
            else None
        )
    phase_trace = trace.finish() if trace is not None else None
    return {
        "backend": planned.lowered.backend,
        "actual_rows": actual,
        "actual_relation_rows": actual_relation_rows,
        "expected_rows": expected,
        "matched": actual == expected if expected is not None else None,
        "search_count": int(search.shape[0]),
        "query_count": int(queries.shape[0]),
        "logical_event_count_upper_bound": logical_event_count_upper_bound,
        "logical_candidate_rows_materialized": False,
        "lowering_metadata": planned.lowered.to_metadata(),
        "planned_lowering_metadata": planned.to_metadata(),
        "runtime_metadata": payload["metadata"],
        "prepared_metadata": prepared.to_metadata(),
        "phase_trace": phase_trace,
    }


def run_optix_points(*args, **kwargs) -> dict[str, object]:
    """Compatibility alias; compiler mode does not accept an app backend choice."""

    return run_compiler_points(*args, **kwargs)


def run_generic_metric_knn_second_consumer_points(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float,
    max_distance: float,
    candidate_provider=None,
    validate_reference: bool = True,
) -> dict[str, object]:
    """Run RTNN through the app-neutral prepared metric-kNN family.

    This is an opt-in functional consumer, not a change to RTNN's historical
    production route.  It proves that the Goal5745 native/compiler capability
    is not Arkade-specific.  RTNN's strict distance window remains app-owned;
    the adapter therefore admits only results strictly inside that window and
    fails closed instead of silently weakening its semantics.
    """

    from rtdsl.metric_knn import (
        MetricKnn3DKind,
        MetricKnn3DSpec,
        compile_metric_knn_3d,
    )

    search = np.ascontiguousarray(search_points, dtype=np.float32)
    queries = np.ascontiguousarray(query_points, dtype=np.float32)
    if search.ndim != 2 or search.shape[1:] != (3,) or search.shape[0] == 0:
        raise ValueError("RTNN search points must be a nonempty Nx3 matrix")
    if queries.ndim != 2 or queries.shape[1:] != (3,) or queries.shape[0] == 0:
        raise ValueError("RTNN query points must be a nonempty Nx3 matrix")
    if not math.isfinite(min_distance) or not math.isfinite(max_distance):
        raise ValueError("RTNN distance bounds must be finite")
    if min_distance != 0.0 or max_distance <= 0.0:
        raise ValueError(
            "generic metric-kNN RTNN consumer currently requires min_distance == 0 "
            "and positive max_distance"
        )
    initial_radius = max(float(max_distance) / 128.0, np.finfo(np.float32).tiny)
    spec = MetricKnn3DSpec(
        metric=MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE,
        data_count=int(search.shape[0]),
        query_count=int(queries.shape[0]),
        k=int(k),
        initial_geometric_radius=initial_radius,
        maximum_rounds=8,
        maximum_candidate_rows=int(search.shape[0]) * int(queries.shape[0]),
    )
    program = compile_metric_knn_3d(
        spec,
        target_identity={
            "application_contract": "rtnn_ranked_distance_window",
            "backend_contract_id": "nvidia.optix_traversal.v1",
        },
        memory_limit_bytes=1 << 30,
    )
    result = (
        program.execute(search, queries)
        if candidate_provider is None
        else program.execute_reference_for_functional_validation(search, queries)
    )
    ids = np.asarray(result["ordered_item_ids"], dtype=np.uint32)
    distances = np.asarray(result["ordered_metric_distances"], dtype=np.float64)
    if ids.shape != (len(queries), int(k)) or distances.shape != ids.shape:
        raise RuntimeError("generic metric-kNN RTNN consumer returned wrong shape")
    if not bool(np.all((distances > min_distance) & (distances < max_distance))):
        raise RuntimeError(
            "generic metric-kNN result does not satisfy RTNN's strict distance window"
        )
    actual = tuple(
        (
            query_id,
            int(ids[query_id, rank - 1]),
            rank,
            float(
                np.float32(
                    np.float32(distances[query_id, rank - 1])
                    * np.float32(distances[query_id, rank - 1])
                )
            ),
        )
        for query_id in range(len(queries))
        for rank in range(1, int(k) + 1)
    )
    expected = (
        _expected_for_points(
            search,
            queries,
            k=k,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        if validate_reference
        else None
    )
    metadata = dict(result["metadata"])
    return {
        "backend": "optix_traversal"
        if candidate_provider is None
        else "explicit_functional_provider",
        "physical_family": metadata.get("physical_family"),
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected if expected is not None else None,
        "search_count": int(search.shape[0]),
        "query_count": int(queries.shape[0]),
        "runtime_metadata": metadata,
        "consumer_is_real_rtnn_paper_app": True,
        "historical_production_route_changed": False,
        "performance_claimed": False,
    }


def run_compiler_true_optix_candidate_points_for_functional_validation(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float,
    max_distance: float,
    validate_reference: bool = True,
) -> dict[str, object]:
    """Execute the existing true-OptiX candidate for one verified RTNN IR.

    This evidence-only front door does not alter the production physical
    registry or accept a backend argument.  The generic compiler capability
    order materializes its already registered OptiX candidate, and this
    function fails closed if another physical template is selected.
    """

    search = np.asarray(search_points, dtype=np.float32)
    queries = np.asarray(query_points, dtype=np.float32)
    if search.ndim != 2 or search.shape[1:] != (3,) or search.shape[0] == 0:
        raise ValueError("RTNN search points must be a nonempty Nx3 matrix")
    if queries.ndim != 2 or queries.shape[1:] != (3,) or queries.shape[0] == 0:
        raise ValueError("RTNN query points must be a nonempty Nx3 matrix")
    packed_search = _pack_point_rows(search)
    packed_queries = _pack_point_rows(queries)
    parameters = {
        "k": int(k),
        "min_distance": float(min_distance),
        "max_distance": float(max_distance),
    }
    extents = {ExtentKind.QUERY_COUNT: int(queries.shape[0])}
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_producer(
        compiled, ActionProducerKind.PREPARED_POINT_CANDIDATES_3D
    )
    planned = (
        plan_registered_point_bounded_selection_candidate_for_functional_validation(
            bound,
            detect_action_target_profile(
                producer_kind=ActionProducerKind.PREPARED_POINT_CANDIDATES_3D,
                cpu_reference_available=False,
            ),
            physical_candidate="optix",
            prepared_search_points=packed_search,
            query_points=packed_queries,
            extents=extents,
            parameters=parameters,
        )
    )
    if planned.lowered.backend != "optix":
        raise RuntimeError(
            "compiler functional validation did not select the registered "
            "true-OptiX prepared-point candidate"
        )
    prepared = prepare_action_execution(
        planned,
        extents=extents,
        parameters=parameters,
        prepared_input=packed_search,
        max_distance_bound=float(max_distance),
    )
    try:
        query_result = prepared.execute_queries(
            packed_queries,
            parameters=parameters,
            extents=extents,
        )
    finally:
        prepared.close()
    payload = query_result.payload
    actual_relation_rows = (
        _relation_rows_from_columns(payload["columns"])
        if "columns" in payload
        else _relation_rows_from_rows(payload["rows"])
    )
    actual = _canonical_rows(actual_relation_rows)
    expected = (
        _expected_for_points(
            search,
            queries,
            k=k,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        if validate_reference
        else None
    )
    return {
        "backend": planned.lowered.backend,
        "actual_rows": actual,
        "actual_relation_rows": actual_relation_rows,
        "expected_rows": expected,
        "matched": actual == expected if expected is not None else None,
        "search_count": int(search.shape[0]),
        "query_count": int(queries.shape[0]),
        "logical_event_count_upper_bound": int(search.shape[0])
        * int(queries.shape[0]),
        "logical_candidate_rows_materialized": False,
        "lowering_metadata": planned.lowered.to_metadata(),
        "planned_lowering_metadata": planned.to_metadata(),
        "runtime_metadata": payload["metadata"],
        "functional_validation_only": True,
        "production_physical_registry_changed": False,
        "application_selected_backend": False,
    }


def run_v2_direct_true_optix_backport_points(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float,
    max_distance: float,
    validate_reference: bool = True,
) -> dict[str, object]:
    """Run the existing generic OptiX family via a legacy direct lifetime.

    This route deliberately performs no Action compilation, planning, registry
    lookup, or prepared-action orchestration.  The app owns only input packing,
    explicit physical-family selection, projection, and optional comparison.
    """

    started = time.perf_counter()
    search = np.asarray(search_points, dtype=np.float32)
    queries = np.asarray(query_points, dtype=np.float32)
    if search.ndim != 2 or search.shape[1:] != (3,) or search.shape[0] == 0:
        raise ValueError("RTNN search points must be a nonempty Nx3 matrix")
    if queries.ndim != 2 or queries.shape[1:] != (3,) or queries.shape[0] == 0:
        raise ValueError("RTNN query points must be a nonempty Nx3 matrix")
    packed_search = _pack_point_rows(search)
    packed_queries = _pack_point_rows(queries)
    prepared = prepare_direct_optix_bounded_selection_3d(
        packed_search,
        max_distance_bound=float(max_distance),
    )
    try:
        physical = prepared.run(
            packed_queries,
            minimum_distance=float(min_distance),
            maximum_distance=float(max_distance),
            k=int(k),
            minimum_boundary="open",
            maximum_boundary="open",
        )
        actual_relation_rows = _relation_rows_from_rows(physical["rows"])
        actual = _canonical_rows(actual_relation_rows)
    finally:
        prepared.close()
    complete_endpoint_seconds = time.perf_counter() - started

    expected = (
        _expected_for_points(
            search,
            queries,
            k=k,
            min_distance=min_distance,
            max_distance=max_distance,
        )
        if validate_reference
        else None
    )
    return {
        "backend": "optix_traversal",
        "v2_provenance": "v2_direct_true_optix_backport",
        "physical_family": "action_bounded_selection_3d",
        "actual_rows": actual,
        "actual_relation_rows": actual_relation_rows,
        "expected_rows": expected,
        "matched": actual == expected if expected is not None else None,
        "search_count": int(search.shape[0]),
        "query_count": int(queries.shape[0]),
        "runtime_metadata": physical["metadata"],
        "complete_endpoint_seconds": complete_endpoint_seconds,
        "complete_endpoint_includes": (
            "validation",
            "packing",
            "native_prepare",
            "query_upload",
            "optix_traversal",
            "synchronization",
            "bounded_output_download",
            "canonical_projection",
            "native_close",
        ),
        "comparator_inside_complete_endpoint_timer": False,
        "compiler_or_planner_used": False,
        "registry_selection_used": False,
        "prepared_action_orchestration_used": False,
        "application_identity_used_for_core_dispatch": False,
    }


def _expected_rows() -> tuple[tuple[int, int, int, float], ...]:
    rows = []
    with (FIXTURE_DIR / "reference_k4.tsv").open(newline="", encoding="ascii") as handle:
        reader = csv.reader(
            (line for line in handle if not line.startswith("#")), delimiter="\t"
        )
        header = next(reader)
        if header != ["query_id", "neighbor_id", "neighbor_rank", "distance_sq"]:
            raise ValueError("unexpected RTNN reference schema")
        for query_id, neighbor_id, rank, distance_sq in reader:
            rows.append((int(query_id), int(neighbor_id), int(rank), float(distance_sq)))
    return tuple(rows)


def _canonical_rows(rows) -> tuple[tuple[int, int, int, float], ...]:
    by_query: dict[int, list[tuple[int, int, float]]] = {}
    for query_id, candidate_id, distance in rows:
        by_query.setdefault(int(query_id), []).append(
            (int(query_id), int(candidate_id), float(distance))
        )
    return tuple(
        (
            query_id,
            candidate_id,
            rank,
            float(np.float32(np.float32(distance) * np.float32(distance))),
        )
        for query_id in sorted(by_query)
        for rank, (_, candidate_id, distance) in enumerate(
            sorted(by_query[query_id], key=lambda row: (row[2], row[1])), start=1
        )
    )


def _compare_rows(actual) -> tuple[tuple[tuple[int, int, int, float], ...], bool, bool]:
    canonical = _canonical_rows(actual)
    expected = _expected_rows()
    identity_equal = tuple(row[:3] for row in canonical) == tuple(
        row[:3] for row in expected
    )
    distance_equal = len(canonical) == len(expected) and all(
        math.isclose(left[3], right[3], rel_tol=0.0, abs_tol=1e-6)
        for left, right in zip(canonical, expected)
    )
    return canonical, identity_equal, distance_equal


def _packed_xyz(path: Path):
    rows = _load_xyz(path)
    values = np.asarray(rows, dtype=np.float64)
    return pack_points(
        ids=np.arange(len(rows), dtype=np.uint32),
        x=values[:, 0],
        y=values[:, 1],
        z=values[:, 2],
        dimension=3,
    )


def run_local_semantic_pair() -> dict[str, object]:
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    parameters = {"k": 4, "min_distance": 0.0, "max_distance": 3.0}
    result = compiled.execute_reference(
        fixture_events(),
        parameters,
        extents={ExtentKind.QUERY_COUNT: 3},
    )
    actual, identity_equal, distance_equal = _compare_rows(
        result.emitted_relations[0].rows
    )
    expected = _expected_rows()
    return {
        "schema": "rtdl.research.action.paper_app_pair.rtnn.v1",
        "app": "rtnn",
        "cohort": "cohort_2_seven_app_paired_migration",
        "v2_semantic_baseline": "goal5531_exact_knn_fixture_and_goal5547_strongest_route",
        "action_pattern": "filter_bounded_emit",
        "row_count": len(actual),
        "actual_rows": actual,
        "expected_rows": expected,
        "identity_and_rank_equal": identity_equal,
        "distance_equal_within_1e_6": distance_equal,
        "matched": identity_equal and distance_equal,
        "compiled_metadata": compiled.to_metadata(),
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_optix_semantic_pair() -> dict[str, object]:
    pair = run_compiler_points(
        _load_xyz(FIXTURE_DIR / "search.xyz"),
        _load_xyz(FIXTURE_DIR / "queries.xyz"),
        k=4,
        min_distance=0.0,
        max_distance=3.0,
    )
    actual = pair["actual_rows"]
    expected = _expected_rows()
    identity_equal = tuple(row[:3] for row in actual) == tuple(
        row[:3] for row in expected
    )
    distance_equal = len(actual) == len(expected) and all(
        math.isclose(left[3], right[3], rel_tol=0.0, abs_tol=1e-6)
        for left, right in zip(actual, expected)
    )
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.rtnn.v1",
        "app": "rtnn",
        "backend": pair["backend"],
        "action_pattern": "filter_bounded_emit",
        "actual_rows": actual,
        "expected_rows": expected,
        "identity_and_rank_equal": identity_equal,
        "distance_equal_within_1e_6": distance_equal,
        "matched": identity_equal and distance_equal,
        "lowering_metadata": pair["lowering_metadata"],
        "runtime_metadata": pair["runtime_metadata"],
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "action_contract",
    "events_from_points",
    "run_compiler_points",
    "run_generic_metric_knn_second_consumer_points",
    "run_local_semantic_pair",
    "run_optix_points",
    "run_optix_semantic_pair",
    "run_reference_points",
)
