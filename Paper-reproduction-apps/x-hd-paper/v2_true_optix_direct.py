"""V2-style direct true-OptiX X-HD endpoint.

This module deliberately contains no Action IR and no compiler entrypoint.
The application explicitly selects the reviewed generic true-OptiX
certified-nearest physical executor, matching the legacy V2 programming model.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

from rtdsl.optix_runtime import (
    prepare_certified_nearest_global_witness_3d_optix,
)


CONTRACT = "rtdl.paper_reproduction.xhd.v2_direct_true_optix.v1"
CELL_MBR_CONTRACT = "rtdl.paper_reproduction.xhd.v2_direct_true_optix_cell_mbr.v1"


def _points(value: Any, *, name: str) -> np.ndarray:
    matrix = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    if matrix.ndim != 2 or matrix.shape[0] <= 0 or matrix.shape[1:] != (3,):
        raise ValueError(f"{name} must be one nonempty float64[n][3] matrix")
    if not bool(np.all(np.isfinite(matrix))):
        raise ValueError(f"{name} must contain only finite coordinates")
    return matrix


def _historical_cell_mbr_module():
    """Load the preserved V2 cell-MBR route without importing V3 control."""

    path = (
        Path(__file__).resolve().parent
        / "scripts"
        / "run_xhd_cell_mbr_frontier_route_gate.py"
    )
    name = "rtdl_xhd_v2_historical_cell_mbr_route"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load historical X-HD V2 route: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_loaded_cell_mbr_true_optix_direct(
    source_points: Any,
    target_points: Any,
    *,
    grid_shape: tuple[int, int, int] = (32, 32, 32),
    max_inline_points: int = 512,
    grid_cell_point_order: str = "input-stable",
) -> dict[str, Any]:
    """Run the strongest eligible historical V2 true-OptiX route.

    This deliberately excludes the fast scalar early-break route
    (``per_source_witness_exact=false``) and the exact CUDA seed route that
    skips traversal.  The selected legacy route uses a CUDA local-grid upper
    bound followed by real OptiX cell-MBR traversal and exact inline nearest
    updates, which matches the paper's hybrid CUDA/RT structure without using
    V3 Action IR or compiler placement.
    """

    started = time.perf_counter()
    queries = _points(source_points, name="source_points")
    targets = _points(target_points, name="target_points")
    shape = tuple(int(value) for value in grid_shape)
    if len(shape) != 3 or any(value <= 0 for value in shape):
        raise ValueError("grid_shape must contain three positive integers")
    if not isinstance(max_inline_points, int) or isinstance(
        max_inline_points, bool
    ) or max_inline_points <= 0:
        raise ValueError("max_inline_points must be a positive integer")
    if grid_cell_point_order not in {"point-id", "input-stable"}:
        raise ValueError(
            "grid_cell_point_order must be 'point-id' or 'input-stable'"
        )

    historical = _historical_cell_mbr_module()
    route = historical._directed_cell_mbr_route(
        queries,
        targets,
        label="a_to_b",
        backend="optix",
        grid_shape=shape,
        radius=None,
        fallback_radius=historical._full_cover_radius(queries, targets),
        max_inline_points=max_inline_points,
        initial_state="local-grid-cell",
        seed_cell_budget=4,
        local_grid_seed_executor="native_cuda",
        grid_branch_bound_seed_executor="auto",
        frontier_nearest_executor="auto",
        frontier_row_order="native",
        frontier_inline_nearest=True,
        cell_order="native",
        grid_cell_point_order=grid_cell_point_order,
        grid_cell_builder="native_cuda",
        skip_frontier_if_exact_seed=False,
        global_bound_early_break=False,
        collect_inline_stats=True,
        collect_frontier_native_phase_timings=True,
        frontier_row_capacity=None,
        emit_nearest_columns=False,
    )
    elapsed = time.perf_counter() - started
    if route.get("per_source_witness_exact") is not True:
        raise RuntimeError("historical true-OptiX route lost exact witnesses")
    if route.get("exact_seed_frontier_skipped") is True:
        raise RuntimeError("historical true-OptiX route skipped traversal")
    if not str(route.get("frontier_native_symbol") or "").startswith(
        "rtdl_optix_collect_cell_mbr_nearest_frontier_3d"
    ):
        raise RuntimeError("historical true-OptiX route lost its native symbol")

    return {
        "contract": CELL_MBR_CONTRACT,
        "method": "v2_direct_true_optix_cell_mbr",
        "application_programming_model": "explicit_physical_backend_selection",
        "v3_action_ir_used": False,
        "v3_compiler_used": False,
        "source_count": int(queries.shape[0]),
        "target_count": int(targets.shape[0]),
        "witness": {
            "source_id": int(route["source_id"]),
            "target_id": int(route["target_id"]),
            "distance": float(route["distance"]),
        },
        "physical_metadata": {
            **route,
            "optix_traversal_used": True,
            "application_selected_backend": True,
            "selection_owner": "application",
            "historical_v2_route_reused": True,
        },
        "registered_primary_timing": {
            "contract_id": (
                "loaded_points_to_exact_directed_witness_v2_direct_true_optix"
            ),
            "elapsed_seconds": elapsed,
            "input_loading_included": False,
            "input_validation_included": True,
            "native_grid_and_seed_included": True,
            "native_prepare_included": True,
            "native_execute_and_synchronize_included": True,
            "output_projection_included": True,
            "native_close_included": True,
            "correctness_comparator_included": False,
        },
    }


def run_loaded_true_optix_direct(
    source_points: Any,
    target_points: Any,
    *,
    grid_shape: tuple[int, int, int] = (32, 32, 32),
    max_inline_points: int = 64,
) -> dict[str, Any]:
    """Return one exact directed-Hausdorff witness through true OptiX.

    The registered interval starts with already-loaded point matrices and
    includes input validation, target-grid/GAS preparation, query upload,
    OptiX traversal, bounded exact continuation, global reduction, projection,
    synchronization, and close.  A correctness comparator is not included.
    """

    started = time.perf_counter()
    queries = _points(source_points, name="source_points")
    targets = _points(target_points, name="target_points")
    shape = tuple(int(value) for value in grid_shape)
    if len(shape) != 3 or any(value <= 0 for value in shape):
        raise ValueError("grid_shape must contain three positive integers")
    if not isinstance(max_inline_points, int) or isinstance(
        max_inline_points, bool
    ) or max_inline_points <= 0:
        raise ValueError("max_inline_points must be a positive integer")

    query_lower = np.min(queries, axis=0)
    query_upper = np.max(queries, axis=0)
    max_heavy = int(queries.shape[0]) * int(targets.shape[0])
    with prepare_certified_nearest_global_witness_3d_optix(
        targets,
        target_ids=np.arange(targets.shape[0], dtype=np.int64),
        grid_shape=shape,
        query_domain_lower_bounds=query_lower,
        query_domain_upper_bounds=query_upper,
        max_inline_points=max_inline_points,
        max_heavy_point_evaluations=max_heavy,
        application_selected_backend=True,
    ) as prepared:
        physical = prepared.run(queries)

    elapsed = time.perf_counter() - started
    actual = dict(physical["actual"])
    if (
        int(actual["source_id"]) < 0
        or int(actual["source_id"]) >= queries.shape[0]
        or int(actual["item_id"]) < 0
        or int(actual["item_id"]) >= targets.shape[0]
        or not math.isfinite(float(actual["value"]))
        or float(actual["value"]) < 0.0
    ):
        raise RuntimeError("true-OptiX X-HD route returned an invalid witness")
    metadata = dict(physical["metadata"])
    if (
        metadata.get("optix_traversal_used") is not True
        or int(metadata.get("optix_launch_count", 0)) <= 0
        or metadata.get("application_selected_backend") is not True
        or metadata.get("selection_owner") != "application"
    ):
        raise RuntimeError("V2 direct X-HD route lost its true-OptiX identity")

    return {
        "contract": CONTRACT,
        "method": "v2_direct_true_optix",
        "application_programming_model": "explicit_physical_backend_selection",
        "v3_action_ir_used": False,
        "v3_compiler_used": False,
        "source_count": int(queries.shape[0]),
        "target_count": int(targets.shape[0]),
        "witness": {
            "source_id": int(actual["source_id"]),
            "target_id": int(actual["item_id"]),
            "distance": float(actual["value"]),
        },
        "physical_metadata": metadata,
        "registered_primary_timing": {
            "contract_id": (
                "loaded_points_to_exact_directed_witness_v2_direct_true_optix"
            ),
            "elapsed_seconds": elapsed,
            "input_loading_included": False,
            "input_validation_included": True,
            "native_prepare_included": True,
            "native_execute_and_synchronize_included": True,
            "output_projection_included": True,
            "native_close_included": True,
            "correctness_comparator_included": False,
        },
    }


__all__ = (
    "CELL_MBR_CONTRACT",
    "CONTRACT",
    "run_loaded_cell_mbr_true_optix_direct",
    "run_loaded_true_optix_direct",
)
