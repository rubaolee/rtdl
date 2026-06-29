from __future__ import annotations

import json
import time
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .numba_partner_continuation import NUMBA_COMPACT_MASK_I64_OPERATION
from .numba_partner_continuation import NUMBA_SEGMENTED_COUNT_I64_OPERATION
from .numba_partner_continuation import numba_partner_available
from .rayjoin_paper_suite import RAYJOIN_SECTION57_TABLE4_SECONDS
from .rayjoin_paper_suite import availability_matrix
from .rayjoin_paper_suite import paper_pairs


RAYJOIN_SECTION57_NUMBA_AUTO_PLANNER_SCHEMA = (
    "rtdl.v4.rayjoin.section57_numba_auto_primitive_planner.v1"
)
RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA = (
    "rtdl.v4.rayjoin.section57_numba_measured_candidates.v1"
)
RAYJOIN_SECTION57_NUMBA_AUTO_PLAN_STATUS = "candidate_planner_not_release_claim"
RAYJOIN_SECTION57_NUMBA_PARTNER_SCOPE = (
    "post_traversal_numba_cuda_jit_continuation_on_device_resident_columns"
)
SECTION57_DEVICE_COLUMN_REQUIREMENT = (
    "V4+Numba Section 5.7 performance measurement requires RTDL to expose "
    "overlay candidate/refinement streams as device-resident columns. Host "
    "overlay summaries are not sufficient for this route."
)


@dataclass(frozen=True)
class Section57PlanStage:
    stage_id: str
    role: str
    owner: str
    primitive: str
    partner: str | None
    execution_boundary: str
    device_resident_input_required: bool
    numba_cuda_jit_required: bool = False
    optix_traversal_callback_injection: bool = False


@dataclass(frozen=True)
class Section57CandidatePlan:
    plan_id: str
    user_semantics: str
    partner: str
    selection_role: str
    expected_output_schema: str
    correctness_comparator: str
    stages: tuple[Section57PlanStage, ...]
    status: str
    skip_reason: str | None = None
    measured_total_sec: float | None = None
    compile_jit_sec: float | None = None
    steady_state_sec: float | None = None
    correctness_status: str = "not_run"


def _split_csv(value: str | Iterable[str] | None, *, default: Iterable[str]) -> tuple[str, ...]:
    if value is None:
        return tuple(default)
    if isinstance(value, str):
        if value.strip() == "":
            return tuple(default)
        return tuple(part.strip() for part in value.split(",") if part.strip())
    return tuple(str(part).strip() for part in value if str(part).strip())


def _path_exists(path: str | Path | None) -> bool:
    return bool(path) and Path(path).exists()


def _numba_cuda_available() -> bool:
    try:
        return bool(numba_partner_available())
    except Exception:
        return False


def _numba_section57_overlay_valid_pair_mask_kernel_factory(cuda):
    """Return the Section 5.7 Numba CUDA mask kernel.

    This kernel is intentionally outside the OptiX traversal loop. It represents
    the bounded V4.0 partner role for Section 5.7: consume device-resident
    candidate/refinement columns after RTDL traversal and produce a compactable
    validity mask. Arbitrary ray-action callback injection remains V4.1 scope.
    """

    @cuda.jit
    def section57_overlay_valid_pair_mask_kernel(candidate_flags, topology_flags, out_flags, count):
        row = cuda.grid(1)
        if row < count:
            out_flags[row] = candidate_flags[row] and topology_flags[row]

    return section57_overlay_valid_pair_mask_kernel


def numba_section57_partner_contract() -> dict[str, object]:
    return {
        "partner": "numba",
        "numba_cuda_jit_required": True,
        "numba_cuda_jit_factory": "_numba_section57_overlay_valid_pair_mask_kernel_factory",
        "numba_cuda_jit_operation": "section57_overlay_valid_pair_mask",
        "existing_numba_continuations": (
            NUMBA_COMPACT_MASK_I64_OPERATION,
            NUMBA_SEGMENTED_COUNT_I64_OPERATION,
        ),
        "device_resident_input_required": True,
        "host_materialization_in_hot_path_allowed": False,
        "execution_boundary": "post_traversal_refinement_or_continuation",
        "optix_traversal_callback_injection": False,
        "v4_1_arbitrary_callback_scope_creep": False,
        "not_wrapper_theater_requirement": (
            "A valid runtime execution must compile a Numba CUDA kernel and run it "
            "on device-resident columns produced by RTDL/V4 traversal stages."
        ),
    }


