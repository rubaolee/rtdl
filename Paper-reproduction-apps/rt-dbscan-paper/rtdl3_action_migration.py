"""App-owned RT-DBSCAN composition adapter for the private RTDL 3.0 study."""

from __future__ import annotations

import json
from pathlib import Path
import time

import numpy as np

import rtdsl as rt
from rtdsl.action_api import (
    bind_action_event_columns,
    bind_action_event_rows,
    compile_action_source,
    compile_bound_action_for_target,
    detect_action_target_profile,
    prepare_bound_numba_action_columns,
    rebind_lowered_action_event_columns,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase
from rtdsl.default_physical_selection import registered_action_required_target_backends
from rtdsl.action_ir import (
    F32,
    U32,
    ActionEmitSpec,
    ActionField,
    ActionRecordType,
    CapacityExtent,
    CapacityMul,
    DeliveryEnforcement,
    DuplicatePolicy,
    ExtentKind,
    LogicalEventContract,
    OrderKey,
    OrderKeyRole,
    OutputOrderKind,
    PhysicalDelivery,
)
from rtdsl.action_numba_continuation import (
    execute_numba_action_continuation,
)
from rtdsl.fixed_radius_graph_compiler import (
    execute_registered_fixed_radius_graph_components_3d,
    plan_registered_fixed_radius_graph_components_3d,
    prepare_registered_fixed_radius_graph_context,
)


APP_DIR = Path(__file__).resolve().parent
FIXTURE = APP_DIR / "data" / "fixtures" / "border_noise3d_component_signature.csv"
EXPECTED = (
    APP_DIR
    / "results"
    / "authorofficial_component_signature_border_noise_pod_optix_summary.json"
)

CANONICAL_ALGORITHM_BINDINGS = {
    "prepared_fixed_radius_spatial_components": (
        "fixed_radius.prepared_spatial_components.v1",
        "nvidia.optix_numba_pipeline.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("prepared_fixed_radius_spatial_components",)

ACTION_SOURCE = """
def action(event, params):
    source = event.source_id
    target = event.target_id
    distance_sq = event.distance_sq
    radius_sq = params.radius_sq
    eligible = distance_sq <= radius_sq
    require(eligible)
    emit("edges", source, target)
"""

def _compiler_plan_metadata_with_evidence_source(
    plan_metadata: dict[str, object],
    evidence_source: dict[str, object],
) -> dict[str, object]:
    metadata = dict(plan_metadata)
    generic = metadata.get("refinement_evidence")
    compact_digest = metadata.get("refinement_evidence_digest")
    source = dict(evidence_source)
    if isinstance(generic, dict):
        evidence_digest = generic.get("artifact_sha256")
        evidence_contract = generic.get("contract")
    elif isinstance(compact_digest, str):
        evidence_digest = compact_digest
        evidence_contract = source.get("artifact_schema")
    else:
        raise RuntimeError(
            "fixed-radius compiler plan lacks a static evidence digest"
        )
    if (
        source.get("status")
        not in {
            "successor_evidence_installed",
            "validated_evidence_without_installed_path",
        }
        or source.get("source_receipt_created_without_artifact_reread")
        is not True
        or (
        evidence_digest != source.get("artifact_sha256")
        or evidence_contract != source.get("artifact_schema")
        )
    ):
        raise RuntimeError(
            "fixed-radius evidence source does not match compiler certificate"
        )
    metadata["refinement_evidence_source"] = source
    return metadata


def _compiler_fixed_radius_target_profile():
    """Probe coarse target facts through one shared compiler-route gateway."""

    return detect_action_target_profile(
        cpu_reference_available=False,
        _compiler_required_backends=(
            registered_action_required_target_backends(
                "fixed_radius_graph_components_3d.v1",
                "radius_components",
            )
        ),
    )


def _plan_compiled_fixed_radius_graph(
    compiled,
    points,
    *,
    epsilon: float,
    min_points: int,
    target_profile=None,
    prepared_context=None,
):
    """One app-local gateway into the compiler-owned selector."""

    target = (
        _compiler_fixed_radius_target_profile()
        if target_profile is None
        else target_profile
    )
    canonical_kwargs = {}
    if target.production_selection_policy == "compiler_owned_default":
        statement, backend = CANONICAL_ALGORITHM_BINDINGS[
            "prepared_fixed_radius_spatial_components"
        ]
        canonical_kwargs = {
            "semantic_statement_stable_id": statement,
            "backend_contract_id": backend,
        }
    return plan_registered_fixed_radius_graph_components_3d(
        compiled,
        target,
        points=points,
        radius=epsilon,
        min_neighbors=min_points,
        prepared_context=prepared_context,
        **canonical_kwargs,
    )


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "distance_candidate",
        (
            ActionField("source_id", U32),
            ActionField("target_id", U32),
            ActionField("distance_sq", F32),
        ),
    )
    parameter_type = ActionRecordType(
        "parameters", (ActionField("radius_sq", F32),)
    )
    edge_type = ActionRecordType(
        "edge_row",
        (ActionField("source_id", U32), ActionField("target_id", U32)),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=parameter_type,
        logical_event=LogicalEventContract(
            key_fields=("source_id", "target_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "edges",
                edge_type,
                CapacityMul(
                    CapacityExtent(ExtentKind.QUERY_COUNT),
                    CapacityExtent(ExtentKind.PRIMITIVE_COUNT),
                ),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("source_id"),
                    OrderKey("target_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
            ),
        ),
    )


def _points() -> np.ndarray:
    rows = []
    for line in FIXTURE.read_text(encoding="ascii").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        coordinates = tuple(float(item) for item in value.split(","))
        if len(coordinates) != 3:
            raise ValueError("RT-DBSCAN bounded Action fixture must be 3-D")
        rows.append(coordinates)
    return np.asarray(rows, dtype=np.float32)


def event_columns() -> dict[str, np.ndarray]:
    return event_columns_from_points(_points())


def event_columns_from_points(points) -> dict[str, np.ndarray]:
    points = np.asarray(points, dtype=np.float32)
    if points.ndim != 2 or points.shape[0] == 0 or points.shape[1] not in {2, 3}:
        raise ValueError("RT-DBSCAN V3 points must be a nonempty Nx2 or Nx3 matrix")
    source_ids = []
    target_ids = []
    distance_sqs = []
    for source_id, source in enumerate(points):
        for target_id, target in enumerate(points):
            delta = np.subtract(source, target, dtype=np.float32)
            squared = np.multiply(delta, delta, dtype=np.float32)
            distance_sq = np.add(
                squared[0], squared[1], dtype=np.float32
            )
            if points.shape[1] == 3:
                distance_sq = np.add(
                    distance_sq, squared[2], dtype=np.float32
                )
            source_ids.append(source_id)
            target_ids.append(target_id)
            distance_sqs.append(distance_sq)
    return {
        "source_id": np.asarray(source_ids, dtype=np.uint32),
        "target_id": np.asarray(target_ids, dtype=np.uint32),
        "distance_sq": np.asarray(distance_sqs, dtype=np.float32),
    }


def _radius_sq_f32(radius: float) -> np.float32:
    radius_f32 = np.float32(radius)
    return np.multiply(radius_f32, radius_f32, dtype=np.float32)


def _expected_from_points(points, *, epsilon: float, min_points: int):
    columns = event_columns_from_points(points)
    edge_rows = tuple(
        (int(source), int(target))
        for source, target, distance_sq in zip(
            columns["source_id"], columns["target_id"], columns["distance_sq"]
        )
        if distance_sq <= _radius_sq_f32(epsilon)
    )
    return _compose_partition(
        edge_rows,
        point_count=int(np.asarray(points).shape[0]),
        min_points=int(min_points),
    )


def run_reference_points(points, *, epsilon: float, min_points: int):
    points = np.asarray(points, dtype=np.float32)
    columns = event_columns_from_points(points)
    compiled, bound = _compiled_and_bound(columns)
    result = bound.execute_reference(
        _events(columns),
        {
            "radius_sq": float(_radius_sq_f32(epsilon))
        },
        extents={
            ExtentKind.QUERY_COUNT: int(points.shape[0]),
            ExtentKind.PRIMITIVE_COUNT: int(points.shape[0]),
        },
    )
    actual = _compose_partition(
        result.emitted_relations[0].rows,
        point_count=int(points.shape[0]),
        min_points=int(min_points),
    )
    expected = _expected_from_points(
        points, epsilon=epsilon, min_points=min_points
    )
    return {
        "backend": "action_cpu_plus_generic_components",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "point_count": int(points.shape[0]),
        "compiled_metadata": compiled.to_metadata(),
    }


def run_numba_points(
    points,
    *,
    epsilon: float,
    min_points: int,
    collect_phase_trace: bool = False,
    validate_reference: bool = True,
):
    """Compatibility name for the normal compiler-owned V3 front door."""

    return run_compiler_points(
        points,
        epsilon=epsilon,
        min_points=min_points,
        collect_phase_trace=collect_phase_trace,
        validate_reference=validate_reference,
    )


def run_compiler_points(
    points,
    *,
    epsilon: float,
    min_points: int,
    collect_phase_trace: bool = False,
    validate_reference: bool = True,
):
    trace = (
        ActionPhaseTrace(
            app="rt_dbscan",
            route="compiler_selected_fixed_radius_graph_components",
        )
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="float32_point_matrix"):
        points = np.ascontiguousarray(points, dtype=np.float32)
    with action_phase(
        trace, "action_compile_or_cache_hit", label="compile_closed_radius_edge_action"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
        target_profile = _compiler_fixed_radius_target_profile()
        physical_context = prepare_registered_fixed_radius_graph_context(
            compiled,
            target_profile,
        )
        refinement_evidence_source = dict(
            physical_context.refinement_evidence_source
        )
    try:
        with action_phase(
            trace, "physical_plan", label="registered_cross_producer_plan"
        ):
            compiler_plan = _plan_compiled_fixed_radius_graph(
                compiled,
                points,
                epsilon=epsilon,
                min_points=min_points,
                target_profile=target_profile,
                prepared_context=physical_context,
            )
        execution = execute_registered_fixed_radius_graph_components_3d(
            compiler_plan,
            points=points,
            radius=epsilon,
            min_neighbors=min_points,
            trace=trace,
        )
    finally:
        physical_context.close()
    actual = execution["actual"]
    if validate_reference:
        with action_phase(trace, "app_validation", label="exact_partition_comparator"):
            expected = _expected_from_points(
                points, epsilon=epsilon, min_points=min_points
            )
        matched = _matched(actual, expected)
    else:
        expected = None
        matched = None
        if trace is not None:
            trace.mark_not_applicable(
                "app_validation",
                reason="caller explicitly executes an independently validated timing route",
            )
    phase_trace = trace.finish() if trace is not None else None
    return {
        "backend": "compiler_selected_fixed_radius_graph_components",
        "selected_backend": execution["selected_backend"],
        "selected_producer_kind": execution["selected_producer_kind"],
        "actual": actual,
        "expected": expected,
        "matched": matched,
        "point_count": int(points.shape[0]),
        "compiled_metadata": compiled.to_metadata(),
        "compiler_plan": _compiler_plan_metadata_with_evidence_source(
            execution["compiler_plan"],
            refinement_evidence_source,
        ),
        "invocation_receipt": execution["invocation_receipt"],
        "route_metadata": execution["route_metadata"],
        "phase_trace": phase_trace,
        "application_selected_backend": False,
        "application_supplied_cost": False,
        "complete_pair_columns_materialized": (
            execution["selected_producer_kind"]
            == "complete_pair_candidate_enumeration.v1"
        ),
    }


def run_compiler_semantic_pair(
    *,
    collect_phase_trace: bool = False,
) -> dict[str, object]:
    expected = _expected()
    return run_compiler_points(
        _points(),
        epsilon=expected["epsilon"],
        min_points=expected["min_points"],
        collect_phase_trace=collect_phase_trace,
        validate_reference=True,
    )


def prepare_compiler_fixed_radius_graph_route() -> dict[str, object]:
    """Prepare only reusable, input-independent compiler state.

    Input conversion, exact input/parameter digests, HMAC issuance,
    capability-specific legality, and physical selection are deliberately
    absent.  Refinement-evidence validation, runtime capability, and
    loaded-native byte attestation are established once here.  Candidate
    density is not acquired: fixed-priority legal selection does not consume
    it, and the complete-pair fallback uses the proof-safe all-pairs resource
    bound.  The formal route pays all required dynamic input work per batch.
    """

    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    target_profile = _compiler_fixed_radius_target_profile()
    physical_context = prepare_registered_fixed_radius_graph_context(
        compiled,
        target_profile,
    )
    return {
        "contract": "rtdl.research.prepared_compiler_fixed_radius_graph_static.v3",
        "compiled": compiled,
        "target_profile": target_profile,
        "physical_context": physical_context,
        "physical_context_metadata": physical_context.to_metadata(),
        "refinement_evidence_source": dict(
            physical_context.refinement_evidence_source
        ),
        "compiled_metadata": compiled.to_metadata(),
        "static_setup_excluded_from_physical_route": True,
        "input_specific_plan_present": False,
        "input_conversion_in_timed_route": True,
        "input_parameter_digest_hmac_selection_in_timed_physical_plan": True,
        "candidate_density_acquired_in_timed_physical_plan": False,
        "evidence_capability_native_attestation_in_timed_physical_plan": False,
        "normal_v3_frontdoor_core_shared": True,
        "application_selected_backend": False,
        "application_supplied_cost": False,
    }


def close_compiler_fixed_radius_graph_route(
    compiler_prepared: dict[str, object],
) -> None:
    """Close the compiler-owned static context used by a prepared app route."""

    if not isinstance(compiler_prepared, dict) or (
        compiler_prepared.get("contract")
        != "rtdl.research.prepared_compiler_fixed_radius_graph_static.v3"
    ):
        raise ValueError("invalid prepared compiler fixed-radius route contract")
    physical_context = compiler_prepared.get("physical_context")
    if physical_context is None or not hasattr(physical_context, "close"):
        raise ValueError("prepared compiler fixed-radius route lacks its owner")
    physical_context.close()


def run_compiler_selected_fixed_radius_graph_route(
    points,
    *,
    epsilon: float,
    min_points: int,
    collect_phase_trace: bool = True,
    compiler_prepared: dict[str, object] | None = None,
) -> dict[str, object]:
    """Execute the normal compiler-selected V3 route without its comparator.

    A formal trial may prepare only static compiler source and coarse target
    facts.  The timed route pays every input-dependent planning operation plus
    physical execution and projection.
    """

    trace = (
        ActionPhaseTrace(
            app="rt_dbscan",
            route="compiler_selected_fixed_radius_graph_components",
        )
        if collect_phase_trace
        else None
    )
    route_started = time.perf_counter()
    with action_phase(trace, "input_adapter", label="float32_point_matrix"):
        points = np.ascontiguousarray(points, dtype=np.float32)
        if (
            points.ndim != 2
            or points.shape[0] == 0
            or points.shape[1] not in {2, 3}
        ):
            raise ValueError(
                "compiler-selected fixed-radius route requires a nonempty Nx2 or Nx3 matrix"
            )

    owns_physical_context = compiler_prepared is None
    if compiler_prepared is None:
        with action_phase(
            trace,
            "action_compile_or_cache_hit",
            label="compile_closed_radius_edge_action",
        ):
            compiled = compile_action_source(ACTION_SOURCE, action_contract())
            target_profile = _compiler_fixed_radius_target_profile()
            physical_context = prepare_registered_fixed_radius_graph_context(
                compiled,
                target_profile,
            )
        compiled_metadata = compiled.to_metadata()
        refinement_evidence_source = dict(
            physical_context.refinement_evidence_source
        )
        static_compiler_setup_included = True
    else:
        if not isinstance(compiler_prepared, dict):
            raise TypeError("compiler_prepared must be a prepared compiler route mapping")
        if (
            compiler_prepared.get("contract")
            != "rtdl.research.prepared_compiler_fixed_radius_graph_static.v3"
            or compiler_prepared.get("static_setup_excluded_from_physical_route")
            is not True
            or compiler_prepared.get("input_specific_plan_present") is not False
            or compiler_prepared.get(
                "input_parameter_digest_hmac_selection_in_timed_physical_plan"
            )
            is not True
            or compiler_prepared.get(
                "candidate_density_acquired_in_timed_physical_plan"
            )
            is not False
            or compiler_prepared.get(
                "evidence_capability_native_attestation_in_timed_physical_plan"
            )
            is not False
        ):
            raise ValueError("invalid prepared compiler fixed-radius route contract")
        compiled = compiler_prepared.get("compiled")
        target_profile = compiler_prepared.get("target_profile")
        physical_context = compiler_prepared.get("physical_context")
        compiled_metadata = dict(compiler_prepared.get("compiled_metadata", {}))
        refinement_evidence_source = dict(
            compiler_prepared.get("refinement_evidence_source", {})
        )
        if (
            refinement_evidence_source.get("status")
            not in {
                "successor_evidence_installed",
                "validated_evidence_without_installed_path",
            }
            or refinement_evidence_source.get(
                "source_receipt_created_without_artifact_reread"
            )
            is not True
        ):
            raise ValueError(
                "prepared compiler route lacks its static evidence source receipt"
            )
        static_compiler_setup_included = False
        if trace is not None:
            trace.mark_not_applicable(
                "action_compile_or_cache_hit",
                reason="only input-independent source compilation and coarse target setup were prepared",
            )

    try:
        with action_phase(
            trace,
            "physical_plan",
            label="input_parameter_digest_hmac_legality_and_selection",
        ):
            compiler_plan = _plan_compiled_fixed_radius_graph(
                compiled,
                points,
                epsilon=epsilon,
                min_points=min_points,
                target_profile=target_profile,
                prepared_context=physical_context,
            )

        execution = execute_registered_fixed_radius_graph_components_3d(
            compiler_plan,
            points=points,
            radius=epsilon,
            min_neighbors=min_points,
            trace=trace,
        )
    finally:
        if owns_physical_context:
            physical_context.close()
    if trace is not None:
        trace.mark_not_applicable(
            "app_validation",
            reason="the independent partition comparator runs outside route timing",
        )
    phase_trace = trace.finish() if trace is not None else None
    route_elapsed = (
        float(phase_trace["reconciliation"]["route_elapsed_seconds"])
        if phase_trace is not None
        else time.perf_counter() - route_started
    )
    route_metadata = dict(execution["route_metadata"])
    candidate_row_count = int(
        route_metadata.get(
            "candidate_row_count",
            route_metadata.get("candidate_rows_materialized", 0),
        )
    )
    return {
        "schema": "rtdl.research.rt_dbscan.compiler_selected_physical_route.v3",
        "physical_producer_kind": execution["selected_producer_kind"],
        "backend": execution["selected_backend"],
        "actual": execution["actual"],
        "point_count": int(points.shape[0]),
        "candidate_row_count": candidate_row_count,
        "complete_pair_columns_materialized": (
            execution["selected_producer_kind"]
            == "complete_pair_candidate_enumeration.v1"
        ),
        "route_elapsed_seconds": route_elapsed,
        "phase_trace": phase_trace,
        "compiled_metadata": compiled_metadata,
        "compiler_plan": _compiler_plan_metadata_with_evidence_source(
            execution["compiler_plan"],
            refinement_evidence_source,
        ),
        "invocation_receipt": execution["invocation_receipt"],
        "route_metadata": route_metadata,
        "comparator_included_in_route_time": False,
        "compiler_setup_included_in_route_time": static_compiler_setup_included,
        "static_compiler_setup_included_in_route_time": static_compiler_setup_included,
        "input_dependent_plan_included_in_route_time": True,
        "input_conversion_included_in_route_time": True,
        "physical_plan_includes_input_parameter_digest_hmac_and_selection": True,
        "candidate_density_acquired_in_route_time": False,
        "complete_pair_fallback_candidate_bound_policy": (
            "worst_case_all_ordered_pairs_without_input_scan"
        ),
        "per_batch_identity_recheck_included_in_route_time": True,
        "normal_v3_frontdoor_core_shared": True,
        "application_selected_backend": False,
        "application_supplied_cost": False,
    }


def run_complete_candidate_action_route(
    points,
    *,
    epsilon: float,
    min_points: int,
    collect_phase_trace: bool = True,
    compiler_prepared: dict[str, object] | None = None,
):
    """Execute the historical Goal5628 complete-pair diagnostic route."""

    trace = (
        ActionPhaseTrace(app="rt_dbscan", route="complete_candidate_action")
        if collect_phase_trace
        else None
    )
    route_started = time.perf_counter()
    with action_phase(trace, "input_adapter", label="float32_point_matrix"):
        points = np.asarray(points, dtype=np.float32)
        if points.ndim != 2 or points.shape[0] == 0 or points.shape[1] not in {2, 3}:
            raise ValueError("RT-DBSCAN V3 points must be a nonempty Nx2 or Nx3 matrix")
    with action_phase(trace, "event_producer", label="complete_pair_distance_columns"):
        columns = event_columns_from_points(points)
    if compiler_prepared is None:
        with action_phase(
            trace, "action_compile_or_cache_hit", label="compile_radius_edge_action"
        ):
            compiled = compile_action_source(ACTION_SOURCE, action_contract())
        with action_phase(
            trace, "binding_certificate", label="complete_pair_column_binding"
        ):
            bound = bind_action_event_columns(
                compiled,
                columns,
                ordering_fields=("source_id", "target_id"),
            )
        with action_phase(trace, "physical_plan", label="capability_plan_and_lower"):
            lowered = compile_bound_action_for_target(
                bound,
                detect_action_target_profile(cpu_reference_available=False),
                extents={
                    ExtentKind.QUERY_COUNT: int(points.shape[0]),
                    ExtentKind.PRIMITIVE_COUNT: int(points.shape[0]),
                },
                parameters={},
            ).lowered
    else:
        max_point_count = int(compiler_prepared["max_point_count"])
        if int(points.shape[0]) > max_point_count:
            raise ValueError("compiler-prepared Action capacity is smaller than the point batch")
        if trace is not None:
            trace.mark_not_applicable(
                "action_compile_or_cache_hit",
                reason="compiler setup is measured once outside the physical-producer route",
            )
            trace.mark_not_applicable(
                "physical_plan",
                reason="the outer physical-alternative planner starts from this prepared lowering",
            )
        with action_phase(
            trace, "binding_certificate", label="prepared_complete_pair_column_rebinding"
        ):
            lowered = rebind_lowered_action_event_columns(
                compiler_prepared["lowered"],
                columns,
                max_row_count=max_point_count * max_point_count,
            )
    prepared = None
    result = None
    try:
        with action_phase(trace, "backend_prepare", label="prepare_radius_edge_columns"):
            prepared = prepare_bound_numba_action_columns(
                lowered,
                columns,
                {
                    "radius_sq": _radius_sq_f32(epsilon)
                },
            )
        if trace is not None:
            trace.fold_device_operation(
                name="complete_candidate_columns_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="Numba prepare owns the upload and exposes no independent timer",
            )
        with action_phase(trace, "execute", label="filter_complete_candidate_columns"):
            result = execute_numba_action_continuation(
                prepared,
                extents={
                    ExtentKind.QUERY_COUNT: int(points.shape[0]),
                    ExtentKind.PRIMITIVE_COUNT: int(points.shape[0]),
                },
            )
        with action_phase(trace, "projection", label="download_edges_and_converge"):
            relation = result.to_host_relation()
            relation_metadata = result.to_metadata()
            actual = _compose_partition(
                relation.rows,
                point_count=int(points.shape[0]),
                min_points=int(min_points),
            )
    finally:
        with action_phase(trace, "backend_prepare", label="release_radius_edge_state"):
            try:
                if result is not None:
                    result.close()
            finally:
                if prepared is not None:
                    prepared.close()
    if trace is not None:
        trace.fold_device_operation(
            name="complete_candidate_edge_rows_download",
            kind="device_to_host_transfer",
            folded_into="projection",
            reason="to_host_relation owns the download and exposes no independent timer",
        )
        trace.fold_device_operation(
            name="complete_candidate_completion_wait",
            kind="device_synchronization_wait",
            folded_into="projection",
            reason="to_host_relation synchronizes before host component convergence",
        )
        trace.mark_not_applicable(
            "app_validation",
            reason="the independent partition comparator runs outside route timing",
        )
    phase_trace = trace.finish() if trace is not None else None
    route_elapsed = (
        float(phase_trace["reconciliation"]["route_elapsed_seconds"])
        if phase_trace is not None
        else time.perf_counter() - route_started
    )
    return {
        "schema": "rtdl.research.rt_dbscan.physical_route.v1",
        "physical_producer_kind": "complete_pair_candidate_enumeration.v1",
        "backend": "numba_complete_candidate_action",
        "actual": actual,
        "point_count": int(points.shape[0]),
        "candidate_row_count": int(points.shape[0]) ** 2,
        "route_elapsed_seconds": route_elapsed,
        "phase_trace": phase_trace,
        "relation_metadata": relation_metadata,
        "comparator_included_in_route_time": False,
        "compiler_setup_included_in_route_time": compiler_prepared is None,
    }


def prepare_complete_candidate_action_route(*, max_point_count: int) -> dict[str, object]:
    """Prepare the Action compiler state before comparing physical producers."""

    if not isinstance(max_point_count, int) or isinstance(max_point_count, bool):
        raise TypeError("max_point_count must be an integer")
    if max_point_count <= 0:
        raise ValueError("max_point_count must be positive")
    probe_points = np.asarray(((0.0, 0.0, 0.0),), dtype=np.float32)
    probe_columns = event_columns_from_points(probe_points)
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_event_columns(
        compiled,
        probe_columns,
        ordering_fields=("source_id", "target_id"),
    )
    target_profile = detect_action_target_profile(cpu_reference_available=False)
    lowered = compile_bound_action_for_target(
        bound,
        target_profile,
        extents={
            ExtentKind.QUERY_COUNT: max_point_count,
            ExtentKind.PRIMITIVE_COUNT: max_point_count,
        },
        parameters={},
    ).lowered
    return {
        "contract": "rtdl.research.prepared_complete_candidate_action_route.v1",
        "lowered": lowered,
        "max_point_count": max_point_count,
        "max_candidate_row_count": max_point_count * max_point_count,
        "compiler_setup_excluded_from_physical_route": True,
        "batch_rebinding_remains_in_physical_route": True,
    }


def run_prepared_spatial_radius_route(
    points,
    *,
    epsilon: float,
    min_points: int,
    collect_phase_trace: bool = True,
):
    """Execute the existing generic prepared spatial radius-component route."""

    trace = (
        ActionPhaseTrace(app="rt_dbscan", route="prepared_spatial_radius")
        if collect_phase_trace
        else None
    )
    route_started = time.perf_counter()
    with action_phase(trace, "input_adapter", label="point3d_rows"):
        points = np.asarray(points, dtype=np.float32)
        if (
            points.ndim != 2
            or points.shape[0] == 0
            or points.shape[1] not in {2, 3}
        ):
            raise ValueError(
                "prepared spatial radius route requires a nonempty Nx2 or Nx3 matrix"
            )
        original_dimension = int(points.shape[1])
        if original_dimension == 2:
            lifted = np.empty((points.shape[0], 3), dtype=np.float32)
            lifted[:, :2] = points
            lifted[:, 2] = np.float32(0.0)
            spatial_points = lifted
        else:
            spatial_points = np.ascontiguousarray(points, dtype=np.float32)
        point_rows = tuple(
            rt.Point3D(id=index, x=float(row[0]), y=float(row[1]), z=float(row[2]))
            for index, row in enumerate(spatial_points)
        )
    if trace is not None:
        trace.mark_not_applicable(
            "event_producer",
            reason="the prepared spatial index is the physical producer",
        )
        trace.mark_not_applicable(
            "action_compile_or_cache_hit",
            reason="the existing generic spatial operator has no Action frontend compilation",
        )
        trace.mark_not_applicable(
            "binding_certificate",
            reason="Point3D records satisfy the public prepared-operator contract",
        )
        trace.mark_not_applicable(
            "physical_plan",
            reason="the outer compiler-selected alternative is timed separately from execution",
        )
    with action_phase(trace, "backend_prepare", label="prepare_optix_radius_index"):
        prepared = rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
            point_rows,
            radius=float(epsilon),
            partner="numba",
        )
    try:
        if trace is not None:
            trace.fold_device_operation(
                name="spatial_point_rows_and_index_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="prepared spatial construction exposes no independent transfer timer",
            )
        with action_phase(trace, "execute", label="prepared_radius_components"):
            result = rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=int(min_points),
                return_metadata=True,
            )
        with action_phase(trace, "projection", label="download_and_canonicalize_partition"):
            columns = result["columns"]
            point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
            raw_labels = np.asarray(
                columns["component_labels"].copy_to_host(), dtype=np.int64
            )
            raw_core_flags = np.asarray(columns["is_core"].copy_to_host(), dtype=np.int64)
            labels = [-1] * int(points.shape[0])
            core_flags = [False] * int(points.shape[0])
            for row_index, point_id in enumerate(point_ids.tolist()):
                labels[int(point_id)] = int(raw_labels[row_index])
                core_flags[int(point_id)] = bool(raw_core_flags[row_index])
            actual = {
                "core_flags": tuple(core_flags),
                "canonical_component_labels": rt.canonical_partition_labels(labels),
            }
            route_metadata = dict(result["metadata"])
    finally:
        with action_phase(trace, "backend_prepare", label="release_optix_radius_index"):
            prepared.close()
    if trace is not None:
        trace.fold_device_operation(
            name="spatial_component_columns_download",
            kind="device_to_host_transfer",
            folded_into="projection",
            reason="device columns expose no independent download timer",
        )
        trace.fold_device_operation(
            name="spatial_component_completion_wait",
            kind="device_synchronization_wait",
            folded_into="projection",
            reason="copy_to_host synchronizes component output visibility",
        )
        trace.mark_not_applicable(
            "app_validation",
            reason="the independent partition comparator runs outside route timing",
        )
    phase_trace = trace.finish() if trace is not None else None
    route_elapsed = (
        float(phase_trace["reconciliation"]["route_elapsed_seconds"])
        if phase_trace is not None
        else time.perf_counter() - route_started
    )
    return {
        "schema": "rtdl.research.rt_dbscan.physical_route.v1",
        "physical_producer_kind": "prepared_spatial_radius_producer.v1",
        "backend": "optix_prepared_radius_components",
        "actual": actual,
        "point_count": int(points.shape[0]),
        "route_elapsed_seconds": route_elapsed,
        "phase_trace": phase_trace,
        "route_metadata": route_metadata,
        "original_input_dimension": original_dimension,
        "spatial_execution_dimension": 3,
        "zero_z_lift_applied": original_dimension == 2,
        "zero_z_lift_semantics": (
            "append_exact_float32_positive_zero_preserves_squared_euclidean_distance"
            if original_dimension == 2
            else "identity"
        ),
        "comparator_included_in_route_time": False,
        "compiler_setup_included_in_route_time": False,
    }


def _events(columns: dict[str, np.ndarray]) -> tuple[dict[str, object], ...]:
    return tuple(
        {name: values[index].item() for name, values in columns.items()}
        for index in range(len(columns["source_id"]))
    )


def _expected() -> dict[str, object]:
    payload = json.loads(EXPECTED.read_text(encoding="utf-8"))
    return {
        "epsilon": float(payload["epsilon"]),
        "min_points": int(payload["min_points"]),
        "canonical_component_labels": tuple(
            int(value) for value in payload["author_partition"]["canonical_component_labels"]
        ),
        "core_flags": tuple(bool(value) for value in payload["author"]["core_flags"]),
    }


def _compose_partition(edge_rows, *, point_count: int, min_points: int) -> dict[str, object]:
    pairs = tuple((int(row[0]), int(row[1])) for row in edge_rows)
    neighbor_counts = [0] * point_count
    for source_id, _ in pairs:
        neighbor_counts[source_id] += 1
    core_flags = tuple(count >= min_points for count in neighbor_counts)
    partition = rt.predicate_aware_boundary_union_reference(
        point_count=point_count,
        candidate_pairs=pairs,
        predicate_flags=core_flags,
    )
    labels = rt.canonical_partition_labels(partition["component_labels"])
    return {
        "edge_count": len(pairs),
        "neighbor_counts": tuple(neighbor_counts),
        "core_flags": core_flags,
        "canonical_component_labels": labels,
        "partition_metadata": partition,
    }


def _matched(actual: dict[str, object], expected: dict[str, object]) -> bool:
    return (
        actual["canonical_component_labels"]
        == expected["canonical_component_labels"]
        and actual["core_flags"] == expected["core_flags"]
    )


def _compiled_and_bound(columns: dict[str, np.ndarray] | None = None):
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    resolved_columns = event_columns() if columns is None else columns
    return compiled, bind_action_event_rows(compiled, _events(resolved_columns))


def run_local_semantic_pair() -> dict[str, object]:
    columns = event_columns()
    compiled, bound = _compiled_and_bound(columns)
    expected = _expected()
    point_count = len(_points())
    result = bound.execute_reference(
        _events(columns),
        {
            "radius_sq": float(_radius_sq_f32(expected["epsilon"]))
        },
        extents={
            ExtentKind.QUERY_COUNT: point_count,
            ExtentKind.PRIMITIVE_COUNT: point_count,
        },
    )
    actual = _compose_partition(
        result.emitted_relations[0].rows,
        point_count=point_count,
        min_points=expected["min_points"],
    )
    return {
        "schema": "rtdl.research.action.paper_app_pair.rt_dbscan.v1",
        "app": "rt_dbscan",
        "backend": "cpu_action_plus_generic_predicate_aware_boundary_union",
        "action_pattern": "filter_bounded_emit",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "compiled_metadata": compiled.to_metadata(),
        "action_owns_component_convergence": False,
        "action_owns_boundary_assignment": False,
        "explicit_host_relation_handoff": True,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_numba_semantic_pair() -> dict[str, object]:
    columns = event_columns()
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_event_columns(
        compiled,
        columns,
        ordering_fields=("source_id", "target_id"),
    )
    lowered = compile_bound_action_for_target(
        bound,
        detect_action_target_profile(cpu_reference_available=False),
        extents={
            ExtentKind.QUERY_COUNT: len(_points()),
            ExtentKind.PRIMITIVE_COUNT: len(_points()),
        },
        parameters={},
    ).lowered
    expected = _expected()
    point_count = len(_points())
    prepared = prepare_bound_numba_action_columns(
        lowered,
        columns,
        {
            "radius_sq": _radius_sq_f32(expected["epsilon"])
        },
    )
    result = execute_numba_action_continuation(
        prepared,
        extents={
            ExtentKind.QUERY_COUNT: point_count,
            ExtentKind.PRIMITIVE_COUNT: point_count,
        },
    )
    try:
        relation = result.to_host_relation()
        relation_metadata = result.to_metadata()
    finally:
        try:
            result.close()
        finally:
            prepared.close()
    actual = _compose_partition(
        relation.rows, point_count=point_count, min_points=expected["min_points"]
    )
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.rt_dbscan.v1",
        "app": "rt_dbscan",
        "backend": "numba_action_plus_host_generic_predicate_aware_boundary_union",
        "action_pattern": "filter_bounded_emit",
        "actual": actual,
        "expected": expected,
        "matched": _matched(actual, expected),
        "lowering_metadata": lowered.to_metadata(),
        "relation_metadata": relation_metadata,
        "action_owns_component_convergence": False,
        "action_owns_boundary_assignment": False,
        "explicit_host_relation_handoff": True,
        "component_operator_device_resident": False,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "action_contract",
    "event_columns_from_points",
    "run_compiler_points",
    "run_compiler_semantic_pair",
    "run_local_semantic_pair",
    "run_numba_points",
    "run_numba_semantic_pair",
    "run_reference_points",
)
