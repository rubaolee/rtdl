"""Private RTDL 3.0 end-to-end driver for the locked LibRTS workload."""

from pathlib import Path
import sys

import rtdsl as rt

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_librts_migration", APP_DIR / "rtdl3_action_migration.py")
_app = load_app_module("rtdl3_librts_app", APP_DIR / "librts_reproduction.py")
_pip = load_app_module("rtdl3_librts_pip", APP_DIR / "librts_author_pip_compat.py")


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_reference"
    elif execution_mode == "compiler":
        pair = _migration.run_optix_semantic_pair()
        selected = "compiler_selected_action"
    else:
        raise ValueError("LibRTS execution_mode must be reference or compiler")
    boundary_matched = bool(
        pair.get(
            "boundary_touch_matched",
            pair.get("boundary_discriminator", {}).get("boundary_matched", False),
        )
    )
    return build_locked_workload_driver_result(
        app="librts",
        workload="tiny_inclusive_range_intersects",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "committed_indexed_and_query_aabb_columns", "owner": "app"},
            {"kind": "spatial_producer", "name": "prepared_aabb_overlap_candidates_2d", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "typed_closed_overlap_filter_emit_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_query_indexed_relation_rows", "owner": "app"},
        ),
        output=pair["actual_rows"],
        matched=bool(pair["matched"] and boundary_matched),
        source_result=pair,
    )


