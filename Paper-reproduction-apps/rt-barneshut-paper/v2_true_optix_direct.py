"""V2-style direct true-OptiX RT-BarnesHut force endpoint.

The app explicitly selects a generic aggregate-hierarchy physical backend and
therefore models the legacy V2 programming surface.  It does not compile an
Action IR, consult target facts, or invoke the V3 placement compiler.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import time
from typing import Any, Mapping

from rtdsl.aggregate_hierarchy_native import (
    prepare_aggregate_frontier_reduce_explicit_native_3d,
)


APP_DIR = Path(__file__).resolve().parent
CONTRACT = "rtdl.paper_reproduction.rt_barneshut.v2_direct_true_optix.v1"


def _load_adapter():
    path = APP_DIR / "aggregate_hierarchy_adapter.py"
    spec = importlib.util.spec_from_file_location(
        "rt_barneshut_v2_true_optix_adapter", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load RT-BarnesHut adapter: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_adapter = _load_adapter()


def read_prepared_arrays(path: Path) -> Mapping[str, Any]:
    return _adapter._load_goal2547_reader()(Path(path))


def _canonical_force_rows(
    rows: tuple[Mapping[str, Any], ...],
    *,
    force_output_scale: float,
) -> tuple[dict[str, float | int], ...]:
    projected = _adapter.aggregate_rows_to_scalar_force_rows(
        rows,
        force_output_scale=force_output_scale,
    )
    return tuple(
        {
            "source_id": int(row["source_id"]),
            "scalar_force": float(format(float(row["scalar_force"]), ".9g")),
        }
        for row in projected
    )


def run_prepared_true_optix_direct(
    prepared_arrays: Mapping[str, Any],
    *,
    max_ratio: float = _adapter.DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = _adapter.DEFAULT_FORCE_OUTPUT_SCALE,
) -> dict[str, Any]:
    """Return complete scalar-force rows through explicit true OptiX."""

    started = time.perf_counter()
    packet = _adapter.prepared_arrays_to_aggregate_hierarchy(
        prepared_arrays,
        max_ratio=max_ratio,
    )
    point_count = packet["hierarchy"].point_count
    with prepare_aggregate_frontier_reduce_explicit_native_3d(
        packet["reduce_spec"],
        backend="optix_traversal",
        max_output_rows=point_count,
    ) as native:
        reduced = native.execute(softening=softening)
    force_rows = _canonical_force_rows(
        reduced["rows"],
        force_output_scale=force_output_scale,
    )
    elapsed = time.perf_counter() - started
    metadata = dict(reduced["metadata"])
    if (
        reduced.get("backend") != "explicit_native"
        or reduced.get("selected_backend") != "optix_traversal"
        or metadata.get("optix_traversal_candidate_selected") is not True
        or metadata.get("application_selected_backend") is not True
        or metadata.get("selection_owner") != "application"
    ):
        raise RuntimeError(
            "V2 direct RT-BarnesHut route lost its true-OptiX identity"
        )

    return {
        "contract": CONTRACT,
        "method": "v2_direct_true_optix",
        "application_programming_model": "explicit_physical_backend_selection",
        "v3_action_ir_used": False,
        "v3_compiler_used": False,
        "point_count": point_count,
        "force_rows": force_rows,
        "checksum_scalar_force": sum(
            float(row["scalar_force"]) for row in force_rows
        ),
        "physical_metadata": metadata,
        "registered_primary_timing": {
            "contract_id": (
                "prepared_hierarchy_to_complete_scalar_force_rows_"
                "v2_direct_true_optix"
            ),
            "elapsed_seconds": elapsed,
            "prepared_array_loading_included": False,
            "hierarchy_binding_and_validation_included": True,
            "native_prepare_included": True,
            "native_execute_and_synchronize_included": True,
            "complete_reduce_rows_included": True,
            "app_force_projection_included": True,
            "native_close_included": True,
            "correctness_comparator_included": False,
        },
    }


__all__ = (
    "CONTRACT",
    "read_prepared_arrays",
    "run_prepared_true_optix_direct",
)
