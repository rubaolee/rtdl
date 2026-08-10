"""Goal5651 successor route for the generic aggregate-hierarchy compiler.

This module is append-only relative to the locked Goal5617/Goal5648 app route.
It owns only prepared-packet adaptation, scalar-force projection, and the
common app comparator.  Physical selection remains compiler-owned.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any, Mapping


APP_DIR = Path(__file__).resolve().parent
for _candidate in APP_DIR.parents:
    if (_candidate / "src" / "rtdsl").exists():
        ROOT = _candidate
        SOURCE_ROOT = ROOT / "src"
        break
    if (_candidate / "rtdsl").exists():
        ROOT = _candidate
        SOURCE_ROOT = ROOT
        break
else:
    raise RuntimeError("could not locate the RTDL source root")
sys.path.insert(0, str(SOURCE_ROOT))

import rtdsl as rt


CANONICAL_ALGORITHM_BINDINGS = {
    "aggregate_hierarchy_frontier_reduce": (
        "aggregate_hierarchy.frontier_reduce.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("aggregate_hierarchy_frontier_reduce",)


def _load_legacy_adapter():
    path = APP_DIR / "aggregate_hierarchy_adapter.py"
    spec = importlib.util.spec_from_file_location(
        "goal5651_locked_rt_barneshut_adapter", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load locked adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_adapter()


def read_prepared_arrays(path: Path) -> Mapping[str, Any]:
    return _legacy._load_goal2547_reader()(Path(path))


def _packet(prepared: Mapping[str, Any], *, max_ratio: float) -> dict[str, Any]:
    return _legacy.prepared_arrays_to_aggregate_hierarchy(
        prepared, max_ratio=max_ratio
    )


def _project_force_rows(
    reduce_rows: tuple[Mapping[str, Any], ...],
    *,
    force_output_scale: float,
) -> tuple[dict[str, float | int], ...]:
    projected = _legacy.aggregate_rows_to_scalar_force_rows(
        reduce_rows,
        force_output_scale=force_output_scale,
    )
    # The established app output writer serializes scalar_force with ".9g".
    # Materialize that same canonical output boundary for every contender so
    # hardware FMA details cannot create unequal rows that the app could never
    # observe in its declared file output.
    return tuple(
        {
            "source_id": int(row["source_id"]),
            "scalar_force": float(format(float(row["scalar_force"]), ".9g")),
        }
        for row in projected
    )


def run_v2_numba_complete_endpoint(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = _legacy.DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = _legacy.DEFAULT_FORCE_OUTPUT_SCALE,
) -> dict[str, Any]:
    """Fastest currently eligible V2 candidate without the validation bridge."""

    packet = _packet(prepared, max_ratio=max_ratio)
    point_count = packet["hierarchy"].point_count
    execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        packet["reduce_spec"],
        backend="numba",
        max_output_rows=point_count,
    )
    reduced = rt.aggregate_frontier_reduce_numba_3d(
        execution, softening=softening
    )
    force_rows = _project_force_rows(
        reduced["rows"], force_output_scale=force_output_scale
    )
    return {
        "contract": "goal5651.rt_barneshut.v2_numba_complete_endpoint.v1",
        "method": "v2_numba",
        "point_count": point_count,
        "force_rows": force_rows,
        "checksum_scalar_force": sum(
            float(row["scalar_force"]) for row in force_rows
        ),
        "complete_endpoint_phases": (
            "generic_hierarchy_binding_and_validation",
            "numba_executor",
            "complete_reduce_rows",
            "app_force_projection",
        ),
        "validation_bridge_inside_endpoint": False,
        "correctness_comparator_inside_endpoint": False,
    }


def run_v2_reference_complete_endpoint(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = _legacy.DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = _legacy.DEFAULT_FORCE_OUTPUT_SCALE,
) -> dict[str, Any]:
    """Eligible CPU-reference V2 candidate on the identical endpoint."""

    packet = _packet(prepared, max_ratio=max_ratio)
    point_count = packet["hierarchy"].point_count
    execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        packet["reduce_spec"],
        backend="reference",
        max_output_rows=point_count,
    )
    reduced = rt.aggregate_frontier_reduce_reference_3d(
        execution, softening=softening
    )
    force_rows = _project_force_rows(
        reduced["rows"], force_output_scale=force_output_scale
    )
    return {
        "contract": "goal5651.rt_barneshut.v2_reference_complete_endpoint.v1",
        "method": "v2_reference",
        "point_count": point_count,
        "force_rows": force_rows,
        "checksum_scalar_force": sum(
            float(row["scalar_force"]) for row in force_rows
        ),
        "complete_endpoint_phases": (
            "generic_hierarchy_binding_and_validation",
            "reference_executor",
            "complete_reduce_rows",
            "app_force_projection",
        ),
        "validation_bridge_inside_endpoint": False,
        "correctness_comparator_inside_endpoint": False,
    }


def run_v3_compiler_complete_endpoint(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = _legacy.DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = _legacy.DEFAULT_FORCE_OUTPUT_SCALE,
) -> dict[str, Any]:
    """V3 complete endpoint; the application supplies no physical backend."""

    packet = _packet(prepared, max_ratio=max_ratio)
    point_count = packet["hierarchy"].point_count
    reduced = rt.run_aggregate_frontier_reduce_default_3d(
        packet["reduce_spec"],
        softening=softening,
        max_output_rows=point_count,
        semantic_statement_stable_id=CANONICAL_ALGORITHM_BINDINGS[
            "aggregate_hierarchy_frontier_reduce"
        ][0],
        backend_contract_id=CANONICAL_ALGORITHM_BINDINGS[
            "aggregate_hierarchy_frontier_reduce"
        ][1],
    )
    force_rows = _project_force_rows(
        reduced["rows"], force_output_scale=force_output_scale
    )
    return {
        "contract": "goal5651.rt_barneshut.v3_compiler_complete_endpoint.v1",
        "method": "v3_compiler",
        "point_count": point_count,
        "force_rows": force_rows,
        "checksum_scalar_force": sum(
            float(row["scalar_force"]) for row in force_rows
        ),
        "selected_backend": reduced["selected_backend"],
        "selected_template": reduced["selected_template"],
        "compiler_metadata": reduced["metadata"],
        "application_selected_backend": False,
        "complete_endpoint_phases": (
            "generic_hierarchy_binding_and_validation",
            "compiler_capability_probe_and_plan",
            "native_or_legal_fallback_prepare",
            "execute_and_synchronize",
            "status_and_complete_output_download",
            "complete_reduce_rows",
            "app_force_projection",
        ),
        "validation_bridge_inside_endpoint": False,
        "correctness_comparator_inside_endpoint": False,
    }


def run_v3_compiler_candidate_complete_endpoint_for_functional_validation(
    prepared: Mapping[str, Any],
    *,
    physical_candidate: str,
    max_ratio: float = _legacy.DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = _legacy.DEFAULT_FORCE_OUTPUT_SCALE,
) -> dict[str, Any]:
    """Run one pre-registered compiler candidate without changing production.

    This is an evidence-only front door.  The application cannot register a
    candidate or alter its priority; it supplies the same generic packet and
    names one of the two compiler-owned candidates for paired validation.
    """

    packet = _packet(prepared, max_ratio=max_ratio)
    point_count = packet["hierarchy"].point_count
    reduced = (
        rt.run_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
            packet["reduce_spec"],
            physical_candidate=physical_candidate,
            softening=softening,
            max_output_rows=point_count,
        )
    )
    force_rows = _project_force_rows(
        reduced["rows"], force_output_scale=force_output_scale
    )
    return {
        "contract": (
            "goal5663.rt_barneshut.compiler_candidate_complete_endpoint.v1"
        ),
        "method": f"v3_compiler_candidate_{physical_candidate}",
        "point_count": point_count,
        "force_rows": force_rows,
        "checksum_scalar_force": sum(
            float(row["scalar_force"]) for row in force_rows
        ),
        "selected_backend": reduced["selected_backend"],
        "selected_template": reduced["selected_template"],
        "compiler_metadata": reduced["metadata"],
        "application_selected_backend": False,
        "functional_validation_only": True,
        "candidate_establishes_production_priority": False,
        "complete_endpoint_phases": (
            "generic_hierarchy_binding_and_validation",
            "compiler_registered_candidate_materialization",
            "native_prepare",
            "execute_and_synchronize",
            "status_and_complete_output_download",
            "complete_reduce_rows",
            "app_force_projection",
        ),
        "validation_bridge_inside_endpoint": False,
        "correctness_comparator_inside_endpoint": False,
    }


def compare_force_rows(
    expected: tuple[Mapping[str, Any], ...],
    actual: tuple[Mapping[str, Any], ...],
    *,
    rel_tol: float = 1.0e-4,
    abs_tol: float = 1.0e-4,
) -> dict[str, Any]:
    return _legacy._compare_scalar_force_rows(
        expected,
        actual,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "compare_force_rows",
    "read_prepared_arrays",
    "run_v2_numba_complete_endpoint",
    "run_v2_reference_complete_endpoint",
    "run_v3_compiler_candidate_complete_endpoint_for_functional_validation",
    "run_v3_compiler_complete_endpoint",
)
