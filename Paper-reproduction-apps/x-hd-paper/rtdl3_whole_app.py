"""Private RTDL 3.0 end-to-end driver for the locked X-HD workload."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_xhd_migration", APP_DIR / "rtdl3_action_migration.py")


def run_v3_app(*, execution_mode: str = "reference"):
    if execution_mode == "reference":
        pair = _migration.run_local_semantic_pair()
        selected = "action_cpu_plus_generic_max_nearest"
    elif execution_mode == "compiler":
        pair = _migration.run_numba_resident_composition_pair()
        selected = "compiler_selected_action_plus_device_global_reducer"
    else:
        raise ValueError("X-HD execution_mode must be reference or compiler")
    return build_locked_workload_driver_result(
        app="x_hd",
        workload="directed_exact_max_of_nearest_witness",
        requested_execution_mode=execution_mode,
        selected_execution=selected,
        stages=(
            {"kind": "input", "name": "locked_directed_point_columns", "owner": "app"},
            {"kind": "spatial_producer", "name": "complete_query_grouped_distance_rows", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "certified_query_min_action_then_global_max_reducer", "owner": "rtdl"},
            {"kind": "output", "name": "directed_hd_value_and_witness", "owner": "app"},
        ),
        output=pair["actual"],
        matched=bool(pair["matched"]),
        source_result=pair,
    )


def run_v3_points(
    sources,
    targets,
    *,
    execution_mode: str = "reference",
    validate_against_reference: bool = True,
    collect_phase_trace: bool = False,
):
    if execution_mode == "reference":
        pair = _migration.run_reference_points(sources, targets)
    elif execution_mode == "compiler":
        import numpy as np

        source_matrix = np.asarray(sources)
        target_matrix = np.asarray(targets)
        use_scalable_3d = (
            source_matrix.ndim == 2
            and target_matrix.ndim == 2
            and source_matrix.shape[1:] == (3,)
            and target_matrix.shape[1:] == (3,)
        )
        if use_scalable_3d:
            pair = _migration.run_scalable_compiler_points(
                source_matrix,
                target_matrix,
                validate_against_reference=validate_against_reference,
                collect_phase_trace=collect_phase_trace,
            )
        else:
            pair = _migration.run_numba_resident_points(
                sources,
                targets,
                validate_against_reference=validate_against_reference,
                collect_phase_trace=collect_phase_trace,
            )
    else:
        raise ValueError("X-HD execution_mode must be reference or compiler")
    return {
        "schema": "rtdl.research.v3.paper_app_driver.xhd_points.v1",
        "app": "x_hd",
        "requested_execution_mode": execution_mode,
        "selected_execution": pair["backend"],
        "application_selected_backend": False,
        "output": pair["actual"],
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


__all__ = ("run_v3_app", "run_v3_points")