def run_v3_wkt(
    indexed_path,
    query_path,
    *,
    minimum_overlap: float = 0.0,
    execution_mode: str = "reference",
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
):
    boxes = tuple(_app.load_boxes(Path(indexed_path)))
    queries = tuple(_app.load_boxes(Path(query_path)))
    if execution_mode == "reference":
        pair = _migration.run_reference_boxes(
            boxes, queries, minimum_overlap=minimum_overlap
        )
    elif execution_mode == "compiler":
        pair = _migration.run_optix_boxes(
            boxes,
            queries,
            minimum_overlap=minimum_overlap,
            validate_against_reference=validate_against_reference,
            collect_phase_trace=collect_phase_trace,
        )
    else:
        raise ValueError("LibRTS execution_mode must be reference or compiler")
    return {
        "schema": "rtdl.research.v3.paper_app_driver.librts_wkt.v1",
        "app": "librts",
        "requested_execution_mode": execution_mode,
        "selected_execution": pair["backend"],
        "application_selected_backend": False,
        "output": pair["actual_rows"],
        "matched": (
            bool(pair["matched"])
            if pair.get("reference_validation_performed", True)
            else None
        ),
        "reference_validation_performed": pair.get(
            "reference_validation_performed", True
        ),
        "source_result": pair,
        "real_input_frontdoor_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_prepared_count_batches(
    indexed_columns,
    query_batches,
    *,
    operation: str,
    execution_mode: str = "compiler",
):
    """Execute distinct count batches through one compiler-owned prepared base."""

    if execution_mode != "compiler":
        raise ValueError("LibRTS prepared count execution_mode must be compiler")
    if operation not in {"point_contains", "range_contains"}:
        raise ValueError("prepared count operation must be point_contains or range_contains")
    batches = tuple((str(name), queries) for name, queries in query_batches)
    if not batches or len({name for name, _ in batches}) != len(batches):
        raise ValueError("query batches must be nonempty with unique names")
    prepared = rt.prepare_compiler_aabb_index_2d_columns(
        indexed_columns,
        operations=(operation,),
        max_query_count=max(len(queries) for _, queries in batches),
        semantic_statement_stable_id=_migration.CANONICAL_ALGORITHM_BINDINGS[
            "prepared_aabb_query"
        ][0],
        backend_contract_id=_migration.CANONICAL_ALGORITHM_BINDINGS[
            "prepared_aabb_query"
        ][1],
    )
    rows = []
    try:
        for name, queries in batches:
            result = prepared.count(
                point_queries=queries if operation == "point_contains" else (),
                box_queries=queries if operation == "range_contains" else (),
                operation=operation,
            )
            rows.append(
                {
                    "batch": name,
                    "query_count": len(queries),
                    "result_count": int(result["counts"][operation]),
                    "primitive": result["primitive"],
                    "contract": result["contract"],
                }
            )
        compiler_plan = prepared.to_metadata()
    finally:
        prepared.close()
    compiler_plan = prepared.to_metadata()
    return {
        "schema": "rtdl.research.v3.paper_app_driver.librts_prepared_count_batches.v1",
        "app": "librts",
        "requested_execution_mode": execution_mode,
        "operation": operation,
        "output": rows,
        "prepared_base_reused_across_batches": True,
        "prepared_base_query_batch_count": len(rows),
        "compiler_plan": compiler_plan,
        "application_selected_backend": False,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_prepared_aabb_portfolio(
    indexed_columns,
    *,
    range_contains_batches,
    point_contains_batches,
    execution_mode: str = "compiler",
):
    """Reuse one prepared geometry base across both containment operations."""

    if execution_mode != "compiler":
        raise ValueError("LibRTS prepared portfolio execution_mode must be compiler")
    range_batches = tuple((str(name), queries) for name, queries in range_contains_batches)
    point_batches = tuple((str(name), queries) for name, queries in point_contains_batches)
    names = [f"range_contains:{name}" for name, _ in range_batches] + [
        f"point_contains:{name}" for name, _ in point_batches
    ]
    if not range_batches or not point_batches or len(names) != len(set(names)):
        raise ValueError("both containment batch sets must be nonempty with unique names")
    prepared = rt.prepare_compiler_aabb_index_2d_columns(
        indexed_columns,
        operations=("range_contains", "point_contains"),
        max_query_count=max(
            max(len(queries) for _, queries in range_batches),
            max(len(queries) for _, queries in point_batches),
        ),
        semantic_statement_stable_id=_migration.CANONICAL_ALGORITHM_BINDINGS[
            "prepared_aabb_query"
        ][0],
        backend_contract_id=_migration.CANONICAL_ALGORITHM_BINDINGS[
            "prepared_aabb_query"
        ][1],
    )
    output = {"range_contains": [], "point_contains": []}
    try:
        for name, queries in range_batches:
            result = prepared.count(box_queries=queries, operation="range_contains")
            output["range_contains"].append(
                {
                    "batch": name,
                    "query_count": len(queries),
                    "result_count": int(result["counts"]["range_contains"]),
                }
            )
        for name, queries in point_batches:
            result = prepared.count(point_queries=queries, operation="point_contains")
            output["point_contains"].append(
                {
                    "batch": name,
                    "query_count": len(queries),
                    "result_count": int(result["counts"]["point_contains"]),
                }
            )
    finally:
        prepared.close()
    return {
        "schema": "rtdl.research.v3.paper_app_driver.librts_prepared_aabb_portfolio.v1",
        "app": "librts",
        "requested_execution_mode": execution_mode,
        "output": output,
        "prepared_geometry_base_count": 1,
        "prepared_base_reused_across_operations": True,
        "prepared_base_query_batch_count": len(range_batches) + len(point_batches),
        "compiler_plan": prepared.to_metadata(),
        "application_selected_backend": False,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_range_intersects_columns(
    indexed_columns,
    query_columns,
    *,
    execution_mode: str = "compiler",
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
):
    if execution_mode != "compiler":
        raise ValueError("LibRTS range-intersects execution_mode must be compiler")
    indexed_boxes = tuple(
        row
        if all(hasattr(row, name) for name in ("min_x", "min_y", "max_x", "max_y"))
        else _app.Box2D(*(float(value) for value in row))
        for row in indexed_columns
    )
    query_boxes = tuple(
        row
        if all(hasattr(row, name) for name in ("min_x", "min_y", "max_x", "max_y"))
        else _app.Box2D(*(float(value) for value in row))
        for row in query_columns
    )
    pair = _migration.run_optix_boxes(
        indexed_boxes,
        query_boxes,
        minimum_overlap=0.0,
        validate_against_reference=validate_against_reference,
        collect_phase_trace=collect_phase_trace,
    )
    return {
        "schema": "rtdl.research.v3.paper_app_driver.librts_range_intersects_columns.v1",
        "app": "librts",
        "requested_execution_mode": execution_mode,
        "output": pair["actual_rows"],
        "matched": pair["matched"],
        "source_result": pair,
        "application_selected_backend": False,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def load_v3_representative_pip_inputs(polygons_path, points_path):
    return _pip.load_author_compatible_pip_inputs(
        polygons_path=Path(polygons_path),
        points_path=Path(points_path),
    )


def run_v3_representative_pip_loaded(inputs, *, execution_mode: str = "compiler"):
    result = _pip.run_author_compatible_pip_loaded(
        inputs,
        execution_mode=execution_mode,
    )
    return {
        "schema": "rtdl.research.v3.paper_app_driver.librts_representative_pip.v1",
        "app": "librts",
        "requested_execution_mode": execution_mode,
        "output": result["candidate_id_rows"],
        "result_count": result["result_count"],
        "source_result": result,
        "application_selected_backend": False,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


__all__ = (
    "load_v3_representative_pip_inputs",
    "run_v3_app",
    "run_v3_prepared_aabb_portfolio",
    "run_v3_prepared_count_batches",
    "run_v3_range_intersects_columns",
    "run_v3_representative_pip_loaded",
    "run_v3_wkt",
)
