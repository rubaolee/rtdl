"""Private RTDL 3.0 end-to-end driver for the locked RTNN workload."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_rtnn_migration", APP_DIR / "rtdl3_action_migration.py")


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_reference"
    elif execution_mode == "compiler":
        pair = _migration.run_optix_semantic_pair()
        selected = "compiler_selected_action"
    else:
        raise ValueError("RTNN execution_mode must be reference or compiler")
    return build_locked_workload_driver_result(
        app="rtnn",
        workload="bounded_exact_ranked_distance_window_topk",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "locked_xyz_query_and_search_columns", "owner": "app"},
            {"kind": "spatial_producer", "name": "prepared_point_candidates_3d", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "typed_filter_bounded_topk_action", "owner": "rtdl"},
            {"kind": "output", "name": "canonical_ranked_neighbor_rows", "owner": "app"},
        ),
        output=pair["actual_rows"],
        matched=bool(pair["matched"]),
        source_result=pair,
    )


def run_v3_points(
    search_points,
    query_points,
    *,
    k: int,
    min_distance: float = 0.0,
    max_distance: float,
    execution_mode: str = "reference",
    collect_phase_trace: bool = False,
):
    if execution_mode == "reference":
        pair = _migration.run_reference_points(
            search_points,
            query_points,
            k=k,
            min_distance=min_distance,
            max_distance=max_distance,
        )
    elif execution_mode == "compiler":
        pair = _migration.run_compiler_points(
            search_points,
            query_points,
            k=k,
            min_distance=min_distance,
            max_distance=max_distance,
            collect_phase_trace=collect_phase_trace,
        )
    else:
        raise ValueError("RTNN execution_mode must be reference or compiler")
    return {
        "schema": "rtdl.research.v3.paper_app_driver.rtnn_points.v1",
        "app": "rtnn",
        "requested_execution_mode": execution_mode,
        "selected_execution": pair["backend"],
        "application_selected_backend": False,
        "output": pair["actual_rows"],
        "matched": bool(pair["matched"]),
        "source_result": pair,
        "real_input_frontdoor_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


__all__ = ("run_v3_app", "run_v3_points")
