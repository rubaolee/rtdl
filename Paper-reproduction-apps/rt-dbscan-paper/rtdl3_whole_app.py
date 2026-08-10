"""Private RTDL 3.0 end-to-end driver for the locked RT-DBSCAN workload."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_rtdbscan_migration", APP_DIR / "rtdl3_action_migration.py")


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_plus_generic_components"
    elif execution_mode == "compiler":
        pair = _migration.run_compiler_semantic_pair()
        selected = pair["selected_producer_kind"]
    else:
        raise ValueError("RT-DBSCAN execution_mode must be reference or compiler")
    return build_locked_workload_driver_result(
        app="rt_dbscan",
        workload="bounded_radius_graph_component_partition",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "locked_point_columns_and_density_parameters", "owner": "app"},
            {"kind": "spatial_producer", "name": "compiler_selected_fixed_radius_graph_producer", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "certified_radius_edge_action_or_equivalent_component_operator", "owner": "rtdl"},
            {"kind": "output", "name": "core_flags_and_canonical_partition", "owner": "app"},
        ),
        output=pair["actual"],
        matched=bool(pair["matched"]),
        source_result=pair,
    )


def run_v3_points(
    points,
    *,
    epsilon: float,
    min_points: int,
    execution_mode: str = "reference",
    collect_phase_trace: bool = False,
    validate_reference: bool = True,
):
    if execution_mode == "reference":
        pair = _migration.run_reference_points(
            points, epsilon=epsilon, min_points=min_points
        )
    elif execution_mode == "compiler":
        pair = _migration.run_compiler_points(
            points,
            epsilon=epsilon,
            min_points=min_points,
            collect_phase_trace=collect_phase_trace,
            validate_reference=validate_reference,
        )
    else:
        raise ValueError("RT-DBSCAN execution_mode must be reference or compiler")
    return {
        "schema": "rtdl.research.v3.paper_app_driver.rt_dbscan_points.v1",
        "app": "rt_dbscan",
        "requested_execution_mode": execution_mode,
        "selected_execution": (
            pair.get("selected_producer_kind", pair["backend"])
            if execution_mode == "compiler"
            else pair["backend"]
        ),
        "application_selected_backend": False,
        "output": pair["actual"],
        "matched": bool(pair["matched"]),
        "source_result": pair,
        "real_input_frontdoor_supported": True,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


__all__ = ("run_v3_app", "run_v3_points")
