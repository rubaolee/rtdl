from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
import rtdsl.v4_point_group as pg_v4
from rtdsl.optix_runtime import prepare_optix_point_group_nearest_witness_2d
from rtdsl.reference import Point

DIRECTED_THRESHOLD_PREPARED_MODES = (
    "directed_threshold_prepared",
    "directed_threshold_prepared_runner",
)


@rt.kernel(backend="rtdl", precision="float_approx")
def hausdorff_nearest_rows_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.knn_rows(k=1))
    return rt.emit(nearest, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_authored_point_sets(copies: int = 1) -> dict[str, tuple[Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_a = (
        Point(id=1, x=0.0, y=0.0),
        Point(id=2, x=1.0, y=0.0),
        Point(id=3, x=1.0, y=1.0),
        Point(id=4, x=0.0, y=1.0),
    )
    base_b = (
        Point(id=101, x=0.0, y=0.0),
        Point(id=102, x=1.2, y=0.1),
        Point(id=103, x=1.0, y=1.3),
        Point(id=104, x=-0.2, y=0.8),
    )

    points_a: list[Point] = []
    points_b: list[Point] = []
    for copy_index in range(copies):
        offset = 10.0 * copy_index
        id_offset = 1000 * copy_index
        for point in base_a:
            points_a.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
        for point in base_b:
            points_b.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
    return {"points_a": tuple(points_a), "points_b": tuple(points_b)}


def _run_nearest(backend: str, query_points: tuple[Point, ...], search_points: tuple[Point, ...]):
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "cpu":
        return rt.run_cpu(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "embree":
        return rt.run_embree(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "optix":
        return rt.run_optix(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "vulkan":
        return rt.run_vulkan(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("hausdorff_distance")
    return {"class": support.performance_class, "note": support.note}


def _enforce_rt_core_requirement(backend: str, optix_summary_mode: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend == "optix_device_max_nearest":
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix or optix_device_max_nearest")
    if optix_summary_mode not in DIRECTED_THRESHOLD_PREPARED_MODES:
        raise RuntimeError(
            "hausdorff_distance RT-core path requires --backend optix "
            "--optix-summary-mode directed_threshold_prepared[_runner] or "
            "--backend optix_device_max_nearest"
        )


def _directed_from_rows(rows: Iterable[dict[str, object]], label: str) -> dict[str, object]:
    nearest_rows = list(rows)
    if not nearest_rows:
        raise ValueError(f"directed Hausdorff pass `{label}` produced no nearest-neighbor rows")

    distance_rows = rt.reduce_rows(
        nearest_rows,
        op="max",
        value="distance",
        output_field="directed_distance",
    )
    directed_distance = float(distance_rows[0]["directed_distance"])
    witness = max(
        nearest_rows,
        key=lambda row: (float(row["distance"]), -int(row["query_id"]), -int(row["neighbor_id"])),
    )
    return {
        "distance": directed_distance,
        "source_id": int(witness["query_id"]),
        "target_id": int(witness["neighbor_id"]),
        "row_count": len(nearest_rows),
        "distance_reduction_rows": distance_rows,
    }


def directed_hausdorff_bruteforce(source: tuple[Point, ...], target: tuple[Point, ...]) -> dict[str, object]:
    if not source or not target:
        raise ValueError("Hausdorff distance requires non-empty point sets")

    best_source: Point | None = None
    best_target: Point | None = None
    best_distance = -1.0
    for source_point in source:
        nearest_target = min(
            target,
            key=lambda target_point: (
                math.hypot(source_point.x - target_point.x, source_point.y - target_point.y),
                target_point.id,
            ),
        )
        distance = math.hypot(source_point.x - nearest_target.x, source_point.y - nearest_target.y)
        if (
            distance > best_distance
            or (math.isclose(distance, best_distance) and best_source is not None and source_point.id < best_source.id)
            or best_source is None
        ):
            best_source = source_point
            best_target = nearest_target
            best_distance = distance

    assert best_source is not None
    assert best_target is not None
    return {
        "distance": best_distance,
        "source_id": best_source.id,
        "target_id": best_target.id,
        "row_count": len(source),
    }


def brute_force_hausdorff(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    directed_ab = directed_hausdorff_bruteforce(points_a, points_b)
    directed_ba = directed_hausdorff_bruteforce(points_b, points_a)
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    return {
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
    }


def expected_tiled_hausdorff(*, copies: int) -> dict[str, object]:
    """Exact Hausdorff summary for make_authored_point_sets without O(N^2) expansion."""
    base = make_authored_point_sets(copies=1)
    expected = brute_force_hausdorff(base["points_a"], base["points_b"])
    expected = json.loads(json.dumps(expected))
    expected["directed_a_to_b"]["row_count"] = 4 * copies
    expected["directed_b_to_a"]["row_count"] = 4 * copies
    expected["directed_a_to_b"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_a_to_b"]["distance"]}
    ]
    expected["directed_b_to_a"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_b_to_a"]["distance"]}
    ]
    return expected


def _directed_threshold_from_count_rows(
    rows: Iterable[dict[str, object]],
    *,
    source: tuple[Point, ...],
    radius: float,
    label: str,
) -> dict[str, object]:
    by_query = {int(row["query_id"]): row for row in rows}
    violating = [
        point.id
        for point in source
        if int(by_query.get(point.id, {}).get("threshold_reached", 0)) == 0
    ]
    return {
        "label": label,
        "radius": radius,
        "source_count": len(source),
        "within_threshold": not violating,
        "violating_source_ids": violating,
        "row_count": len(by_query),
    }


def _run_prepared_directed_threshold(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    backend: str,
    radius: float,
    label: str,
    query_repeat: int = 1,
    warmup: int = 0,
    use_productized_runner: bool = False,
) -> dict[str, object]:
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if use_productized_runner:
        cache = rt.ExplicitPreparedSessionCache(max_entries=1)
        source_fingerprint = {
            "kind": "directed_threshold_query_points_2d",
            "label": label,
            "count": len(source),
            "first_id": int(source[0].id) if source else None,
            "last_id": int(source[-1].id) if source else None,
        }
        target_fingerprint = {
            "kind": "directed_threshold_search_points_2d",
            "label": label,
            "count": len(target),
            "first_id": int(target[0].id) if target else None,
            "last_id": int(target[-1].id) if target else None,
        }
        result = rt.run_fixed_radius_threshold_reached_count_2d_prepared_session(
            search_points=target,
            query_points=source,
            radius=radius,
            threshold=1,
            backend=backend,
            partner="none",
            cache=cache,
            max_radius=radius,
            search_fingerprint=target_fingerprint,
            query_fingerprint=source_fingerprint,
            device="cuda:0" if backend == "optix" else "cpu",
            warmup_count=warmup,
            measured_repeat_count=query_repeat,
            require_repeat5_material_probe=backend == "optix" and query_repeat >= 5,
            retain_repeat_outputs=True,
        )
        metadata = result.to_metadata()
        outputs = tuple(result.output) if isinstance(result.output, tuple) else (result.output,)
        if not outputs:
            raise RuntimeError("prepared threshold runner produced no measured outputs")
        covered_counts = {int(output["threshold_reached_count"]) for output in outputs}
        if len(covered_counts) != 1:
            raise RuntimeError("prepared threshold runner changed covered-source count")
        covered_count = next(iter(covered_counts))
        measured_seconds = [float(value) for value in metadata["measured_repeat_seconds"]]
        if len(measured_seconds) != query_repeat:
            raise RuntimeError("prepared threshold runner repeat accounting mismatch")
        inner_query_seconds = [
            float(output.get("run_phases", {}).get("query_fixed_radius_threshold_reached_count_sec"))
            for output in outputs
            if isinstance(output.get("run_phases", {}).get("query_fixed_radius_threshold_reached_count_sec"), (int, float))
        ]
        query_seconds_for_phase_total = (
            inner_query_seconds if len(inner_query_seconds) == query_repeat else measured_seconds
        )
        query_sec = float(statistics.median(query_seconds_for_phase_total))
        runner_outer_query_sec = float(statistics.median(measured_seconds))
        report_phases = {
            phase["phase"]: phase
            for phase in metadata["prepared_execution_report"]["phase_timings"]
        }
        warmup_seconds = [
            float(value)
            for value in report_phases.get("warmup", {}).get("repeat_seconds", ())
        ]
        legacy_aligned_prepare_sec = float(
            metadata.get(
                "legacy_aligned_prepare_sec",
                metadata["prepared_execution_report"]["summary_sec"]["setup"],
            )
        )
        outer_prepare_sec = float(metadata.get("outer_prepare_sec", metadata["prepared_execution_report"]["summary_sec"]["setup"]))
        outer_cache_load_sec = float(metadata.get("outer_cache_load_sec", 0.0))
        violating = [] if covered_count == len(source) else None
        return {
            "label": label,
            "radius": radius,
            "source_count": len(source),
            "covered_source_count": covered_count,
            "within_threshold": covered_count == len(source),
            "violating_source_ids": violating,
            "identity_parity_available": violating is not None,
            "row_count": None,
            "summary_mode": "scalar_threshold_count",
            "generic_primitive": outputs[-1]["primitive"],
            "summary_primitive": outputs[-1]["summary_primitive"],
            "run_phases": {
                "scene_prepare_sec": legacy_aligned_prepare_sec,
                f"{backend}_prepare_sec": legacy_aligned_prepare_sec,
                "runner_outer_prepare_sec": outer_prepare_sec,
                "runner_outer_cache_load_sec": outer_cache_load_sec,
                "runner_native_prepare_sec": metadata.get("native_prepare_sec"),
                "query_fixed_radius_threshold_reached_count_sec": query_sec,
                f"{backend}_query_sec": query_sec,
                "query_fixed_radius_threshold_reached_count_total_sec": float(
                    sum(query_seconds_for_phase_total)
                ),
                "runner_outer_query_sec": runner_outer_query_sec,
                "runner_outer_query_total_sec": float(sum(measured_seconds)),
                "query_repeat": int(query_repeat),
                "query_warmup": int(warmup),
                "warmup_total_sec": float(sum(warmup_seconds)),
            },
            "query_repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_run_count": len(query_seconds_for_phase_total),
                "query_sec_median": query_sec,
                "query_sec_total": float(sum(query_seconds_for_phase_total)),
                "runner_outer_query_sec_median": runner_outer_query_sec,
                "runner_outer_query_sec_total": float(sum(measured_seconds)),
                "reported_query_metric": "inner_primitive_query_median_with_runner_outer_metric_disclosed",
                "reported_prepare_metric": "legacy_aligned_native_prepare_with_runner_outer_metric_disclosed",
            },
            "prepared_execution_session_runner": {
                "used": True,
                "schema": metadata["schema"],
                "status": metadata["status"],
                "productized_execution_path": metadata["productized_execution_path"],
                "runtime_executed": bool(metadata["runtime_executed"]),
                "runtime_trunk_executes_end_to_end": bool(
                    metadata["runtime_trunk_executes_end_to_end"]
                ),
                "cache_hit": bool(metadata["prepared_session"]["cache_hit"]),
                "measured_repeat_count": int(metadata["measured_repeat_count"]),
                "measured_repeat_seconds": tuple(metadata["measured_repeat_seconds"]),
                "output_finalize_sec": float(metadata["output_finalize_sec"]),
                "prepared_execution_report": metadata["prepared_execution_report"],
                "prepared_execution_report_validation": metadata[
                    "prepared_execution_report_validation"
                ],
                "material_probe_repeat_requirement_met": bool(
                    metadata["material_probe_repeat_requirement_met"]
                ),
                "repeat5_material_probe_candidate": bool(
                    metadata["repeat5_material_probe_candidate"]
                ),
                "native_scalar_count_used": bool(metadata["native_scalar_count_used"]),
                "threshold_summary_rows_materialized_on_host": bool(
                    metadata["threshold_summary_rows_materialized_on_host"]
                ),
                "hot_path_host_materialization": bool(metadata["hot_path_host_materialization"]),
                "prepared_search_structure_resident_between_rtdl_phases": bool(
                    metadata["prepared_search_structure_resident_between_rtdl_phases"]
                ),
                "query_points_device_resident_between_rtdl_phases": bool(
                    metadata["query_points_device_resident_between_rtdl_phases"]
                ),
                "internal_device_residency_between_rtdl_phases": bool(
                    metadata["internal_device_residency_between_rtdl_phases"]
                ),
                "internal_residency_scope": metadata["internal_residency_scope"],
                "large_input_fingerprint_hot_path_avoided": bool(
                    metadata["large_input_fingerprint_hot_path_avoided"]
                ),
                "release_authorized": bool(metadata["release_authorized"]),
                "public_speedup_claim_authorized": bool(
                    metadata["public_speedup_claim_authorized"]
                ),
                "broad_v3_faster_than_v2_claim_authorized": bool(
                    metadata["broad_v3_faster_than_v2_claim_authorized"]
                ),
                "true_zero_copy_claim_authorized": bool(
                    metadata["true_zero_copy_claim_authorized"]
                ),
                "automatic_partner_selection_authorized": bool(
                    metadata["automatic_partner_selection_authorized"]
                ),
                "app_specific_native_engine_logic_allowed": bool(
                    metadata["app_specific_native_engine_logic_allowed"]
                ),
            },
        }
    kwargs: dict[str, object] = {"search_points": target, "backend": backend}
    if backend == "optix":
        kwargs["max_radius"] = radius
    query_runs: list[dict[str, object]] = []
    with rt.prepare_generic_fixed_radius_count_threshold_2d(**kwargs) as prepared:
        for iteration in range(warmup + query_repeat):
            result = prepared.count_threshold_reached(source, radius=radius, threshold=1)
            query_runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < warmup,
                    "threshold_reached_count": int(result["threshold_reached_count"]),
                    "query_sec": float(
                        result["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
                    ),
                }
            )
        prepare_sec = float(prepared.scene_prepare_sec)
    measured = [row for row in query_runs if not bool(row["is_warmup"])]
    if not measured:
        raise RuntimeError("prepared Hausdorff threshold repeat produced no measured rows")
    covered_counts = {int(row["threshold_reached_count"]) for row in measured}
    if len(covered_counts) != 1:
        raise RuntimeError("prepared Hausdorff threshold repeat changed covered-source count")
    covered_count = next(iter(covered_counts))
    query_secs = [float(row["query_sec"]) for row in measured]
    query_sec = float(statistics.median(query_secs))
    violating = [] if covered_count == len(source) else None
    return {
        "label": label,
        "radius": radius,
        "source_count": len(source),
        "covered_source_count": covered_count,
        "within_threshold": covered_count == len(source),
        "violating_source_ids": violating,
        "identity_parity_available": violating is not None,
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
        "generic_primitive": result["primitive"],
        "summary_primitive": result["summary_primitive"],
        "run_phases": {
            "scene_prepare_sec": prepare_sec,
            f"{backend}_prepare_sec": prepare_sec,
            "query_fixed_radius_threshold_reached_count_sec": query_sec,
            f"{backend}_query_sec": query_sec,
            "query_fixed_radius_threshold_reached_count_total_sec": float(sum(query_secs)),
            "query_repeat": int(query_repeat),
            "query_warmup": int(warmup),
        },
        "query_repeat_protocol": {
            "repeat": int(query_repeat),
            "warmup": int(warmup),
            "measured_run_count": len(measured),
            "query_sec_median": query_sec,
            "query_sec_total": float(sum(query_secs)),
        },
    }


def _native_continuation_backend(
    backend: str,
    *,
    embree_result_mode: str,
    optix_summary_mode: str,
) -> str:
    if backend == "optix_device_max_nearest":
        return "optix_device_query_nearest_witness_partner_global_max"
    if backend == "optix" and optix_summary_mode == "directed_threshold_prepared_runner":
        return "optix_threshold_count_prepared_execution_runner"
    if backend == "optix" and optix_summary_mode == "directed_threshold_prepared":
        return "optix_threshold_count"
    if backend == "embree" and optix_summary_mode == "directed_threshold_prepared_runner":
        return "embree_threshold_count_prepared_execution_runner"
    if backend == "embree" and optix_summary_mode == "directed_threshold_prepared":
        return "embree_threshold_count"
    if backend == "embree" and embree_result_mode == "directed_summary":
        return "embree_directed_hausdorff"
    return "none"


def _run_partner_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    partner: str,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_partner_columns(source, partner=partner)
    target_columns = rt.point_rows_to_partner_columns(target, partner=partner)
    result = rt.directed_max_of_nearest_distance_2d_partner_columns(
        source_columns,
        target_columns,
        partner=partner,
        materialize_nearest_distances=partner != "numba",
        return_metadata=True,
    )
    metadata = result["metadata"]
    summary = {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }
    for key in (
        "numba_strategy",
        "numba_score_row_operation",
        "numba_score_row_count",
        "numba_logical_pair_count",
        "v2_8_partner_continuation_operations",
        "v2_8_partner_continuation_operations_semantics",
        "host_score_row_materialization_used",
        "score_rows_generated_on_partner_device",
        "nearest_distance_column_materialized",
        "host_present_group_compaction_used",
        "nan_validation_host_sync_used",
        "native_engine_row_contract",
    ):
        if key in metadata:
            summary[key] = metadata[key]
    return summary


def _run_partner_numpy_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_numpy_columns(source)
    target_columns = rt.point_rows_to_numpy_columns(target)
    result = rt.directed_hausdorff_2d_numpy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }


def _run_partner_cupy_witness_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
) -> dict[str, object]:
    source_columns = rt.point_rows_to_partner_columns(source, partner="cupy")
    target_columns = rt.point_rows_to_partner_columns(target, partner="cupy")
    result = rt.directed_hausdorff_2d_cupy_columns(
        source_columns,
        target_columns,
        return_metadata=True,
    )
    metadata = result["metadata"]
    return {
        "label": label,
        "distance": float(metadata["distance"]),
        "source_id": int(metadata["source_id"]),
        "target_id": int(metadata["target_id"]),
        "row_count": int(metadata["source_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
    }


def _run_partner_numba_witness_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
) -> dict[str, object]:
    import numpy as np

    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass
    from numba import cuda

    source_count = len(source)
    target_count = len(target)
    if source_count <= 0 or target_count <= 0:
        raise ValueError("directed Hausdorff requires non-empty source and target rows")
    source_ids = np.asarray([int(point.id) for point in source], dtype=np.int64)
    source_x = np.asarray([float(point.x) for point in source], dtype=np.float64)
    source_y = np.asarray([float(point.y) for point in source], dtype=np.float64)
    target_x = np.asarray([float(point.x) for point in target], dtype=np.float64)
    target_y = np.asarray([float(point.y) for point in target], dtype=np.float64)
    target_ids = np.asarray([int(point.id) for point in target], dtype=np.int64)
    score_rows = rt.pairwise_l2_sq_score_rows_2d_partner_columns(
        {
            "ids": cuda.to_device(source_ids),
            "x": cuda.to_device(source_x),
            "y": cuda.to_device(source_y),
        },
        {
            "ids": cuda.to_device(target_ids),
            "x": cuda.to_device(target_x),
            "y": cuda.to_device(target_y),
        },
        partner="numba",
        return_metadata=True,
    )

    result = rt.group_argmin_then_global_argmax_partner_columns(
        score_rows["columns"],
        group_count=source_count,
        partner="numba",
        numba_known_dense_groups=True,
        numba_validate_group_ids=False,
        numba_validate_nan_scores=False,
        return_metadata=True,
    )
    metadata = result["metadata"]
    score_metadata = score_rows["metadata"]
    source_index = int(metadata["winner_group_id"])
    return {
        "label": label,
        "distance": math.sqrt(float(metadata["winner_score"])),
        "source_id": int(source[source_index].id),
        "target_id": int(metadata["winner_item_id"]),
        "row_count": source_count,
        "dense_score_row_count": int(score_metadata["row_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
        "v2_6_numba_partner_continuation_operations": metadata[
            "v2_6_numba_partner_continuation_operations"
        ],
        "v2_6_numba_score_row_operation": score_metadata["operation"],
        "numba_pairwise_score_rows_elapsed_seconds": score_metadata[
            "numba_pairwise_score_rows_elapsed_seconds"
        ],
        "host_score_row_materialization_used": False,
        "score_rows_generated_on_partner_device": True,
        "numba_known_dense_groups": metadata["numba_known_dense_groups"],
        "host_present_group_compaction_used": metadata["host_present_group_compaction_used"],
        "nan_validation_host_sync_used": metadata["nan_validation_host_sync_used"],
        "native_engine_row_contract": metadata["native_engine_row_contract"],
    }


def _run_partner_numba_block_nearest_exact_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    label: str,
    block_size: int = 256,
) -> dict[str, object]:
    import numpy as np

    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass
    from numba import cuda

    source_count = len(source)
    target_count = len(target)
    if source_count <= 0 or target_count <= 0:
        raise ValueError("directed Hausdorff requires non-empty source and target rows")
    source_ids = np.asarray([int(point.id) for point in source], dtype=np.int64)
    source_x = np.asarray([float(point.x) for point in source], dtype=np.float64)
    source_y = np.asarray([float(point.y) for point in source], dtype=np.float64)
    target_x = np.asarray([float(point.x) for point in target], dtype=np.float64)
    target_y = np.asarray([float(point.y) for point in target], dtype=np.float64)
    target_ids = np.asarray([int(point.id) for point in target], dtype=np.int64)
    partial_rows = rt.pairwise_l2_sq_block_nearest_rows_2d_partner_columns(
        {
            "ids": cuda.to_device(source_ids),
            "x": cuda.to_device(source_x),
            "y": cuda.to_device(source_y),
        },
        {
            "ids": cuda.to_device(target_ids),
            "x": cuda.to_device(target_x),
            "y": cuda.to_device(target_y),
        },
        partner="numba",
        block_size=block_size,
        return_metadata=True,
    )

    result = rt.group_argmin_then_global_argmax_partner_columns(
        partial_rows["columns"],
        group_count=source_count,
        partner="numba",
        numba_known_dense_groups=True,
        numba_validate_group_ids=False,
        numba_validate_nan_scores=False,
        return_metadata=True,
    )
    metadata = result["metadata"]
    partial_metadata = partial_rows["metadata"]
    source_index = int(metadata["winner_group_id"])
    return {
        "label": label,
        "distance": math.sqrt(float(metadata["winner_score"])),
        "source_id": int(source[source_index].id),
        "target_id": int(metadata["winner_item_id"]),
        "row_count": source_count,
        "logical_pair_count": int(partial_metadata["logical_pair_count"]),
        "partial_nearest_row_count": int(partial_metadata["row_count"]),
        "target_tile_count": int(partial_metadata["target_tile_count"]),
        "partner_reference_contract": metadata["partner_reference_contract"],
        "v2_6_numba_partner_continuation_operations": metadata[
            "v2_6_numba_partner_continuation_operations"
        ],
        "v2_6_numba_score_row_operation": partial_metadata["operation"],
        "numba_pairwise_block_nearest_rows_elapsed_seconds": partial_metadata[
            "numba_pairwise_block_nearest_rows_elapsed_seconds"
        ],
        "host_score_row_materialization_used": False,
        "score_rows_generated_on_partner_device": True,
        "bounded_tile_summary_rows": True,
        "numba_known_dense_groups": metadata["numba_known_dense_groups"],
        "host_present_group_compaction_used": metadata["host_present_group_compaction_used"],
        "nan_validation_host_sync_used": metadata["nan_validation_host_sync_used"],
        "native_engine_row_contract": metadata["native_engine_row_contract"],
    }


def _make_spatial_point_groups_for_device_nearest(
    points: tuple[Point, ...],
    *,
    radius: float,
) -> tuple[tuple[Point, ...], tuple[dict[str, object], ...]]:
    if not points:
        raise ValueError("point-group nearest requires non-empty target points")
    if radius <= 0.0:
        raise ValueError("point-group nearest radius must be positive")
    cell_size = max(float(radius) * 2.0, 1.0e-9)
    min_x = min(float(point.x) for point in points)
    min_y = min(float(point.y) for point in points)
    keyed = sorted(
        (
            (
                math.floor((float(point.x) - min_x) / cell_size),
                math.floor((float(point.y) - min_y) / cell_size),
                index,
                point,
            )
            for index, point in enumerate(points)
        ),
        key=lambda item: (item[0], item[1], item[2]),
    )
    ordered_points = tuple(item[3] for item in keyed)
    groups: list[dict[str, object]] = []
    start = 0
    group_id = 0
    while start < len(ordered_points):
        cell_x = keyed[start][0]
        cell_y = keyed[start][1]
        end = start + 1
        while end < len(ordered_points) and keyed[end][0] == cell_x and keyed[end][1] == cell_y:
            end += 1
        chunk = ordered_points[start:end]
        groups.append(
            {
                "id": group_id,
                "point_offset": start,
                "point_count": end - start,
                "min_x": min(float(point.x) for point in chunk),
                "min_y": min(float(point.y) for point in chunk),
                "max_x": max(float(point.x) for point in chunk),
                "max_y": max(float(point.y) for point in chunk),
            }
        )
        start = end
        group_id += 1
    return ordered_points, tuple(groups)


def _points_to_cupy_query_columns(cp, points: tuple[Point, ...]) -> dict[str, object]:
    import numpy as np

    return {
        "ids": cp.asarray([int(point.id) for point in points], dtype=cp.uint32),
        "x": cp.asarray([float(point.x) for point in points], dtype=cp.float64),
        "y": cp.asarray([float(point.y) for point in points], dtype=cp.float64),
    }


def _points_to_torch_query_columns(torch, points: tuple[Point, ...]) -> dict[str, object]:
    device = torch.device("cuda:0")
    return {
        "ids": torch.tensor([int(point.id) for point in points], dtype=torch.uint32, device=device),
        "x": torch.tensor([float(point.x) for point in points], dtype=torch.float64, device=device),
        "y": torch.tensor([float(point.y) for point in points], dtype=torch.float64, device=device),
    }


def _normalize_points(points: tuple[Point, ...], *, origin_x: float, origin_y: float) -> tuple[Point, ...]:
    return tuple(
        Point(id=int(point.id), x=float(point.x) - float(origin_x), y=float(point.y) - float(origin_y))
        for point in points
    )


def _split_source_by_coordinate_span(
    source: tuple[Point, ...],
    *,
    max_span: float,
) -> tuple[tuple[Point, ...], ...]:
    if max_span <= 0.0:
        raise ValueError("coordinate normalization span must be positive")
    ordered = sorted(source, key=lambda point: (float(point.x), float(point.y), int(point.id)))
    chunks: list[tuple[Point, ...]] = []
    start = 0
    while start < len(ordered):
        min_x = float(ordered[start].x)
        end = start + 1
        while end < len(ordered) and float(ordered[end].x) - min_x <= max_span:
            end += 1
        chunk = tuple(sorted(ordered[start:end], key=lambda point: int(point.id)))
        chunks.append(chunk)
        start = end
    return tuple(chunks)


def _target_halo_for_source_chunk(
    target: tuple[Point, ...],
    source_chunk: tuple[Point, ...],
    *,
    radius: float,
) -> tuple[Point, ...]:
    min_x = min(float(point.x) for point in source_chunk) - float(radius)
    max_x = max(float(point.x) for point in source_chunk) + float(radius)
    min_y = min(float(point.y) for point in source_chunk) - float(radius)
    max_y = max(float(point.y) for point in source_chunk) + float(radius)
    return tuple(
        point
        for point in target
        if min_x <= float(point.x) <= max_x and min_y <= float(point.y) <= max_y
    )


def _best_directed_result(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        raise RuntimeError("chunked max-nearest produced no directed rows")
    return max(
        rows,
        key=lambda row: (
            float(row["distance"]),
            -int(row["source_id"]),
            -int(row["target_id"]),
        ),
    )


def _materialize_device_max_nearest_result(cp, partner: str, consumer: dict[str, object], neighbor_ids) -> dict[str, object]:
    columns = consumer["columns"]
    if partner == "cupy":
        query_id = int(cp.asnumpy(columns["item_ids"])[0])
        row_index = int(cp.asnumpy(columns["row_indices"])[0])
        distance = float(cp.asnumpy(columns["scores"])[0])
        if "neighbor_ids" in columns:
            neighbor_id = int(cp.asnumpy(columns["neighbor_ids"])[0])
        else:
            neighbor_id = int(cp.asnumpy(neighbor_ids[row_index : row_index + 1])[0])
        valid_count = int(cp.asnumpy(columns["valid_count"])[0])
    elif partner == "torch":
        query_id = int(columns["item_ids"].detach().cpu()[0].item())
        row_index = int(columns["row_indices"].detach().cpu()[0].item())
        distance = float(columns["scores"].detach().cpu()[0].item())
        valid_count = int(columns["valid_count"].detach().cpu()[0].item())
        neighbor_id = int(neighbor_ids[row_index : row_index + 1].detach().cpu()[0].item())
    elif partner == "numba":
        query_id = int(columns["item_ids"].copy_to_host()[0])
        row_index = int(columns["row_indices"].copy_to_host()[0])
        distance = float(columns["scores"].copy_to_host()[0])
        valid_count = int(columns["valid_count"].copy_to_host()[0])
        neighbor_id = int(cp.asnumpy(neighbor_ids[row_index : row_index + 1])[0])
    else:
        raise ValueError(f"unsupported device max-nearest partner `{partner}`")
    return {
        "distance": distance,
        "source_id": query_id,
        "target_id": neighbor_id,
        "row_index": row_index,
        "valid_count": valid_count,
    }


def _run_optix_device_max_nearest_directed(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    partner: str,
    label: str,
    radius: float,
    query_repeat: int,
    warmup: int,
    coordinate_normalization_span: float | None = None,
) -> dict[str, object]:
    if partner not in {"cupy", "numba", "torch"}:
        raise ValueError("optix_device_max_nearest partner must be 'cupy', 'numba', or 'torch'")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if coordinate_normalization_span is not None:
        span = float(coordinate_normalization_span)
        if span <= 0.0:
            raise ValueError("coordinate_normalization_span must be positive")
        min_x = min(float(point.x) for point in source)
        max_x = max(float(point.x) for point in source)
        if max_x - min_x > span:
            return _run_optix_device_max_nearest_directed_chunked_normalized(
                source,
                target,
                partner=partner,
                label=label,
                radius=radius,
                query_repeat=query_repeat,
                warmup=warmup,
                coordinate_normalization_span=span,
            )
    ordered_target, groups = _make_spatial_point_groups_for_device_nearest(target, radius=radius)
    prepare_start = time.perf_counter()
    cp = None
    torch = None
    scene = None
    session = None
    if partner in {"torch", "cupy"}:
        if partner == "torch":
            try:
                import torch
            except Exception as exc:
                raise RuntimeError("optix_device_max_nearest partner='torch' requires Torch CUDA") from exc
        else:
            try:
                import cupy as cp
            except Exception as exc:
                raise RuntimeError("optix_device_max_nearest partner='cupy' requires CuPy CUDA") from exc
        session = pg_v4.prepare_point_group_nearest_witness_2d_device_arrays_v4(
            ordered_target,
            groups,
            max_radius=radius,
            partner=partner,
        )
        if partner == "torch":
            assert torch is not None
            query_columns = _points_to_torch_query_columns(torch, source)
            output_columns = session.allocate_outputs(query_columns)
            torch.cuda.synchronize()
        else:
            assert cp is not None
            query_columns = _points_to_cupy_query_columns(cp, source)
            output_columns = session.allocate_outputs(query_columns)
            cp.cuda.runtime.deviceSynchronize()
    else:
        try:
            import cupy as cp
        except Exception as exc:
            raise RuntimeError("optix_device_max_nearest partner='numba' requires CuPy device columns") from exc
        scene = prepare_optix_point_group_nearest_witness_2d(
            ordered_target,
            groups,
            max_radius=radius,
        )
        query_columns = _points_to_cupy_query_columns(cp, source)
        output_columns = {
            "query_ids": cp.empty((len(source),), dtype=cp.uint32),
            "neighbor_ids": cp.empty((len(source),), dtype=cp.uint32),
            "distances": cp.empty((len(source),), dtype=cp.float64),
        }
        cp.cuda.runtime.deviceSynchronize()
    prepare_sec = time.perf_counter() - prepare_start
    hot_samples: list[float] = []
    materialize_samples: list[float] = []
    materialized_rows: list[dict[str, object]] = []
    producer_metadata: dict[str, object] | None = None
    consumer_metadata: dict[str, object] | None = None
    try:
        for iteration in range(warmup + query_repeat):
            hot_start = time.perf_counter()
            if partner in {"torch", "cupy"}:
                assert session is not None
                producer = session.run(
                    query_columns,
                    radius=radius,
                    output_columns=output_columns,
                    return_metadata=True,
                )
                if partner == "torch":
                    assert torch is not None
                    query_ids_i64 = output_columns["query_ids"].to(torch.int64)
                    neighbor_ids_i64 = output_columns["neighbor_ids"].to(torch.int64)
                    candidate_item_ids = torch.where(
                        neighbor_ids_i64.ne(0xFFFFFFFF),
                        query_ids_i64,
                        torch.full_like(query_ids_i64, 0xFFFFFFFF),
                    )
                    consumer = rt.global_argmax_u32_f64_partner_columns(
                        {"item_ids": candidate_item_ids, "scores": output_columns["distances"]},
                        partner="torch",
                        validate_non_empty_on_host=False,
                        return_metadata=True,
                        synchronize=False,
                    )
                    torch.cuda.synchronize()
                else:
                    assert cp is not None
                    candidate_item_ids = cp.where(
                        output_columns["neighbor_ids"] != cp.uint32(0xFFFFFFFF),
                        output_columns["query_ids"],
                        cp.uint32(0xFFFFFFFF),
                    ).astype(cp.uint32, copy=False)
                    consumer = rt.global_argmax_u32_f64_partner_columns(
                        {"item_ids": candidate_item_ids, "scores": output_columns["distances"]},
                        partner="cupy",
                        validate_non_empty_on_host=False,
                        return_metadata=True,
                        synchronize=False,
                    )
                    cp.cuda.runtime.deviceSynchronize()
            else:
                assert scene is not None
                assert cp is not None
                producer = scene.write_device_nearest_witness_columns_from_device_query_columns(
                    query_columns,
                    radius=radius,
                    query_ids_out=output_columns["query_ids"],
                    neighbor_ids_out=output_columns["neighbor_ids"],
                    distances_out=output_columns["distances"],
                )
                candidate_item_ids = cp.where(
                    output_columns["neighbor_ids"] != cp.uint32(0xFFFFFFFF),
                    output_columns["query_ids"],
                    cp.uint32(0xFFFFFFFF),
                ).astype(cp.uint32, copy=False)
                consumer = rt.global_argmax_u32_f64_partner_columns(
                    {"item_ids": candidate_item_ids, "scores": output_columns["distances"]},
                    partner="numba",
                    validate_non_empty_on_host=False,
                    return_metadata=True,
                )
                cp.cuda.runtime.deviceSynchronize()
            hot_elapsed = time.perf_counter() - hot_start
            materialize_start = time.perf_counter()
            materialized = _materialize_device_max_nearest_result(
                cp,
                partner,
                consumer,
                output_columns["neighbor_ids"],
            )
            materialize_elapsed = time.perf_counter() - materialize_start
            producer_metadata = dict(producer["metadata"])
            consumer_metadata = dict(consumer["metadata"])
            if iteration >= warmup:
                hot_samples.append(hot_elapsed)
                materialize_samples.append(materialize_elapsed)
                materialized_rows.append(materialized)
    finally:
        if session is not None:
            session.close()
        if scene is not None:
            scene.close()
    if not materialized_rows:
        raise RuntimeError("optix_device_max_nearest produced no measured rows")
    signatures = {
        (
            int(row["source_id"]),
            int(row["target_id"]),
            int(row["row_index"]),
            int(round(float(row["distance"]) * 1_000_000_000.0)),
            int(row["valid_count"]),
        )
        for row in materialized_rows
    }
    if len(signatures) != 1:
        raise RuntimeError("optix_device_max_nearest directed result changed across repeats")
    final = materialized_rows[-1]
    return {
        "label": label,
        "distance": float(final["distance"]),
        "source_id": int(final["source_id"]),
        "target_id": int(final["target_id"]),
        "row_count": len(source),
        "valid_count": int(final["valid_count"]),
        "complete_within_radius": int(final["valid_count"]) == len(source),
        "radius": float(radius),
        "partner": partner,
        "prepared_scene_used": True,
        "prepared_query_columns_used": True,
        "prepared_output_columns_used": True,
        "device_query_columns_used": True,
        "device_output_columns_used": True,
        "device_result_materialization_after_hot_window": True,
        "host_query_upload_in_hot_window": False,
        "host_row_materialization_before_consumer": False,
        "hot_device_synchronized_before_timer_stop": True,
        "native_engine_row_contract": "generic_point_group_nearest_witness_2d_device_columns",
        "partner_reference_contract": "generic_global_argmax_u32_f64",
        "producer_metadata": producer_metadata or {},
        "consumer_metadata": consumer_metadata or {},
        "group_count": len(groups),
        "coordinate_normalization_used": False,
        "run_phases": {
            "prepare_sec": prepare_sec,
            "hot_device_median_sec": float(statistics.median(hot_samples)),
            "hot_device_total_sec": float(sum(hot_samples)),
            "materialize_median_sec": float(statistics.median(materialize_samples)),
            "materialize_total_sec": float(sum(materialize_samples)),
            "query_repeat": int(query_repeat),
            "query_warmup": int(warmup),
        },
    }


def _run_optix_device_max_nearest_directed_chunked_normalized(
    source: tuple[Point, ...],
    target: tuple[Point, ...],
    *,
    partner: str,
    label: str,
    radius: float,
    query_repeat: int,
    warmup: int,
    coordinate_normalization_span: float,
) -> dict[str, object]:
    source_chunks = _split_source_by_coordinate_span(
        source,
        max_span=float(coordinate_normalization_span),
    )
    chunk_results: list[dict[str, object]] = []
    missing_chunks: list[int] = []
    for chunk_index, source_chunk in enumerate(source_chunks):
        target_halo = _target_halo_for_source_chunk(target, source_chunk, radius=radius)
        if not target_halo:
            missing_chunks.append(chunk_index)
            continue
        origin_x = min(
            min(float(point.x) for point in source_chunk),
            min(float(point.x) for point in target_halo),
        )
        origin_y = min(
            min(float(point.y) for point in source_chunk),
            min(float(point.y) for point in target_halo),
        )
        normalized_source = _normalize_points(source_chunk, origin_x=origin_x, origin_y=origin_y)
        normalized_target = _normalize_points(target_halo, origin_x=origin_x, origin_y=origin_y)
        chunk = _run_optix_device_max_nearest_directed(
            normalized_source,
            normalized_target,
            partner=partner,
            label=f"{label}:chunk{chunk_index}",
            radius=radius,
            query_repeat=query_repeat,
            warmup=warmup,
            coordinate_normalization_span=None,
        )
        chunk["coordinate_normalization_origin"] = {"x": origin_x, "y": origin_y}
        chunk["source_chunk_count"] = len(source_chunk)
        chunk["target_halo_count"] = len(target_halo)
        chunk_results.append(chunk)
    if missing_chunks:
        raise RuntimeError(f"coordinate-normalized chunks had no target halo: {missing_chunks}")
    best = _best_directed_result(chunk_results)
    valid_count = sum(int(row["valid_count"]) for row in chunk_results)
    prepare_sec = sum(float(row["run_phases"]["prepare_sec"]) for row in chunk_results)
    hot_device_median_sec = sum(float(row["run_phases"]["hot_device_median_sec"]) for row in chunk_results)
    hot_device_total_sec = sum(float(row["run_phases"]["hot_device_total_sec"]) for row in chunk_results)
    materialize_median_sec = sum(float(row["run_phases"]["materialize_median_sec"]) for row in chunk_results)
    materialize_total_sec = sum(float(row["run_phases"]["materialize_total_sec"]) for row in chunk_results)
    return {
        "label": label,
        "distance": float(best["distance"]),
        "source_id": int(best["source_id"]),
        "target_id": int(best["target_id"]),
        "row_count": len(source),
        "valid_count": int(valid_count),
        "complete_within_radius": int(valid_count) == len(source),
        "radius": float(radius),
        "partner": partner,
        "prepared_scene_used": True,
        "prepared_query_columns_used": True,
        "prepared_output_columns_used": True,
        "device_query_columns_used": True,
        "device_output_columns_used": True,
        "device_result_materialization_after_hot_window": True,
        "host_query_upload_in_hot_window": False,
        "host_row_materialization_before_consumer": False,
        "hot_device_synchronized_before_timer_stop": True,
        "native_engine_row_contract": "generic_point_group_nearest_witness_2d_device_columns",
        "partner_reference_contract": "generic_global_argmax_u32_f64",
        "producer_metadata": dict(best.get("producer_metadata") or {}),
        "consumer_metadata": dict(best.get("consumer_metadata") or {}),
        "group_count": sum(int(row["group_count"]) for row in chunk_results),
        "coordinate_normalization_used": True,
        "coordinate_normalization_span": float(coordinate_normalization_span),
        "coordinate_normalization_chunk_count": len(chunk_results),
        "coordinate_normalization_contract": (
            "Generic spatial chunking with radius halo; each chunk is translated "
            "to local coordinates before the same V4 point-group nearest-witness "
            "surface runs."
        ),
        "chunk_summaries": tuple(
            {
                "chunk_index": index,
                "distance": float(row["distance"]),
                "source_id": int(row["source_id"]),
                "target_id": int(row["target_id"]),
                "row_count": int(row["row_count"]),
                "valid_count": int(row["valid_count"]),
                "source_chunk_count": int(row["source_chunk_count"]),
                "target_halo_count": int(row["target_halo_count"]),
                "origin": row["coordinate_normalization_origin"],
                "hot_device_median_sec": float(row["run_phases"]["hot_device_median_sec"]),
                "prepare_sec": float(row["run_phases"]["prepare_sec"]),
            }
            for index, row in enumerate(chunk_results)
        ),
        "run_phases": {
            "prepare_sec": prepare_sec,
            "hot_device_median_sec": hot_device_median_sec,
            "hot_device_total_sec": hot_device_total_sec,
            "materialize_median_sec": materialize_median_sec,
            "materialize_total_sec": materialize_total_sec,
            "query_repeat": int(query_repeat),
            "query_warmup": int(warmup),
        },
    }


def run_app(
    backend: str = "cpu_python_reference",
    copies: int = 1,
    *,
    embree_result_mode: str = "rows",
    optix_summary_mode: str = "rows",
    hausdorff_threshold: float = 0.4,
    require_rt_core: bool = False,
    partner: str = "cupy",
    query_repeat: int = 1,
    warmup: int = 0,
    coordinate_normalization_span: float | None = None,
) -> dict[str, object]:
    input_start = time.perf_counter()
    case = make_authored_point_sets(copies=copies)
    run_phases: dict[str, float] = {"input_construction_sec": time.perf_counter() - input_start}
    points_a = case["points_a"]
    points_b = case["points_b"]
    if not points_a or not points_b:
        raise ValueError("Hausdorff distance requires non-empty point sets")
    if embree_result_mode not in {"rows", "directed_summary"}:
        raise ValueError("embree_result_mode must be 'rows' or 'directed_summary'")
    if optix_summary_mode not in {"rows", *DIRECTED_THRESHOLD_PREPARED_MODES}:
        raise ValueError(
            "optix_summary_mode must be 'rows', 'directed_threshold_prepared', "
            "or 'directed_threshold_prepared_runner'"
        )
    if backend == "partner_exact" and partner not in {"torch", "cupy", "numba"}:
        raise ValueError("partner must be 'torch', 'cupy', or 'numba'")
    if hausdorff_threshold < 0:
        raise ValueError("hausdorff_threshold must be non-negative")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    _enforce_rt_core_requirement(backend, optix_summary_mode, require_rt_core)
    native_continuation_backend = _native_continuation_backend(
        backend,
        embree_result_mode=embree_result_mode,
        optix_summary_mode=optix_summary_mode,
    )

    if backend == "optix_device_max_nearest":
        query_start = time.perf_counter()
        directed_ab = _run_optix_device_max_nearest_directed(
            points_a,
            points_b,
            partner=partner,
            label="a_to_b",
            radius=hausdorff_threshold,
            query_repeat=query_repeat,
            warmup=warmup,
            coordinate_normalization_span=coordinate_normalization_span,
        )
        directed_ba = _run_optix_device_max_nearest_directed(
            points_b,
            points_a,
            partner=partner,
            label="b_to_a",
            radius=hausdorff_threshold,
            query_repeat=query_repeat,
            warmup=warmup,
            coordinate_normalization_span=coordinate_normalization_span,
        )
        run_phases["optix_device_max_nearest_directed_summary_sec"] = time.perf_counter() - query_start
        run_phases["scene_prepare_sec"] = float(directed_ab["run_phases"]["prepare_sec"]) + float(
            directed_ba["run_phases"]["prepare_sec"]
        )
        run_phases["hot_device_sec"] = float(directed_ab["run_phases"]["hot_device_median_sec"]) + float(
            directed_ba["run_phases"]["hot_device_median_sec"]
        )
        run_phases["materialize_sec"] = float(directed_ab["run_phases"]["materialize_median_sec"]) + float(
            directed_ba["run_phases"]["materialize_median_sec"]
        )
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": partner,
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": "device_max_nearest",
            "hausdorff_threshold": hausdorff_threshold,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL/OptiX uses the generic prepared point-group nearest-witness "
                "device-query-column primitive, then the selected partner runs a "
                "generic global max reduction on device before compact materialization."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": True,
            "native_continuation_backend": native_continuation_backend,
            "rt_core_accelerated": True,
            "partner_reference_contract": "generic_global_argmax_u32_f64",
            "coordinate_normalization_span": coordinate_normalization_span,
            "coordinate_normalization_used": bool(
                directed_ab.get("coordinate_normalization_used") or directed_ba.get("coordinate_normalization_used")
            ),
            "run_phases": run_phases,
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "reported_query_metric": "sum_of_directed_hot_device_medians",
            },
            "claim_boundary": {
                "v3_0_internal_evidence": True,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
                "app_specific_native_engine_logic_allowed": False,
            },
        }

    if backend == "partner_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_exact_directed(points_a, points_b, partner=partner, label="a_to_b")
        directed_ba = _run_partner_exact_directed(points_b, points_a, partner=partner, label="b_to_a")
        run_phases["partner_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": partner,
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 partner exact mode converts Python point rows into generic partner "
                "point columns, computes nearest distance per source point, then reduces the "
                "nearest distances with max. The native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": directed_ab["partner_reference_contract"],
            "host_score_row_materialization_used": directed_ab.get("host_score_row_materialization_used")
            if partner == "numba"
            else None,
            "score_rows_generated_on_partner_device": directed_ab.get("score_rows_generated_on_partner_device")
            if partner == "numba"
            else None,
            "numba_strategy": directed_ab.get("numba_strategy") if partner == "numba" else None,
            "run_phases": run_phases,
            "claim_boundary": {
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "numba_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    if backend == "partner_numpy_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_numpy_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_numpy_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_numpy_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "numpy",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 NumPy reference mode converts Python point rows into generic "
                "partner point columns, computes per-source nearest witnesses, and "
                "uses a generic group-argmin-then-global-argmax continuation. The "
                "native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "run_phases": run_phases,
        }

    if backend == "partner_cupy_witness_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_cupy_witness_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_cupy_witness_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_cupy_witness_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "cupy",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2 CuPy witness mode converts Python point rows into generic "
                "partner device columns, computes per-source nearest witnesses, and "
                "uses the generic CuPy group-argmin-then-global-argmax continuation. "
                "The native engine is not app-customized."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "run_phases": run_phases,
        }

    if backend == "partner_numba_witness_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_numba_witness_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_numba_witness_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_numba_witness_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "numba",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2.6 Numba witness mode turns point rows into generic grouped "
                "score rows on the Numba device, then uses group_argmin_then_global_argmax_partner_columns "
                "with user-selected partner=\"numba\". The native engine is not "
                "app-customized and RT traversal is not called in this exact dense path."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "host_score_row_materialization_used": False,
            "score_rows_generated_on_partner_device": True,
            "run_phases": run_phases,
            "claim_boundary": {
                "v2_6_release_authorized": False,
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "numba_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    if backend == "partner_numba_block_nearest_exact":
        query_start = time.perf_counter()
        directed_ab = _run_partner_numba_block_nearest_exact_directed(points_a, points_b, label="a_to_b")
        directed_ba = _run_partner_numba_block_nearest_exact_directed(points_b, points_a, label="b_to_a")
        run_phases["partner_numba_block_nearest_exact_directed_summary_sec"] = time.perf_counter() - query_start
        undirected = max(
            (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
            key=lambda item: (float(item[1]["distance"]), item[0]),
        )
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "partner": "numba",
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": None,
            "hausdorff_threshold": None,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": float(undirected[1]["distance"]),
            "witness_direction": undirected[0],
            "oracle": oracle,
            "matches_oracle": math.isclose(
                float(undirected[1]["distance"]),
                float(oracle["hausdorff_distance"]),
                rel_tol=1e-5,
                abs_tol=1e-5,
            ),
            "rtdl_role": (
                "RTDL v2.6 Numba block-nearest witness mode summarizes point-pair "
                "tiles into generic nearest score rows on the Numba device, then "
                "uses group_argmin_then_global_argmax_partner_columns with "
                "user-selected partner=\"numba\". The native engine is not "
                "app-customized and RT traversal is not called in this exact dense path."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": False,
            "native_continuation_backend": "none",
            "rt_core_accelerated": False,
            "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
            "host_score_row_materialization_used": False,
            "score_rows_generated_on_partner_device": True,
            "bounded_tile_summary_rows": True,
            "run_phases": run_phases,
            "claim_boundary": {
                "v2_6_release_authorized": False,
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "numba_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    if backend in {"embree", "optix"} and optix_summary_mode in DIRECTED_THRESHOLD_PREPARED_MODES:
        use_productized_runner = optix_summary_mode == "directed_threshold_prepared_runner"
        directed_ab = _run_prepared_directed_threshold(
            points_a,
            points_b,
            backend=backend,
            radius=hausdorff_threshold,
            label="a_to_b",
            query_repeat=query_repeat,
            warmup=warmup,
            use_productized_runner=use_productized_runner,
        )
        directed_ba = _run_prepared_directed_threshold(
            points_b,
            points_a,
            backend=backend,
            radius=hausdorff_threshold,
            label="b_to_a",
            query_repeat=query_repeat,
            warmup=warmup,
            use_productized_runner=use_productized_runner,
        )
        run_phases["scene_prepare_sec"] = float(directed_ab["run_phases"]["scene_prepare_sec"]) + float(
            directed_ba["run_phases"]["scene_prepare_sec"]
        )
        run_phases["query_fixed_radius_threshold_reached_count_sec"] = float(
            directed_ab["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        ) + float(
            directed_ba["run_phases"]["query_fixed_radius_threshold_reached_count_sec"]
        )
        if "runner_outer_query_sec" in directed_ab["run_phases"] and "runner_outer_query_sec" in directed_ba["run_phases"]:
            run_phases["runner_outer_query_sec"] = float(
                directed_ab["run_phases"]["runner_outer_query_sec"]
            ) + float(directed_ba["run_phases"]["runner_outer_query_sec"])
        if (
            "runner_outer_query_total_sec" in directed_ab["run_phases"]
            and "runner_outer_query_total_sec" in directed_ba["run_phases"]
        ):
            run_phases["runner_outer_query_total_sec"] = float(
                directed_ab["run_phases"]["runner_outer_query_total_sec"]
            ) + float(directed_ba["run_phases"]["runner_outer_query_total_sec"])
        if (
            "runner_outer_prepare_sec" in directed_ab["run_phases"]
            and "runner_outer_prepare_sec" in directed_ba["run_phases"]
        ):
            run_phases["runner_outer_prepare_sec"] = float(
                directed_ab["run_phases"]["runner_outer_prepare_sec"]
            ) + float(directed_ba["run_phases"]["runner_outer_prepare_sec"])
        if (
            "runner_outer_cache_load_sec" in directed_ab["run_phases"]
            and "runner_outer_cache_load_sec" in directed_ba["run_phases"]
        ):
            run_phases["runner_outer_cache_load_sec"] = float(
                directed_ab["run_phases"]["runner_outer_cache_load_sec"]
            ) + float(directed_ba["run_phases"]["runner_outer_cache_load_sec"])
        if (
            isinstance(directed_ab["run_phases"].get("runner_native_prepare_sec"), (int, float))
            and isinstance(directed_ba["run_phases"].get("runner_native_prepare_sec"), (int, float))
        ):
            run_phases["runner_native_prepare_sec"] = float(
                directed_ab["run_phases"]["runner_native_prepare_sec"]
            ) + float(directed_ba["run_phases"]["runner_native_prepare_sec"])
        run_phases[f"{backend}_prepare_sec"] = run_phases["scene_prepare_sec"]
        run_phases[f"{backend}_query_sec"] = run_phases["query_fixed_radius_threshold_reached_count_sec"]
        postprocess_start = time.perf_counter()
        within_threshold = bool(directed_ab["within_threshold"] and directed_ba["within_threshold"])
        run_phases["python_postprocess_sec"] = time.perf_counter() - postprocess_start
        validation_start = time.perf_counter()
        oracle = expected_tiled_hausdorff(copies=copies)
        oracle_within_threshold = float(oracle["hausdorff_distance"]) <= hausdorff_threshold + 1e-12
        run_phases["validation_sec"] = time.perf_counter() - validation_start
        session_key = rt.make_prepared_session_cache_key(
            primitive="fixed_radius_threshold_2d",
            backend=backend,
            input_fingerprints={
                "source_points": {"count": len(points_a), "copies": copies},
                "target_points": {"count": len(points_b), "copies": copies},
            },
            parameters={"threshold": hausdorff_threshold},
            partner="none",
            device="cuda:0" if backend == "optix" else "cpu",
        )
        session_policy = rt.RtdlPreparedSessionResidencyPolicy(
            cache_key=session_key,
            cache_enabled=False,
            lifetime_state="session_retained",
            reuse_scope="explicit_user_session",
            invalidation_events=("explicit_invalidate", "backend_context_reset", "close"),
        )
        runner_ab = directed_ab.get("prepared_execution_session_runner")
        runner_ba = directed_ba.get("prepared_execution_session_runner")
        runner_used = bool(runner_ab and runner_ba)
        runtime_executed_count = sum(
            1
            for runner in (runner_ab, runner_ba)
            if isinstance(runner, dict) and bool(runner.get("runtime_executed"))
        )
        runner_cache_hit_count = sum(
            1
            for runner in (runner_ab, runner_ba)
            if isinstance(runner, dict) and bool(runner.get("cache_hit"))
        )
        both_runtime_trunk = bool(
            runner_used
            and all(
                bool(runner.get("runtime_trunk_executes_end_to_end"))
                for runner in (runner_ab, runner_ba)
                if isinstance(runner, dict)
            )
        )
        both_no_threshold_rows = bool(
            runner_used
            and all(
                not bool(runner.get("threshold_summary_rows_materialized_on_host"))
                for runner in (runner_ab, runner_ba)
                if isinstance(runner, dict)
            )
        )
        both_internal_residency = bool(
            runner_used
            and all(
                bool(runner.get("internal_device_residency_between_rtdl_phases"))
                for runner in (runner_ab, runner_ba)
                if isinstance(runner, dict)
            )
        )
        runner_summary = {
            "used": runner_used,
            "productized_execution_path": "prepared_execution_session_runner"
            if runner_used
            else None,
            "both_directed_legs_runtime_executed": runtime_executed_count == 2,
            "runtime_executed_count": runtime_executed_count,
            "cache_hit_count": runner_cache_hit_count,
            "both_directed_legs_runtime_trunk_end_to_end": both_runtime_trunk,
            "both_directed_legs_no_threshold_rows_materialized_on_host": both_no_threshold_rows,
            "both_directed_legs_internal_device_residency_between_rtdl_phases": both_internal_residency,
            "directed_a_to_b": runner_ab,
            "directed_b_to_a": runner_ba,
            "release_authorized": False,
            "all_app_rerun_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "whole_hausdorff_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_external_buffer_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        }
        return {
            "app": "hausdorff_distance",
            "backend": backend,
            "copies": copies,
            "point_count_a": len(points_a),
            "point_count_b": len(points_b),
            "embree_result_mode": None,
            "optix_summary_mode": optix_summary_mode,
            "hausdorff_threshold": hausdorff_threshold,
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff_distance": None,
            "within_threshold": within_threshold,
            "oracle": oracle,
            "oracle_within_threshold": oracle_within_threshold,
            "matches_oracle": within_threshold == oracle_within_threshold,
            "oracle_decision_matches": within_threshold == oracle_within_threshold,
            "oracle_identity_matches": (
                True
                if directed_ab["identity_parity_available"] and directed_ba["identity_parity_available"]
                else None
            ),
            "rtdl_role": (
                f"RTDL/{backend} uses prepared fixed-radius threshold traversal to answer "
                "the Hausdorff decision subproblem: every source point has at least "
                "one target within the threshold. Python combines the two directed "
                "decisions and validates against the deterministic oracle."
            ),
            "optix_performance": _optix_performance(),
            "native_continuation_active": native_continuation_backend != "none",
            "native_continuation_backend": native_continuation_backend,
            "rt_core_accelerated": backend == "optix",
            "run_phases": run_phases,
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_query_total_sec": float(
                    directed_ab["run_phases"]["query_fixed_radius_threshold_reached_count_total_sec"]
                )
                + float(directed_ba["run_phases"]["query_fixed_radius_threshold_reached_count_total_sec"]),
                "reported_query_metric": "sum_of_directed_query_medians",
            },
            "prepared_session_residency": {
                "cache_key": session_key.to_metadata(),
                "policy": session_policy.to_metadata(),
                "explicit_reuse_helper": (
                    "prepared_execution_session_runner"
                    if use_productized_runner
                    else "get_or_prepare_explicit_session"
                ),
                "cache_enabled_by_default": use_productized_runner,
                "cold_hot_phase_split_required": True,
                "prepare_once_query_many_pattern": True,
                "productized_execution_path": "prepared_execution_session_runner"
                if use_productized_runner
                else None,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "public_speedup_claim_authorized": False,
            },
            "prepared_execution_session_runner": runner_summary,
            "claim_boundary": {
                "public_speedup_claim_authorized": False,
                "broad_rt_core_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "all_app_rerun_authorized": False,
                "whole_hausdorff_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "v4_external_buffer_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
                "app_specific_native_engine_logic_allowed": False,
                "full_paper_reproduction_claim_authorized": False,
            },
        }

    if backend == "embree" and embree_result_mode == "directed_summary":
        query_start = time.perf_counter()
        directed_ab = rt.directed_hausdorff_2d_embree(points_a, points_b)
        directed_ba = rt.directed_hausdorff_2d_embree(points_b, points_a)
        run_phases["native_directed_summary_sec"] = time.perf_counter() - query_start
        rtdl_role = (
            "RTDL/Embree runs k=1 nearest-neighbor traversal and directed max reduction "
            "inside the native Embree summary path; Python keeps only undirected comparison "
            "and oracle validation."
        )
    elif embree_result_mode == "directed_summary":
        query_start = time.perf_counter()
        oracle_summary = expected_tiled_hausdorff(copies=copies)
        run_phases["analytic_summary_sec"] = time.perf_counter() - query_start
        directed_ab = oracle_summary["directed_a_to_b"]
        directed_ba = oracle_summary["directed_b_to_a"]
        rtdl_role = (
            "Compact CPU/reference mode uses the exact deterministic tiled-fixture Hausdorff "
            "summary so large app-level Embree comparisons do not spend time in an O(N^2) oracle."
        )
    else:
        query_start = time.perf_counter()
        rows_ab = _run_nearest(backend, points_a, points_b)
        rows_ba = _run_nearest(backend, points_b, points_a)
        run_phases["query_and_materialize_sec"] = time.perf_counter() - query_start
        reduction_start = time.perf_counter()
        directed_ab = _directed_from_rows(rows_ab, "a_to_b")
        directed_ba = _directed_from_rows(rows_ba, "b_to_a")
        run_phases["python_reduction_sec"] = time.perf_counter() - reduction_start
        rtdl_role = (
            "RTDL emits k=1 nearest-neighbor rows; rt.reduce_rows(max) computes directed "
            "Hausdorff distances, while Python keeps witness selection and undirected comparison."
        )
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    validation_start = time.perf_counter()
    oracle = (
        expected_tiled_hausdorff(copies=copies)
        if embree_result_mode == "directed_summary"
        else brute_force_hausdorff(points_a, points_b)
    )
    run_phases["validation_sec"] = time.perf_counter() - validation_start

    return {
        "app": "hausdorff_distance",
        "backend": backend,
        "partner": None,
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "embree_result_mode": embree_result_mode if backend == "embree" else None,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else None,
        "hausdorff_threshold": None,
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
        "oracle": oracle,
        "matches_oracle": math.isclose(
            float(undirected[1]["distance"]),
            float(oracle["hausdorff_distance"]),
            rel_tol=1e-5,
            abs_tol=1e-5,
        ),
        "rtdl_role": rtdl_role,
        "optix_performance": _optix_performance(),
        "native_continuation_active": native_continuation_backend != "none",
        "native_continuation_backend": native_continuation_backend,
        "rt_core_accelerated": False,
        "run_phases": run_phases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived Hausdorff distance app: RTDL nearest-neighbor rows plus Python reduction."
    )
    parser.add_argument(
        "--backend",
        choices=(
            "cpu_python_reference",
            "cpu",
            "embree",
            "optix",
            "vulkan",
            "partner_exact",
            "partner_numpy_exact",
            "partner_cupy_witness_exact",
            "partner_numba_witness_exact",
            "partner_numba_block_nearest_exact",
            "optix_device_max_nearest",
        ),
        default="cpu_python_reference",
    )
    parser.add_argument("--partner", choices=("torch", "cupy", "numba"), default="cupy")
    parser.add_argument("--copies", type=int, default=1, help="tile the small authored point sets")
    parser.add_argument(
        "--embree-result-mode",
        choices=("rows", "directed_summary"),
        default="rows",
        help="Embree-only: emit KNN rows or native directed-Hausdorff summaries",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", *DIRECTED_THRESHOLD_PREPARED_MODES),
        default="rows",
        help=(
            "OptiX/Embree threshold mode: use prepared fixed-radius threshold traversal, "
            "with *_runner selecting the productized prepared-execution runner"
        ),
    )
    parser.add_argument(
        "--hausdorff-threshold",
        type=float,
        default=0.4,
        help="Decision radius for --optix-summary-mode directed_threshold_prepared",
    )
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    parser.add_argument("--repeat", type=int, default=1, help="Repeat hot prepared-query phase.")
    parser.add_argument("--warmup", type=int, default=0, help="Prepared-query warmup iterations to drop.")
    parser.add_argument(
        "--coordinate-normalization-span",
        type=float,
        default=None,
        help=(
            "OptiX device-max only: split large-coordinate source sets into local-origin chunks "
            "with this maximum x-span before running the same V4 point-group surface."
        ),
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                args.copies,
                embree_result_mode=args.embree_result_mode,
                optix_summary_mode=args.optix_summary_mode,
                hausdorff_threshold=args.hausdorff_threshold,
                require_rt_core=args.require_rt_core,
                partner=args.partner,
                query_repeat=args.repeat,
                warmup=args.warmup,
                coordinate_normalization_span=args.coordinate_normalization_span,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