def section57_device_column_component_status() -> dict[str, object]:
    """Report whether the codebase exposes the components needed by the route.

    This is a static capability audit, not performance evidence. It is used to
    distinguish "the repository lacks the route pieces" from "the route pieces
    exist and still require NVIDIA RT-core POD validation on real Section 5.7
    inputs."
    """

    from . import closed_shape_topology
    from . import optix_runtime

    required_symbols = {
        "segment_pair_candidate_device_columns": (
            "OPTIX_SEGMENT_PAIR_CANDIDATE_DEVICE_COLUMNS_SYMBOL",
            "PreparedOptixSegmentPairIntersection.candidate_device_columns",
        ),
        "segment_pair_grouped_count_device_columns": (
            "OPTIX_SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_SYMBOL",
            "PreparedOptixSegmentPairIntersection.left_id_count_device_columns",
        ),
        "segment_pair_exact_device_columns_prepared_left": (
            "OPTIX_SEGMENT_PAIR_EXACT_DEVICE_COLUMNS_PREPARED_LEFT_SYMBOL",
            "PreparedOptixSegmentPairIntersection.exact_device_columns_prepared_left",
        ),
        "closed_shape_relation_status_device_columns": (
            "OPTIX_CLOSED_SHAPE_MEMBERSHIP_RELATION_STATUS_CANDIDATE_DEVICE_COLUMNS_PREPARED_POINTS_SYMBOL",
            "PreparedOptixPointClosedShapeMembership2D.relation_status_candidate_device_columns_prepared_points",
        ),
    }
    components: dict[str, dict[str, object]] = {}
    for name, (symbol_name, method_path) in required_symbols.items():
        class_name, method_name = method_path.split(".", 1)
        owner_class = getattr(optix_runtime, class_name, None)
        components[name] = {
            "symbol_constant": symbol_name,
            "symbol_declared": hasattr(optix_runtime, symbol_name),
            "method": method_path,
            "python_method_declared": bool(owner_class is not None and hasattr(owner_class, method_name)),
        }
    relation_status_numba_owner = getattr(
        closed_shape_topology,
        "PreparedClosedShapeMembershipCandidateRefinerCupy",
        None,
    )
    relation_status_numba = bool(
        relation_status_numba_owner is not None
        and hasattr(
            relation_status_numba_owner,
            "count_relation_status_corrected_prepared_points_numba",
        )
    )
    components["numba_relation_status_continuation"] = {
        "method": (
            "PreparedClosedShapeMembershipCandidateRefinerCupy."
            "count_relation_status_corrected_prepared_points_numba"
        ),
        "python_method_declared": relation_status_numba,
        "partner": "numba",
    }
    all_declared = all(
        bool(row.get("symbol_declared", True)) and bool(row.get("python_method_declared", False))
        for row in components.values()
    )
    return {
        "required": True,
        "static_components_declared": bool(all_declared),
        "components": components,
        "end_to_end_composition_status": (
            "components_present_pod_validation_required"
            if all_declared
            else "missing_required_component_declaration"
        ),
        "performance_evidence_status": "not_measured",
        "claim_boundary": "Static component presence is not a paper-reproduction or speedup claim.",
    }


def _author_columns(*, query_exec: str | Path | None, polyover_exec: str | Path | None) -> dict[str, object]:
    query_ready = _path_exists(query_exec)
    polyover_ready = _path_exists(polyover_exec)
    ready = query_ready and polyover_ready
    return {
        "column": "author_code",
        "status": "ready" if ready else "blocked_missing_author_baseline",
        "query_exec": None if query_exec is None else str(query_exec),
        "polyover_exec": None if polyover_exec is None else str(polyover_exec),
        "query_exec_exists": query_ready,
        "polyover_exec_exists": polyover_ready,
        "required_for_full_paper_reproduction_claim": True,
        "correctness_required": "topology_geometry_hash_match_when_available",
        "performance_required": "same_section57_contract_timing_when_available",
    }


