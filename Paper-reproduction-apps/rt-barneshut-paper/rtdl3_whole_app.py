"""Private RTDL 3.0 driver using the stronger aggregate-hierarchy operator."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))

from rtdl3_whole_app_contract import build_locked_workload_driver_result, load_app_module

_migration = load_app_module("rtdl3_rtbh_migration", APP_DIR / "rtdl3_action_migration.py")
_adapter = load_app_module("rtdl3_rtbh_adapter", APP_DIR / "aggregate_hierarchy_adapter.py")


def _prepared_force_driver_result(
    result,
    *,
    execution_mode: str,
    force_output,
):
    comparison = result["comparison_to_reference_executor_force_rows"]
    output = {
        "source_count": int(comparison["source_count"]),
        "checksum_scalar_force": round(float(result["checksum_scalar_force"]), 9),
        "mismatch_count": int(comparison["mismatch_count"]),
    }
    return {
        "schema": "rtdl.research.v3.paper_app_driver.rt_barneshut_prepared_arrays.v1",
        "app": "rt_barneshut",
        "requested_execution_mode": execution_mode,
        "selected_execution": "generic_aggregate_hierarchy_numba",
        "application_selected_backend": False,
        "output": output,
        "matched": bool(comparison["match"]),
        "source_result": result,
        "real_input_frontdoor_supported": True,
        "prepared_state_input_supported": True,
        "complete_force_rows_materialized": force_output is not None,
        "force_output": None if force_output is None else str(Path(force_output)),
        "independent_tree_construction_supported": False,
        "v2_scoped_application_surface_rewritten": True,
        "paper_reproduction_complete": False,
        "runtime_performance_claimed": False,
    }


def run_v3_app(*, execution_mode: str = "compiler"):
    if execution_mode != "compiler":
        raise ValueError("RT-BarnesHut execution_mode must be compiler")
    result = _adapter.run_generic_aggregate_frontier_numba_force_bridge(
        _migration._synthetic_prepared()
    )
    result = dict(result)
    result["checksum_scalar_force"] = round(
        float(result["checksum_scalar_force"]), 9
    )
    comparison = result["comparison_to_reference_executor_force_rows"]
    output = {
        "source_count": int(comparison["source_count"]),
        "checksum_scalar_force": float(result["checksum_scalar_force"]),
        "mismatch_count": int(comparison["mismatch_count"]),
    }
    return build_locked_workload_driver_result(
        app="rt_barneshut",
        workload="synthetic_prepared_aggregate_force_rows",
        requested_execution_mode=execution_mode,
        selected_execution="generic_aggregate_hierarchy_numba",
        stages=(
            {"kind": "input", "name": "app_owned_prepared_hierarchy_arrays", "owner": "app"},
            {"kind": "spatial_producer", "name": "aggregate_hierarchy_3d", "owner": "rtdl"},
            {"kind": "action_or_operator", "name": "generic_frontier_reduce_numba", "owner": "rtdl"},
            {"kind": "output", "name": "app_owned_scalar_force_rows", "owner": "app"},
        ),
        output=output,
        matched=bool(comparison["match"]),
        source_result=result,
    )


def run_v3_prepared_arrays(
    path,
    *,
    max_ratio: float = 0.5,
    force_output=None,
    execution_mode: str = "compiler",
):
    if execution_mode != "compiler":
        raise ValueError("RT-BarnesHut execution_mode must be compiler")
    result = _adapter.read_prepared_arrays_and_run_generic_numba_force_bridge(
        Path(path),
        max_ratio=max_ratio,
        force_output=None if force_output is None else Path(force_output),
    )
    return _prepared_force_driver_result(
        result,
        execution_mode=execution_mode,
        force_output=force_output,
    )


def run_v3_prepared_mapping(
    prepared,
    *,
    max_ratio: float = 0.5,
    force_output=None,
    return_force_rows: bool = False,
    execution_mode: str = "compiler",
):
    """Run the V3 composition from an already loaded prepared-state mapping.

    The Goal5634 primary interval begins after the immutable prepared arrays
    have been loaded and hashed.  This front door preserves the established
    prepared-state-only claim boundary while keeping file I/O outside that
    registered interval.
    """

    if execution_mode != "compiler":
        raise ValueError("RT-BarnesHut execution_mode must be compiler")
    result = _adapter.run_generic_aggregate_frontier_numba_force_bridge(
        prepared,
        max_ratio=max_ratio,
        force_output=None if force_output is None else Path(force_output),
        return_force_rows=return_force_rows,
    )
    return _prepared_force_driver_result(
        result,
        execution_mode=execution_mode,
        force_output=force_output,
    )


__all__ = ("run_v3_app", "run_v3_prepared_arrays", "run_v3_prepared_mapping")
