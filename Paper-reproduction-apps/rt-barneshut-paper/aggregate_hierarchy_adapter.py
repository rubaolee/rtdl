from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any, Callable, Mapping


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT = (
    "rt_barneshut_prepared_arrays_to_generic_aggregate_hierarchy_3d_v1"
)
AUTHOR_PREPARED_ARRAYS_SCHEMA = "generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1"
DEFAULT_SIZE_DISTANCE_RATIO = 0.5
DEFAULT_PARITY_REL_TOL = 1.0e-12
DEFAULT_PARITY_ABS_TOL = 1.0e-12
DEFAULT_FORCE_OUTPUT_SCALE = 0.1


def _normalize_author_payload_continuation(
    values: Any,
    *,
    node_count: int,
    stop_zero: bool,
) -> tuple[int, ...] | None:
    if values is None:
        return None
    normalized: list[int] = []
    for raw in values:
        value = int(raw)
        if value < 0 or value >= node_count or (stop_zero and value == 0):
            normalized.append(-1)
        else:
            normalized.append(value)
    return tuple(normalized)


def _load_goal2547_reader() -> Callable[[Path], Mapping[str, Any]]:
    module_path = ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"
    spec = importlib.util.spec_from_file_location("goal2547_rt_barneshut_prepared_reader_for_adapter", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load prepared-array reader from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.read_prepared_arrays_3d


def prepared_arrays_to_aggregate_hierarchy(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
) -> dict[str, Any]:
    """Map an app-owned prepared-array packet to the generic RTDL hierarchy contract."""

    node_count = len(prepared["node_cx"])
    author_payload_continuation = (
        prepared.get("contract_source") == "rt_barneshut_author_binary_prepared_state_v1"
    )
    node_next_index = prepared.get("node_next_prim_index")
    node_resume_index = prepared.get("node_resume_index")
    node_rope_index = prepared.get("node_auto_rope_index")
    if author_payload_continuation:
        node_next_index = _normalize_author_payload_continuation(
            node_next_index,
            node_count=node_count,
            stop_zero=True,
        )
        node_rope_index = _normalize_author_payload_continuation(
            node_rope_index,
            node_count=node_count,
            stop_zero=True,
        )

    hierarchy = rt.aggregate_hierarchy_3d(
        point_x=prepared["point_x"],
        point_y=prepared["point_y"],
        point_z=prepared["point_z"],
        point_weight=prepared["point_mass"],
        node_cx=prepared["node_cx"],
        node_cy=prepared["node_cy"],
        node_cz=prepared["node_cz"],
        node_half_size=prepared["node_half_size"],
        node_weight=prepared["node_mass"],
        member_offsets=prepared["member_offsets"],
        member_indices=prepared["member_indices"],
        child_offsets=prepared["child_offsets"],
        child_indices=prepared["child_indices"],
        node_next_index=node_next_index,
        node_resume_index=node_resume_index,
        node_rope_index=node_rope_index,
        source_leaf_node_index=prepared.get("source_leaf_node_index"),
        node_subtree_end_index=prepared.get("node_subtree_end_index"),
    )
    prepared_hierarchy = rt.prepare_aggregate_hierarchy_3d(hierarchy)
    opening = (
        rt.ContinuationPayloadOpening(max_ratio=max_ratio)
        if author_payload_continuation
        else rt.SizeDistanceOpening(max_ratio=max_ratio)
    )
    reduce_spec = rt.aggregate_frontier_reduce_spec_3d(
        prepared_hierarchy,
        opening=opening,
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    )
    app_owned_fields = tuple(
        field
        for field in (
            "contract_source",
            "tree",
            "points",
            "nodes",
        )
        if field in prepared
    )
    promoted_descriptor_fields = tuple(
        field
        for field in ("source_leaf_node_index", "node_subtree_end_index")
        if field in prepared
    )
    return {
        "contract": RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT,
        "source_schema": AUTHOR_PREPARED_ARRAYS_SCHEMA,
        "source_contract": prepared.get("contract_source", "unknown_prepared_arrays"),
        "hierarchy": hierarchy,
        "prepared_hierarchy": prepared_hierarchy,
        "reduce_spec": reduce_spec,
        "metadata": {
            "adapter_contract": RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT,
            "generic_contract_version": rt.AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
            "hierarchy": hierarchy.to_metadata(),
            "prepared_hierarchy": prepared_hierarchy.to_metadata(),
            "reduce_spec": reduce_spec.to_metadata(),
            "generic_descriptor_fields_promoted": promoted_descriptor_fields,
            "app_owned_fields_not_promoted_to_core": app_owned_fields,
            "backend_execution_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "whole_program_speedup_claim_authorized": False,
            "claim_boundary": (
                "app_adapter_only",
                "maps_prepared_arrays_to_generic_schema",
                "does_not_run_backend",
                "does_not_move_comparator_or_payload_policy_to_core",
            ),
        },
    }


def _rows_by_source(rows: tuple[Mapping[str, Any], ...]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_id"]): row for row in rows}


def _compare_reduce_rows(
    reference_rows: tuple[Mapping[str, Any], ...],
    candidate_rows: tuple[Mapping[str, Any], ...],
    *,
    rel_tol: float,
    abs_tol: float,
) -> dict[str, Any]:
    reference_by_source = _rows_by_source(reference_rows)
    candidate_by_source = _rows_by_source(candidate_rows)
    sources = sorted(set(reference_by_source) | set(candidate_by_source))
    mismatch_count = 0
    max_abs_delta = 0.0
    max_rel_delta = 0.0
    first_mismatch: dict[str, Any] | None = None

    for source_id in sources:
        ref = reference_by_source.get(source_id)
        cand = candidate_by_source.get(source_id)
        if ref is None or cand is None:
            mismatch_count += 1
            if first_mismatch is None:
                first_mismatch = {
                    "source_id": source_id,
                    "reason": "missing_source_row",
                    "reference_present": ref is not None,
                    "candidate_present": cand is not None,
                }
            continue

        row_mismatch = False
        for key in ("visited_node_count", "aggregate_contribution_count", "exact_contribution_count", "status_code"):
            if int(ref[key]) != int(cand[key]):
                row_mismatch = True
                if first_mismatch is None:
                    first_mismatch = {
                        "source_id": source_id,
                        "reason": f"{key}_mismatch",
                        "reference": int(ref[key]),
                        "candidate": int(cand[key]),
                    }
                break

        if not row_mismatch:
            for key in ("reducer_value_0", "reducer_value_1", "reducer_value_2"):
                ref_value = float(ref[key])
                cand_value = float(cand[key])
                abs_delta = abs(ref_value - cand_value)
                denom = max(abs(ref_value), abs(cand_value), abs_tol)
                rel_delta = abs_delta / denom
                max_abs_delta = max(max_abs_delta, abs_delta)
                max_rel_delta = max(max_rel_delta, rel_delta)
                if abs_delta > abs_tol and rel_delta > rel_tol:
                    row_mismatch = True
                    if first_mismatch is None:
                        first_mismatch = {
                            "source_id": source_id,
                            "reason": f"{key}_mismatch",
                            "reference": ref_value,
                            "candidate": cand_value,
                            "abs_delta": abs_delta,
                            "rel_delta": rel_delta,
                        }
                    break

        if row_mismatch:
            mismatch_count += 1

    return {
        "source_count": len(sources),
        "mismatch_count": mismatch_count,
        "max_abs_delta": max_abs_delta,
        "max_rel_delta": max_rel_delta,
        "first_mismatch": first_mismatch,
        "match": mismatch_count == 0,
        "rel_tol": rel_tol,
        "abs_tol": abs_tol,
    }


def aggregate_rows_to_scalar_force_rows(
    rows: tuple[Mapping[str, Any], ...],
    *,
    force_output_scale: float = DEFAULT_FORCE_OUTPUT_SCALE,
) -> tuple[dict[str, float | int], ...]:
    """Translate generic scalar reducer rows into this app's scalar force rows."""

    scale = float(force_output_scale)
    return tuple(
        {
            "source_id": int(row["source_id"]),
            "scalar_force": float(row["reducer_value_0"]) * scale,
        }
        for row in rows
    )


def write_scalar_force_rows(path: Path, rows: tuple[Mapping[str, Any], ...]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(f"{int(row['source_id'])} {float(row['scalar_force']):.9g}\n")


def _compare_scalar_force_rows(
    reference_rows: tuple[Mapping[str, Any], ...],
    candidate_rows: tuple[Mapping[str, Any], ...],
    *,
    rel_tol: float,
    abs_tol: float,
) -> dict[str, Any]:
    reference_by_source = {int(row["source_id"]): row for row in reference_rows}
    candidate_by_source = {int(row["source_id"]): row for row in candidate_rows}
    source_ids = sorted(set(reference_by_source) | set(candidate_by_source))
    mismatch_count = 0
    max_abs_delta = 0.0
    max_rel_delta = 0.0
    first_mismatch: dict[str, Any] | None = None
    for source_id in source_ids:
        ref = reference_by_source.get(source_id)
        cand = candidate_by_source.get(source_id)
        if ref is None or cand is None:
            mismatch_count += 1
            if first_mismatch is None:
                first_mismatch = {
                    "source_id": source_id,
                    "reason": "missing_source_row",
                    "reference_present": ref is not None,
                    "candidate_present": cand is not None,
                }
            continue
        ref_value = float(ref["scalar_force"])
        cand_value = float(cand["scalar_force"])
        abs_delta = abs(ref_value - cand_value)
        denom = max(abs(ref_value), abs(cand_value), abs_tol)
        rel_delta = abs_delta / denom
        max_abs_delta = max(max_abs_delta, abs_delta)
        max_rel_delta = max(max_rel_delta, rel_delta)
        if abs_delta > abs_tol and rel_delta > rel_tol:
            mismatch_count += 1
            if first_mismatch is None:
                first_mismatch = {
                    "source_id": source_id,
                    "reason": "scalar_force_mismatch",
                    "reference": ref_value,
                    "candidate": cand_value,
                    "abs_delta": abs_delta,
                    "rel_delta": rel_delta,
                }
    return {
        "source_count": len(source_ids),
        "mismatch_count": mismatch_count,
        "max_abs_delta": max_abs_delta,
        "max_rel_delta": max_rel_delta,
        "first_mismatch": first_mismatch,
        "match": mismatch_count == 0,
        "rel_tol": rel_tol,
        "abs_tol": abs_tol,
    }


def run_generic_aggregate_frontier_numba_parity(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    rel_tol: float = DEFAULT_PARITY_REL_TOL,
    abs_tol: float = DEFAULT_PARITY_ABS_TOL,
) -> dict[str, Any]:
    """Run app-prepared arrays through public RTDL reference and Numba executors."""

    packet = prepared_arrays_to_aggregate_hierarchy(prepared, max_ratio=max_ratio)
    reduce_spec = packet["reduce_spec"]
    point_count = packet["hierarchy"].point_count
    reference_execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        reduce_spec,
        backend="reference",
        max_output_rows=point_count,
    )
    numba_execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        reduce_spec,
        backend="numba",
        max_output_rows=point_count,
    )
    reference_result = rt.aggregate_frontier_reduce_reference_3d(reference_execution, softening=softening)
    numba_result = rt.aggregate_frontier_reduce_numba_3d(numba_execution, softening=softening)
    comparison = _compare_reduce_rows(
        reference_result["rows"],
        numba_result["rows"],
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )
    return {
        "mode": "generic_aggregate_frontier_numba_parity",
        "adapter_contract": RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT,
        "source_schema": AUTHOR_PREPARED_ARRAYS_SCHEMA,
        "source_contract": packet["source_contract"],
        "point_count": point_count,
        "node_count": packet["hierarchy"].node_count,
        "opening": reduce_spec.opening.to_metadata(),
        "reducer": reduce_spec.reducer,
        "reference_backend": reference_result["backend"],
        "candidate_backend": numba_result["backend"],
        "candidate_backend_status": numba_result["backend_status"],
        "comparison": comparison,
        "claim_boundary": (
            "app_owned_parity_gate",
            "uses_public_generic_rtdl_aggregate_hierarchy_api",
            "not_author_binary_comparator",
            "not_paper_reproduction_completion",
            "not_performance_claim",
        ),
    }


def read_prepared_arrays_and_run_generic_numba_parity(
    path: Path,
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    rel_tol: float = DEFAULT_PARITY_REL_TOL,
    abs_tol: float = DEFAULT_PARITY_ABS_TOL,
    reader: Callable[[Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    prepared_reader = _load_goal2547_reader() if reader is None else reader
    prepared = prepared_reader(Path(path))
    return run_generic_aggregate_frontier_numba_parity(
        prepared,
        max_ratio=max_ratio,
        softening=softening,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )


def run_generic_aggregate_frontier_numba_force_bridge(
    prepared: Mapping[str, Any],
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = DEFAULT_FORCE_OUTPUT_SCALE,
    force_output: Path | None = None,
    rel_tol: float = DEFAULT_PARITY_REL_TOL,
    abs_tol: float = DEFAULT_PARITY_ABS_TOL,
    return_force_rows: bool = False,
) -> dict[str, Any]:
    """Run public generic RTDL executors and materialize this app's scalar force format."""

    packet = prepared_arrays_to_aggregate_hierarchy(prepared, max_ratio=max_ratio)
    reduce_spec = packet["reduce_spec"]
    point_count = packet["hierarchy"].point_count
    reference_execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        reduce_spec,
        backend="reference",
        max_output_rows=point_count,
    )
    numba_execution = rt.aggregate_frontier_reduce_execution_contract_3d(
        reduce_spec,
        backend="numba",
        max_output_rows=point_count,
    )
    reference_result = rt.aggregate_frontier_reduce_reference_3d(reference_execution, softening=softening)
    numba_result = rt.aggregate_frontier_reduce_numba_3d(numba_execution, softening=softening)
    reference_force_rows = aggregate_rows_to_scalar_force_rows(
        reference_result["rows"],
        force_output_scale=force_output_scale,
    )
    numba_force_rows = aggregate_rows_to_scalar_force_rows(
        numba_result["rows"],
        force_output_scale=force_output_scale,
    )
    comparison = _compare_scalar_force_rows(
        reference_force_rows,
        numba_force_rows,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
    )
    if force_output is not None:
        write_scalar_force_rows(Path(force_output), numba_force_rows)
    result = {
        "mode": "generic_aggregate_frontier_numba_force_bridge",
        "adapter_contract": RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT,
        "source_schema": AUTHOR_PREPARED_ARRAYS_SCHEMA,
        "source_contract": packet["source_contract"],
        "point_count": point_count,
        "node_count": packet["hierarchy"].node_count,
        "opening": reduce_spec.opening.to_metadata(),
        "reducer": reduce_spec.reducer,
        "force_output_scale": float(force_output_scale),
        "force_output": None if force_output is None else str(Path(force_output)),
        "reference_backend": reference_result["backend"],
        "candidate_backend": numba_result["backend"],
        "candidate_backend_status": numba_result["backend_status"],
        "checksum_scalar_force": sum(float(row["scalar_force"]) for row in numba_force_rows),
        "comparison_to_reference_executor_force_rows": comparison,
        "claim_boundary": (
            "app_owned_force_output_bridge",
            "maps_generic_scalar_reducer_to_app_scalar_force_rows",
            "uses_public_generic_rtdl_aggregate_hierarchy_api",
            "not_author_binary_comparator",
            "not_paper_reproduction_completion",
            "not_performance_claim",
        ),
    }
    if return_force_rows:
        result["candidate_force_rows"] = tuple(numba_force_rows)
    return result


def read_prepared_arrays_and_run_generic_numba_force_bridge(
    path: Path,
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
    softening: float = 0.0,
    force_output_scale: float = DEFAULT_FORCE_OUTPUT_SCALE,
    force_output: Path | None = None,
    rel_tol: float = DEFAULT_PARITY_REL_TOL,
    abs_tol: float = DEFAULT_PARITY_ABS_TOL,
    return_force_rows: bool = False,
    reader: Callable[[Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    prepared_reader = _load_goal2547_reader() if reader is None else reader
    prepared = prepared_reader(Path(path))
    return run_generic_aggregate_frontier_numba_force_bridge(
        prepared,
        max_ratio=max_ratio,
        softening=softening,
        force_output_scale=force_output_scale,
        force_output=force_output,
        rel_tol=rel_tol,
        abs_tol=abs_tol,
        return_force_rows=return_force_rows,
    )


def read_prepared_arrays_as_aggregate_hierarchy(
    path: Path,
    *,
    max_ratio: float = DEFAULT_SIZE_DISTANCE_RATIO,
    reader: Callable[[Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    prepared_reader = _load_goal2547_reader() if reader is None else reader
    prepared = prepared_reader(Path(path))
    return prepared_arrays_to_aggregate_hierarchy(prepared, max_ratio=max_ratio)


def describe_adapter_contract() -> dict[str, Any]:
    return {
        "adapter_contract": RT_BARNESHUT_TO_AGGREGATE_HIERARCHY_ADAPTER_CONTRACT,
        "input_schema": AUTHOR_PREPARED_ARRAYS_SCHEMA,
        "output_contract": rt.AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION,
        "opening_policy": rt.AGGREGATE_HIERARCHY_3D_OPENING_SIZE_DISTANCE,
        "reducer": rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
        "backend_execution_authorized": False,
        "app_owned_numba_parity_mode": "available_via_public_generic_rtdl_api",
        "app_owned_force_output_bridge": "available_via_public_generic_rtdl_api",
        "app_owned_fields_not_promoted_to_core": (
            "contract_source",
            "tree",
            "points",
            "nodes",
        ),
        "generic_descriptor_fields_promoted": (
            "source_leaf_node_index",
            "node_subtree_end_index",
        ),
        "claim_boundary": (
            "schema_adapter_only",
            "no_cuda",
            "no_native_backend",
            "no_speedup_claim",
        ),
    }