def _baseline_columns(
    *,
    pair_id: str,
    dataset_root: str | Path,
    query_exec: str | Path | None,
    polyover_exec: str | Path | None,
    exact_input_ready: bool,
) -> dict[str, object]:
    author = _author_columns(query_exec=query_exec, polyover_exec=polyover_exec)
    return {
        "author_code": author,
        "v2_14_exact_suite": {
            "column": "v2_14_exact_suite",
            "status": "ready" if exact_input_ready else "blocked_missing_inputs",
            "command": (
                "python scripts/rtdl_v2_14_benchmark_run_plan.py "
                f"--overlay-dataset-root {dataset_root} "
                f"--overlay-pairs {pair_id}"
            ),
            "correctness_required": "same_section57_contract",
        },
    }


def _candidate_status(
    *,
    exact_input_ready: bool,
    partner: str,
    numba_available: bool,
    section57_device_columns_ready: bool,
) -> tuple[str, str | None]:
    if partner != "numba":
        return "rejected_partner_not_numba", "This Section 5.7 automatic route is specifically the Numba partner route."
    if not exact_input_ready:
        return "skipped_missing_inputs", "Section 5.7 exact or same-source CDB inputs are missing."
    if not numba_available:
        return "skipped_numba_cuda_unavailable", "Numba CUDA is not available on this machine."
    if not section57_device_columns_ready:
        return (
            "blocked_missing_section57_device_columns",
            "Section 5.7 currently exposes host overlay summaries, not a device-resident candidate/refinement column stream for Numba.",
        )
    return "ready_for_measurement", None


def _numba_candidate_plans(
    *,
    exact_input_ready: bool,
    partner: str,
    numba_available: bool,
    section57_device_columns_ready: bool,
) -> tuple[Section57CandidatePlan, ...]:
    primary_status, primary_reason = _candidate_status(
        exact_input_ready=exact_input_ready,
        partner=partner,
        numba_available=numba_available,
        section57_device_columns_ready=section57_device_columns_ready,
    )
    secondary_status, secondary_reason = _candidate_status(
        exact_input_ready=exact_input_ready,
        partner=partner,
        numba_available=numba_available,
        section57_device_columns_ready=section57_device_columns_ready,
    )
    digest_status, digest_reason = _candidate_status(
        exact_input_ready=exact_input_ready,
        partner=partner,
        numba_available=numba_available,
        section57_device_columns_ready=section57_device_columns_ready,
    )
    primary_stages = (
        Section57PlanStage(
            stage_id="broadphase_candidate_pairs",
            role="candidate_pair_generation",
            owner="rtdl_v4",
            primitive="shape_pair_relation_or_aabb_index_query",
            partner=None,
            execution_boundary="pre_traversal_or_native_query",
            device_resident_input_required=True,
        ),
        Section57PlanStage(
            stage_id="rt_refinement_lsi_pip",
            role="rayjoin_lsi_pip_refinement",
            owner="rtdl_v4",
            primitive="ray_segment_intersection_and_point_location",
            partner=None,
            execution_boundary="native_rt_traversal",
            device_resident_input_required=True,
        ),
        Section57PlanStage(
            stage_id="numba_valid_pair_mask",
            role="post_traversal_valid_pair_filter",
            owner="numba_partner",
            primitive="section57_overlay_valid_pair_mask",
            partner="numba",
            execution_boundary="post_traversal_refinement",
            device_resident_input_required=True,
            numba_cuda_jit_required=True,
            optix_traversal_callback_injection=False,
        ),
        Section57PlanStage(
            stage_id="numba_mask_compaction",
            role="post_traversal_compaction",
            owner="numba_partner",
            primitive=NUMBA_COMPACT_MASK_I64_OPERATION,
            partner="numba",
            execution_boundary="post_traversal_continuation",
            device_resident_input_required=True,
            numba_cuda_jit_required=True,
            optix_traversal_callback_injection=False,
        ),
    )
    secondary_stages = primary_stages[:-1] + (
        Section57PlanStage(
            stage_id="numba_segmented_overlay_counts",
            role="post_traversal_grouped_count",
            owner="numba_partner",
            primitive=NUMBA_SEGMENTED_COUNT_I64_OPERATION,
            partner="numba",
            execution_boundary="post_traversal_continuation",
            device_resident_input_required=True,
            numba_cuda_jit_required=True,
            optix_traversal_callback_injection=False,
        ),
    )
    digest_stages = primary_stages[:-1] + (
        Section57PlanStage(
            stage_id="numba_exact_lsi_stream_digest",
            role="post_traversal_geometry_digest",
            owner="numba_partner",
            primitive="exact_lsi_id_xy_stream_digest",
            partner="numba",
            execution_boundary="post_traversal_continuation",
            device_resident_input_required=True,
            numba_cuda_jit_required=True,
            optix_traversal_callback_injection=False,
        ),
    )
    return (
        Section57CandidatePlan(
            plan_id="v4_numba_post_traversal_mask_compact",
            user_semantics="section57_polygon_overlay",
            partner=partner,
            selection_role="v4_numba_selected_plan",
            expected_output_schema="overlay_valid_pair_rows_then_optional_chain_assembly",
            correctness_comparator="topology_geometry_hash_against_v2_14_and_author_when_available",
            stages=primary_stages,
            status=primary_status,
            skip_reason=primary_reason,
        ),
        Section57CandidatePlan(
            plan_id="v4_numba_post_traversal_segmented_counts",
            user_semantics="section57_polygon_overlay",
            partner=partner,
            selection_role="v4_numba_selected_plan",
            expected_output_schema="overlay_grouped_counts_and_witness_summaries",
            correctness_comparator="topology_geometry_hash_against_v2_14_and_author_when_available",
            stages=secondary_stages,
            status=secondary_status,
            skip_reason=secondary_reason,
        ),
        Section57CandidatePlan(
            plan_id="v4_numba_post_traversal_lsi_stream_digest",
            user_semantics="section57_polygon_overlay",
            partner=partner,
            selection_role="v4_numba_selected_plan",
            expected_output_schema="exact_lsi_id_xy_stream_digest_not_full_overlay_output",
            correctness_comparator="topology_geometry_hash_against_v2_14_and_author_when_available",
            stages=digest_stages,
            status=digest_status,
            skip_reason=digest_reason,
        ),
    )


