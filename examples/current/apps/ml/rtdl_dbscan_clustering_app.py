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


EPSILON = 0.35
MIN_POINTS = 3
K_MAX = 16
NOISE_CLUSTER_ID = -1


@rt.kernel(backend="rtdl", precision="float_approx")
def dbscan_neighbor_rows_kernel():
    points = rt.input("points", rt.Points, role="probe")
    candidates = rt.traverse(points, points, accel="bvh")
    neighbors = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=EPSILON, k_max=K_MAX))
    return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance"])


def make_dbscan_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_points = (
        rt.Point(id=1, x=0.00, y=0.00),
        rt.Point(id=2, x=0.12, y=0.04),
        rt.Point(id=3, x=-0.10, y=0.08),
        rt.Point(id=4, x=0.08, y=-0.12),
        rt.Point(id=5, x=2.00, y=2.00),
        rt.Point(id=6, x=2.14, y=2.05),
        rt.Point(id=7, x=1.88, y=1.94),
        rt.Point(id=8, x=4.50, y=0.00),
    )

    points: list[rt.Point] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        x_offset = 6.0 * copy_index
        for point in base_points:
            points.append(rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
    return {"points": tuple(points)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(dbscan_neighbor_rows_kernel, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(dbscan_neighbor_rows_kernel, **case))
    if backend == "embree":
        return tuple(rt.run_embree(dbscan_neighbor_rows_kernel, **case))
    if backend == "optix":
        return tuple(rt.run_optix(dbscan_neighbor_rows_kernel, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(dbscan_neighbor_rows_kernel, **case))
    if backend == "scipy":
        return tuple(
            rt.run_scipy_fixed_radius_neighbors(
                case["points"],
                case["points"],
                radius=EPSILON,
                k_max=K_MAX,
            )
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _neighbors_by_point(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
) -> dict[int, set[int]]:
    point_ids = {point.id for point in points}
    neighborhoods: dict[int, set[int]] = {point.id: set() for point in points}
    for row in rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        if query_id in point_ids and neighbor_id in point_ids:
            neighborhoods[query_id].add(neighbor_id)
    return neighborhoods


def _neighbor_counts_by_point(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
) -> dict[int, int]:
    counts: dict[int, int] = {point.id: 0 for point in points}
    for row in rt.reduce_rows(
        tuple(rows),
        group_by="query_id",
        op="count",
        output_field="neighbor_count",
    ):
        query_id = int(row["query_id"])
        if query_id in counts:
            counts[query_id] = int(row["neighbor_count"])
    return counts


def cluster_from_neighbor_rows(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
    *,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    if min_points < 1:
        raise ValueError("min_points must be at least 1")

    neighbor_rows = tuple(rows)
    neighborhoods = _neighbors_by_point(points, neighbor_rows)
    neighbor_counts = _neighbor_counts_by_point(points, neighbor_rows)
    core_ids = {point_id for point_id, count in neighbor_counts.items() if count >= min_points}
    labels: dict[int, int] = {}
    cluster_id = 0

    for point_id in sorted(neighborhoods):
        if point_id in labels:
            continue
        if point_id not in core_ids:
            labels[point_id] = NOISE_CLUSTER_ID
            continue

        cluster_id += 1
        frontier = [point_id]
        labels[point_id] = cluster_id
        while frontier:
            current_id = frontier.pop(0)
            for neighbor_id in sorted(neighborhoods[current_id]):
                previous_label = labels.get(neighbor_id)
                if previous_label is None or previous_label == NOISE_CLUSTER_ID:
                    labels[neighbor_id] = cluster_id
                if neighbor_id in core_ids and previous_label is None:
                    frontier.append(neighbor_id)

    return tuple(
        {
            "point_id": point_id,
            "cluster_id": labels.get(point_id, NOISE_CLUSTER_ID),
            "is_core": point_id in core_ids,
            "neighbor_count": neighbor_counts[point_id],
        }
        for point_id in sorted(neighborhoods)
    )


def brute_force_dbscan(
    points: tuple[rt.Point, ...],
    *,
    epsilon: float = EPSILON,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        for neighbor in points:
            distance = math.hypot(query.x - neighbor.x, query.y - neighbor.y)
            if distance <= epsilon:
                rows.append({"query_id": query.id, "neighbor_id": neighbor.id, "distance": distance})
    rows.sort(key=lambda row: (int(row["query_id"]), float(row["distance"]), int(row["neighbor_id"])))
    return cluster_from_neighbor_rows(points, rows, min_points=min_points)


def brute_force_core_flag_rows(
    points: tuple[rt.Point, ...],
    *,
    epsilon: float = EPSILON,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        count = 0
        for neighbor in points:
            if math.hypot(query.x - neighbor.x, query.y - neighbor.y) <= epsilon:
                count += 1
        rows.append(
            {
                "point_id": query.id,
                "neighbor_count": count,
                "is_core": count >= min_points,
            }
        )
    return tuple(sorted(rows, key=lambda row: int(row["point_id"])))


def expected_tiled_core_flag_rows(*, copies: int) -> tuple[dict[str, object], ...]:
    """Exact DBSCAN core summary for make_dbscan_case without O(N^2) expansion."""
    base_rows = (
        (1, MIN_POINTS, True),
        (2, MIN_POINTS, True),
        (3, MIN_POINTS, True),
        (4, MIN_POINTS, True),
        (5, 3, True),
        (6, 3, True),
        (7, 3, True),
        (8, 1, False),
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        for point_id, neighbor_count, is_core in base_rows:
            rows.append(
                {
                    "point_id": point_id + id_offset,
                    "neighbor_count": neighbor_count,
                    "is_core": is_core,
                }
            )
    return tuple(rows)


def expected_tiled_cluster_rows(*, copies: int) -> tuple[dict[str, object], ...]:
    """Exact clustered rows for make_dbscan_case without O(N^2) expansion."""
    base_rows = (
        (1, 1, True, MIN_POINTS),
        (2, 1, True, MIN_POINTS),
        (3, 1, True, MIN_POINTS),
        (4, 1, True, MIN_POINTS),
        (5, 2, True, 3),
        (6, 2, True, 3),
        (7, 2, True, 3),
        (8, NOISE_CLUSTER_ID, False, 1),
    )
    rows: list[dict[str, object]] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        cluster_offset = 2 * copy_index
        for point_id, cluster_id, is_core, neighbor_count in base_rows:
            rows.append(
                {
                    "point_id": point_id + id_offset,
                    "cluster_id": (
                        NOISE_CLUSTER_ID
                        if cluster_id == NOISE_CLUSTER_ID
                        else cluster_id + cluster_offset
                    ),
                    "is_core": is_core,
                    "neighbor_count": neighbor_count,
                }
            )
    return tuple(rows)


def expected_tiled_component_signature(*, copies: int) -> dict[str, object]:
    """Compact exact component summary for make_dbscan_case without per-point rows."""
    return {
        "point_count": 8 * int(copies),
        "cluster_count": 2 * int(copies),
        "clustered_point_count": 7 * int(copies),
        "noise_count": int(copies),
        "core_count": 7 * int(copies),
        "size_histogram": {"3": int(copies), "4": int(copies)},
        "min_size": 3,
        "max_size": 4,
    }


def _core_flag_rows_from_count_rows(
    points: tuple[rt.Point, ...],
    count_rows: Iterable[dict[str, object]],
    *,
    min_points: int = MIN_POINTS,
) -> tuple[dict[str, object], ...]:
    counts: dict[int, int] = {point.id: 0 for point in points}
    threshold_reached: dict[int, int] = {point.id: 0 for point in points}
    for row in count_rows:
        point_id = int(row["query_id"])
        if point_id not in counts:
            continue
        counts[point_id] = int(row["neighbor_count"])
        threshold_reached[point_id] = int(row.get("threshold_reached", 0))
    return tuple(
        {
            "point_id": point_id,
            "neighbor_count": counts[point_id],
            "is_core": counts[point_id] >= min_points or threshold_reached[point_id] == 1,
        }
        for point_id in sorted(counts)
    )


def _run_optix_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    result = rt.run_generic_fixed_radius_count_threshold_2d(
        case["points"],
        case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
        backend="optix",
    )
    return _core_flag_rows_from_count_rows(case["points"], result["rows"])


def _run_optix_prepared_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=case["points"],
        backend="optix",
        max_radius=EPSILON,
        prepare_scene=rt.prepare_optix_fixed_radius_count_threshold_2d,
    ) as prepared:
        result = prepared.run(
            case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
    return _core_flag_rows_from_count_rows(case["points"], result["rows"])


def _run_optix_prepared_core_count(case: dict[str, tuple[rt.Point, ...]]) -> dict[str, int | str | None]:
    result = rt.run_generic_prepared_fixed_radius_threshold_reached_count_2d(
        search_points=case["points"],
        query_points=case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
        backend="optix",
        max_radius=EPSILON,
        prepare_scene=rt.prepare_optix_fixed_radius_count_threshold_2d,
    )
    core_count = int(result["threshold_reached_count"])
    return {
        "point_count": len(case["points"]),
        "threshold_reached_count": core_count,
        "core_count": core_count,
        "row_count": None,
        "summary_mode": "scalar_threshold_count",
        "generic_primitive": result["primitive"],
        "summary_primitive": result["summary_primitive"],
    }


def _run_embree_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    result = rt.run_generic_fixed_radius_count_threshold_2d(
        case["points"],
        case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
        backend="embree",
    )
    return _core_flag_rows_from_count_rows(case["points"], result["rows"])


def _run_embree_prepared_core_flag_summary(case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=case["points"],
        backend="embree",
        prepare_scene=rt.prepare_embree_fixed_radius_count_threshold_2d,
    ) as prepared:
        result = prepared.run(
            case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
    return _core_flag_rows_from_count_rows(case["points"], result["rows"])


def _run_scipy_core_count(case: dict[str, tuple[rt.Point, ...]]) -> dict[str, int | str | None]:
    count_rows = rt.run_scipy_fixed_radius_count_threshold(
        case["points"],
        case["points"],
        radius=EPSILON,
        threshold=MIN_POINTS,
        k_max=K_MAX,
    )
    core_count = sum(1 for row in count_rows if int(row["threshold_reached"]) != 0)
    return {
        "point_count": len(case["points"]),
        "threshold_reached_count": int(core_count),
        "core_count": int(core_count),
        "row_count": None,
        "summary_mode": "scipy_ckdtree_threshold_count",
    }


def _partner_column_to_list(column, partner: str) -> list[object]:
    if partner == "torch":
        return column.detach().cpu().tolist()
    if partner == "cupy":
        import cupy

        return cupy.asnumpy(column).tolist()
    if partner == "numba":
        return column.copy_to_host().tolist()
    raise ValueError("partner must be 'torch', 'cupy', or 'numba'")


def _component_signature_from_numpy_arrays(labels, core_flags, *, aggregation_backend: str) -> dict[str, object]:
    import numpy as np

    labels_np = np.asarray(labels)
    core_np = np.asarray(core_flags)
    if labels_np.shape[0] != core_np.shape[0]:
        raise ValueError("component_labels and is_core columns must have the same length")
    clustered_labels = labels_np[labels_np != NOISE_CLUSTER_ID]
    if clustered_labels.size:
        _, counts = np.unique(clustered_labels, return_counts=True)
        sizes, size_counts = np.unique(counts, return_counts=True)
        size_histogram = {str(int(size)): int(count) for size, count in zip(sizes, size_counts)}
        min_size = int(counts.min())
        max_size = int(counts.max())
        cluster_count = int(counts.size)
        clustered_point_count = int(counts.sum())
    else:
        size_histogram = {}
        min_size = None
        max_size = None
        cluster_count = 0
        clustered_point_count = 0
    return {
        "point_count": int(labels_np.shape[0]),
        "cluster_count": cluster_count,
        "clustered_point_count": clustered_point_count,
        "noise_count": int(np.count_nonzero(labels_np == NOISE_CLUSTER_ID)),
        "core_count": int(np.count_nonzero(core_np)),
        "size_histogram": dict(sorted(size_histogram.items(), key=lambda item: int(item[0]))),
        "min_size": min_size,
        "max_size": max_size,
        "aggregation_backend": aggregation_backend,
        "materialized_python_rows": False,
    }


def _component_signature_from_cupy_arrays(labels_dev, core_flags_dev, *, aggregation_backend: str) -> dict[str, object]:
    import cupy

    if int(labels_dev.size) != int(core_flags_dev.size):
        raise ValueError("component_labels and is_core columns must have the same length")
    clustered_labels = labels_dev[labels_dev != NOISE_CLUSTER_ID]
    if int(clustered_labels.size):
        _, counts = cupy.unique(clustered_labels, return_counts=True)
        sizes, size_counts = cupy.unique(counts, return_counts=True)
        sizes_host = cupy.asnumpy(sizes)
        size_counts_host = cupy.asnumpy(size_counts)
        size_histogram = {
            str(int(size)): int(count) for size, count in zip(sizes_host.tolist(), size_counts_host.tolist())
        }
        min_size = int(cupy.min(counts).item())
        max_size = int(cupy.max(counts).item())
        cluster_count = int(counts.size)
        clustered_point_count = int(cupy.sum(counts).item())
    else:
        size_histogram = {}
        min_size = None
        max_size = None
        cluster_count = 0
        clustered_point_count = 0
    return {
        "point_count": int(labels_dev.size),
        "cluster_count": cluster_count,
        "clustered_point_count": clustered_point_count,
        "noise_count": int(cupy.sum(labels_dev == NOISE_CLUSTER_ID).item()),
        "core_count": int(cupy.sum(core_flags_dev != 0).item()),
        "size_histogram": dict(sorted(size_histogram.items(), key=lambda item: int(item[0]))),
        "min_size": min_size,
        "max_size": max_size,
        "aggregation_backend": aggregation_backend,
        "materialized_python_rows": False,
    }


def _host_numpy_from_partner_column(column, partner: str):
    import numpy as np

    if partner == "numba":
        host = column.copy_to_host()
        return np.asarray(host.tolist() if hasattr(host, "tolist") else host)
    if partner == "cupy":
        import cupy

        return cupy.asnumpy(column)
    if partner == "torch":
        return np.asarray(column.detach().cpu())
    raise ValueError("partner must be 'torch', 'cupy', or 'numba'")


def _component_signature_from_partner_columns(columns: dict[str, object], partner: str) -> dict[str, object]:
    labels_column = columns["component_labels"]
    core_column = columns["is_core"]
    if partner == "cupy":
        import cupy

        return _component_signature_from_cupy_arrays(
            cupy.asarray(labels_column),
            cupy.asarray(core_column),
            aggregation_backend="cupy_device_unique",
        )
    if partner == "numba":
        try:
            import cupy

            return _component_signature_from_cupy_arrays(
                cupy.asarray(labels_column),
                cupy.asarray(core_column),
                aggregation_backend="numba_device_columns_via_cupy_cuda_array_interface",
            )
        except Exception as exc:
            signature = _component_signature_from_numpy_arrays(
                _host_numpy_from_partner_column(labels_column, partner),
                _host_numpy_from_partner_column(core_column, partner),
                aggregation_backend="numba_host_numpy_compact_fallback",
            )
            signature["aggregation_fallback_reason"] = type(exc).__name__
            return signature
    raise ValueError("partner must be 'cupy' or 'numba'")


def _component_signature_matches(actual: dict[str, object] | None, expected: dict[str, object] | None) -> bool:
    if actual is None or expected is None:
        return False
    comparable_fields = (
        "point_count",
        "cluster_count",
        "clustered_point_count",
        "noise_count",
        "core_count",
        "size_histogram",
        "min_size",
        "max_size",
    )
    return all(actual.get(field) == expected.get(field) for field in comparable_fields)


def _points_to_3d_rows(points: tuple[rt.Point, ...]) -> tuple[rt.Point3D, ...]:
    return tuple(rt.Point3D(id=point.id, x=point.x, y=point.y, z=0.0) for point in points)


def _densify_cluster_labels(rows: Iterable[dict[str, object]]) -> tuple[dict[str, object], ...]:
    dense_by_original: dict[int, int] = {}
    next_cluster_id = 1
    dense_rows: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: int(item["point_id"])):
        original_label = int(row["cluster_id"])
        dense_label = original_label
        if original_label != NOISE_CLUSTER_ID:
            if original_label not in dense_by_original:
                dense_by_original[original_label] = next_cluster_id
                next_cluster_id += 1
            dense_label = dense_by_original[original_label]
        dense_rows.append(
            {
                "point_id": int(row["point_id"]),
                "cluster_id": int(dense_label),
                "is_core": bool(row["is_core"]),
                "neighbor_count": int(row["neighbor_count"]),
            }
        )
    return tuple(dense_rows)


def _run_optix_grouped_stream_clusters(
    points: tuple[rt.Point, ...],
    *,
    partner: str,
    query_repeat: int = 1,
    warmup: int = 0,
    grouped_union_query_block_size: int | None = None,
    output_mode: str = "full",
) -> tuple[tuple[dict[str, object], ...], dict[str, object] | None, dict[str, object]]:
    if partner not in {"cupy", "numba"}:
        raise ValueError("optix_grouped_stream_components requires partner='cupy' or partner='numba'")
    if output_mode not in {"full", "component_signature"}:
        raise ValueError("optix_grouped_stream_components supports output_mode='full' or 'component_signature'")
    if int(query_repeat) < 1:
        raise ValueError("query_repeat must be at least 1")
    if int(warmup) < 0:
        raise ValueError("warmup must be non-negative")

    point_rows_3d = _points_to_3d_rows(points)
    prepare_start = time.perf_counter()
    measured_runs: list[dict[str, object]] = []
    last_result: dict[str, object] | None = None
    with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        point_rows_3d,
        radius=EPSILON,
        component_threshold=MIN_POINTS,
        backend="optix",
        partner=partner,
        strategy="grouped_stream",
        grouped_union_query_block_size=grouped_union_query_block_size,
    ) as prepared:
        prepare_sec = time.perf_counter() - prepare_start
        total_runs = int(warmup) + int(query_repeat)
        for iteration in range(total_runs):
            run_start = time.perf_counter()
            result = rt.fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=MIN_POINTS,
                return_metadata=True,
            )
            elapsed = time.perf_counter() - run_start
            last_result = result
            if iteration >= int(warmup):
                measured_runs.append(
                    {
                        "iteration": iteration - int(warmup),
                        "elapsed_sec": elapsed,
                        "metadata": dict(result["metadata"]),
                    }
                )
    if last_result is None or not measured_runs:
        raise RuntimeError("OptiX grouped-stream DBSCAN route produced no measured component-label run")

    materialize_start = time.perf_counter()
    columns = last_result["columns"]
    component_signature: dict[str, object] | None = None
    if output_mode == "component_signature":
        rows = ()
        component_signature = _component_signature_from_partner_columns(columns, partner)
    else:
        point_ids = _partner_column_to_list(columns["point_ids"], partner)
        labels = _partner_column_to_list(columns["component_labels"], partner)
        core_flags = _partner_column_to_list(columns["is_core"], partner)
        neighbor_counts = _partner_column_to_list(columns["neighbor_counts"], partner)
        rows = _densify_cluster_labels(
            {
                "point_id": int(point_id),
                "cluster_id": int(cluster_id),
                "is_core": bool(is_core),
                "neighbor_count": int(neighbor_count),
            }
            for point_id, cluster_id, is_core, neighbor_count in zip(
                point_ids,
                labels,
                core_flags,
                neighbor_counts,
            )
        )
    materialize_sec = time.perf_counter() - materialize_start
    elapsed_samples = tuple(float(row["elapsed_sec"]) for row in measured_runs)
    metadata = dict(last_result["metadata"])
    metadata.update(
        {
            "adapter": "dbscan_app_optix_grouped_stream_component_labels",
            "app_contract": "dbscan_cluster_rows_from_generic_fixed_radius_graph_components_2d_lifted_to_3d",
            "app_specific_native_engine_logic_allowed": False,
            "automatic_partner_selection_authorized": False,
            "backend": "optix",
            "partner": partner,
            "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
            "front_door_operation": "fixed_radius_graph_component_labels_3d",
            "output_mode": output_mode,
            "native_execution_path": metadata.get("native_execution_path", "prepared_rt_core_grouped_union_3d_self_query"),
            "native_engine_summary_contract": metadata.get(
                "native_engine_row_contract",
                "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
            ),
            "partner_reference_contract": metadata.get(
                "partner_reference_contract",
                f"generic_prepared_optix_{partner}_grouped_stream_component_labels_3d",
            ),
            "prepare_sec": prepare_sec,
            "hot_component_label_elapsed_sec_median": statistics.median(elapsed_samples),
            "hot_component_label_elapsed_sec_min": min(elapsed_samples),
            "hot_component_label_elapsed_sec_max": max(elapsed_samples),
            "prepared_query_repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_iterations": len(measured_runs),
            },
            "device_result_materialization_after_hot_window": True,
            "post_window_row_materialization_sec": materialize_sec if output_mode == "full" else None,
            "post_window_component_signature_sec": materialize_sec if output_mode == "component_signature" else None,
            "component_signature_after_hot_window": output_mode == "component_signature",
            "signature_aggregation_backend": (
                component_signature.get("aggregation_backend") if component_signature is not None else None
            ),
            "signature_materializes_python_rows": (
                component_signature.get("materialized_python_rows") if component_signature is not None else None
            ),
            "materializes_python_rows": output_mode == "full",
            "host_row_materialization_before_consumer": False,
            "materializes_neighbor_rows": False,
            "materializes_directed_adjacency_stream": False,
            "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", True)),
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "boundary": (
                "DBSCAN app bridge over the generic OptiX fixed-radius graph component "
                "front door; DBSCAN naming, 2D-to-3D lifting, label densification, and "
                "validation remain app logic."
            ),
        }
    )
    return rows, component_signature, metadata


def _run_partner_exact_clusters(
    points: tuple[rt.Point, ...],
    *,
    partner: str,
    spatial_bucket: bool = False,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    if partner not in {"torch", "cupy"}:
        raise ValueError("partner exact-cluster reference paths require partner='torch' or partner='cupy'")
    point_columns = rt.point_rows_to_partner_columns(points, partner=partner)
    adapter = (
        rt.radius_graph_components_2d_spatial_bucket_partner_columns
        if spatial_bucket
        else rt.radius_graph_components_2d_partner_columns
    )
    result = adapter(
        point_columns,
        radius=EPSILON,
        min_neighbors=MIN_POINTS,
        partner=partner,
        return_metadata=True,
    )
    columns = result["columns"]
    point_ids = _partner_column_to_list(columns["point_ids"], partner)
    labels = _partner_column_to_list(columns["component_labels"], partner)
    core_flags = _partner_column_to_list(columns["is_core"], partner)
    neighbor_counts = _partner_column_to_list(columns["neighbor_counts"], partner)
    rows = tuple(
        {
            "point_id": int(point_id),
            "cluster_id": int(cluster_id),
            "is_core": bool(is_core),
            "neighbor_count": int(neighbor_count),
        }
        for point_id, cluster_id, is_core, neighbor_count in zip(
            point_ids,
            labels,
            core_flags,
            neighbor_counts,
        )
    )
    return tuple(sorted(rows, key=lambda row: int(row["point_id"]))), result["metadata"]


def _native_continuation_backend(
    backend: str,
    *,
    output_mode: str,
    optix_summary_mode: str,
    embree_summary_mode: str,
) -> str:
    if backend == "optix" and (
        output_mode in {"core_flags", "core_count"}
        or optix_summary_mode in {"rt_core_flags", "rt_core_flags_prepared"}
    ):
        return "optix_threshold_count"
    if backend == "embree" and (
        output_mode == "core_flags" or embree_summary_mode in {"rt_core_flags", "rt_core_flags_prepared"}
    ):
        return "embree_threshold_count"
    if backend == "optix_grouped_stream_components":
        return "optix_grouped_stream_component_labels"
    return "none"


def _cluster_sizes(cluster_rows: tuple[dict[str, object], ...]) -> dict[int, int]:
    sizes: dict[int, int] = {}
    for row in cluster_rows:
        cluster_id = int(row["cluster_id"])
        if cluster_id == NOISE_CLUSTER_ID:
            continue
        sizes[cluster_id] = sizes.get(cluster_id, 0) + 1
    return dict(sorted(sizes.items()))


class PreparedDbscanCoreFlagSession:
    def __init__(self, backend: str = "optix", *, copies: int = 1):
        if backend != "optix":
            raise ValueError("PreparedDbscanCoreFlagSession currently supports backend='optix'")
        self.backend = backend
        self.copies = copies
        self.case = make_dbscan_case(copies=copies)
        self._prepared = rt.prepare_generic_fixed_radius_count_threshold_2d(
            search_points=self.case["points"],
            backend="optix",
            max_radius=EPSILON,
            prepare_scene=rt.prepare_optix_fixed_radius_count_threshold_2d,
        )
        self._closed = False

    def run(self, *, output_mode: str = "core_flags") -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared DBSCAN core-flag session is closed")
        if output_mode not in {"core_flags", "core_count"}:
            raise ValueError("prepared DBSCAN core-flag session currently supports output_mode='core_flags' or 'core_count'")
        if output_mode == "core_count":
            result = self._prepared.count_threshold_reached(
                self.case["points"],
                radius=EPSILON,
                threshold=MIN_POINTS,
            )
            core_count = int(result["threshold_reached_count"])
            oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=self.copies)
            oracle_core_count = sum(1 for row in oracle_core_flag_rows if bool(row["is_core"]))
            return {
                "app": "dbscan_clustering",
                "backend": self.backend,
                "execution_mode": "prepared_session",
                "output_mode": output_mode,
                "optix_summary_mode": "rt_core_flags_prepared",
                "embree_summary_mode": "not_applicable",
                "epsilon": EPSILON,
                "min_points": MIN_POINTS,
                "k_max": K_MAX,
                "copies": self.copies,
                "point_count": len(self.case["points"]),
                "threshold_reached_count": core_count,
                "core_count": core_count,
                "oracle_core_count": oracle_core_count,
                "neighbor_row_count": 0,
                "cluster_rows": (),
                "cluster_sizes": {},
                "core_flag_rows": (),
                "native_continuation_active": True,
                "native_continuation_backend": "optix_threshold_count",
                "noise_point_ids": (),
                "oracle_cluster_rows": (),
                "oracle_core_flag_rows": (),
                "matches_oracle": int(core_count) == oracle_core_count,
                "summary_mode": "scalar_threshold_count",
                "generic_primitive": result["primitive"],
                "summary_primitive": result["summary_primitive"],
                "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits only scalar DBSCAN core counts; point identities and cluster expansion remain outside this scalar mode.",
                "boundary": "Prepared OptiX core_count covers the RT-heavy fixed-radius core predicate count only. Use core_flags when per-point core labels are required; full DBSCAN cluster expansion remains Python-side.",
            }
        result = self._prepared.run(
            self.case["points"],
            radius=EPSILON,
            threshold=MIN_POINTS,
        )
        core_flag_rows = _core_flag_rows_from_count_rows(self.case["points"], result["rows"])
        oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=self.copies)
        core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
        oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_core_flag_rows]
        return {
            "app": "dbscan_clustering",
            "backend": self.backend,
            "execution_mode": "prepared_session",
            "output_mode": output_mode,
            "optix_summary_mode": "rt_core_flags_prepared",
            "embree_summary_mode": "not_applicable",
            "epsilon": EPSILON,
            "min_points": MIN_POINTS,
            "k_max": K_MAX,
            "copies": self.copies,
            "point_count": len(self.case["points"]),
            "neighbor_row_count": 0,
            "cluster_rows": (),
            "cluster_sizes": {},
            "core_flag_rows": core_flag_rows,
            "native_continuation_active": True,
            "native_continuation_backend": "optix_threshold_count",
            "noise_point_ids": (),
            "oracle_cluster_rows": (),
            "oracle_core_flag_rows": oracle_core_flag_rows,
            "matches_oracle": core_flags == oracle_core_flags,
            "generic_primitive": result["primitive"],
            "summary_primitive": result["summary_primitive"],
            "rtdl_role": "Prepared OptiX reuses the fixed-radius count-threshold RT traversal scene and emits compact DBSCAN core flags without materializing neighbor rows; Python clustering expansion remains outside this prepared summary path.",
            "boundary": "Prepared OptiX core flags cover the RT-heavy fixed-radius density predicate only. Full DBSCAN cluster expansion remains Python-side and is not claimed as a backend primitive.",
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._prepared.close()

    def __enter__(self) -> "PreparedDbscanCoreFlagSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_session(backend: str = "optix", *, copies: int = 1) -> PreparedDbscanCoreFlagSession:
    return PreparedDbscanCoreFlagSession(backend, copies=copies)


def run_app(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    optix_summary_mode: str = "rows",
    embree_summary_mode: str = "rows",
    output_mode: str = "full",
    partner: str = "cupy",
    skip_validation: bool = False,
    query_repeat: int = 1,
    warmup: int = 0,
    grouped_union_query_block_size: int | None = None,
) -> dict[str, object]:
    if optix_summary_mode not in {"rows", "rt_core_flags", "rt_core_flags_prepared"}:
        raise ValueError("optix_summary_mode must be 'rows', 'rt_core_flags', or 'rt_core_flags_prepared'")
    if embree_summary_mode not in {"rows", "rt_core_flags", "rt_core_flags_prepared"}:
        raise ValueError("embree_summary_mode must be 'rows', 'rt_core_flags', or 'rt_core_flags_prepared'")
    if output_mode not in {"full", "core_flags", "core_count", "component_signature"}:
        raise ValueError("output_mode must be 'full', 'core_flags', 'core_count', or 'component_signature'")
    case = make_dbscan_case(copies=copies)
    points = case["points"]
    core_flag_rows: tuple[dict[str, object], ...] = ()
    scalar_core_count: dict[str, int | str | None] | None = None
    component_signature: dict[str, object] | None = None
    oracle_component_signature: dict[str, object] | None = None
    partner_metadata: dict[str, object] | None = None
    if backend == "optix_grouped_stream_components":
        if output_mode not in {"full", "component_signature"}:
            raise ValueError(
                "optix_grouped_stream_components currently supports output_mode='full' "
                "or 'component_signature'"
            )
        neighbor_rows = ()
        cluster_rows, component_signature, partner_metadata = _run_optix_grouped_stream_clusters(
            points,
            partner=partner,
            query_repeat=query_repeat,
            warmup=warmup,
            grouped_union_query_block_size=grouped_union_query_block_size,
            output_mode=output_mode,
        )
    elif backend in {"partner_exact_clusters", "partner_spatial_exact_clusters"}:
        neighbor_rows = ()
        cluster_rows, partner_metadata = _run_partner_exact_clusters(
            points,
            partner=partner,
            spatial_bucket=backend == "partner_spatial_exact_clusters",
        )
    elif output_mode == "core_count" and backend == "optix":
        neighbor_rows = ()
        cluster_rows = ()
        scalar_core_count = _run_optix_prepared_core_count(case)
    elif output_mode == "core_count" and backend == "scipy":
        neighbor_rows = ()
        cluster_rows = ()
        scalar_core_count = _run_scipy_core_count(case)
    elif output_mode == "core_count":
        neighbor_rows = ()
        cluster_rows = ()
        oracle_scalar_rows = expected_tiled_core_flag_rows(copies=copies)
        oracle_core_count_for_scalar = sum(1 for row in oracle_scalar_rows if bool(row["is_core"]))
        scalar_core_count = {
            "point_count": len(points),
            "threshold_reached_count": oracle_core_count_for_scalar,
            "core_count": oracle_core_count_for_scalar,
            "row_count": None,
            "summary_mode": "scalar_threshold_count_oracle",
        }
    elif output_mode == "component_signature":
        raise ValueError("output_mode='component_signature' is currently supported only by optix_grouped_stream_components")
    elif output_mode == "core_flags" and backend == "embree":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_prepared_core_flag_summary(case)
    elif output_mode == "core_flags" and backend == "optix":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_core_flag_summary(case)
    elif output_mode == "core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = expected_tiled_core_flag_rows(copies=copies)
    elif backend == "optix" and optix_summary_mode == "rt_core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_core_flag_summary(case)
    elif backend == "optix" and optix_summary_mode == "rt_core_flags_prepared":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_optix_prepared_core_flag_summary(case)
    elif backend == "embree" and embree_summary_mode == "rt_core_flags":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_core_flag_summary(case)
    elif backend == "embree" and embree_summary_mode == "rt_core_flags_prepared":
        neighbor_rows = ()
        cluster_rows = ()
        core_flag_rows = _run_embree_prepared_core_flag_summary(case)
    else:
        neighbor_rows = _run_rows(backend, case)
        cluster_rows = cluster_from_neighbor_rows(points, neighbor_rows)
    validation_skipped = skip_validation and backend in {
        "optix_grouped_stream_components",
        "partner_exact_clusters",
        "partner_spatial_exact_clusters",
    }
    if validation_skipped:
        oracle_rows = ()
        oracle_core_flag_rows = ()
    elif backend == "optix_grouped_stream_components" and output_mode == "component_signature":
        oracle_rows = ()
        oracle_core_flag_rows = ()
        oracle_component_signature = expected_tiled_component_signature(copies=copies)
    elif backend == "optix_grouped_stream_components":
        oracle_rows = expected_tiled_cluster_rows(copies=copies)
        oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=copies)
    elif output_mode in {"core_flags", "core_count"} or core_flag_rows:
        oracle_rows = ()
        oracle_core_flag_rows = expected_tiled_core_flag_rows(copies=copies)
    else:
        oracle_rows = brute_force_dbscan(points)
        oracle_core_flag_rows = brute_force_core_flag_rows(points)
    if component_signature is not None and oracle_component_signature is not None:
        matches_oracle = _component_signature_matches(component_signature, oracle_component_signature)
    elif scalar_core_count is not None:
        oracle_core_count = sum(1 for row in oracle_core_flag_rows if bool(row["is_core"]))
        matches_oracle = int(scalar_core_count["core_count"]) == oracle_core_count
    elif core_flag_rows:
        core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in core_flag_rows]
        oracle_core_flags = [(int(row["point_id"]), bool(row["is_core"])) for row in oracle_core_flag_rows]
        matches_oracle = core_flags == oracle_core_flags
    elif validation_skipped:
        matches_oracle = None
    else:
        matches_oracle = cluster_rows == oracle_rows
    native_continuation_backend = _native_continuation_backend(
        backend,
        output_mode=output_mode,
        optix_summary_mode=optix_summary_mode,
        embree_summary_mode=embree_summary_mode,
    )

    cluster_sizes = _cluster_sizes(cluster_rows)
    noise_point_ids = [
        int(row["point_id"]) for row in cluster_rows if int(row["cluster_id"]) == NOISE_CLUSTER_ID
    ]
    core_count = (
        int(component_signature["core_count"])
        if component_signature is not None
        else int(scalar_core_count["core_count"])
        if scalar_core_count is not None
        else sum(1 for row in core_flag_rows if bool(row.get("is_core", False)))
        if core_flag_rows
        else sum(1 for row in cluster_rows if bool(row.get("is_core", False)))
    )
    oracle_core_count = (
        int(oracle_component_signature["core_count"])
        if oracle_component_signature is not None
        else sum(1 for row in oracle_core_flag_rows if bool(row.get("is_core", False)))
    )

    return {
        "app": "dbscan_clustering",
        "backend": backend,
        "output_mode": output_mode,
        "optix_summary_mode": optix_summary_mode if backend == "optix" else "not_applicable",
        "embree_summary_mode": embree_summary_mode if backend == "embree" else "not_applicable",
        "partner": (
            partner
            if backend
            in {"optix_grouped_stream_components", "partner_exact_clusters", "partner_spatial_exact_clusters"}
            else None
        ),
        "epsilon": EPSILON,
        "min_points": MIN_POINTS,
        "k_max": K_MAX,
        "copies": copies,
        "point_count": len(points),
        "neighbor_row_count": len(neighbor_rows),
        "cluster_rows": cluster_rows,
        "cluster_sizes": cluster_sizes,
        "component_signature": component_signature,
        "oracle_component_signature": oracle_component_signature,
        "core_flag_rows": core_flag_rows,
        "threshold_reached_count": (
            int(scalar_core_count["threshold_reached_count"]) if scalar_core_count is not None else None
        ),
        "core_count": core_count,
        "native_continuation_active": native_continuation_backend != "none",
        "native_continuation_backend": native_continuation_backend,
        "noise_point_ids": noise_point_ids,
        "noise_count": (
            int(component_signature["noise_count"]) if component_signature is not None else len(noise_point_ids)
        ),
        "oracle_cluster_rows": oracle_rows,
        "oracle_core_flag_rows": oracle_core_flag_rows,
        "oracle_core_count": oracle_core_count,
        "validation_skipped": validation_skipped,
        "summary_mode": scalar_core_count["summary_mode"] if scalar_core_count is not None else None,
        "generic_primitive": (
            scalar_core_count.get("generic_primitive") if scalar_core_count is not None else None
        ),
        "summary_primitive": (
            scalar_core_count.get("summary_primitive") if scalar_core_count is not None else None
        ),
        "partner_reference_contract": (
            partner_metadata["partner_reference_contract"] if partner_metadata else None
        ),
        "partner_metadata": partner_metadata,
        "matches_oracle": matches_oracle,
        "rtdl_role": "Default RTDL emits fixed-radius neighbor rows; rt.reduce_rows(count) identifies core candidates for Python cluster expansion. The optix_grouped_stream_components path uses the generic fixed-radius graph component front door with explicit CuPy or Numba partner continuation for full rows or compact component signatures.",
        "boundary": "Bounded app-level DBSCAN demo only. The default rows/core predicate prototype still does not yet expose clustering expansion as a native engine primitive. The grouped-stream path is a generic fixed-radius graph component route, not a DBSCAN-specific native engine ABI, automatic partner choice, public speedup claim, or true-zero-copy claim. The spatial-bucket path uses a host-built sparse bucket index as an explicit transitional debt.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived DBSCAN app: RTDL neighbor rows plus Python density-cluster expansion."
    )
    parser.add_argument(
        "--backend",
        choices=(
            "cpu_python_reference",
            "cpu",
            "embree",
            "optix",
            "vulkan",
            "scipy",
            "optix_grouped_stream_components",
            "partner_exact_clusters",
            "partner_spatial_exact_clusters",
        ),
        default="cpu_python_reference",
    )
    parser.add_argument("--partner", choices=("torch", "cupy", "numba"), default="cupy")
    parser.add_argument("--copies", type=int, default=1, help="tile the authored clustering fixture")
    parser.add_argument(
        "--output-mode",
        choices=("full", "core_flags", "core_count", "component_signature"),
        default="full",
        help=(
            "full emits neighbor/cluster rows; core_flags emits compact DBSCAN core predicates; "
            "core_count emits only scalar core counts; component_signature emits compact grouped-stream "
            "cluster-size aggregates"
        ),
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "rt_core_flags", "rt_core_flags_prepared"),
        default="rows",
        help="when backend=optix, use native fixed-radius threshold counts for core flags only; prepared mode reuses an OptiX BVH handle inside the run",
    )
    parser.add_argument(
        "--embree-summary-mode",
        choices=("rows", "rt_core_flags", "rt_core_flags_prepared"),
        default="rows",
        help="when backend=embree, use native fixed-radius threshold counts for core flags only; prepared mode reuses an Embree BVH handle inside the run",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="For partner exact-cluster timing rows, skip the O(n^2) Python oracle after separate validation has been recorded.",
    )
    parser.add_argument("--query-repeat", type=int, default=1, help="measured prepared grouped-stream repeats")
    parser.add_argument("--warmup", type=int, default=0, help="unmeasured prepared grouped-stream warmup repeats")
    parser.add_argument("--grouped-union-query-block-size", type=int, default=None)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                copies=args.copies,
                optix_summary_mode=args.optix_summary_mode,
                embree_summary_mode=args.embree_summary_mode,
                output_mode=args.output_mode,
                partner=args.partner,
                skip_validation=args.skip_validation,
                query_repeat=args.query_repeat,
                warmup=args.warmup,
                grouped_union_query_block_size=args.grouped_union_query_block_size,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