def _select_candidate(candidates: Iterable[dict[str, object]], *, select: str) -> dict[str, object] | None:
    if select != "fastest_valid":
        raise ValueError("the Section 5.7 automatic route currently supports select='fastest_valid' only")
    measured = [
        candidate
        for candidate in candidates
        if candidate.get("status") == "measured"
        and candidate.get("correctness_status") == "pass"
        and candidate.get("measured_total_sec") is not None
    ]
    if not measured:
        return None
    return min(measured, key=lambda row: float(row["measured_total_sec"]))


def _positive_float(value: object) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    value = float(value)
    if value <= 0.0:
        return None
    return value


def _load_measured_candidate_rows(path: str | Path | None) -> tuple[list[dict[str, object]], dict[str, object]]:
    if path is None:
        return [], {
            "provided": False,
            "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
            "accepted_count": 0,
            "rejected_count": 0,
            "rejections": [],
        }
    measurement_path = Path(path)
    try:
        payload = json.loads(measurement_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [], {
            "provided": True,
            "path": str(measurement_path),
            "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
            "accepted_count": 0,
            "rejected_count": 1,
            "rejections": [{"reason": "measurement_file_unreadable", "detail": str(exc)}],
        }
    if not isinstance(payload, dict):
        return [], {
            "provided": True,
            "path": str(measurement_path),
            "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
            "accepted_count": 0,
            "rejected_count": 1,
            "rejections": [{"reason": "measurement_payload_not_object"}],
        }
    rows = payload.get("rows")
    if payload.get("schema") != RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA or not isinstance(rows, list):
        return [], {
            "provided": True,
            "path": str(measurement_path),
            "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
            "observed_schema": payload.get("schema"),
            "accepted_count": 0,
            "rejected_count": 1,
            "rejections": [{"reason": "measurement_schema_or_rows_invalid"}],
        }
    return [row for row in rows if isinstance(row, dict)], {
        "provided": True,
        "path": str(measurement_path),
        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
        "accepted_count": 0,
        "rejected_count": 0,
        "rejections": [],
    }


def _measurement_rejection_reason(
    row: dict[str, object],
    *,
    candidate: dict[str, object] | None,
) -> str | None:
    if candidate is None:
        return "candidate_not_found_for_pair_and_plan"
    if row.get("correctness_status") != "pass":
        return "correctness_not_pass"
    if _positive_float(row.get("measured_total_sec")) is None:
        return "missing_positive_measured_total_sec"
    if row.get("measurement_source") != "pod_runtime":
        return "measurement_source_not_pod_runtime"
    if row.get("topology_geometry_hash_match") is not True:
        return "topology_geometry_hash_not_confirmed"
    if row.get("device_column_route") is not True:
        return "device_column_route_not_confirmed"
    if row.get("host_materialization_in_hot_path") is not False:
        return "host_materialization_in_hot_path_not_rejected"
    return None


def _apply_measured_candidates(
    candidates: list[dict[str, object]],
    *,
    measured_candidates_path: str | Path | None,
) -> dict[str, object]:
    rows, summary = _load_measured_candidate_rows(measured_candidates_path)
    if not rows:
        return summary
    by_key = {
        (candidate.get("pair_id"), candidate.get("plan_id")): candidate
        for candidate in candidates
    }
    accepted_count = 0
    rejections: list[dict[str, object]] = list(summary.get("rejections", []))
    for row in rows:
        key = (row.get("pair_id"), row.get("plan_id"))
        candidate = by_key.get(key)
        reason = _measurement_rejection_reason(row, candidate=candidate)
        if reason is not None:
            rejections.append(
                {
                    "pair_id": row.get("pair_id"),
                    "plan_id": row.get("plan_id"),
                    "reason": reason,
                }
            )
            if candidate is not None:
                candidate.setdefault("measurement_rejections", []).append(reason)
                candidate["status"] = "measured_rejected"
                candidate["correctness_status"] = row.get("correctness_status", "not_pass")
                candidate["rejection_reason"] = reason
                candidate["measured_total_sec"] = _positive_float(row.get("measured_total_sec"))
                candidate["steady_state_sec"] = _positive_float(row.get("steady_state_sec"))
                candidate["measurement_source"] = row.get("measurement_source")
                candidate["topology_geometry_hash_match"] = row.get("topology_geometry_hash_match")
                candidate["device_column_route"] = row.get("device_column_route")
                candidate["host_materialization_in_hot_path"] = row.get("host_materialization_in_hot_path")
            continue
        assert candidate is not None
        candidate["status"] = "measured"
        candidate["correctness_status"] = "pass"
        candidate["skip_reason"] = None
        candidate["measured_total_sec"] = _positive_float(row.get("measured_total_sec"))
        candidate["steady_state_sec"] = _positive_float(row.get("steady_state_sec"))
        compile_jit_sec = row.get("compile_jit_sec")
        candidate["compile_jit_sec"] = (
            None
            if not isinstance(compile_jit_sec, (int, float))
            else max(0.0, float(compile_jit_sec))
        )
        candidate["v4_vs_v2_14_speedup"] = row.get("v4_vs_v2_14_speedup")
        candidate["measurement_source"] = row.get("measurement_source")
        candidate["topology_geometry_hash_match"] = True
        candidate["device_column_route"] = True
        candidate["host_materialization_in_hot_path"] = False
        candidate["measurement_artifact"] = {
            key: row[key]
            for key in (
                "v2_14_total_sec",
                "author_rt_process_sec",
                "notes",
            )
            if key in row
        }
        accepted_count += 1
    summary["accepted_count"] = accepted_count
    summary["rejected_count"] = len(rejections)
    summary["rejections"] = rejections
    return summary


def _claim_classification(
    *,
    rows: list[dict[str, object]],
    selected_plan: dict[str, object] | None,
) -> str:
    if any(not bool(row["exact_input_ready"]) for row in rows):
        return "blocked_missing_inputs"
    if any(row["baselines"]["author_code"]["status"] == "blocked_missing_author_baseline" for row in rows):
        return "blocked_missing_author_baseline"
    if selected_plan is None:
        return "not_release_ready"
    speedup = selected_plan.get("v4_vs_v2_14_speedup")
    if speedup is None:
        return "candidate_stage_measured_no_app_speedup_claim"
    if isinstance(speedup, (int, float)) and float(speedup) >= 1.2:
        return "high_performance"
    if isinstance(speedup, (int, float)) and float(speedup) >= 0.98:
        return "parity"
    return "regression"


def section57_polygon_overlay(
    *,
    dataset_root: str | Path = "data/rayjoin_section57_cdb",
    partner: str = "numba",
    select: str = "fastest_valid",
    pairs: str | Iterable[str] | None = None,
    query_exec: str | Path | None = None,
    polyover_exec: str | Path | None = None,
    output_dir: str | Path = "artifacts/rayjoin_section57_numba_auto",
    input_provenance: str = "paper_preprocessed_cdb",
    warmup: int = 1,
    repeat: int = 3,
    check_runtime: bool = True,
    section57_device_columns_ready: bool = False,
    measured_candidates_path: str | Path | None = None,
) -> dict[str, object]:
    """Plan the V4+Numba RayJoin Section 5.7 automatic primitive route.

    This is a semantic entrypoint: callers name the workload and partner, not
    primitive names. The current function builds the auditable candidate
    scoreboard and blocks complete paper-reproduction claims when exact inputs,
    author baselines, or Numba CUDA are unavailable.
    """

    partner = str(partner).strip().lower()
    if partner != "numba":
        raise ValueError("the Section 5.7 automatic route supports partner='numba'")
    started = time.perf_counter()
    pair_ids = _split_csv(pairs, default=(pair.pair_id for pair in paper_pairs()))
    availability = availability_matrix(Path(dataset_root), pair_ids=pair_ids, program_ids=("overlay",))
    numba_available = _numba_cuda_available() if check_runtime else False
    rows: list[dict[str, object]] = []
    all_candidates: list[dict[str, object]] = []
    for row in availability:
        candidates = [
            asdict(candidate)
            for candidate in _numba_candidate_plans(
                exact_input_ready=bool(row.exact_input_ready),
                partner=partner,
                numba_available=numba_available,
                section57_device_columns_ready=bool(section57_device_columns_ready),
            )
        ]
        for candidate in candidates:
            candidate["pair_id"] = row.pair_id
            candidate["paper_label"] = row.paper_label
            candidate["compile_jit_sec"] = None
            candidate["measurement_policy"] = {
                "warmup": int(warmup),
                "repeat": int(repeat),
                "compile_jit_overhead_separated": True,
            }
        all_candidates.extend(candidates)
        rows.append(
            {
                "pair_id": row.pair_id,
                "paper_label": row.paper_label,
                "exact_input_ready": bool(row.exact_input_ready),
                "blocker": row.blocker,
                "left_path": row.left.path,
                "right_path": row.right.path,
                "paper_rayjoin_table4_seconds": {
                    "processing_sec": RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"][row.pair_id][0],
                    "preprocessing_sec": RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"][row.pair_id][1],
                },
                "baselines": _baseline_columns(
                    pair_id=row.pair_id,
                    dataset_root=dataset_root,
                    query_exec=query_exec,
                    polyover_exec=polyover_exec,
                    exact_input_ready=bool(row.exact_input_ready),
                ),
                "candidate_plans": candidates,
                "correctness_gate": {
                    "status": "not_run" if row.exact_input_ready else "blocked_missing_inputs",
                    "topology_geometry_hash_required": True,
                    "row_count_only_sufficient": False,
                },
            }
        )
    measurement_import = _apply_measured_candidates(
        all_candidates,
        measured_candidates_path=measured_candidates_path,
    )
    selected = _select_candidate(all_candidates, select=select)
    payload = {
        "schema": RAYJOIN_SECTION57_NUMBA_AUTO_PLANNER_SCHEMA,
        "status": RAYJOIN_SECTION57_NUMBA_AUTO_PLAN_STATUS,
        "user_semantics": {
            "workload": "rayjoin_section57_polygon_overlay",
            "partner": partner,
            "select": select,
            "primitive_names_required_from_user": False,
        },
        "dataset_root": str(dataset_root),
        "output_dir": str(output_dir),
        "input_provenance": input_provenance,
        "pairs": pair_ids,
        "numba_partner_contract": numba_section57_partner_contract(),
        "runtime_probe": {
            "numba_cuda_available": numba_available,
            "checked_runtime": bool(check_runtime),
            "section57_device_columns_ready": bool(section57_device_columns_ready),
            "section57_device_columns_requirement": SECTION57_DEVICE_COLUMN_REQUIREMENT,
            "section57_device_column_components": section57_device_column_component_status(),
        },
        "columns": ("author_code", "v2_14_exact_suite", "v4_numba_selected_plan"),
        "candidate_scoreboard": all_candidates,
        "selected_plan": selected,
        "measurement_import": measurement_import,
        "selection_policy": {
            "name": select,
            "measured_candidate_required": True,
            "hardcoded_default_allowed": False,
            "valid_measurement_required": {
                "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
                "measurement_source": "pod_runtime",
                "correctness_status": "pass",
                "topology_geometry_hash_match": True,
                "device_column_route": True,
                "host_materialization_in_hot_path": False,
            },
        },
        "rows": rows,
        "claim_classification": _claim_classification(rows=rows, selected_plan=selected),
        "non_authorizations": {
            "full_paper_reproduction_claim": False,
            "public_high_performance_claim": False,
            "v4_1_arbitrary_callback_claim": False,
        },
        "elapsed_planner_sec": time.perf_counter() - started,
    }
    return payload


def write_section57_numba_auto_evidence(
    payload: dict[str, object],
    *,
    output_json: str | Path | None = None,
    output_md: str | Path | None = None,
) -> None:
    if output_json is not None:
        path = Path(output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if output_md is not None:
        path = Path(output_md)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_section57_numba_auto_markdown(payload), encoding="utf-8")


def render_section57_numba_auto_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# RayJoin Section 5.7 V4+Numba Auto-Primitive Planner",
        "",
        f"Schema: `{payload['schema']}`",
        f"Claim classification: `{payload['claim_classification']}`",
        f"Dataset root: `{payload['dataset_root']}`",
        "",
        "## User Semantics",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for key, value in payload["user_semantics"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Candidate Scoreboard",
            "",
            "| Pair | Plan | Status | Skip Reason | Correctness | Numba JIT | Boundary |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for candidate in payload["candidate_scoreboard"]:
        stages = candidate.get("stages") or ()
        numba_jit = any(bool(stage.get("numba_cuda_jit_required")) for stage in stages)
        boundary_ok = all(not bool(stage.get("optix_traversal_callback_injection")) for stage in stages)
        lines.append(
            f"| {candidate['paper_label']} | `{candidate['plan_id']}` | `{candidate['status']}` | "
            f"{candidate.get('skip_reason') or ''} | `{candidate.get('correctness_status')}` | "
            f"{numba_jit} | {'post-traversal only' if boundary_ok else 'invalid callback injection'} |"
        )
    lines.extend(
        [
            "",
            "## Measurement Import",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Provided | `{payload['measurement_import'].get('provided')}` |",
            f"| Accepted rows | `{payload['measurement_import'].get('accepted_count')}` |",
            f"| Rejected rows | `{payload['measurement_import'].get('rejected_count')}` |",
            "",
            "## Author / V2.14 / V4 Columns",
            "",
            "| Pair | Author Code | V2.14 Exact Suite | V4+Numba Candidates |",
            "|---|---|---|---:|",
        ]
    )
    for row in payload["rows"]:
        author = row["baselines"]["author_code"]["status"]
        v214 = row["baselines"]["v2_14_exact_suite"]["status"]
        lines.append(
            f"| {row['paper_label']} | `{author}` | `{v214}` | {len(row['candidate_plans'])} |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Primitive names are not required from the user.",
            "- Numba partner work must use `numba.cuda.jit` on device-resident arrays.",
            "- Numba stays outside the OptiX traversal loop in V4.0.",
            "- Full paper reproduction requires author-code correctness and timing.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "RAYJOIN_SECTION57_NUMBA_AUTO_PLANNER_SCHEMA",
    "RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA",
    "RAYJOIN_SECTION57_NUMBA_AUTO_PLAN_STATUS",
    "RAYJOIN_SECTION57_NUMBA_PARTNER_SCOPE",
    "Section57CandidatePlan",
    "Section57PlanStage",
    "numba_section57_partner_contract",
    "render_section57_numba_auto_markdown",
    "section57_polygon_overlay",
    "write_section57_numba_auto_evidence",
]
