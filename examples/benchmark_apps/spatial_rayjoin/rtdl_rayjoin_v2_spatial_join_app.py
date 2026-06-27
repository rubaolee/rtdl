from __future__ import annotations

import argparse
import contextlib
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.benchmark_apps._support.rtdl_language_reference import county_soil_overlay_reference
from examples.benchmark_apps._support.rtdl_language_reference import county_zip_join_reference
from rtdsl.baseline_runner import DatasetCase
from rtdsl.baseline_runner import load_representative_case
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_probe_points
from rtdsl.datasets import chains_to_segment_columns
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import chains_to_topology_rows
from rtdsl.datasets import load_cdb
from rtdsl.v3_0_topology_stream_accounting import build_topology_stream_m3_phase_table
from rtdsl.v3_0_topology_stream_accounting import build_topology_stream_prepared_handle_metadata


_WORKLOADS = ("pip", "lsi", "overlay_seed")
_PREPARED_OPTIX_WORKLOADS = ("pip", "lsi", "overlay_seed")
_PIP_BOUNDARY_EVENT_COUNT_MODE = "boundary_event_point_id_count_device_columns"
_PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE = "relation_status_corrected_executor_validated"
_PIP_COUNT_MODES = (
    "exact",
    "exact_prepared_points",
    "exact_prepared_points_executor",
    _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE,
    "device_filtered_validated",
    "device_filtered_prepared_points_validated",
    "point_id_count_device_columns_validated",
    _PIP_BOUNDARY_EVENT_COUNT_MODE,
)
_PIP_POSITIVE_COUNT_MODES = (
    "device_filtered_validated",
    "device_filtered_prepared_points_validated",
    "point_id_count_device_columns_validated",
)
_PIP_DEVICE_FILTER_BOUNDARY_MODES = ("inclusive", "crossing_only")
_PIP_POINT_ORDER_MODES = ("natural", "x_then_y", "y_then_x", "morton_xy")
_LSI_SEGMENT_ORDER_MODES = ("natural", "x_then_y", "y_then_x", "morton_xy")
RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION = "rtdl.rayjoin.v2_6.numba_compact_mask_preview.v1"

_DEFAULT_DATASETS = {
    "pip": "tests/fixtures/rayjoin/br_county_subset.cdb",
    "lsi": "tests/fixtures/rayjoin/br_county_subset.cdb",
    "overlay_seed": "tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
}


@rt.kernel(backend="rtdl", precision="float_approx")
def rayjoin_point_location_positive_hits_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(
            exact=False,
            boundary_mode="inclusive",
            result_mode="positive_hits",
        ),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


_KERNELS = {
    "pip": rayjoin_point_location_positive_hits_reference,
    "lsi": county_zip_join_reference,
    "overlay_seed": county_soil_overlay_reference,
}

_BASELINE_WORKLOAD = {
    "pip": "pip",
    "lsi": "lsi",
    "overlay_seed": "overlay",
}


def _resolve_dataset_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def _split_dataset_paths(dataset: str) -> tuple[Path, ...]:
    return tuple(_resolve_dataset_path(part.strip()) for part in dataset.split("+") if part.strip())


def _load_external_cdb_case(
    workload: str,
    dataset: str,
    *,
    segment_column_inputs: bool = False,
) -> DatasetCase:
    paths = _split_dataset_paths(dataset)
    if workload == "pip":
        if len(paths) == 1:
            point_dataset = polygon_dataset = load_cdb(paths[0])
            note = "External CDB point-location case using probe points and polygons from one file."
        elif len(paths) == 2:
            point_dataset = load_cdb(paths[0])
            polygon_dataset = load_cdb(paths[1])
            note = "External CDB point-location case using points from the left file and polygons from the right file."
        else:
            raise ValueError("external PIP dataset must be `path.cdb` or `points.cdb + polygons.cdb`")
        return DatasetCase(
            workload="pip",
            dataset=dataset,
            inputs={
                "points": chains_to_probe_points(point_dataset),
                "polygons": chains_to_polygons(polygon_dataset),
            },
            note=note,
        )
    if workload == "lsi":
        if len(paths) != 2:
            raise ValueError("external LSI dataset must be `left.cdb + right.cdb`")
        left = load_cdb(paths[0])
        right = load_cdb(paths[1])
        if segment_column_inputs:
            return DatasetCase(
                workload="lsi",
                dataset=dataset,
                inputs={
                    "left": chains_to_segment_columns(left),
                    "right": chains_to_segment_columns(right),
                },
                note=(
                    "External CDB line-segment intersection case using direct generic "
                    "segment columns from left/right chain edges."
                ),
            )
        return DatasetCase(
            workload="lsi",
            dataset=dataset,
            inputs={
                "left": segments_from_records(chains_to_segments(left)),
                "right": segments_from_records(chains_to_segments(right)),
            },
            note="External CDB line-segment intersection case using left/right chain segments.",
        )
    if workload == "overlay_seed":
        if len(paths) != 2:
            raise ValueError("external overlay_seed dataset must be `left.cdb + right.cdb`")
        left = load_cdb(paths[0])
        right = load_cdb(paths[1])
        return DatasetCase(
            workload="overlay",
            dataset=dataset,
            inputs={
                "left": chains_to_polygons(left),
                "right": chains_to_polygons(right),
            },
            note="External CDB overlay pair-dependency case using left/right polygon chains.",
        )
    raise ValueError("workload must be one of: pip, lsi, overlay_seed")


def _load_rayjoin_case(workload: str, dataset: str, *, segment_column_inputs: bool = False) -> DatasetCase:
    baseline_workload = _BASELINE_WORKLOAD[workload]
    try:
        return load_representative_case(baseline_workload, dataset)
    except ValueError:
        paths = _split_dataset_paths(dataset)
        if paths and all(path.exists() for path in paths):
            return _load_external_cdb_case(
                workload,
                dataset,
                segment_column_inputs=segment_column_inputs,
            )
        raise


def _run_backend(kernel, backend: str, inputs: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(kernel, **inputs)
    if backend == "cpu":
        return rt.run_cpu(kernel, **inputs)
    if backend == "embree":
        return rt.run_embree(kernel, **inputs)
    if backend == "optix":
        return rt.run_optix(kernel, **inputs)
    raise ValueError("backend must be one of: cpu_python_reference, cpu, embree, optix")


def _positive_pip_assignments(rows: tuple[dict[str, object], ...]) -> tuple[dict[str, int], ...]:
    return tuple(
        {
            "point_id": int(row["point_id"]),
            "polygon_id": int(row["polygon_id"]),
        }
        for row in rows
        if int(row["contains"]) == 1
    )


def _summarize_rows(workload: str, rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    if workload == "pip":
        positives = _positive_pip_assignments(rows)
        return {
            "positive_hit_row_count": len(rows),
            "positive_assignment_count": len(positives),
            "positive_assignments": positives,
            "output_contract": "point_to_polygon_positive_hit_rows",
        }
    if workload == "lsi":
        return {
            "intersection_count": len(rows),
            "output_contract": "segment_segment_intersection_rows",
        }
    active_seed_pairs = tuple(
        {
            "left_polygon_id": int(row["left_polygon_id"]),
            "right_polygon_id": int(row["right_polygon_id"]),
            "requires_lsi": int(row["requires_lsi"]),
            "requires_pip": int(row["requires_pip"]),
        }
        for row in rows
        if int(row["requires_lsi"]) == 1 or int(row["requires_pip"]) == 1
    )
    return {
        "pair_dependency_row_count": len(rows),
        "active_seed_count": len(active_seed_pairs),
        "active_seed_pairs": active_seed_pairs,
        "output_contract": "overlay_pair_dependency_rows_with_lsi_pip_flags",
    }


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def _count_input_records(value: object) -> int:
    count_attr = getattr(value, "count", None)
    if count_attr is not None and not callable(count_attr):
        return int(count_attr)
    try:
        return len(value)  # type: ignore[arg-type]
    except TypeError:
        return 1


def _topology_stream_query_count(workload: str, inputs: dict[str, object]) -> int:
    if workload == "pip":
        return _count_input_records(inputs["points"])
    if workload == "lsi":
        return _count_input_records(inputs["left"])
    return _count_input_records(inputs["left"])


def _topology_stream_runtime_query_count(
    *,
    workload: str,
    inputs: dict[str, object],
    prepared_point_columns_metadata: dict[str, object] | None = None,
    packed_query_stream: object | None = None,
) -> int:
    if prepared_point_columns_metadata is not None and "point_count" in prepared_point_columns_metadata:
        return int(prepared_point_columns_metadata["point_count"])
    if packed_query_stream is not None:
        return _count_input_records(packed_query_stream)
    return _topology_stream_query_count(workload, inputs)


def _phase_time(phases: dict[str, float], label: str, fn):
    start = time.perf_counter()
    value = fn()
    phases[label] = time.perf_counter() - start
    return value


def _phase_repeat_time(
    phases: dict[str, float],
    label: str,
    *,
    query_repeat: int,
    warmup: int,
    fn,
    stability_value=None,
):
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    runs = []
    for iteration in range(warmup + query_repeat):
        start = time.perf_counter()
        value = fn()
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": iteration < warmup,
                "elapsed_sec": time.perf_counter() - start,
                "value": value,
            }
        )
    measured = [row for row in runs if not bool(row["is_warmup"])]
    if not measured:
        raise RuntimeError(f"{label} repeat produced no measured rows")
    if stability_value is not None:
        stable_values = {stability_value(row["value"]) for row in measured}
        if len(stable_values) != 1:
            raise RuntimeError(f"{label} repeat changed result identity")
    elapsed = [float(row["elapsed_sec"]) for row in measured]
    phases[label] = float(statistics.median(elapsed))
    phases[f"{label}_total_sec"] = float(sum(elapsed))
    phases[f"{label}_repeat"] = int(query_repeat)
    phases[f"{label}_warmup"] = int(warmup)
    return measured[-1]["value"]


def _phase_batched_count_executor_repeat_time(
    phases: dict[str, float],
    label: str,
    *,
    query_repeat: int,
    warmup: int,
    batch_request_count: int,
    executor,
    exact_count: int,
) -> int:
    """Time a reusable count executor as a batched repeated-request contract."""

    query_repeat = int(query_repeat)
    warmup = int(warmup)
    batch_request_count = int(batch_request_count)
    if batch_request_count <= 0:
        raise ValueError("batch_request_count must be positive")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if query_repeat % batch_request_count != 0:
        raise ValueError("query_repeat must be divisible by batch_request_count for batch executor timing")
    if warmup % batch_request_count != 0:
        raise ValueError("warmup must be divisible by batch_request_count for batch executor timing")

    warmup_batches = warmup // batch_request_count
    measured_batches = query_repeat // batch_request_count
    per_request_elapsed = []
    total_elapsed = 0.0
    for iteration in range(warmup_batches + measured_batches):
        start = time.perf_counter()
        counts = executor.run()
        elapsed = time.perf_counter() - start
        if any(int(count) != int(exact_count) for count in counts):
            raise RuntimeError(
                "batched device-side closed-shape count did not match exact prepared count: "
                f"{tuple(counts[:5])} != {exact_count}"
            )
        if iteration >= warmup_batches:
            per_request_elapsed.append(elapsed / batch_request_count)
            total_elapsed += elapsed
    if not per_request_elapsed:
        raise RuntimeError(f"{label} batch repeat produced no measured rows")
    phases[label] = float(statistics.median(per_request_elapsed))
    phases[f"{label}_total_sec"] = float(total_elapsed)
    phases[f"{label}_repeat"] = int(query_repeat)
    phases[f"{label}_warmup"] = int(warmup)
    phases[f"{label}_batch_request_count"] = int(batch_request_count)
    phases[f"{label}_batch_count"] = int(measured_batches)
    phases[f"{label}_contract"] = "batched_repeated_request_throughput"
    return int(exact_count)


@contextlib.contextmanager
def _temporary_env(name: str, value: str | None):
    previous = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


def _run_prepared_count_with_boundary_mode(prepared, packed_points, boundary_mode: str | None) -> int:
    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", boundary_mode):
        return int(prepared.count(packed_points))


def _run_prepared_device_filtered_count_with_boundary_mode(
    prepared,
    packed_points,
    boundary_mode: str | None,
) -> int:
    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", boundary_mode):
        return int(prepared.count_device_filtered(packed_points))


def _run_prepared_device_filtered_prepared_points_count_with_boundary_mode(
    prepared,
    prepared_point_columns,
    boundary_mode: str | None,
) -> int:
    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", boundary_mode):
        return int(prepared.count_device_filtered_prepared_points(prepared_point_columns))


def _run_prepared_point_id_count_device_columns_with_boundary_mode(
    prepared,
    packed_points,
    boundary_mode: str | None,
    *,
    group_capacity: int,
) -> tuple[int, dict[str, object]]:
    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", boundary_mode):
        columns = prepared.point_id_count_device_columns(
            packed_points,
            group_capacity=group_capacity,
        )
    try:
        if columns.overflow:
            raise RuntimeError("point-id count device-column continuation overflowed group capacity")
        return int(columns.source_row_count), columns.to_metadata()
    finally:
        columns.close()


def _record_id(record: object) -> int:
    if hasattr(record, "id"):
        return int(getattr(record, "id"))
    if isinstance(record, dict):
        return int(record["id"])
    raise TypeError(f"record does not expose an id field: {record!r}")


def _order_points_for_locality(points, mode: str):
    if mode not in _PIP_POINT_ORDER_MODES:
        raise ValueError("point_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    return rt.spatial_order_points_2d(points, mode)


def _order_segments_for_locality(segments, mode: str):
    if mode not in _LSI_SEGMENT_ORDER_MODES:
        raise ValueError("segment_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    return rt.spatial_order_segments_2d(segments, mode)


def preflight_rayjoin_pip_fast_count_domain(
    *,
    dataset: str | None = None,
    count_mode: str = "device_filtered_prepared_points_validated",
    device_filtered_boundary_mode: str | None = "inclusive",
    point_order_mode: str = "natural",
    query_axis: str | None = None,
    scalar_count_pipeline: bool = True,
    device_predicate_eps: float | None = None,
    require_match: bool = False,
) -> dict[str, Any]:
    """Check whether a PIP dataset is safe for a validated fast count route.

    This is app-level benchmark policy over generic RTDL primitives. It does not
    authorize the native engine to infer RayJoin semantics; it only records
    whether the chosen generic count route matches the exact prepared count for
    the supplied input domain.
    """

    if count_mode not in _PIP_POSITIVE_COUNT_MODES:
        raise ValueError(
            "count_mode must be one of the validated positive PIP count modes: "
            f"{', '.join(_PIP_POSITIVE_COUNT_MODES)}"
        )
    if device_filtered_boundary_mode is not None and device_filtered_boundary_mode not in _PIP_DEVICE_FILTER_BOUNDARY_MODES:
        raise ValueError("device_filtered_boundary_mode must be 'inclusive' or 'crossing_only'")
    if point_order_mode not in _PIP_POINT_ORDER_MODES:
        raise ValueError("point_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    if device_predicate_eps is not None and float(device_predicate_eps) < 0.0:
        raise ValueError("device_predicate_eps must be non-negative")

    from rtdsl.optix_runtime import pack_points
    from rtdsl.optix_runtime import pack_polygons
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    resolved_dataset = dataset or _DEFAULT_DATASETS["pip"]
    case = _load_rayjoin_case("pip", resolved_dataset)
    ordered_points = _order_points_for_locality(case.inputs["points"], point_order_mode)
    packed_points = pack_points(records=ordered_points, dimension=2)
    packed_shapes = pack_polygons(records=case.inputs["polygons"])

    point_id_count_metadata: dict[str, object] | None = None
    prepared_point_columns_metadata: dict[str, object] | None = None
    prepared_point_columns = None

    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", query_axis), _temporary_env(
        "RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE",
        "1" if scalar_count_pipeline else None,
    ), _temporary_env(
        "RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS",
        None if device_predicate_eps is None else f"{float(device_predicate_eps):.17g}",
    ):
        prepared = prepare_point_closed_shape_membership_2d_optix(packed_shapes)
        try:
            exact_count = _run_prepared_count_with_boundary_mode(prepared, packed_points, None)
            if count_mode == "device_filtered_validated":
                fast_count = _run_prepared_device_filtered_count_with_boundary_mode(
                    prepared,
                    packed_points,
                    device_filtered_boundary_mode,
                )
            elif count_mode == "device_filtered_prepared_points_validated":
                prepared_point_columns = prepared.prepare_point_probe_columns(packed_points)
                prepared_point_columns_metadata = prepared_point_columns.to_metadata()
                fast_count = _run_prepared_device_filtered_prepared_points_count_with_boundary_mode(
                    prepared,
                    prepared_point_columns,
                    device_filtered_boundary_mode,
                )
            else:
                point_id_group_capacity = max(
                    1,
                    max(_record_id(point) for point in ordered_points) + 1,
                )
                fast_count, point_id_count_metadata = _run_prepared_point_id_count_device_columns_with_boundary_mode(
                    prepared,
                    packed_points,
                    device_filtered_boundary_mode,
                    group_capacity=point_id_group_capacity,
                )
        finally:
            if prepared_point_columns is not None:
                prepared_point_columns.close()
            prepared.close()

    matches = int(fast_count) == int(exact_count)
    result = {
        "schema": "rtdl.rayjoin.pip_fast_count_domain_preflight.v1",
        "dataset": resolved_dataset,
        "count_mode": count_mode,
        "device_filtered_boundary_mode": device_filtered_boundary_mode,
        "query_axis": query_axis,
        "scalar_count_pipeline": bool(scalar_count_pipeline),
        "device_predicate_eps": None if device_predicate_eps is None else float(device_predicate_eps),
        "point_order_mode": point_order_mode,
        "point_count": int(getattr(packed_points, "count", len(ordered_points))),
        "shape_count": int(getattr(packed_shapes, "polygon_count", len(case.inputs["polygons"]))),
        "exact_count": int(exact_count),
        "fast_count": int(fast_count),
        "matches_exact": matches,
        "status": "validated_fast_route_allowed" if matches else "fast_route_rejected",
        "fallback_required": not matches,
        "fallback_reason": None if matches else "fast count route did not match exact prepared count",
        "prepared_point_probe_columns": prepared_point_columns_metadata,
        "point_id_count_device_columns": point_id_count_metadata,
        "native_engine_boundary": (
            "The engine sees generic point/closed-shape count primitives. "
            "RayJoin CDB topology policy remains in Python preflight/fallback logic."
        ),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }
    if require_match and not matches:
        raise RuntimeError(
            "validated-domain preflight rejected fast PIP count route: "
            f"{fast_count} != {exact_count}"
        )
    return result


def run_rayjoin_prepared_optix_workload(
    workload: str,
    *,
    dataset: str | None = None,
    result_mode: str = "count",
    include_rows: bool = False,
    count_mode: str = "exact",
    device_filtered_boundary_mode: str | None = None,
    point_order_mode: str = "natural",
    segment_order_mode: str = "natural",
    query_repeat: int = 1,
    warmup: int = 0,
    device_filtered_batch_request_count: int | None = None,
    device_filtered_batch_stream_count: int | str | None = None,
    exact_executor_max_candidate_rows: int | None = None,
    prepare_left_for_count: bool = False,
) -> dict[str, object]:
    """Run the RayJoin-style prepared OptiX route with phase boundaries.

    This is the serious v2.8 benchmark route for RayJoin-style PIP, LSI,
    and overlay-seed pair-dependency flags.
    It keeps RayJoin policy in Python while using generic prepared RTDL
    primitives underneath.
    """

    if workload not in _PREPARED_OPTIX_WORKLOADS:
        raise ValueError("prepared_optix route currently supports only: pip, lsi, overlay_seed")
    if result_mode not in {"count", "rows"}:
        raise ValueError("result_mode must be 'count' or 'rows'")
    if count_mode not in _PIP_COUNT_MODES:
        raise ValueError(
            "count_mode must be 'exact', 'exact_prepared_points', 'exact_prepared_points_executor', "
            f"'{_PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE}', "
            "'device_filtered_validated', "
            "'device_filtered_prepared_points_validated', "
            "'point_id_count_device_columns_validated', or "
            f"'{_PIP_BOUNDARY_EVENT_COUNT_MODE}'"
        )
    if count_mode != "exact" and (workload != "pip" or result_mode != "count"):
        raise ValueError("PIP-specific count_mode is only valid for PIP count workloads")
    if device_filtered_boundary_mode is not None:
        if device_filtered_boundary_mode not in _PIP_DEVICE_FILTER_BOUNDARY_MODES:
            raise ValueError("device_filtered_boundary_mode must be 'inclusive' or 'crossing_only'")
        if count_mode not in _PIP_POSITIVE_COUNT_MODES or workload != "pip" or result_mode != "count":
            raise ValueError(
                "device_filtered_boundary_mode is only valid for PIP count workloads "
                "using a validated device-side count mode"
            )
    if point_order_mode not in _PIP_POINT_ORDER_MODES:
        raise ValueError("point_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    if point_order_mode != "natural" and workload != "pip":
        raise ValueError("point_order_mode is currently only valid for PIP closed-shape membership workloads")
    if segment_order_mode not in _LSI_SEGMENT_ORDER_MODES:
        raise ValueError("segment_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    if segment_order_mode != "natural" and workload != "lsi":
        raise ValueError("segment_order_mode is currently only valid for LSI segment-pair workloads")
    if prepare_left_for_count and (workload != "lsi" or result_mode != "count"):
        raise ValueError("prepare_left_for_count is currently only valid for LSI count workloads")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if device_filtered_batch_request_count is not None:
        device_filtered_batch_request_count = int(device_filtered_batch_request_count)
        if device_filtered_batch_request_count <= 0:
            raise ValueError("device_filtered_batch_request_count must be positive")
        if (
            workload != "pip"
            or result_mode != "count"
            or count_mode != "device_filtered_prepared_points_validated"
        ):
            raise ValueError(
                "device_filtered_batch_request_count is only valid for PIP "
                "device_filtered_prepared_points_validated count workloads"
            )
    if isinstance(device_filtered_batch_stream_count, str) and device_filtered_batch_stream_count != "auto":
        raise ValueError("device_filtered_batch_stream_count must be positive, None, or 'auto'")
    if exact_executor_max_candidate_rows is not None:
        exact_executor_max_candidate_rows = int(exact_executor_max_candidate_rows)
        if exact_executor_max_candidate_rows < 0:
            raise ValueError("exact_executor_max_candidate_rows must be non-negative")
        if workload != "pip" or result_mode != "count" or count_mode != "exact_prepared_points_executor":
            raise ValueError(
                "exact_executor_max_candidate_rows is only valid for PIP "
                "exact_prepared_points_executor count workloads"
            )

    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    case = _load_rayjoin_case(
        workload,
        resolved_dataset,
        segment_column_inputs=workload == "lsi",
    )
    phases: dict[str, float] = {}
    rows: tuple[dict[str, object], ...] = ()
    native_phase_timings: dict[str, object] | None = None

    if workload == "overlay_seed":
        from rtdsl.optix_runtime import pack_polygons
        from rtdsl.optix_runtime import prepare_shape_pair_relation_flags_optix

        packed_left = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_polygons(records=case.inputs["left"]),
        )
        packed_right = _phase_time(
            phases,
            "static_shape_pack_sec",
            lambda: pack_polygons(records=case.inputs["right"]),
        )
        prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_shape_pair_relation_flags_optix(packed_right),
        )
        try:
            if result_mode == "count":
                row_count = int(
                    _phase_repeat_time(
                        phases,
                        "prepared_query_sec",
                        query_repeat=query_repeat,
                        warmup=warmup,
                        fn=lambda: prepared.count_active(packed_left),
                    )
                )
            else:
                def run_raw_once():
                    view = prepared.run_raw(packed_left)
                    try:
                        row_count_inner = int(view.row_count)
                        rows_inner = tuple(view.to_dict_rows()) if include_rows else ()
                        return row_count_inner, rows_inner
                    finally:
                        view.close()

                row_count, rows = _phase_repeat_time(
                    phases,
                    "prepared_query_sec",
                    query_repeat=query_repeat,
                    warmup=warmup,
                    fn=run_raw_once,
                    stability_value=lambda value: int(value[0]),
                )
            native_phase_timings = {
                "native_row_count": row_count,
                "native_count_mode": "active_relation_flags" if result_mode == "count" else "full_pair_dependency_rows",
                "prepared_shape_pair_relation": True,
            }
        finally:
            prepared.close()
        summary = {
            (
                "active_seed_count"
                if result_mode == "count"
                else "pair_dependency_row_count"
            ): row_count,
            "output_contract": (
                "overlay_active_pair_dependency_count"
                if result_mode == "count"
                else "overlay_pair_dependency_rows_with_lsi_pip_flags"
            ),
        }
    elif workload == "lsi":
        from rtdsl.optix_runtime import pack_segments
        from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix
        from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix

        packed_left = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_segments(records=case.inputs["left"], order_mode=segment_order_mode),
        )
        packed_right = _phase_time(
            phases,
            "static_segment_pack_sec",
            lambda: pack_segments(records=case.inputs["right"], order_mode=segment_order_mode),
        )
        prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_segment_pair_intersection_optix(packed_right),
        )
        prepared_left = None
        if prepare_left_for_count and result_mode == "count":
            prepared_left = _phase_time(
                phases,
                "prepare_left_set_sec",
                lambda: prepare_segment_pair_left_set_optix(packed_left),
            )
        count_route_metadata = None
        try:
            if result_mode == "count":
                if prepared_left is not None:
                    count_result = _phase_repeat_time(
                        phases,
                        "prepared_query_sec",
                        query_repeat=query_repeat,
                        warmup=warmup,
                        fn=lambda: prepared.count_prepared_left_exact_intersections(prepared_left),
                        stability_value=lambda value: int(value["count"]),
                    )
                    row_count = int(count_result["count"])
                    count_route_metadata = {
                        "front_door_schema": count_result["schema"],
                        "primitive": count_result["primitive"],
                        "output_contract": count_result["output_contract"],
                        "route": count_result["route"],
                        "native_symbol": count_result["native_symbol"],
                        "right_group_count": int(count_result["right_group_count"]),
                        "experimental_front_door": bool(
                            count_result["claim_boundary"]["experimental_front_door"]
                        ),
                        "public_speedup_claim_authorized": bool(
                            count_result["claim_boundary"]["public_speedup_claim_authorized"]
                        ),
                    }
                else:
                    row_count = int(
                        _phase_repeat_time(
                            phases,
                            "prepared_query_sec",
                            query_repeat=query_repeat,
                            warmup=warmup,
                            fn=lambda: prepared.count(packed_left),
                        )
                    )
                    count_route_metadata = {
                        "front_door_schema": None,
                        "route": "prepared_right_host_left_exact_count",
                    }
            else:
                def run_raw_once():
                    view = prepared.run_raw(packed_left)
                    try:
                        row_count_inner = int(view.row_count)
                        rows_inner = tuple(view.to_dict_rows()) if include_rows else ()
                        return row_count_inner, rows_inner
                    finally:
                        view.close()

                row_count, rows = _phase_repeat_time(
                    phases,
                    "prepared_query_sec",
                    query_repeat=query_repeat,
                    warmup=warmup,
                    fn=run_raw_once,
                    stability_value=lambda value: int(value[0]),
                )
            native_phase_timings = prepared.last_phase_timings()
        finally:
            if prepared_left is not None:
                prepared_left.close()
            prepared.close()
        summary = {
            "intersection_count": row_count,
            "output_contract": (
                "segment_segment_intersection_count"
                if result_mode == "count"
                else "segment_segment_intersection_rows"
            ),
            "prepared_left_for_count": bool(prepared_left is not None),
            "segment_pair_count_route": count_route_metadata,
            "segment_order_execution": (
                "fused_into_pack_segments"
                if segment_order_mode != "natural"
                else "natural_input_order"
            ),
        }
    else:
        from rtdsl.optix_runtime import pack_points
        from rtdsl.optix_runtime import pack_polygons
        from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

        ordered_points = _phase_time(
            phases,
            "query_point_order_sec",
            lambda: _order_points_for_locality(case.inputs["points"], point_order_mode),
        )
        packed_points = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_points(records=ordered_points, dimension=2),
        )
        packed_shapes = _phase_time(
            phases,
            "static_shape_pack_sec",
            lambda: pack_polygons(records=case.inputs["polygons"]),
        )
        prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_point_closed_shape_membership_2d_optix(packed_shapes),
        )
        point_id_count_metadata: dict[str, object] | None = None
        prepared_point_columns_metadata: dict[str, object] | None = None
        prepared_point_batch_executor_metadata: dict[str, object] | None = None
        exact_prepared_points_executor_metadata: dict[str, object] | None = None
        relation_status_corrected_executor_metadata: dict[str, object] | None = None
        exact_prepared_points_executor_capacity: int | None = None
        prepared_point_columns = None
        boundary_event_count_metadata: dict[str, object] | None = None
        boundary_event_columns = None
        boundary_event_count_columns = None
        exact_prepared_points_executor = None
        relation_status_corrected_executor = None
        prepared_point_batch_executor = None
        try:
            if result_mode == "count":
                if count_mode in {"exact_prepared_points", "exact_prepared_points_executor"}:
                    validation_exact_count = int(
                        _phase_time(
                            phases,
                            "validation_exact_query_sec",
                            lambda: _run_prepared_count_with_boundary_mode(prepared, packed_points, None),
                        )
                    )
                    prepared_point_columns = _phase_time(
                        phases,
                        "prepare_query_points_sec",
                        lambda: prepared.prepare_point_probe_columns(packed_points),
                    )
                    prepared_point_columns_metadata = prepared_point_columns.to_metadata()
                    if count_mode == "exact_prepared_points_executor":
                        if exact_executor_max_candidate_rows:
                            exact_prepared_points_executor_capacity = int(exact_executor_max_candidate_rows)
                        else:
                            exact_prepared_points_executor_capacity = max(
                                1,
                                int(validation_exact_count) * 2,
                                _count_input_records(ordered_points),
                            )
                        exact_prepared_points_executor = _phase_time(
                            phases,
                            "prepare_exact_scalar_count_executor_sec",
                            lambda: prepared.prepare_exact_prepared_points_scalar_count_executor(
                                prepared_point_columns,
                                max_candidate_rows=exact_prepared_points_executor_capacity,
                            ),
                        )
                        exact_prepared_points_executor_metadata = exact_prepared_points_executor.to_metadata()
                        row_count = int(
                            _phase_repeat_time(
                                phases,
                                "prepared_query_sec",
                                query_repeat=query_repeat,
                                warmup=warmup,
                                fn=lambda: exact_prepared_points_executor.run(),
                            )
                        )
                    else:
                        row_count = int(
                            _phase_repeat_time(
                                phases,
                                "prepared_query_sec",
                                query_repeat=query_repeat,
                                warmup=warmup,
                                fn=lambda: prepared.count_prepared_points_exact(prepared_point_columns),
                            )
                        )
                    if row_count != validation_exact_count:
                        raise RuntimeError(
                            "exact prepared-points closed-shape count did not match host-points exact prepared count: "
                            f"{row_count} != {validation_exact_count}"
                        )
                elif count_mode == _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE:
                    validation_exact_count = int(
                        _phase_time(
                            phases,
                            "validation_exact_query_sec",
                            lambda: _run_prepared_count_with_boundary_mode(prepared, packed_points, None),
                        )
                    )
                    prepared_point_columns = _phase_time(
                        phases,
                        "prepare_query_points_sec",
                        lambda: prepared.prepare_point_probe_columns(packed_points),
                    )
                    prepared_point_columns_metadata = prepared_point_columns.to_metadata()
                    relation_status_corrected_executor = _phase_time(
                        phases,
                        "prepare_relation_status_corrected_scalar_count_executor_sec",
                        lambda: prepared.prepare_relation_status_corrected_scalar_count_executor(
                            prepared_point_columns,
                        ),
                    )
                    relation_status_corrected_executor_metadata = (
                        relation_status_corrected_executor.to_metadata()
                    )
                    relation_status_result = _phase_repeat_time(
                        phases,
                        "prepared_query_sec",
                        query_repeat=query_repeat,
                        warmup=warmup,
                        fn=lambda: relation_status_corrected_executor.run(),
                        stability_value=lambda value: int(value["row_count"]),
                    )
                    row_count = int(relation_status_result["row_count"])
                    native_phase_timings = {
                        "mode": "relation_status_corrected_scalar_count_executor_run",
                        "point_upload": 0.0,
                        "candidate_count_pass": float(relation_status_result["traversal_seconds"]),
                        "candidate_write_pass": 0.0,
                        "candidate_download": 0.0,
                        "exact_refine": 0.0,
                        "raw_candidate_count": int(relation_status_result["candidate_row_count"]),
                        "emitted_count": row_count,
                        "boundary_candidate_count": int(
                            relation_status_result["boundary_candidate_row_count"]
                        ),
                        "dropped_candidate_count": int(
                            relation_status_result["dropped_candidate_row_count"]
                        ),
                        "row_stream_materialized": bool(
                            relation_status_result["row_stream_materialized"]
                        ),
                        "boundary_candidate_row_stream_materialized": bool(
                            relation_status_result["boundary_candidate_row_stream_materialized"]
                        ),
                        "native_exact_device_scalar_count_produced": bool(
                            relation_status_result["native_exact_device_scalar_count_produced"]
                        ),
                        "relation_status_correction_used": bool(
                            relation_status_result["relation_status_correction_used"]
                        ),
                        "reusable_native_executor_used": bool(
                            relation_status_result["reusable_native_executor_used"]
                        ),
                    }
                    if row_count != validation_exact_count:
                        raise RuntimeError(
                            "validated relation-status corrected closed-shape count did not match exact prepared count: "
                            f"{row_count} != {validation_exact_count}"
                        )
                elif count_mode in _PIP_POSITIVE_COUNT_MODES:
                    validation_exact_count = int(
                        _phase_time(
                            phases,
                            "validation_exact_query_sec",
                            lambda: _run_prepared_count_with_boundary_mode(prepared, packed_points, None),
                        )
                    )
                    if count_mode == "device_filtered_validated":
                        row_count = int(
                            _phase_repeat_time(
                                phases,
                                "prepared_query_sec",
                                query_repeat=query_repeat,
                                warmup=warmup,
                                fn=lambda: _run_prepared_device_filtered_count_with_boundary_mode(
                                    prepared,
                                    packed_points,
                                    device_filtered_boundary_mode,
                                ),
                            )
                        )
                    elif count_mode == "device_filtered_prepared_points_validated":
                        prepared_point_columns = _phase_time(
                            phases,
                            "prepare_query_points_sec",
                            lambda: prepared.prepare_point_probe_columns(packed_points),
                        )
                        prepared_point_columns_metadata = prepared_point_columns.to_metadata()
                        if device_filtered_batch_request_count is None:
                            row_count = int(
                                _phase_repeat_time(
                                    phases,
                                    "prepared_query_sec",
                                    query_repeat=query_repeat,
                                    warmup=warmup,
                                    fn=lambda: _run_prepared_device_filtered_prepared_points_count_with_boundary_mode(
                                        prepared,
                                        prepared_point_columns,
                                        device_filtered_boundary_mode,
                                    ),
                                )
                            )
                        else:
                            with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", device_filtered_boundary_mode):
                                prepared_point_batch_executor = _phase_time(
                                    phases,
                                    "prepare_batch_executor_sec",
                                    lambda: prepared.prepare_device_filtered_prepared_points_batch_executor(
                                        prepared_point_columns,
                                        device_filtered_batch_request_count,
                                        stream_count=device_filtered_batch_stream_count,
                                    ),
                                )
                                prepared_point_batch_executor_metadata = prepared_point_batch_executor.to_metadata()
                                row_count = int(
                                    _phase_batched_count_executor_repeat_time(
                                        phases,
                                        "prepared_query_sec",
                                        query_repeat=query_repeat,
                                        warmup=warmup,
                                        batch_request_count=device_filtered_batch_request_count,
                                        executor=prepared_point_batch_executor,
                                        exact_count=validation_exact_count,
                                    )
                                )
                            prepared_point_batch_executor_metadata["timing_contract"] = (
                                "batched_repeated_request_throughput_not_one_shot_latency"
                            )
                    else:
                        point_id_group_capacity = max(
                            1,
                            max(_record_id(point) for point in ordered_points) + 1,
                        )
                        row_count, point_id_count_metadata = _phase_time(
                            phases,
                            "prepared_query_sec",
                            lambda: _run_prepared_point_id_count_device_columns_with_boundary_mode(
                                prepared,
                                packed_points,
                                device_filtered_boundary_mode,
                                group_capacity=point_id_group_capacity,
                            ),
                        )
                    if row_count != validation_exact_count:
                        raise RuntimeError(
                            "validated device-side closed-shape count did not match exact prepared count: "
                            f"{row_count} != {validation_exact_count}"
                        )
                elif count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE:
                    validation_exact_count = None
                    point_id_group_capacity = max(
                        1,
                        max(_record_id(point) for point in ordered_points) + 1,
                    )
                    boundary_event_columns = _phase_time(
                        phases,
                        "boundary_event_device_columns_sec",
                        lambda: prepared.first_boundary_crossing_device_columns(packed_points),
                    )
                    if boundary_event_columns.overflow:
                        raise RuntimeError("boundary-event device-column continuation overflowed event capacity")
                    boundary_event_count_columns = _phase_time(
                        phases,
                        "boundary_event_grouped_count_sec",
                        lambda: boundary_event_columns.grouped_count_by_point_id_device_columns(
                            group_capacity=point_id_group_capacity,
                        ),
                    )
                    if boundary_event_count_columns.overflow:
                        raise RuntimeError("boundary-event grouped-count continuation overflowed group capacity")
                    row_count = int(boundary_event_columns.row_count)
                    phases["prepared_query_sec"] = (
                        phases["boundary_event_device_columns_sec"]
                        + phases["boundary_event_grouped_count_sec"]
                    )
                    boundary_event_count_metadata = {
                        "boundary_event_device_columns": boundary_event_columns.to_metadata(),
                        "point_id_grouped_count_device_columns": boundary_event_count_columns.to_metadata(),
                        "contract": "point_closed_shape_first_boundary_event_count_by_point_id",
                        "positive_membership_equivalent": False,
                    }
                else:
                    validation_exact_count = None
                    row_count = int(
                        _phase_repeat_time(
                            phases,
                            "prepared_query_sec",
                            query_repeat=query_repeat,
                            warmup=warmup,
                            fn=lambda: prepared.count(packed_points),
                        )
                    )
            else:
                validation_exact_count = None
                def run_positive_hits_once():
                    view = prepared.run_raw(packed_points, result_mode="positive_hits")
                    try:
                        row_count_inner = int(view.row_count)
                        rows_inner = tuple(view.to_dict_rows()) if include_rows else ()
                        return row_count_inner, rows_inner
                    finally:
                        view.close()

                row_count, rows = _phase_repeat_time(
                    phases,
                    "prepared_query_sec",
                    query_repeat=query_repeat,
                    warmup=warmup,
                    fn=run_positive_hits_once,
                    stability_value=lambda value: int(value[0]),
                )
            if native_phase_timings is None:
                native_phase_timings = prepared.last_phase_timings()
        finally:
            if exact_prepared_points_executor is not None:
                exact_prepared_points_executor.close()
            if relation_status_corrected_executor is not None:
                relation_status_corrected_executor.close()
            if prepared_point_batch_executor is not None:
                prepared_point_batch_executor.close()
            if prepared_point_columns is not None:
                prepared_point_columns.close()
            if boundary_event_count_columns is not None:
                boundary_event_count_columns.close()
            if boundary_event_columns is not None:
                boundary_event_columns.close()
            prepared.close()
        if result_mode == "count":
            pip_count_output_contracts = {
                "exact": "point_to_shape_positive_hit_count",
                "exact_prepared_points": "point_to_shape_positive_hit_count_exact_prepared_points",
                "exact_prepared_points_executor": (
                    "point_to_shape_positive_hit_count_exact_prepared_points_executor"
                ),
                _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE: (
                    "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated"
                ),
                "device_filtered_validated": "point_to_shape_positive_hit_count_device_filtered_validated",
                "device_filtered_prepared_points_validated": (
                    "point_to_shape_positive_hit_count_device_filtered_prepared_points_validated"
                ),
                "point_id_count_device_columns_validated": (
                    "point_to_shape_positive_hit_count_by_point_id_device_columns_validated"
                ),
                _PIP_BOUNDARY_EVENT_COUNT_MODE: (
                    "point_closed_shape_first_boundary_event_count_by_point_id_device_columns"
                ),
            }
            output_contract = pip_count_output_contracts[count_mode]
        else:
            output_contract = "point_to_shape_positive_hit_rows"
        summary = {
            "positive_hit_row_count": row_count if count_mode != _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "positive_assignment_count": row_count if count_mode != _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "boundary_event_row_count": row_count if count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "output_contract": output_contract,
            "count_mode": count_mode,
            "device_filtered_boundary_mode": (
                device_filtered_boundary_mode
                if count_mode in _PIP_POSITIVE_COUNT_MODES
                else None
            ),
            "device_filtered_is_exact_authority": False,
            "device_filtered_count_matches_exact": (
                True
                if count_mode in _PIP_POSITIVE_COUNT_MODES
                and result_mode == "count"
                else None
            ),
            "exact_prepared_points_matches_host_exact": (
                True
                if count_mode in {"exact_prepared_points", "exact_prepared_points_executor"}
                and result_mode == "count"
                else None
            ),
            "exact_prepared_points_reuses_query_columns": (
                True
                if count_mode in {"exact_prepared_points", "exact_prepared_points_executor"}
                and result_mode == "count"
                else None
            ),
            "exact_prepared_points_executor": exact_prepared_points_executor_metadata,
            "relation_status_corrected_executor": relation_status_corrected_executor_metadata,
            "relation_status_corrected_matches_host_exact": (
                True
                if count_mode == _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE
                and result_mode == "count"
                else None
            ),
            "relation_status_corrected_executor_reuses_query_columns": (
                True
                if count_mode == _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE
                and result_mode == "count"
                else None
            ),
            "exact_prepared_points_executor_capacity": exact_prepared_points_executor_capacity,
            "exact_prepared_points_executor_capacity_policy": (
                "explicit_max_candidate_rows"
                if count_mode == "exact_prepared_points_executor"
                and exact_executor_max_candidate_rows
                else (
                    "auto_max_of_2x_validation_exact_count_and_query_count"
                    if count_mode == "exact_prepared_points_executor"
                    else None
                )
            ),
            "point_id_count_device_columns": point_id_count_metadata,
            "prepared_point_probe_columns": prepared_point_columns_metadata,
            "prepared_point_batch_executor": prepared_point_batch_executor_metadata,
            "boundary_event_grouped_count_device_columns": boundary_event_count_metadata,
            "boundary_event_contract_not_positive_membership": (
                True if count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE else None
            ),
            "validation_exact_count": validation_exact_count,
            "point_order_mode": point_order_mode,
        }

    if workload == "overlay_seed":
        device_resident_continuation_status = "overlay_seed_prepared_pair_dependency_flags_complete"
    elif workload == "pip" and count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE:
        device_resident_continuation_status = (
            "boundary_event_grouped_count_device_columns_complete: first-boundary-event columns "
            "and grouped point-id counts remain CUDA-resident; this is not a PIP membership contract"
        )
    elif workload == "pip" and count_mode in {"exact_prepared_points", "exact_prepared_points_executor"}:
        device_resident_continuation_status = (
            "partial_exact_prepared_points: query point columns remain prepared on the device, "
            "but exact authority still downloads candidates and refines membership on the host"
        )
    elif workload == "pip" and count_mode == _PIP_RELATION_STATUS_CORRECTED_EXECUTOR_VALIDATED_MODE:
        device_resident_continuation_status = (
            "validated_relation_status_corrected_executor: query point columns remain prepared on the device, "
            "the reusable native scalar-count executor fuses relation-status correction into the device path, "
            "and exact prepared count remains the validation authority"
        )
    else:
        device_resident_continuation_status = (
            "not_complete: prepared query can avoid Python row materialization for counts, "
            "but generic downstream row-stream continuation still needs pod/native work"
        )

    topology_stream_output_contract = str(summary["output_contract"])
    topology_stream_query_prepared = bool(
        summary.get("prepared_point_probe_columns")
        or summary.get("prepared_left_for_count")
        or summary.get("prepared_point_batch_executor")
        or summary.get("exact_prepared_points_executor")
        or summary.get("relation_status_corrected_executor")
    )
    if summary.get("exact_prepared_points_executor"):
        topology_stream_query_residency = "device_resident_prepared_point_probe_columns_with_reusable_exact_executor"
    elif summary.get("relation_status_corrected_executor"):
        topology_stream_query_residency = (
            "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor"
        )
    elif summary.get("prepared_point_probe_columns"):
        topology_stream_query_residency = "device_resident_prepared_point_probe_columns"
    elif summary.get("prepared_point_batch_executor"):
        topology_stream_query_residency = "device_resident_prepared_point_batch_executor"
    elif summary.get("prepared_left_for_count"):
        topology_stream_query_residency = "prepared_left_segment_set_handle"
    else:
        topology_stream_query_residency = "host_packed_query_stream"
    topology_stream_query_count = _topology_stream_runtime_query_count(
        workload=workload,
        inputs=case.inputs,
        prepared_point_columns_metadata=(
            prepared_point_columns_metadata
            if workload == "pip"
            else None
        ),
        packed_query_stream=(
            packed_points
            if workload == "pip"
            else packed_left
        ),
    )
    topology_stream_generic_capability = {
        "pip": "point_location_topology_stream",
        "lsi": "segment_intersection_topology_stream",
        "overlay_seed": "shape_pair_topology_stream",
    }[workload]
    topology_stream_m3_phase_table = build_topology_stream_m3_phase_table(
        phases_sec=phases,
        native_phase_timings=native_phase_timings or {},
        output_contract=topology_stream_output_contract,
        query_count=topology_stream_query_count,
        repeat=query_repeat,
        warmup=warmup,
        query_stream_resident=topology_stream_query_prepared,
        table_basis=(
            "prepared_optix_app_phase_timers_plus_native_last_phase_timings; "
            "non-authorizing V3 topology-stream accounting"
        ),
    )
    topology_stream_prepared_handle = build_topology_stream_prepared_handle_metadata(
        backend="optix",
        generic_capability=topology_stream_generic_capability,
        output_contract=topology_stream_output_contract,
        query_count=topology_stream_query_count,
        static_scene_prepared=True,
        query_stream_prepared=topology_stream_query_prepared,
        query_stream_residency=topology_stream_query_residency,
        m3_phase_table=topology_stream_m3_phase_table,
    )

    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "execution_route": "prepared_optix",
        "backend": "optix",
        "dataset": resolved_dataset,
        "dataset_note": case.note,
        "result_mode": result_mode,
        "count_mode": count_mode,
        "row_count": row_count,
        "summary": summary,
        "phases_sec": phases,
        "native_phase_timings": native_phase_timings or {},
        "topology_stream_m3_phase_table": topology_stream_m3_phase_table,
        "topology_stream_prepared_handle": topology_stream_prepared_handle,
        "repeat_protocol": {
            "repeat": int(query_repeat),
            "warmup": int(warmup),
            "measured_query_total_sec": float(phases.get("prepared_query_sec_total_sec", phases["prepared_query_sec"])),
            "reported_query_metric": "prepared_query_median",
        },
        "point_order_mode": point_order_mode if workload == "pip" else None,
        "segment_order_mode": segment_order_mode if workload == "lsi" else None,
        "device_resident_continuation_status": device_resident_continuation_status,
        "native_engine_boundary": (
            "The engine sees generic prepared point/closed-shape, segment-pair, or shape-pair contracts. "
            "RayJoin application policy and paper-specific interpretation stay in Python."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
            "requires_pod_for_optix_perf": False,
        },
    }
    if include_rows and result_mode == "rows":
        payload["rows"] = rows
    return payload


class PreparedExecutionRayJoinPointLocationTopologyStream:
    """Prepared app adapter for the generic point-location topology stream."""

    def __init__(
        self,
        points,
        shapes,
        *,
        dataset: str,
        dataset_note: str,
        point_order_mode: str = "morton_xy",
        point_eps: float = 1.0e-9,
    ) -> None:
        if point_order_mode not in _PIP_POINT_ORDER_MODES:
            raise ValueError("point_order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
        self._dataset = dataset
        self._dataset_note = dataset_note
        self._point_order_mode = point_order_mode
        self._point_eps = float(point_eps)
        self._closed = False
        self._prepare_phases_sec: dict[str, float] = {}
        self._point_count = _count_input_records(tuple(points))
        self._shape_count = _count_input_records(tuple(shapes))

        from rtdsl.optix_runtime import pack_points
        from rtdsl.optix_runtime import pack_polygons
        from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

        self._ordered_points = _phase_time(
            self._prepare_phases_sec,
            "query_point_order_sec",
            lambda: _order_points_for_locality(tuple(points), point_order_mode),
        )
        self._packed_points = _phase_time(
            self._prepare_phases_sec,
            "query_pack_sec",
            lambda: pack_points(records=self._ordered_points, dimension=2),
        )
        self._packed_shapes = _phase_time(
            self._prepare_phases_sec,
            "static_shape_pack_sec",
            lambda: pack_polygons(records=tuple(shapes)),
        )
        self._prepared = _phase_time(
            self._prepare_phases_sec,
            "prepare_static_scene_sec",
            lambda: prepare_point_closed_shape_membership_2d_optix(self._packed_shapes),
        )
        self._validation_exact_count = int(
            _phase_time(
                self._prepare_phases_sec,
                "validation_exact_query_sec",
                lambda: _run_prepared_count_with_boundary_mode(self._prepared, self._packed_points, None),
            )
        )
        self._prepared_point_columns = _phase_time(
            self._prepare_phases_sec,
            "prepare_query_points_sec",
            lambda: self._prepared.prepare_point_probe_columns(self._packed_points),
        )
        self._prepared_point_columns_metadata = self._prepared_point_columns.to_metadata()
        self._executor = _phase_time(
            self._prepare_phases_sec,
            "prepare_relation_status_corrected_scalar_count_executor_sec",
            lambda: self._prepared.prepare_relation_status_corrected_scalar_count_executor(
                self._prepared_point_columns,
                point_eps=self._point_eps,
            ),
        )
        self._executor_metadata = self._executor.to_metadata()

    @property
    def query_count(self) -> int:
        return self._point_count

    @property
    def shape_count(self) -> int:
        return self._shape_count

    @property
    def prepare_phases_sec(self) -> dict[str, float]:
        return dict(self._prepare_phases_sec)

    def run(self) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared execution RayJoin point-location topology stream is closed")
        phases: dict[str, float] = {}
        relation_status_result = _phase_time(
            phases,
            "prepared_query_sec",
            self._executor.run,
        )
        row_count = int(relation_status_result["row_count"])
        native_phase_timings = {
            "mode": "relation_status_corrected_scalar_count_executor_run",
            "point_upload": 0.0,
            "candidate_count_pass": float(relation_status_result["traversal_seconds"]),
            "candidate_write_pass": 0.0,
            "candidate_download": 0.0,
            "exact_refine": 0.0,
            "raw_candidate_count": int(relation_status_result["candidate_row_count"]),
            "emitted_count": row_count,
            "boundary_candidate_count": int(
                relation_status_result["boundary_candidate_row_count"]
            ),
            "dropped_candidate_count": int(
                relation_status_result["dropped_candidate_row_count"]
            ),
            "row_stream_materialized": bool(
                relation_status_result["row_stream_materialized"]
            ),
            "boundary_candidate_row_stream_materialized": bool(
                relation_status_result["boundary_candidate_row_stream_materialized"]
            ),
            "native_exact_device_scalar_count_produced": bool(
                relation_status_result["native_exact_device_scalar_count_produced"]
            ),
            "relation_status_correction_used": bool(
                relation_status_result["relation_status_correction_used"]
            ),
            "reusable_native_executor_used": bool(
                relation_status_result["reusable_native_executor_used"]
            ),
        }
        topology_stream_output_contract = (
            "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated"
        )
        topology_stream_phases = {**self._prepare_phases_sec, **phases}
        topology_stream_m3_phase_table = build_topology_stream_m3_phase_table(
            phases_sec=topology_stream_phases,
            native_phase_timings=native_phase_timings,
            output_contract=topology_stream_output_contract,
            query_count=self.query_count,
            repeat=1,
            warmup=0,
            query_stream_resident=True,
            table_basis=(
                "prepared_execution_runner_point_location_topology_stream_phase_timers; "
                "non-authorizing V3 topology-stream accounting"
            ),
        )
        topology_stream_prepared_handle = build_topology_stream_prepared_handle_metadata(
            backend="optix",
            generic_capability="point_location_topology_stream",
            output_contract=topology_stream_output_contract,
            query_count=self.query_count,
            static_scene_prepared=True,
            query_stream_prepared=True,
            query_stream_residency=(
                "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor"
            ),
            m3_phase_table=topology_stream_m3_phase_table,
        )
        return {
            "app": "rayjoin_v2_spatial_join",
            "workload": "pip",
            "execution_route": "prepared_execution_runner_point_location_topology_stream",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": self._dataset_note,
            "row_count": row_count,
            "summary": {
                "positive_hit_row_count": row_count,
                "output_contract": topology_stream_output_contract,
                "validation_exact_count": self._validation_exact_count,
                "relation_status_corrected_matches_host_exact": row_count == self._validation_exact_count,
                "point_order_mode": self._point_order_mode,
            },
            "phases_sec": phases,
            "prepare_phases_sec": self.prepare_phases_sec,
            "native_phase_timings": native_phase_timings,
            "prepared_point_probe_columns": self._prepared_point_columns_metadata,
            "relation_status_corrected_executor": self._executor_metadata,
            "topology_stream_m3_phase_table": topology_stream_m3_phase_table,
            "topology_stream_prepared_handle": topology_stream_prepared_handle,
            "device_resident_continuation_status": (
                "prepared_execution_runner_relation_status_corrected_executor: query point "
                "columns remain prepared on the device, the reusable native scalar-count "
                "executor fuses relation-status correction into the device path, and exact "
                "prepared count remains the validation authority"
            ),
            "native_engine_boundary": (
                "The engine sees a generic prepared point-location topology stream. "
                "RayJoin workload interpretation and dataset policy stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
            },
            "metadata": {
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        for handle in (
            getattr(self, "_executor", None),
            getattr(self, "_prepared_point_columns", None),
            getattr(self, "_prepared", None),
        ):
            close = getattr(handle, "close", None)
            if callable(close):
                close()
        self._closed = True

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def run_rayjoin_prepared_execution_point_location_topology_stream_workload(
    workload: str = "pip",
    *,
    dataset: str | None = None,
    point_order_mode: str = "morton_xy",
    query_repeat: int = 1,
    warmup: int = 0,
    point_eps: float = 1.0e-9,
) -> dict[str, object]:
    if workload != "pip":
        raise ValueError("prepared_execution_point_location_topology_stream currently supports only PIP")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    resolved_dataset = dataset or _DEFAULT_DATASETS["pip"]
    case = _load_rayjoin_case("pip", resolved_dataset)
    points = tuple(case.inputs["points"])
    shapes = tuple(case.inputs["polygons"])

    from rtdsl.prepared_execution import make_prepared_input_fingerprint
    from rtdsl.prepared_execution import run_point_location_topology_stream_prepared_session
    from rtdsl.prepared_session_residency import ExplicitPreparedSessionCache

    cache = ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> PreparedExecutionRayJoinPointLocationTopologyStream:
        return PreparedExecutionRayJoinPointLocationTopologyStream(
            points,
            shapes,
            dataset=resolved_dataset,
            dataset_note=case.note,
            point_order_mode=point_order_mode,
            point_eps=point_eps,
        )

    result = run_point_location_topology_stream_prepared_session(
        query_stream_fingerprint={
            "points": make_prepared_input_fingerprint(points),
            "point_order_mode": point_order_mode,
        },
        static_scene_fingerprint={
            "polygons": make_prepared_input_fingerprint(shapes),
        },
        output_contract="point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
        query_count=len(points),
        shape_count=len(shapes),
        backend="optix",
        partner="none",
        cache=cache,
        prepare_session=prepare_session,
        run_topology_stream=lambda prepared: prepared.run(),
        validate_output=lambda output: {
            "matches_validation_exact_count": (
                int(output["row_count"]) == int(output["summary"]["validation_exact_count"])
            )
        },
        warmup_count=warmup,
        measured_repeat_count=query_repeat,
    )
    payload = dict(result.output)
    payload["prepared_execution_session_runner"] = result.to_metadata()
    payload["runtime_trunk_executes_end_to_end"] = bool(
        result.to_metadata()["runtime_trunk_executes_end_to_end"]
    )
    payload["internal_device_residency_between_rtdl_phases"] = bool(
        result.to_metadata()["internal_device_residency_between_rtdl_phases"]
    )
    payload["hot_path_host_materialization"] = bool(
        result.to_metadata()["hot_path_host_materialization"]
    )
    payload["release_authorized"] = False
    payload["public_speedup_claim_authorized"] = False
    payload["broad_v3_faster_than_v2_claim_authorized"] = False
    payload["full_all_app_rerun_authorized_by_this_packet"] = False
    return payload


def run_rayjoin_prepared_optix_cupy_refined_pip(
    *,
    dataset: str | None = None,
    result_mode: str = "count",
    include_rows: bool = False,
    candidate_max_rows: int | None = None,
    point_eps: float = 1.0e-9,
    query_repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    """Run PIP through generic RT candidates plus a prepared CuPy exact refiner.

    This route is the app-facing counterpart of the Goal3427 prepared refiner
    timing probe. Native OptiX produces generic point/closed-shape candidate
    columns with instance ordinals; CuPy owns the exact simple-ring refinement.
    RayJoin interpretation remains Python-side.
    """

    if result_mode not in {"count", "rows"}:
        raise ValueError("result_mode must be 'count' or 'rows'")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    resolved_dataset = dataset or _DEFAULT_DATASETS["pip"]
    case = _load_rayjoin_case("pip", resolved_dataset)
    points = tuple(case.inputs["points"])
    shapes = tuple(case.inputs["polygons"])
    max_rows = int(candidate_max_rows or max(1024, len(points) * 8))
    if max_rows <= 0:
        raise ValueError("candidate_max_rows must be positive")

    prepared = prepare_rayjoin_optix_cupy_refined_pip(
        points,
        shapes,
        dataset=resolved_dataset,
        dataset_note=case.note,
        candidate_max_rows=max_rows,
        point_eps=point_eps,
    )
    try:
        payload = prepared.run(
            result_mode=result_mode,
            include_rows=include_rows,
            query_repeat=query_repeat,
            warmup=warmup,
        )
        payload["phases_sec"] = {
            **prepared.prepare_phases_sec,
            **payload["phases_sec"],
        }
        payload["prepared_reuse"] = {
            **payload["prepared_reuse"],
            "enabled": False,
            "prepare_paid_in_call": True,
        }
        return payload
    finally:
        prepared.close()


class PreparedRayJoinOptixCupyRefinedPip:
    """App-layer prepared handle for generic OptiX candidates plus CuPy PIP refinement."""

    def __init__(
        self,
        points,
        shapes,
        *,
        dataset: str = "direct_points_shapes",
        dataset_note: str = "Direct point/closed-shape inputs supplied by the caller.",
        candidate_max_rows: int | None = None,
        point_eps: float = 1.0e-9,
    ) -> None:
        self._points = tuple(points)
        self._shapes = tuple(shapes)
        self._dataset = dataset
        self._dataset_note = dataset_note
        self._default_candidate_max_rows = int(
            candidate_max_rows or max(1024, len(self._points) * 8)
        )
        if self._default_candidate_max_rows <= 0:
            raise ValueError("candidate_max_rows must be positive")
        self._closed = False
        phases: dict[str, float] = {}

        from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

        self._prepared_refiner = _phase_time(
            phases,
            "prepare_cupy_refiner_sec",
            lambda: rt.prepare_closed_shape_membership_candidate_refiner_exact_cupy(
                self._points,
                self._shapes,
                point_eps=point_eps,
            ),
        )
        self._prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_point_closed_shape_membership_2d_optix(self._shapes),
        )
        self.prepare_phases_sec = phases

    def close(self) -> None:
        if not self._closed:
            self._prepared.close()
            # The CuPy refiner owns CuPy arrays and a cached raw kernel, not a
            # custom native handle. Dropping the reference lets CuPy/Python
            # release lookup storage promptly when callers close the app handle.
            self._prepared_refiner = None
            self._closed = True

    def __enter__(self) -> "PreparedRayJoinOptixCupyRefinedPip":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def run(
        self,
        *,
        result_mode: str = "count",
        include_rows: bool = False,
        candidate_max_rows: int | None = None,
        query_repeat: int = 1,
        warmup: int = 0,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared RayJoin OptiX+CuPy PIP handle is closed")
        if result_mode not in {"count", "rows"}:
            raise ValueError("result_mode must be 'count' or 'rows'")
        if query_repeat <= 0:
            raise ValueError("query_repeat must be positive")
        if warmup < 0:
            raise ValueError("warmup must be non-negative")
        max_rows = int(candidate_max_rows or self._default_candidate_max_rows)
        if max_rows <= 0:
            raise ValueError("candidate_max_rows must be positive")

        phases: dict[str, float] = {}
        rows: tuple[dict[str, int], ...] = ()

        def run_once():
            columns = self._prepared.candidate_device_columns(self._points, max_rows=max_rows)
            try:
                candidate_metadata_inner = columns.to_metadata()
                refined_inner = self._prepared_refiner.refine(columns)
                return candidate_metadata_inner, refined_inner
            finally:
                columns.close()

        candidate_metadata, refined = _phase_repeat_time(
            phases,
            "prepared_query_sec",
            query_repeat=query_repeat,
            warmup=warmup,
            fn=run_once,
            stability_value=lambda value: int(value[1]["row_count"]),
        )
        phases["prepared_cupy_refine_sec"] = phases["prepared_query_sec"]
        row_count = int(refined["row_count"])
        if include_rows and result_mode == "rows":
            import cupy as cp  # type: ignore

            materialize_start = time.perf_counter()
            point_ids = cp.asnumpy(refined["point_id"]).tolist()
            shape_ids = cp.asnumpy(refined["shape_id"]).tolist()
            rows = tuple(
                {
                    "point_id": int(point_id),
                    "polygon_id": int(shape_id),
                    "contains": 1,
                }
                for point_id, shape_id in zip(point_ids, shape_ids)
            )
            phases["host_row_materialize_sec"] = time.perf_counter() - materialize_start

        summary = {
            "positive_hit_row_count": row_count,
            "positive_assignment_count": row_count,
            "output_contract": (
                "point_to_shape_positive_hit_rows_prepared_optix_candidate_columns_plus_cupy_refine"
                if result_mode == "rows"
                else "point_to_shape_positive_hit_count_prepared_optix_candidate_columns_plus_cupy_refine"
            ),
        }
        payload: dict[str, object] = {
            "app": "rayjoin_v2_spatial_join",
            "workload": "pip",
            "execution_route": "prepared_optix_cupy_refined_pip",
            "backend": "optix+cupy",
            "dataset": self._dataset,
            "dataset_note": self._dataset_note,
            "result_mode": result_mode,
            "row_count": row_count,
            "summary": summary,
            "phases_sec": phases,
            "candidate_columns": candidate_metadata,
            "partner_refinement": {
                key: value
                for key, value in refined.items()
                if key not in {"point_id", "shape_id", "membership"}
            },
            "prepared_reuse": {
                "enabled": True,
                "point_count": len(self._points),
                "shape_count": len(self._shapes),
                "candidate_max_rows": max_rows,
                "prepare_static_scene_sec": self.prepare_phases_sec["prepare_static_scene_sec"],
                "prepare_cupy_refiner_sec": self.prepare_phases_sec["prepare_cupy_refiner_sec"],
                "prepare_paid_once": True,
            },
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_query_total_sec": float(phases["prepared_query_sec_total_sec"]),
                "reported_query_metric": "prepared_query_median",
            },
            "device_resident_continuation_status": (
                "candidate_columns_and_prepared_cupy_refiner_complete: generic RT candidate "
                "columns and prepared CuPy lookup columns stay device-side; host row materialization "
                "is optional when include_rows is requested"
            ),
            "native_engine_boundary": (
                "The engine sees generic point/closed-shape candidate columns with instance ordinals. "
                "CuPy performs caller-side simple-ring refinement; RayJoin/CDB interpretation stays in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }
        if include_rows and result_mode == "rows":
            payload["rows"] = rows
        return payload


def prepare_rayjoin_optix_cupy_refined_pip(
    points,
    shapes,
    *,
    dataset: str = "direct_points_shapes",
    dataset_note: str = "Direct point/closed-shape inputs supplied by the caller.",
    candidate_max_rows: int | None = None,
    point_eps: float = 1.0e-9,
) -> PreparedRayJoinOptixCupyRefinedPip:
    return PreparedRayJoinOptixCupyRefinedPip(
        points,
        shapes,
        dataset=dataset,
        dataset_note=dataset_note,
        candidate_max_rows=candidate_max_rows,
        point_eps=point_eps,
    )


def run_rayjoin_prepared_optix_compact_grouped_count_segments(
    left_segments,
    right_segments,
    *,
    dataset: str = "direct_segments",
    dataset_note: str = "Direct segment inputs supplied by the caller.",
    include_rows: bool = False,
) -> dict[str, object]:
    phases: dict[str, float] = {}
    rows: tuple[dict[str, int], ...] = ()

    from rtdsl.segment_columns import segment_columns_2d
    from rtdsl.segment_columns import segment_columns_with_ids

    left_columns = _phase_time(
        phases,
        "query_column_prepare_sec",
        lambda: segment_columns_2d(left_segments),
    )
    right_segments, right_segment_count = _reusable_segment_input(right_segments)
    original_left_ids = tuple(int(value) for value in left_columns.ids)
    remapped_left_segments = segment_columns_with_ids(left_columns, range(left_columns.count))

    from rtdsl.optix_runtime import pack_segments
    from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix

    packed_left = _phase_time(
        phases,
        "query_pack_sec",
        lambda: pack_segments(records=remapped_left_segments),
    )
    prepared = _phase_time(
        phases,
        "prepare_static_scene_sec",
        lambda: prepare_segment_pair_intersection_optix(right_segments),
    )
    candidate_metadata: dict[str, object]
    compact_metadata: dict[str, object]
    candidate_row_count = 0
    try:
        candidate_start = time.perf_counter()
        columns = prepared.candidate_device_columns(
            packed_left,
            max_rows=remapped_left_segments.count * right_segment_count,
        )
        phases["candidate_device_columns_sec"] = time.perf_counter() - candidate_start
        try:
            candidate_metadata = columns.to_metadata()
            candidate_row_count = int(columns.row_count)
            compact_start = time.perf_counter()
            compact = columns.grouped_count_by_left_id_compact_device_columns(
                group_capacity=max(1, remapped_left_segments.count),
            )
            phases["compact_grouped_count_sec"] = time.perf_counter() - compact_start
            try:
                compact_metadata = compact.to_metadata()
                if include_rows:
                    import cupy as cp  # type: ignore

                    copy_start = time.perf_counter()
                    keys = cp.asnumpy(compact.as_cupy_group_keys()).tolist()
                    counts = cp.asnumpy(compact.as_cupy_counts()).tolist()
                    phases["compact_validation_copy_sec"] = time.perf_counter() - copy_start
                    rows = tuple(
                        {
                            "left_id": original_left_ids[int(key)],
                            "count": int(count),
                        }
                        for key, count in zip(keys, counts)
                    )
            finally:
                compact.close()
        finally:
            columns.close()
    finally:
        prepared.close()

    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": "lsi",
        "execution_route": "prepared_optix_compact_grouped_count",
        "backend": "optix",
        "dataset": dataset,
        "dataset_note": dataset_note,
        "row_count": candidate_row_count,
        "summary": {
            "intersection_count": candidate_row_count,
            "left_group_count": int(compact_metadata["row_count"]),
            "output_contract": "segment_segment_intersection_count_by_left_id_compact_device_columns",
        },
        "phases_sec": phases,
        "candidate_columns": candidate_metadata,
        "compact_grouped_count_columns": compact_metadata,
        "left_id_remap": {
            "enabled": True,
            "reason": "generic grouped-count primitive uses direct-address key capacity",
            "original_left_id_count": len(original_left_ids),
        },
        "device_resident_continuation_status": (
            "compact_grouped_count_device_columns_complete: group_key/count columns remain CUDA-resident; "
            "row_count scalar is host-visible; validation copy is optional"
        ),
        "native_engine_boundary": (
            "The engine sees generic segment-pair candidate columns and generic grouped-count compact columns. "
            "RayJoin workload interpretation and left-ID remapping stay in Python."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "requires_pod_for_optix_perf": False,
        },
    }
    if include_rows:
        payload["rows"] = rows
    return payload


class PreparedRayJoinOptixCompactGroupedCountSegments:
    """Python app-layer prepared handle for repeated compact count queries."""

    def __init__(
        self,
        right_segments,
        *,
        dataset: str = "direct_segments",
        dataset_note: str = "Direct segment inputs supplied by the caller.",
    ) -> None:
        self._right_segments, self._right_segment_count = _reusable_segment_input(right_segments)
        self._dataset = dataset
        self._dataset_note = dataset_note
        self._closed = False
        phases: dict[str, float] = {}

        from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix

        self._prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_segment_pair_intersection_optix(self._right_segments),
        )
        self.prepare_static_scene_sec = phases["prepare_static_scene_sec"]

    def close(self) -> None:
        if not self._closed:
            self._prepared.close()
            self._closed = True

    def __enter__(self) -> "PreparedRayJoinOptixCompactGroupedCountSegments":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def pack_left_segments(self, left_segments) -> "RayJoinOptixCompactGroupedCountPackedLeftSegments":
        return pack_rayjoin_optix_compact_grouped_count_left_segments(left_segments)

    def run(
        self,
        left_segments,
        *,
        include_rows: bool = False,
        dataset_note: str | None = None,
    ) -> dict[str, object]:
        packed_left = self.pack_left_segments(left_segments)
        try:
            payload = self.run_packed_left(
                packed_left,
                include_rows=include_rows,
                dataset_note=dataset_note,
            )
        finally:
            packed_left.close()
        payload["phases_sec"] = {
            "query_column_prepare_sec": packed_left.column_prepare_seconds,
            "query_pack_sec": packed_left.pack_seconds,
            **payload["phases_sec"],
        }
        payload["packed_left_reuse"] = {
            **payload["packed_left_reuse"],
            "enabled": False,
            "column_prepare_paid_in_call": True,
            "query_pack_paid_in_call": True,
        }
        return payload

    def run_packed_left(
        self,
        packed_left: "RayJoinOptixCompactGroupedCountPackedLeftSegments",
        *,
        include_rows: bool = False,
        dataset_note: str | None = None,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared RayJoin compact grouped-count handle is closed")
        if not isinstance(packed_left, RayJoinOptixCompactGroupedCountPackedLeftSegments):
            raise TypeError("packed_left must be produced by pack_rayjoin_optix_compact_grouped_count_left_segments")

        phases: dict[str, float] = {}
        rows: tuple[dict[str, int], ...] = ()
        original_left_ids = packed_left.original_left_ids
        candidate_metadata: dict[str, object]
        compact_metadata: dict[str, object]
        candidate_row_count = 0
        candidate_start = time.perf_counter()
        columns = self._prepared.candidate_device_columns(
            packed_left.packed_segments,
            max_rows=packed_left.count * self._right_segment_count,
        )
        phases["candidate_device_columns_sec"] = time.perf_counter() - candidate_start
        try:
            candidate_metadata = columns.to_metadata()
            candidate_row_count = int(columns.row_count)
            compact_start = time.perf_counter()
            compact = columns.grouped_count_by_left_id_compact_device_columns(
                group_capacity=max(1, packed_left.count),
            )
            phases["compact_grouped_count_sec"] = time.perf_counter() - compact_start
            try:
                compact_metadata = compact.to_metadata()
                if include_rows:
                    import cupy as cp  # type: ignore

                    copy_start = time.perf_counter()
                    keys = cp.asnumpy(compact.as_cupy_group_keys()).tolist()
                    counts = cp.asnumpy(compact.as_cupy_counts()).tolist()
                    phases["compact_validation_copy_sec"] = time.perf_counter() - copy_start
                    rows = tuple(
                        {
                            "left_id": original_left_ids[int(key)],
                            "count": int(count),
                        }
                        for key, count in zip(keys, counts)
                    )
            finally:
                compact.close()
        finally:
            columns.close()

        payload: dict[str, object] = {
            "app": "rayjoin_v2_spatial_join",
            "workload": "lsi",
            "execution_route": "prepared_optix_compact_grouped_count_reuse",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": dataset_note or self._dataset_note,
            "row_count": candidate_row_count,
            "summary": {
                "intersection_count": candidate_row_count,
                "left_group_count": int(compact_metadata["row_count"]),
                "output_contract": "segment_segment_intersection_count_by_left_id_compact_device_columns",
            },
            "phases_sec": phases,
            "candidate_columns": candidate_metadata,
            "compact_grouped_count_columns": compact_metadata,
            "prepared_reuse": {
                "enabled": True,
                "right_segment_count": self._right_segment_count,
                "prepare_static_scene_sec": self.prepare_static_scene_sec,
                "prepare_static_scene_paid_once": True,
            },
            "packed_left_reuse": {
                "enabled": True,
                "left_segment_count": packed_left.count,
                "column_prepare_seconds": packed_left.column_prepare_seconds,
                "pack_seconds": packed_left.pack_seconds,
                "query_pack_paid_in_call": False,
            },
            "left_id_remap": {
                "enabled": True,
                "reason": "generic grouped-count primitive uses direct-address key capacity",
                "original_left_id_count": len(original_left_ids),
            },
            "device_resident_continuation_status": (
                "compact_grouped_count_device_columns_complete: group_key/count columns remain CUDA-resident; "
                "row_count scalar is host-visible; validation copy is optional"
            ),
            "native_engine_boundary": (
                "The engine sees generic segment-pair candidate columns and generic grouped-count compact columns. "
                "RayJoin workload interpretation, prepared-handle reuse, and left-ID remapping stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_0_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "requires_pod_for_optix_perf": False,
            },
        }
        if include_rows:
            payload["rows"] = rows
        return payload

    def run_packed_left_dense_count(
        self,
        packed_left: "RayJoinOptixCompactGroupedCountPackedLeftSegments",
        *,
        include_rows: bool = False,
        dataset_note: str | None = None,
        query_repeat: int = 1,
        warmup: int = 0,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared RayJoin compact grouped-count handle is closed")
        if not isinstance(packed_left, RayJoinOptixCompactGroupedCountPackedLeftSegments):
            raise TypeError("packed_left must be produced by pack_rayjoin_optix_compact_grouped_count_left_segments")
        if query_repeat <= 0:
            raise ValueError("query_repeat must be positive")
        if warmup < 0:
            raise ValueError("warmup must be non-negative")

        phases: dict[str, float] = {}
        rows: tuple[dict[str, int], ...]

        def run_once():
            dense = self._prepared.left_id_count_prepared_left_device_columns(
                packed_left.prepared_left_set,
                group_capacity=max(1, packed_left.count),
            )
            try:
                dense_metadata_inner = dense.to_metadata()
                rows_inner: tuple[dict[str, int], ...] = ()
                if include_rows:
                    import cupy as cp  # type: ignore

                    counts = cp.asnumpy(dense.as_cupy_counts()).tolist()
                    rows_inner = tuple(
                        {
                            "left_id": packed_left.original_left_ids[index],
                            "count": int(count),
                        }
                        for index, count in enumerate(counts[: packed_left.count])
                    )
                return dense_metadata_inner, rows_inner
            finally:
                dense.close()

        dense_metadata, rows = _phase_repeat_time(
            phases,
            "prepared_query_sec",
            query_repeat=query_repeat,
            warmup=warmup,
            fn=run_once,
            stability_value=lambda value: int(value[0]["source_row_count"]),
        )
        phases["left_id_count_device_columns_sec"] = phases["prepared_query_sec"]

        payload: dict[str, object] = {
            "app": "rayjoin_v2_spatial_join",
            "workload": "lsi",
            "execution_route": "prepared_optix_left_id_dense_count_prepared_left_reuse",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": dataset_note or self._dataset_note,
            "row_count": int(dense_metadata["source_row_count"]),
            "summary": {
                "intersection_count": int(dense_metadata["source_row_count"]),
                "left_group_capacity": packed_left.count,
                "output_contract": "segment_segment_intersection_count_by_left_id_dense_device_column",
            },
            "phases_sec": phases,
            "dense_left_id_count_columns": dense_metadata,
            "prepared_reuse": {
                "enabled": True,
                "right_segment_count": self._right_segment_count,
                "prepare_static_scene_sec": self.prepare_static_scene_sec,
                "prepare_static_scene_paid_once": True,
            },
            "packed_left_reuse": {
                "enabled": True,
                "left_segment_count": packed_left.count,
                "column_prepare_seconds": packed_left.column_prepare_seconds,
                "pack_seconds": packed_left.pack_seconds,
                "prepared_left_set_seconds": packed_left.prepared_left_set_seconds,
                "native_prepared_left_set_enabled": True,
                "native_prepared_left_set_paid_once": True,
                "query_pack_paid_in_call": False,
            },
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_query_total_sec": float(phases["prepared_query_sec_total_sec"]),
                "reported_query_metric": "prepared_query_median",
            },
            "left_id_remap": {
                "enabled": True,
                "reason": "generic left-id count primitive uses direct-address key capacity",
                "original_left_id_count": len(packed_left.original_left_ids),
            },
            "device_resident_continuation_status": (
                "dense_left_id_count_device_column_complete: count[index] remains CUDA-resident during the route; "
                "left segment-set upload is paid once by the prepared-left handle; validation copy is optional"
            ),
            "native_engine_boundary": (
                "The engine sees generic segment-pair left-id count device columns. "
                "RayJoin workload interpretation, prepared-handle reuse, prepared-left reuse, and left-ID remapping stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_0_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "requires_pod_for_optix_perf": False,
            },
        }
        if include_rows:
            payload["rows"] = rows
        return payload


def _segment_record_dict(segment) -> dict[str, float | int]:
    if isinstance(segment, dict):
        return dict(segment)
    return {
        "id": int(getattr(segment, "id")),
        "x0": float(getattr(segment, "x0")),
        "y0": float(getattr(segment, "y0")),
        "x1": float(getattr(segment, "x1")),
        "y1": float(getattr(segment, "y1")),
    }


def _reusable_segment_input(segments):
    if hasattr(segments, "count") and all(hasattr(segments, field) for field in ("ids", "x0", "y0", "x1", "y1")):
        return segments, int(segments.count)
    records = tuple(segments)
    return records, len(records)


def _reusable_shape_input(shapes):
    if hasattr(shapes, "polygon_count") and all(
        hasattr(shapes, field) for field in ("refs", "vertices_xy", "vertex_xy_count")
    ):
        return shapes, int(shapes.polygon_count)
    records = tuple(shapes)
    return records, len(records)


class RayJoinOptixCompactGroupedCountPackedLeftSegments:
    """App-layer packed left segments for repeated compact count queries."""

    def __init__(self, left_segments) -> None:
        phases: dict[str, float] = {}
        from rtdsl.segment_columns import segment_columns_2d
        from rtdsl.segment_columns import segment_columns_with_ids

        left_columns = _phase_time(
            phases,
            "query_column_prepare_sec",
            lambda: segment_columns_2d(left_segments),
        )
        self.original_left_ids = tuple(int(value) for value in left_columns.ids)
        remapped_left_segments = segment_columns_with_ids(left_columns, range(left_columns.count))

        from rtdsl.optix_runtime import pack_segments
        from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix

        self.packed_segments = _phase_time(
            phases,
            "query_pack_sec",
            lambda: pack_segments(records=remapped_left_segments),
        )
        self.prepared_left_set = _phase_time(
            phases,
            "prepared_left_set_sec",
            lambda: prepare_segment_pair_left_set_optix(self.packed_segments),
        )
        self.column_prepare_seconds = phases["query_column_prepare_sec"]
        self.pack_seconds = phases["query_pack_sec"]
        self.prepared_left_set_seconds = phases["prepared_left_set_sec"]
        self.count = len(self.original_left_ids)
        self._closed = False

    def close(self) -> None:
        if not self._closed:
            self.prepared_left_set.close()
            self._closed = True

    def __enter__(self) -> "RayJoinOptixCompactGroupedCountPackedLeftSegments":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def pack_rayjoin_optix_compact_grouped_count_left_segments(
    left_segments,
) -> RayJoinOptixCompactGroupedCountPackedLeftSegments:
    return RayJoinOptixCompactGroupedCountPackedLeftSegments(left_segments)


def prepare_rayjoin_optix_compact_grouped_count_segments(
    right_segments,
    *,
    dataset: str = "direct_segments",
    dataset_note: str = "Direct segment inputs supplied by the caller.",
) -> PreparedRayJoinOptixCompactGroupedCountSegments:
    return PreparedRayJoinOptixCompactGroupedCountSegments(
        right_segments,
        dataset=dataset,
        dataset_note=dataset_note,
    )


def run_rayjoin_prepared_optix_compact_grouped_count_workload(
    workload: str = "lsi",
    *,
    dataset: str | None = None,
    include_rows: bool = False,
) -> dict[str, object]:
    if workload != "lsi":
        raise ValueError("prepared_optix_compact_grouped_count currently supports only the lsi workload")
    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    case = _load_rayjoin_case(
        workload,
        resolved_dataset,
        segment_column_inputs=workload == "lsi",
    )
    return run_rayjoin_prepared_optix_compact_grouped_count_segments(
        case.inputs["left"],
        case.inputs["right"],
        dataset=resolved_dataset,
        dataset_note=case.note,
        include_rows=include_rows,
    )


def run_rayjoin_prepared_optix_left_id_dense_count_workload(
    workload: str = "lsi",
    *,
    dataset: str | None = None,
    include_rows: bool = False,
    query_repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    if workload != "lsi":
        raise ValueError("prepared_optix_left_id_dense_count currently supports only the lsi workload")
    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    case = _load_rayjoin_case(
        workload,
        resolved_dataset,
        segment_column_inputs=workload == "lsi",
    )
    with prepare_rayjoin_optix_compact_grouped_count_segments(
        case.inputs["right"],
        dataset=resolved_dataset,
        dataset_note=case.note,
    ) as prepared:
        packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(case.inputs["left"])
        try:
            return prepared.run_packed_left_dense_count(
                packed_left,
                include_rows=include_rows,
                dataset_note=case.note,
                query_repeat=query_repeat,
                warmup=warmup,
            )
        finally:
            packed_left.close()


class PreparedExecutionRayJoinSegmentIntersectionTopologyStream:
    """Prepared app adapter for the generic segment-intersection topology stream."""

    def __init__(
        self,
        left_segments,
        right_segments,
        *,
        dataset: str,
        dataset_note: str,
    ) -> None:
        self._dataset = dataset
        self._dataset_note = dataset_note
        self._closed = False
        self._left_segments, self._left_segment_count = _reusable_segment_input(left_segments)
        self._right_segments, self._right_segment_count = _reusable_segment_input(right_segments)
        self._prepared = prepare_rayjoin_optix_compact_grouped_count_segments(
            self._right_segments,
            dataset=dataset,
            dataset_note=dataset_note,
        )
        self._packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(
            self._left_segments
        )
        self._prepare_phases_sec = {
            "prepare_static_scene_sec": float(self._prepared.prepare_static_scene_sec),
            "query_column_prepare_sec": float(self._packed_left.column_prepare_seconds),
            "query_pack_sec": float(self._packed_left.pack_seconds),
            "prepared_left_set_sec": float(self._packed_left.prepared_left_set_seconds),
        }

    @property
    def query_count(self) -> int:
        return self._left_segment_count

    @property
    def right_segment_count(self) -> int:
        return self._right_segment_count

    @property
    def prepare_phases_sec(self) -> dict[str, float]:
        return dict(self._prepare_phases_sec)

    def run_hot(self) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared execution segment-intersection topology stream is closed")
        payload = self._prepared.run_packed_left_dense_count(
            self._packed_left,
            include_rows=False,
            query_repeat=1,
            warmup=0,
        )
        return {
            "row_count": int(payload["row_count"]),
            "summary": dict(payload["summary"]),
            "phases_sec": dict(payload["phases_sec"]),
            "dense_left_id_count_columns": dict(payload["dense_left_id_count_columns"]),
        }

    def finalize_run(self, hot_output: dict[str, object]) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared execution segment-intersection topology stream is closed")
        payload = dict(hot_output)
        phases = dict(payload["phases_sec"])
        dense_metadata = dict(payload["dense_left_id_count_columns"])
        row_count = int(payload["row_count"])
        native_query_sec = float(
            dense_metadata.get("reduction_seconds")
            or phases.get("left_id_count_device_columns_sec")
            or phases["prepared_query_sec"]
        )
        native_phase_timings = {
            "mode": "segment_intersection_left_id_dense_count_prepared_left_device_columns",
            "left_upload": 0.0,
            "native_query_sec": native_query_sec,
            "candidate_count_pass": native_query_sec,
            "exact_refine": 0.0,
            "count_download": 0.0,
            "row_download": 0.0,
            "row_stream_materialized": False,
            "count_column_materialized_on_host": bool(
                dense_metadata.get("count_column_materialized_on_host")
            ),
            "group_key_column_materialized_on_host": bool(
                dense_metadata.get("group_key_column_materialized_on_host")
            ),
            "source_row_count_materialized_on_host_for_metadata": bool(
                dense_metadata.get("source_row_count_materialized_on_host_for_metadata")
            ),
            "device_resident_dense_count_column": bool(dense_metadata.get("device_resident")),
            "native_symbol": dense_metadata.get("native_symbol"),
            "source_row_count": int(dense_metadata.get("source_row_count", row_count)),
            "overflow": bool(dense_metadata.get("overflow")),
        }
        topology_stream_output_contract = (
            "segment_segment_intersection_count_by_left_id_dense_device_column"
        )
        topology_stream_phases = {**self._prepare_phases_sec, **phases}
        topology_stream_m3_phase_table = build_topology_stream_m3_phase_table(
            phases_sec=topology_stream_phases,
            native_phase_timings=native_phase_timings,
            output_contract=topology_stream_output_contract,
            query_count=self.query_count,
            repeat=1,
            warmup=0,
            query_stream_resident=True,
            table_basis=(
                "prepared_execution_runner_segment_intersection_topology_stream_phase_timers; "
                "non-authorizing V3 topology-stream accounting"
            ),
        )
        topology_stream_prepared_handle = build_topology_stream_prepared_handle_metadata(
            backend="optix",
            generic_capability="segment_intersection_topology_stream",
            output_contract=topology_stream_output_contract,
            query_count=self.query_count,
            static_scene_prepared=True,
            query_stream_prepared=True,
            query_stream_residency=(
                "device_resident_prepared_left_segment_set_dense_left_id_count"
            ),
            m3_phase_table=topology_stream_m3_phase_table,
        )
        return {
            "app": "rayjoin_v2_spatial_join",
            "workload": "lsi",
            "execution_route": "prepared_execution_runner_segment_intersection_topology_stream",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": self._dataset_note,
            "row_count": row_count,
            "summary": {
                "intersection_count": row_count,
                "left_group_capacity": self._packed_left.count,
                "output_contract": topology_stream_output_contract,
                "right_segment_count": self.right_segment_count,
            },
            "phases_sec": phases,
            "prepare_phases_sec": self.prepare_phases_sec,
            "native_phase_timings": native_phase_timings,
            "dense_left_id_count_columns": dense_metadata,
            "prepared_reuse": {
                "enabled": True,
                "right_segment_count": self.right_segment_count,
                "prepare_static_scene_sec": self._prepared.prepare_static_scene_sec,
                "prepare_static_scene_paid_once": True,
            },
            "packed_left_reuse": {
                "enabled": True,
                "left_segment_count": self._packed_left.count,
                "column_prepare_seconds": self._packed_left.column_prepare_seconds,
                "pack_seconds": self._packed_left.pack_seconds,
                "prepared_left_set_seconds": self._packed_left.prepared_left_set_seconds,
                "native_prepared_left_set_enabled": True,
                "native_prepared_left_set_paid_once": True,
                "query_pack_paid_in_call": False,
            },
            "left_id_remap": {
                "enabled": True,
                "reason": "generic segment-intersection count primitive uses direct-address key capacity",
                "original_left_id_count": len(self._packed_left.original_left_ids),
            },
            "topology_stream_m3_phase_table": topology_stream_m3_phase_table,
            "topology_stream_prepared_handle": topology_stream_prepared_handle,
            "device_resident_continuation_status": (
                "prepared_execution_runner_segment_intersection_topology_stream: "
                "left segment query stream is a prepared device-resident left-set, "
                "dense left-id counts remain CUDA-resident inside RTDL, and only scalar "
                "metadata is materialized for this summary"
            ),
            "native_engine_boundary": (
                "The engine sees a generic segment-intersection topology stream with "
                "left-id dense-count continuation. RayJoin workload interpretation, "
                "dataset policy, and left-ID remapping stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
            },
            "metadata": {
                "internal_device_residency_between_rtdl_phases": bool(
                    dense_metadata.get("device_resident")
                ),
                "hot_path_host_materialization": False,
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
            },
        }

    def run(self) -> dict[str, object]:
        return self.finalize_run(self.run_hot())

    def close(self) -> None:
        if self._closed:
            return
        for handle in (
            getattr(self, "_packed_left", None),
            getattr(self, "_prepared", None),
        ):
            close = getattr(handle, "close", None)
            if callable(close):
                close()
        self._closed = True

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def run_rayjoin_prepared_execution_segment_intersection_topology_stream_workload(
    workload: str = "lsi",
    *,
    dataset: str | None = None,
    query_repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    if workload != "lsi":
        raise ValueError("prepared_execution_segment_intersection_topology_stream currently supports only LSI")
    if query_repeat <= 0:
        raise ValueError("query_repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    resolved_dataset = dataset or _DEFAULT_DATASETS["lsi"]
    case = _load_rayjoin_case(
        "lsi",
        resolved_dataset,
        segment_column_inputs=True,
    )
    left_segments = tuple(case.inputs["left"])
    right_segments = tuple(case.inputs["right"])

    from rtdsl.prepared_execution import make_prepared_input_fingerprint
    from rtdsl.prepared_execution import run_segment_intersection_topology_stream_prepared_session
    from rtdsl.prepared_session_residency import ExplicitPreparedSessionCache

    cache = ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> PreparedExecutionRayJoinSegmentIntersectionTopologyStream:
        return PreparedExecutionRayJoinSegmentIntersectionTopologyStream(
            left_segments,
            right_segments,
            dataset=resolved_dataset,
            dataset_note=case.note,
        )

    output_contract = "segment_segment_intersection_count_by_left_id_dense_device_column"
    result = run_segment_intersection_topology_stream_prepared_session(
        query_stream_fingerprint={
            "left_segments": make_prepared_input_fingerprint(left_segments),
            "query_stream_shape": "prepared_left_segment_set",
        },
        static_scene_fingerprint={
            "right_segments": make_prepared_input_fingerprint(right_segments),
        },
        output_contract=output_contract,
        query_count=len(left_segments),
        right_segment_count=len(right_segments),
        backend="optix",
        partner="none",
        cache=cache,
        prepare_session=prepare_session,
        run_topology_stream=lambda prepared: prepared.run(),
        measured_run_prepared=lambda prepared: prepared.run_hot(),
        finalize_output=lambda prepared, output: prepared.finalize_run(output),
        validate_output=lambda output: {
            "dense_source_row_count_matches_summary": (
                int(output["row_count"])
                == int(output["dense_left_id_count_columns"]["source_row_count"])
            ),
            "dense_output_device_resident": bool(
                output["dense_left_id_count_columns"]["device_resident"]
            ),
            "output_contract_matches": (
                output["summary"]["output_contract"] == output_contract
            ),
        },
        warmup_count=warmup,
        measured_repeat_count=query_repeat,
    )
    payload = dict(result.output)
    payload["prepared_execution_session_runner"] = result.to_metadata()
    payload["productized_execution_path"] = "prepared_execution_session_runner"
    payload["runtime_trunk_executes_end_to_end"] = bool(
        result.to_metadata()["runtime_trunk_executes_end_to_end"]
    )
    payload["internal_device_residency_between_rtdl_phases"] = bool(
        result.to_metadata()["internal_device_residency_between_rtdl_phases"]
    )
    payload["hot_path_host_materialization"] = bool(
        result.to_metadata()["hot_path_host_materialization"]
    )
    payload["release_authorized"] = False
    payload["public_speedup_claim_authorized"] = False
    payload["broad_v3_faster_than_v2_claim_authorized"] = False
    payload["full_all_app_rerun_authorized_by_this_packet"] = False
    payload["focused_pod_spend_authorized_by_this_packet"] = False
    return payload


class RayJoinOptixShapePairActiveCountPackedLeftShapes:
    """App-layer packed left closed shapes for repeated active-count queries."""

    def __init__(self, left_shapes) -> None:
        phases: dict[str, float] = {}
        from rtdsl.optix_runtime import pack_polygons
        from rtdsl.optix_runtime import prepare_shape_pair_relation_left_set_optix

        self.packed_polygons = _phase_time(
            phases,
            "left_shape_pack_sec",
            lambda: pack_polygons(records=left_shapes),
        )
        self.prepared_left_set = _phase_time(
            phases,
            "prepared_left_set_sec",
            lambda: prepare_shape_pair_relation_left_set_optix(self.packed_polygons),
        )
        self.pack_seconds = phases["left_shape_pack_sec"]
        self.prepared_left_set_seconds = phases["prepared_left_set_sec"]
        self.count = int(self.packed_polygons.polygon_count)
        self.id_capacity = max(
            1,
            max(
                int(self.packed_polygons.refs[index].id)
                for index in range(int(self.packed_polygons.polygon_count))
            )
            + 1
            if int(self.packed_polygons.polygon_count)
            else 1,
        )
        self._closed = False

    def close(self) -> None:
        if not self._closed:
            self.prepared_left_set.close()
            self._closed = True

    def __enter__(self) -> "RayJoinOptixShapePairActiveCountPackedLeftShapes":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def pack_rayjoin_optix_shape_pair_active_count_left_shapes(
    left_shapes,
) -> RayJoinOptixShapePairActiveCountPackedLeftShapes:
    return RayJoinOptixShapePairActiveCountPackedLeftShapes(left_shapes)


class PreparedRayJoinOptixShapePairActiveCount:
    """Python app-layer prepared handle for repeated generic shape-pair active counts."""

    def __init__(
        self,
        right_shapes,
        *,
        dataset: str = "direct_shapes",
        dataset_note: str = "Direct closed-shape inputs supplied by the caller.",
    ) -> None:
        self._right_shapes, self._right_shape_count = _reusable_shape_input(right_shapes)
        self._dataset = dataset
        self._dataset_note = dataset_note
        self._closed = False
        phases: dict[str, float] = {}

        from rtdsl.optix_runtime import prepare_shape_pair_relation_flags_optix

        self._prepared = _phase_time(
            phases,
            "prepare_static_scene_sec",
            lambda: prepare_shape_pair_relation_flags_optix(self._right_shapes),
        )
        self.prepare_static_scene_sec = phases["prepare_static_scene_sec"]

    def close(self) -> None:
        if not self._closed:
            self._prepared.close()
            self._closed = True

    def __enter__(self) -> "PreparedRayJoinOptixShapePairActiveCount":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def pack_left_shapes(self, left_shapes) -> RayJoinOptixShapePairActiveCountPackedLeftShapes:
        return pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)

    def run(
        self,
        left_shapes,
        *,
        dataset_note: str | None = None,
        query_repeat: int = 1,
        warmup: int = 0,
    ) -> dict[str, object]:
        packed_left = self.pack_left_shapes(left_shapes)
        try:
            payload = self.run_packed_left(
                packed_left,
                dataset_note=dataset_note,
                query_repeat=query_repeat,
                warmup=warmup,
            )
        finally:
            packed_left.close()
        payload["phases_sec"] = {
            "left_shape_pack_sec": packed_left.pack_seconds,
            "prepared_left_set_sec": packed_left.prepared_left_set_seconds,
            **payload["phases_sec"],
        }
        payload["packed_left_reuse"] = {
            **payload["packed_left_reuse"],
            "enabled": False,
            "left_shape_pack_paid_in_call": True,
            "native_prepared_left_set_paid_in_call": True,
        }
        return payload

    def run_packed_left(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        dataset_note: str | None = None,
        query_repeat: int = 1,
        warmup: int = 0,
    ) -> dict[str, object]:
        return self.run_packed_left_device_continuation(
            packed_left,
            dataset_note=dataset_note,
            query_repeat=query_repeat,
            warmup=warmup,
        )

    def run_packed_left_host_exact(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        dataset_note: str | None = None,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared RayJoin shape-pair active-count handle is closed")
        if not isinstance(packed_left, RayJoinOptixShapePairActiveCountPackedLeftShapes):
            raise TypeError("packed_left must be produced by pack_rayjoin_optix_shape_pair_active_count_left_shapes")

        phases: dict[str, float] = {}
        active_count = int(
            _phase_time(
                phases,
                "active_count_sec",
                lambda: self._prepared.count_active(packed_left.packed_polygons),
            )
        )
        native_phase_timings = self._prepared.last_phase_timings()
        return {
            "app": "rayjoin_v2_spatial_join",
            "workload": "overlay_seed",
            "execution_route": "prepared_optix_shape_pair_active_count_reuse",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": dataset_note or self._dataset_note,
            "row_count": active_count,
            "summary": {
                "active_seed_count": active_count,
                "output_contract": "overlay_active_pair_dependency_count",
            },
            "phases_sec": phases,
            "native_phase_timings": native_phase_timings,
            "prepared_reuse": {
                "enabled": True,
                "right_shape_count": self._right_shape_count,
                "prepare_static_scene_sec": self.prepare_static_scene_sec,
                "prepare_static_scene_paid_once": True,
            },
            "packed_left_reuse": {
                "enabled": True,
                "left_shape_count": packed_left.count,
                "pack_seconds": packed_left.pack_seconds,
                "left_shape_pack_paid_in_call": False,
            },
            "device_resident_continuation_status": (
                "shape_pair_active_count_complete: generic shape-pair relation flags are "
                "reduced to a scalar active count without materializing full relation rows; "
                "full overlay row continuation remains a separate route"
            ),
            "native_engine_boundary": (
                "The engine sees generic prepared shape-pair relation flags and active-count reduction. "
                "RayJoin overlay-seed interpretation and repeated-query reuse stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    def run_packed_left_device_continuation(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        dataset_note: str | None = None,
        query_repeat: int = 1,
        warmup: int = 0,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared RayJoin shape-pair active-count handle is closed")
        if not isinstance(packed_left, RayJoinOptixShapePairActiveCountPackedLeftShapes):
            raise TypeError("packed_left must be produced by pack_rayjoin_optix_shape_pair_active_count_left_shapes")
        if query_repeat <= 0:
            raise ValueError("query_repeat must be positive")
        if warmup < 0:
            raise ValueError("warmup must be non-negative")

        phases: dict[str, float] = {}
        executor = _phase_time(
            phases,
            "prepare_active_count_executor_sec",
            lambda: self._prepared.prepare_active_count_prepared_left_executor(
                packed_left.prepared_left_set
            ),
        )
        try:
            active_count = int(
                _phase_repeat_time(
                    phases,
                    "prepared_query_sec",
                    query_repeat=query_repeat,
                    warmup=warmup,
                    fn=executor.run,
                    stability_value=lambda value: int(value),
                )
            )
            executor_metadata = executor.to_metadata()
        finally:
            executor.close()
        phases["active_count_device_continuation_sec"] = phases["prepared_query_sec"]
        native_phase_timings = self._prepared.last_phase_timings()
        topology_stream_output_contract = "overlay_active_pair_dependency_count"
        topology_stream_query_count = int(packed_left.count) * int(self._right_shape_count)
        topology_m3_phases = {
            "prepare_static_scene_sec": self.prepare_static_scene_sec,
            "left_shape_pack_sec": packed_left.pack_seconds,
            "prepare_left_set_sec": packed_left.prepared_left_set_seconds,
            **phases,
        }
        topology_stream_m3_phase_table = build_topology_stream_m3_phase_table(
            phases_sec=topology_m3_phases,
            native_phase_timings=native_phase_timings or {},
            output_contract=topology_stream_output_contract,
            query_count=topology_stream_query_count,
            repeat=query_repeat,
            warmup=warmup,
            query_stream_resident=True,
            table_basis=(
                "prepared_optix_shape_pair_active_count_phase_timers_plus_native_last_phase_timings; "
                "non-authorizing V3 topology-stream accounting"
            ),
        )
        topology_stream_prepared_handle = build_topology_stream_prepared_handle_metadata(
            backend="optix",
            generic_capability="point_location_topology_stream",
            output_contract=topology_stream_output_contract,
            query_count=topology_stream_query_count,
            static_scene_prepared=True,
            query_stream_prepared=True,
            query_stream_residency=(
                "device_resident_prepared_left_shape_set_with_reusable_active_count_executor"
            ),
            m3_phase_table=topology_stream_m3_phase_table,
        )
        return {
            "app": "rayjoin_v2_spatial_join",
            "workload": "overlay_seed",
            "execution_route": "prepared_optix_shape_pair_active_count_device_continuation_reuse",
            "backend": "optix",
            "dataset": self._dataset,
            "dataset_note": dataset_note or self._dataset_note,
            "row_count": active_count,
            "summary": {
                "active_seed_count": active_count,
                "output_contract": topology_stream_output_contract,
            },
            "phases_sec": phases,
            "native_phase_timings": native_phase_timings,
            "topology_stream_m3_phase_table": topology_stream_m3_phase_table,
            "topology_stream_prepared_handle": topology_stream_prepared_handle,
            "prepared_reuse": {
                "enabled": True,
                "right_shape_count": self._right_shape_count,
                "prepare_static_scene_sec": self.prepare_static_scene_sec,
                "prepare_static_scene_paid_once": True,
            },
            "packed_left_reuse": {
                "enabled": True,
                "left_shape_count": packed_left.count,
                "pack_seconds": packed_left.pack_seconds,
                "native_prepared_left_set_enabled": True,
                "native_prepared_left_set_seconds": packed_left.prepared_left_set_seconds,
                "native_prepared_left_set_paid_once": True,
                "left_shape_pack_paid_in_call": False,
            },
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_query_total_sec": float(phases["prepared_query_sec_total_sec"]),
                "reported_query_metric": "prepared_query_median",
            },
            "prepared_active_count_executor": {
                **executor_metadata,
                "prepare_seconds": phases["prepare_active_count_executor_sec"],
                "timed_query_uses_executor_run": True,
            },
            "device_resident_continuation_status": (
                "shape_pair_active_count_prepared_left_executor_device_continuation_probe: generic "
                "shape-pair relation segment flags stay on device, the left closed-shape "
                "payload is reused through a prepared-left native handle, reusable native "
                "buffers/params back repeated active-count runs, containment and active-count "
                "reduction run in a generic CUDA continuation, and only the scalar count is copied back"
            ),
            "native_engine_boundary": (
                "The engine sees generic prepared shape-pair relation flags and a generic "
                "device-side active-count continuation. RayJoin overlay-seed interpretation "
                "and repeated-query reuse stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "v2_8_release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    def active_relation_device_columns(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        max_rows: int | None = None,
    ):
        if self._closed:
            raise RuntimeError("prepared RayJoin shape-pair active-count handle is closed")
        if not isinstance(packed_left, RayJoinOptixShapePairActiveCountPackedLeftShapes):
            raise TypeError("packed_left must be produced by pack_rayjoin_optix_shape_pair_active_count_left_shapes")
        return self._prepared.active_relation_device_columns(
            packed_left.packed_polygons,
            max_rows=max_rows,
        )

    def run_packed_left_active_relation_device_columns(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        max_rows: int | None = None,
        dataset_note: str | None = None,
    ) -> dict[str, object]:
        phases: dict[str, float] = {}
        columns = _phase_time(
            phases,
            "active_relation_device_columns_sec",
            lambda: self.active_relation_device_columns(packed_left, max_rows=max_rows),
        )
        try:
            metadata = columns.to_metadata()
            native_phase_timings = self._prepared.last_phase_timings()
            active_count = int(columns.active_relation_count)
            row_count = int(columns.row_count)
            return {
                "app": "rayjoin_v2_spatial_join",
                "workload": "overlay_seed",
                "execution_route": "prepared_optix_shape_pair_active_relation_device_columns_reuse",
                "backend": "optix",
                "dataset": self._dataset,
                "dataset_note": dataset_note or self._dataset_note,
                "row_count": row_count,
                "summary": {
                    "active_seed_count": active_count,
                    "device_relation_column_row_count": row_count,
                    "output_contract": "overlay_active_pair_dependency_relation_columns",
                    "overflow": bool(columns.overflow),
                    "retry_capacity_hint": columns.retry_capacity_hint,
                },
                "phases_sec": phases,
                "native_phase_timings": native_phase_timings,
                "device_relation_columns": metadata,
                "prepared_reuse": {
                    "enabled": True,
                    "right_shape_count": self._right_shape_count,
                    "prepare_static_scene_sec": self.prepare_static_scene_sec,
                    "prepare_static_scene_paid_once": True,
                },
                "packed_left_reuse": {
                    "enabled": True,
                    "left_shape_count": packed_left.count,
                    "pack_seconds": packed_left.pack_seconds,
                    "left_shape_pack_paid_in_call": False,
                },
                "device_resident_continuation_status": (
                    "shape_pair_active_relation_device_columns: generic shape-pair relation flags "
                    "stay on device and compact active relation ids plus dependency flags into "
                    "resident columns; full overlay witness expansion remains a separate route"
                ),
                "native_engine_boundary": (
                    "The engine sees generic shape-pair relation flags and generic active relation "
                    "device columns. RayJoin overlay interpretation and any richer relation-row "
                    "continuation stay in Python or partner code."
                ),
                "claim_boundary": {
                    "full_rayjoin_reproduction": False,
                    "paper_scale_perf_claim_authorized": False,
                    "rtdl_beats_rayjoin_claim_authorized": False,
                    "whole_app_speedup_claim_authorized": False,
                    "v2_8_release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "rt_core_speedup_claim_authorized": False,
                    "true_zero_copy_claim_authorized": False,
                },
            }
        finally:
            columns.close()

    def run_packed_left_active_relation_grouped_count_by_left(
        self,
        packed_left: RayJoinOptixShapePairActiveCountPackedLeftShapes,
        *,
        max_rows: int | None = None,
        group_capacity: int | None = None,
        dataset_note: str | None = None,
    ) -> dict[str, object]:
        phases: dict[str, float] = {}
        resolved_group_capacity = (
            int(group_capacity)
            if group_capacity is not None
            else max(1, int(packed_left.id_capacity))
        )
        columns = _phase_time(
            phases,
            "active_relation_device_columns_sec",
            lambda: self.active_relation_device_columns(packed_left, max_rows=max_rows),
        )
        try:
            grouped = _phase_time(
                phases,
                "active_relation_grouped_count_by_left_sec",
                lambda: columns.grouped_count_by_left_id_compact_device_columns(
                    group_capacity=resolved_group_capacity,
                ),
            )
            try:
                grouped_metadata = grouped.to_metadata()
                grouped_sum = None
                grouped_row_count = int(grouped.row_count)
                try:
                    counts = grouped.as_cupy_counts()
                    import cupy as cp  # type: ignore

                    grouped_sum = int(cp.sum(counts).get()) if int(counts.size) else 0
                except Exception as exc:  # pragma: no cover - pod dependency diagnostic
                    grouped_metadata["cupy_sum_error"] = str(exc)
                native_phase_timings = self._prepared.last_phase_timings()
                active_count = int(columns.active_relation_count)
                return {
                    "app": "rayjoin_v2_spatial_join",
                    "workload": "overlay_seed",
                    "execution_route": "prepared_optix_shape_pair_active_relation_grouped_count_by_left_reuse",
                    "backend": "optix",
                    "dataset": self._dataset,
                    "dataset_note": dataset_note or self._dataset_note,
                    "row_count": grouped_row_count,
                    "summary": {
                        "active_seed_count": active_count,
                        "grouped_left_row_count": grouped_row_count,
                        "group_capacity": resolved_group_capacity,
                        "grouped_count_sum": grouped_sum,
                        "grouped_count_sum_matches_active_count": (
                            grouped_sum == active_count if grouped_sum is not None else None
                        ),
                        "output_contract": "overlay_active_pair_dependency_count_by_left_id",
                        "relation_column_overflow": bool(columns.overflow),
                        "grouped_count_overflow": bool(grouped.overflow),
                    },
                    "phases_sec": phases,
                    "native_phase_timings": native_phase_timings,
                    "relation_column_metadata": columns.to_metadata(),
                    "grouped_count_metadata": grouped_metadata,
                    "prepared_reuse": {
                        "enabled": True,
                        "right_shape_count": self._right_shape_count,
                        "prepare_static_scene_sec": self.prepare_static_scene_sec,
                        "prepare_static_scene_paid_once": True,
                    },
                    "packed_left_reuse": {
                        "enabled": True,
                        "left_shape_count": packed_left.count,
                        "pack_seconds": packed_left.pack_seconds,
                        "left_shape_pack_paid_in_call": False,
                    },
                    "device_resident_continuation_status": (
                        "shape_pair_active_relation_grouped_count_by_left: generic active "
                        "relation columns feed the existing generic compact grouped-count "
                        "device-column reducer; richer overlay witnesses remain outside this route"
                    ),
                    "native_engine_boundary": (
                        "The engine sees generic relation columns and a generic grouped count by id. "
                        "RayJoin interpretation stays in Python."
                    ),
                    "claim_boundary": {
                        "full_rayjoin_reproduction": False,
                        "paper_scale_perf_claim_authorized": False,
                        "rtdl_beats_rayjoin_claim_authorized": False,
                        "whole_app_speedup_claim_authorized": False,
                        "v2_8_release_authorized": False,
                        "public_speedup_claim_authorized": False,
                        "rt_core_speedup_claim_authorized": False,
                        "true_zero_copy_claim_authorized": False,
                    },
                }
            finally:
                grouped.close()
        finally:
            columns.close()


def prepare_rayjoin_optix_shape_pair_active_count(
    right_shapes,
    *,
    dataset: str = "direct_shapes",
    dataset_note: str = "Direct closed-shape inputs supplied by the caller.",
) -> PreparedRayJoinOptixShapePairActiveCount:
    return PreparedRayJoinOptixShapePairActiveCount(
        right_shapes,
        dataset=dataset,
        dataset_note=dataset_note,
    )


def run_rayjoin_prepared_optix_shape_pair_active_count_workload(
    workload: str = "overlay_seed",
    *,
    dataset: str | None = None,
    query_repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    if workload != "overlay_seed":
        raise ValueError("prepared_optix_shape_pair_active_count currently supports only the overlay_seed workload")
    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    case = _load_rayjoin_case(workload, resolved_dataset)
    with prepare_rayjoin_optix_shape_pair_active_count(
        case.inputs["right"],
        dataset=resolved_dataset,
        dataset_note=case.note,
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(case.inputs["left"])
        try:
            return prepared.run_packed_left(
                packed_left,
                dataset_note=case.note,
                query_repeat=query_repeat,
                warmup=warmup,
            )
        finally:
            packed_left.close()


def run_rayjoin_workload(
    workload: str,
    *,
    backend: str = "cpu_python_reference",
    dataset: str | None = None,
    include_rows: bool = True,
) -> dict[str, object]:
    if workload not in _WORKLOADS:
        raise ValueError("workload must be one of: pip, lsi, overlay_seed")
    resolved_dataset = dataset or _DEFAULT_DATASETS[workload]
    baseline_workload = _BASELINE_WORKLOAD[workload]
    case = _load_rayjoin_case(workload, resolved_dataset)
    kernel = _KERNELS[workload]
    start = time.perf_counter()
    rows = _run_backend(kernel, backend, case.inputs)
    elapsed_sec = time.perf_counter() - start
    reference_rows = rows
    parity_vs_cpu_python_reference = True
    if backend != "cpu_python_reference":
        reference_rows = rt.run_cpu_python_reference(kernel, **case.inputs)
        parity_vs_cpu_python_reference = rt.compare_baseline_rows(
            baseline_workload,
            reference_rows,
            rows,
        )
    summary = _summarize_rows(workload, rows)
    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "backend": backend,
        "dataset": resolved_dataset,
        "dataset_note": case.note,
        "elapsed_sec": elapsed_sec,
        "row_count": len(rows),
        "summary": summary,
        "parity_vs_cpu_python_reference": parity_vs_cpu_python_reference,
        "rt_core_accelerated": backend == "optix",
        "native_engine_boundary": (
            "The engine sees generic point, segment, polygon, traversal, and row contracts. "
            "RayJoin application policy, face metadata, PIP positive filtering, and overlay "
            "continuation stay in Python/partner code."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "v2_0_release_authorized": False,
            "requires_pod_for_optix_perf": backend != "optix",
        },
    }
    if include_rows:
        payload["rows"] = rows
    return payload


def run_rayjoin_suite(
    *,
    backend: str = "cpu_python_reference",
    execution_route: str = "generic_kernel",
    result_mode: str = "rows",
    include_rows: bool = True,
    pip_count_mode: str = "exact",
    point_order_mode: str = "natural",
    query_repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    if execution_route == "prepared_optix":
        workloads = {
            workload: run_rayjoin_prepared_optix_workload(
                workload,
                result_mode=result_mode,
                include_rows=include_rows,
                count_mode=pip_count_mode if workload == "pip" else "exact",
                point_order_mode=point_order_mode if workload == "pip" else "natural",
                query_repeat=query_repeat,
                warmup=warmup,
                prepare_left_for_count=workload == "lsi" and result_mode == "count",
            )
            for workload in _PREPARED_OPTIX_WORKLOADS
        }
        prepared_query_total_sec = sum(
            float(result.get("phases_sec", {}).get("prepared_query_sec", 0.0))
            for result in workloads.values()
        )
        prepared_pack_total_sec = sum(
            float(result.get("phases_sec", {}).get("query_pack_sec", 0.0))
            + float(result.get("phases_sec", {}).get("static_shape_pack_sec", 0.0))
            for result in workloads.values()
        )
        prepared_scene_total_sec = sum(
            float(result.get("phases_sec", {}).get("prepare_static_scene_sec", 0.0))
            for result in workloads.values()
        )
        return {
            "app": "rayjoin_v2_spatial_join",
            "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
            "backend": "optix",
            "execution_route": execution_route,
            "workloads": workloads,
            "prepared_query_total_sec": prepared_query_total_sec,
            "prepared_query_total_measured_sec": sum(
                float(result.get("phases_sec", {}).get("prepared_query_sec_total_sec", 0.0))
                for result in workloads.values()
            ),
            "prepared_pack_total_sec": prepared_pack_total_sec,
            "prepared_scene_total_sec": prepared_scene_total_sec,
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "reported_query_metric": "sum_of_workload_prepared_query_medians",
            },
            "all_match_cpu_python_reference": None,
            "implementation_stage": "prepared_v2_benchmark_route",
            "next_stage": (
                "Run this route on an RTX pod against RayJoin-exported streams and compare "
                "phase boundaries to RayJoin query_exec. Full polygon materialization remains "
                "outside the overlay-seed benchmark contract."
            ),
        }
    if execution_route == "prepared_optix_left_id_dense_count":
        return {
            "app": "rayjoin_v2_spatial_join",
            "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
            "backend": "optix",
            "execution_route": execution_route,
            "workloads": {
                "lsi": run_rayjoin_prepared_optix_left_id_dense_count_workload(
                    "lsi",
                    include_rows=include_rows,
                )
            },
            "all_match_cpu_python_reference": None,
            "implementation_stage": "prepared_dense_left_id_count_route",
            "native_engine_boundary": (
                "The engine sees a generic segment-pair left-id count device-column primitive. "
                "RayJoin interpretation and ID remapping stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }
    if execution_route == "prepared_execution_segment_intersection_topology_stream":
        return {
            "app": "rayjoin_v2_spatial_join",
            "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
            "backend": "optix",
            "execution_route": execution_route,
            "workloads": {
                "lsi": run_rayjoin_prepared_execution_segment_intersection_topology_stream_workload(
                    "lsi",
                    query_repeat=query_repeat,
                    warmup=warmup,
                )
            },
            "all_match_cpu_python_reference": None,
            "implementation_stage": "prepared_execution_segment_intersection_topology_stream_route",
            "native_engine_boundary": (
                "The engine sees a generic segment-intersection topology stream. "
                "RayJoin interpretation and ID remapping stay in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }
    if execution_route == "prepared_optix_shape_pair_active_count":
        return {
            "app": "rayjoin_v2_spatial_join",
            "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
            "backend": "optix",
            "execution_route": execution_route,
            "workloads": {
                "overlay_seed": run_rayjoin_prepared_optix_shape_pair_active_count_workload(
                    "overlay_seed",
                )
            },
            "all_match_cpu_python_reference": None,
            "implementation_stage": "prepared_shape_pair_active_count_route",
            "native_engine_boundary": (
                "The engine sees a generic prepared shape-pair active-count primitive. "
                "RayJoin overlay-seed interpretation stays in Python."
            ),
            "claim_boundary": {
                "full_rayjoin_reproduction": False,
                "paper_scale_perf_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }
    workloads = {
        workload: run_rayjoin_workload(
            workload,
            backend=backend,
            include_rows=include_rows,
        )
        for workload in _WORKLOADS
    }
    return {
        "app": "rayjoin_v2_spatial_join",
        "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
        "backend": backend,
        "execution_route": execution_route,
        "workloads": workloads,
        "all_match_cpu_python_reference": all(
            bool(row["parity_vs_cpu_python_reference"])
            for row in workloads.values()
        ),
        "implementation_stage": "first_v2_user_slice",
        "next_stage": (
            "Run the same suite on an OptiX pod, then promote the highest-value path "
            "from compatibility evidence into reviewed performance evidence."
        ),
    }


def v2_5_plan_payload() -> dict[str, object]:
    return {
        "app": "rayjoin_v2_spatial_join",
        "paper": "RayJoin: Fast and Precise Spatial Join, ICS 2024",
        "v2_5_primitive_first_plan": {
            "selected_path": "prepared_generic_rtdl_count_or_parity",
            "selected_primitives": (
                "prepared_point_closed_shape_positive_hit_count",
                "prepared_segment_pair_intersection_count",
                "prepared_shape_pair_overlap_seed_count",
            ),
            "typed_hit_stream_forced": False,
            "partner_continuation_required": False,
            "partner_continuation_reserved_for": (
                "optional compact-mask or grouped-count post-processing only when "
                "that continuation enters benchmark timing"
            ),
            "alternative_path": "compact_mask_i64_or_segmented_count_i64_triton_continuation",
        },
        "native_engine_boundary": (
            "The native engine sees generic prepared point/closed-shape, segment-pair, "
            "and shape-pair contracts. RayJoin paper semantics and row interpretation "
            "stay in the app layer."
        ),
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "triton_speedup_claim_authorized": False,
            "primitive_first_plan_only": True,
        },
    }


def primitive_first_plan_payload() -> dict[str, object]:
    """Current alias for the legacy v2.5 primitive-first planning payload."""

    payload = v2_5_plan_payload()
    return {
        **payload,
        "mode": "primitive_first_plan",
        "legacy_mode_alias": "v2_5_plan",
    }


def describe_rayjoin_v2_6_numba_compact_mask_continuation(
    workload: str = "pip",
) -> dict[str, object]:
    if workload not in _WORKLOADS:
        raise ValueError("workload must be one of: pip, lsi, overlay_seed")
    return {
        "contract_version": RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION,
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "mode": "v2_6_numba_compact_mask_plan",
        "selected_partner": "numba",
        "status": "preview_ready_not_promoted",
        "operation": "compact_mask_i64",
        "numba_descriptor": rt.describe_numba_compact_mask_i64(),
        "requires_device_resident_columns": True,
        "uses_v2_6_neutral_partner_handoff": True,
        "uses_v2_8_segmented_typed_stream_front_door": True,
        "uses_legacy_torch_carrier": False,
        "uses_torch_conversion": False,
        "input_columns": ("candidate_row_ids:int64", "keep_mask:bool"),
        "output_columns": ("selected_candidate_row_ids:int64", "original_indices:int64"),
        "post_rt_continuation_only": True,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "app_owned_lowering": (
            "RayJoin workload semantics, positive-hit filtering, pair-dependency "
            "interpretation, and paper-specific policy remain app code. RTDL/Numba "
            "sees only generic candidate row ids and a boolean keep mask."
        ),
        "integration_decision": (
            "Keep prepared generic RTDL count/parity primitives as the recommended "
            "fast path when scalar counts are enough. Use the v2.6 Numba compact-mask "
            "path for retained row streams or downstream tensor post-processing."
        ),
    }


def describe_rayjoin_segmented_compact_mask_numba_continuation(
    workload: str = "pip",
) -> dict[str, object]:
    """Current alias for the legacy v2.6 Numba compact-mask continuation."""

    plan = describe_rayjoin_v2_6_numba_compact_mask_continuation(workload)
    return {
        **plan,
        "mode": "segmented_compact_mask_numba_plan",
        "legacy_mode_alias": "v2_6_numba_compact_mask_plan",
        "legacy_helper_alias": "describe_rayjoin_v2_6_numba_compact_mask_continuation",
    }


def v2_6_numba_compact_mask_plan_payload(workload: str = "pip") -> dict[str, object]:
    plan = describe_rayjoin_v2_6_numba_compact_mask_continuation(workload)
    return {
        **plan,
        "command_shape": (
            "Use run_rayjoin_v2_6_numba_compact_mask_preview(...) from Python with "
            "Numba CUDA device arrays for candidate_row_ids:int64 and keep_mask:bool. "
            "The legacy v2.6 app helper now routes through the generic v2.8 "
            "segmented typed-stream partner front door."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "numba_speedup_claim_authorized": False,
            "v2_6_release_authorized": False,
        },
    }


def segmented_compact_mask_numba_plan_payload(workload: str = "pip") -> dict[str, object]:
    """Current alias for the legacy v2.6 Numba compact-mask plan payload."""

    plan = describe_rayjoin_segmented_compact_mask_numba_continuation(workload)
    return {
        **v2_6_numba_compact_mask_plan_payload(workload),
        "mode": "segmented_compact_mask_numba_plan",
        "legacy_mode_alias": "v2_6_numba_compact_mask_plan",
        "legacy_plan": plan,
        "command_shape": (
            "Use run_rayjoin_segmented_compact_mask_numba_preview(...) from Python "
            "with Numba CUDA device arrays for candidate_row_ids:int64 and "
            "keep_mask:bool. The legacy v2.6 helper remains available as a "
            "compatibility alias."
        ),
    }


def run_rayjoin_v2_6_numba_compact_mask_preview(
    inputs: dict[str, object],
    *,
    workload: str = "pip",
    block_size: int = 256,
) -> dict[str, object]:
    plan = describe_rayjoin_v2_6_numba_compact_mask_continuation(workload)
    candidate_row_ids = inputs["candidate_row_ids"]
    keep_mask = inputs["keep_mask"]
    handoff = rt.prepare_v2_6_neutral_partner_handoff(
        {
            "candidate_row_ids": candidate_row_ids,
            "keep_mask": keep_mask,
        },
        partner="numba",
        consumer="rayjoin_v2_6_numba_compact_mask_continuation",
        access_modes={"candidate_row_ids": "read", "keep_mask": "read"},
    )
    handoff_validation = rt.validate_v2_6_neutral_partner_handoff(handoff)
    if handoff_validation["status"] != "accept":
        raise RuntimeError(
            "RayJoin v2.6 Numba neutral handoff rejected: "
            f"{handoff_validation['errors']}"
        )

    result = rt.execute_compact_mask_typed_stream_partner_columns(
        values=candidate_row_ids,
        mask=keep_mask,
        partner="numba",
        stream_id=f"rayjoin_{workload}_v2_8_compact_mask_schema",
        producer_primitive="app_supplied_candidate_row_stream",
        block_size=block_size,
    )
    partner_metadata = result["partner_metadata"]
    outputs = {
        "selected_candidate_row_ids": result["outputs"]["values"],
        "original_indices": result["outputs"]["original_indices"],
    }
    return {
        "app": "rayjoin_v2_spatial_join",
        "workload": workload,
        "mode": "v2_6_numba_compact_mask_preview",
        "partner": "numba",
        "status": "preview_not_promoted",
        "operation": "compact_mask_i64",
        "outputs": outputs,
        "metadata": {
            "v2_6_numba_compact_mask_plan": plan,
            "v2_6_neutral_handoff_validation": handoff_validation,
            "v2_8_typed_stream_front_door_request": {
                "adapter_version": result["adapter_version"],
                "operation": result["operation"],
                "stream_id": result["stream_id"],
                "input_column_mapping": result["input_column_mapping"],
                "requires_caller_supplied_partner_columns": result[
                    "requires_caller_supplied_partner_columns"
                ],
            },
            "execution_path": "v2_8_segmented_typed_stream_compact_mask_front_door",
            "legacy_execution_path_alias": "v2_6_numba_compact_mask_front_door",
            "block_size": int(block_size),
            "stable_input_order": bool(partner_metadata.get("stable_input_order")),
            "host_prefix_sum_used": bool(partner_metadata.get("host_prefix_sum_used")),
            "v2_8_segmented_typed_stream_front_door_used": True,
            "v2_8_partner_consumer_promoted": bool(result["partner_consumer_promoted"]),
            "v2_8_release_authorized": bool(result["release_authorized"]),
            "post_rt_continuation_only": True,
            "replaces_rt_traversal": False,
            "promoted_performance_path": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "uses_legacy_torch_carrier": False,
            "uses_torch_conversion": False,
            "phase_timing": {
                "phases_sec": {
                    "partner_continuation": float(
                        partner_metadata.get("numba_partner_continuation_elapsed_seconds", 0.0)
                    )
                }
            },
        },
    }


def run_rayjoin_segmented_compact_mask_numba_preview(
    inputs: dict[str, object],
    *,
    workload: str = "pip",
    block_size: int = 256,
) -> dict[str, object]:
    """Current alias for the legacy v2.6 compact-mask preview runner."""

    payload = run_rayjoin_v2_6_numba_compact_mask_preview(
        inputs,
        workload=workload,
        block_size=block_size,
    )
    return {
        **payload,
        "mode": "segmented_compact_mask_numba_preview",
        "legacy_mode_alias": "v2_6_numba_compact_mask_preview",
    }


def _side_aware_owner_face_from_topology_row(row: dict[str, int]) -> tuple[int, str]:
    if int(row.get("has_left_face", 0)) and int(row.get("left_face_id", 0)) != 0:
        return int(row["left_face_id"]), "left"
    if int(row.get("has_right_face", 0)) and int(row.get("right_face_id", 0)) != 0:
        return int(row["right_face_id"]), "right"
    return -1, "either"


def _device_i64_tuple(values) -> tuple[int, ...]:
    if hasattr(values, "copy_to_host"):
        values = values.copy_to_host()
    elif hasattr(values, "get"):
        values = values.get()
    return tuple(int(value) for value in values.tolist())


def _side_aware_topology_result_rows(result: dict[str, object]) -> tuple[dict[str, int], ...]:
    point_ids = _device_i64_tuple(result["point_id"])
    shape_ids = _device_i64_tuple(result["shape_id"])
    owner_face_ids = _device_i64_tuple(result["owner_face_id"])
    owner_side_codes = _device_i64_tuple(result["owner_side_code"])
    return tuple(
        {
            "point_id": point_id,
            "shape_id": shape_id,
            "owner_face_id": owner_face_id,
            "owner_side_code": owner_side_code,
        }
        for point_id, shape_id, owner_face_id, owner_side_code in zip(
            point_ids,
            shape_ids,
            owner_face_ids,
            owner_side_codes,
        )
    )


def run_rayjoin_v2_9_numba_side_aware_topology_reference(
    *,
    dataset: str | None = None,
    limit_chains: int | None = None,
    include_rows: bool = True,
) -> dict[str, object]:
    """Run the app-facing Numba side-aware topology reference route.

    This is an app-owned continuation route over generic topology columns. It is
    deliberately separate from the promoted RTDL/OptiX RayJoin route.
    """

    resolved_dataset = dataset or _DEFAULT_DATASETS["pip"]
    phases: dict[str, float] = {}
    cdb = _phase_time(
        phases,
        "load_cdb_sec",
        lambda: load_cdb(_resolve_dataset_path(resolved_dataset)),
    )
    topology_rows = _phase_time(
        phases,
        "topology_rows_sec",
        lambda: chains_to_topology_rows(cdb, limit_chains=limit_chains),
    )
    if not topology_rows:
        raise ValueError("side-aware topology reference requires at least one topology row")

    candidate_point_ids: list[int] = []
    candidate_shape_ids: list[int] = []
    candidate_point_ordinals: list[int] = []
    candidate_shape_ordinals: list[int] = []
    owner_point_ids: list[int] = []
    owner_point_ordinals: list[int] = []
    owner_face_ids: list[int] = []
    owner_side_codes: list[str] = []
    topology_shape_ids: list[int] = []
    topology_left_face_ids: list[int] = []
    topology_right_face_ids: list[int] = []
    topology_has_left_faces: list[int] = []
    topology_has_right_faces: list[int] = []

    for ordinal, row in enumerate(topology_rows):
        chain_id = int(row["chain_id"])
        point_id = int(row["first_point_id"])
        owner_face, owner_side = _side_aware_owner_face_from_topology_row(row)
        candidate_point_ids.append(point_id)
        candidate_shape_ids.append(chain_id)
        candidate_point_ordinals.append(ordinal)
        candidate_shape_ordinals.append(ordinal)
        owner_point_ids.append(point_id)
        owner_point_ordinals.append(ordinal)
        owner_face_ids.append(owner_face)
        owner_side_codes.append(owner_side)
        topology_shape_ids.append(chain_id)
        topology_left_face_ids.append(int(row["left_face_id"]))
        topology_right_face_ids.append(int(row["right_face_id"]))
        topology_has_left_faces.append(int(row["has_left_face"]))
        topology_has_right_faces.append(int(row["has_right_face"]))

    reference = _phase_time(
        phases,
        "python_column_reference_sec",
        lambda: rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(
            candidate_point_ids=tuple(candidate_point_ids),
            candidate_shape_ids=tuple(candidate_shape_ids),
            candidate_point_ordinals=tuple(candidate_point_ordinals),
            candidate_shape_ordinals=tuple(candidate_shape_ordinals),
            topology_shape_ids=tuple(topology_shape_ids),
            topology_shape_ordinals=tuple(candidate_shape_ordinals),
            topology_left_face_ids=tuple(topology_left_face_ids),
            topology_right_face_ids=tuple(topology_right_face_ids),
            topology_has_left_faces=tuple(topology_has_left_faces),
            topology_has_right_faces=tuple(topology_has_right_faces),
            owner_point_ids=tuple(owner_point_ids),
            owner_point_ordinals=tuple(owner_point_ordinals),
            owner_face_ids=tuple(owner_face_ids),
            owner_side_codes=tuple(owner_side_codes),
        ),
    )
    numba_result = _phase_time(
        phases,
        "numba_side_aware_topology_sec",
        lambda: rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba(
            candidate_point_ids=tuple(candidate_point_ids),
            candidate_shape_ids=tuple(candidate_shape_ids),
            candidate_point_ordinals=tuple(candidate_point_ordinals),
            candidate_shape_ordinals=tuple(candidate_shape_ordinals),
            topology_shape_ids=tuple(topology_shape_ids),
            topology_shape_ordinals=tuple(candidate_shape_ordinals),
            topology_left_face_ids=tuple(topology_left_face_ids),
            topology_right_face_ids=tuple(topology_right_face_ids),
            topology_has_left_faces=tuple(topology_has_left_faces),
            topology_has_right_faces=tuple(topology_has_right_faces),
            owner_point_ids=tuple(owner_point_ids),
            owner_point_ordinals=tuple(owner_point_ordinals),
            owner_face_ids=tuple(owner_face_ids),
            owner_side_codes=tuple(owner_side_codes),
        ),
    )
    numba_rows = _side_aware_topology_result_rows(numba_result)
    reference_rows = tuple(
        {
            "point_id": int(point_id),
            "shape_id": int(shape_id),
            "owner_face_id": int(owner_face_id),
            "owner_side_code": int(owner_side_code),
        }
        for point_id, shape_id, owner_face_id, owner_side_code in zip(
            reference["point_id"],
            reference["shape_id"],
            reference["owner_face_id"],
            reference["owner_side_code"],
        )
    )
    parity = reference_rows == numba_rows
    payload: dict[str, object] = {
        "app": "rayjoin_v2_spatial_join",
        "workload": "overlay_seed",
        "execution_route": "v2_9_numba_side_aware_topology_reference",
        "backend": "python+numba",
        "dataset": resolved_dataset,
        "row_count": len(numba_rows),
        "summary": {
            "input_topology_row_count": len(topology_rows),
            "candidate_count": len(candidate_point_ids),
            "python_reference_row_count": len(reference_rows),
            "numba_row_count": len(numba_rows),
            "parity_vs_python_columns": parity,
            "output_contract": "side_aware_owner_face_membership_rows",
        },
        "phases_sec": phases,
        "partner_reference": {
            "partner": "numba",
            "raw_cuda_kernel_required": False,
            "app_owned_policy": "owner_face_side",
            "helper": "filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba",
            "metadata": numba_result.get("_metadata", {}),
        },
        "native_engine_boundary": (
            "This route uses generic topology columns and an explicit Python-owned "
            "owner-face/side policy. It does not add RayJoin-specific native engine logic."
        ),
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
        },
    }
    if include_rows:
        payload["rows"] = numba_rows
        payload["reference_rows"] = reference_rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run RTDL v2 RayJoin-style PIP, LSI, and overlay-seed workloads."
    )
    parser.add_argument(
        "--workload",
        choices=(*_WORKLOADS, "all"),
        default="all",
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix"),
        default="cpu_python_reference",
    )
    parser.add_argument(
        "--execution-route",
        choices=(
            "generic_kernel",
            "prepared_optix",
            "prepared_optix_cupy_refined_pip",
            "prepared_optix_compact_grouped_count",
            "prepared_optix_left_id_dense_count",
            "prepared_optix_shape_pair_active_count",
            "prepared_execution_point_location_topology_stream",
            "prepared_execution_segment_intersection_topology_stream",
            "primitive_first_plan",
            "segmented_compact_mask_numba_plan",
            "v2_6_numba_compact_mask_plan",
            "v2_9_numba_side_aware_topology_reference",
        ),
        default="generic_kernel",
        help="Use the generic kernel route or the prepared OptiX benchmark route for PIP/LSI.",
    )
    parser.add_argument(
        "--result-mode",
        choices=("rows", "count"),
        default="rows",
        help="For prepared_optix, return witness rows or scalar counts.",
    )
    parser.add_argument(
        "--pip-count-mode",
        choices=_PIP_COUNT_MODES,
        default="exact",
        help=(
            "For prepared_optix PIP count, optionally time the device-filtered count "
            "only after validating it against the exact prepared count."
        ),
    )
    parser.add_argument(
        "--point-order-mode",
        choices=_PIP_POINT_ORDER_MODES,
        default="natural",
        help="For PIP prepared routes, choose the query point order used by both legacy and runner A/B paths.",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Override the default dataset for a single workload run.",
    )
    parser.add_argument(
        "--candidate-max-rows",
        type=int,
        default=None,
        help="Maximum candidate rows for prepared_optix_cupy_refined_pip; overflow fails closed.",
    )
    parser.add_argument(
        "--no-rows",
        action="store_true",
        help="Omit full row arrays and keep only summaries.",
    )
    parser.add_argument("--repeat", type=int, default=1, help="Repeat hot prepared-query phase.")
    parser.add_argument("--warmup", type=int, default=0, help="Prepared-query warmup iterations to drop.")
    args = parser.parse_args(argv)
    include_rows = not args.no_rows
    if args.execution_route == "prepared_optix_shape_pair_active_count" and args.point_order_mode != "natural":
        raise ValueError(
            "--point-order-mode is only valid for PIP point-location routes; "
            "prepared_optix_shape_pair_active_count uses overlay shape-pair inputs"
        )
    if args.workload == "all":
        if args.dataset is not None:
            raise ValueError("--dataset is only valid when --workload is not all")
        if args.execution_route == "primitive_first_plan":
            payload = primitive_first_plan_payload()
        elif args.execution_route in {"segmented_compact_mask_numba_plan", "v2_6_numba_compact_mask_plan"}:
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    workload: (
                        segmented_compact_mask_numba_plan_payload(workload)
                        if args.execution_route == "segmented_compact_mask_numba_plan"
                        else v2_6_numba_compact_mask_plan_payload(workload)
                    )
                    for workload in _WORKLOADS
                },
            }
        elif args.execution_route == "v2_9_numba_side_aware_topology_reference":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "overlay_seed": run_rayjoin_v2_9_numba_side_aware_topology_reference(
                        include_rows=include_rows,
                    )
                },
            }
        elif args.execution_route == "prepared_optix_compact_grouped_count":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "lsi": run_rayjoin_prepared_optix_compact_grouped_count_workload(
                        "lsi",
                        include_rows=include_rows,
                    )
                },
            }
        elif args.execution_route == "prepared_optix_left_id_dense_count":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "lsi": run_rayjoin_prepared_optix_left_id_dense_count_workload(
                        "lsi",
                        include_rows=include_rows,
                        query_repeat=args.repeat,
                        warmup=args.warmup,
                    )
                },
            }
        elif args.execution_route == "prepared_optix_cupy_refined_pip":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "pip": run_rayjoin_prepared_optix_cupy_refined_pip(
                        result_mode=args.result_mode,
                        include_rows=include_rows,
                        candidate_max_rows=args.candidate_max_rows,
                        query_repeat=args.repeat,
                        warmup=args.warmup,
                    )
                },
            }
        elif args.execution_route == "prepared_optix_shape_pair_active_count":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "overlay_seed": run_rayjoin_prepared_optix_shape_pair_active_count_workload(
                        "overlay_seed",
                        query_repeat=args.repeat,
                        warmup=args.warmup,
                    )
                },
            }
        elif args.execution_route == "prepared_execution_point_location_topology_stream":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "pip": run_rayjoin_prepared_execution_point_location_topology_stream_workload(
                        "pip",
                        point_order_mode=args.point_order_mode,
                        query_repeat=args.repeat,
                        warmup=args.warmup,
                    )
                },
            }
        elif args.execution_route == "prepared_execution_segment_intersection_topology_stream":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    "lsi": run_rayjoin_prepared_execution_segment_intersection_topology_stream_workload(
                        "lsi",
                        query_repeat=args.repeat,
                        warmup=args.warmup,
                    )
                },
            }
        else:
            payload = run_rayjoin_suite(
                backend=args.backend,
                execution_route=args.execution_route,
                result_mode=args.result_mode,
                include_rows=include_rows,
                pip_count_mode=args.pip_count_mode,
                point_order_mode=args.point_order_mode,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
    else:
        if args.execution_route == "primitive_first_plan":
            payload = primitive_first_plan_payload()
        elif args.execution_route in {"segmented_compact_mask_numba_plan", "v2_6_numba_compact_mask_plan"}:
            payload = (
                segmented_compact_mask_numba_plan_payload(args.workload)
                if args.execution_route == "segmented_compact_mask_numba_plan"
                else v2_6_numba_compact_mask_plan_payload(args.workload)
            )
        elif args.execution_route == "v2_9_numba_side_aware_topology_reference":
            if args.workload != "overlay_seed":
                raise ValueError("v2_9_numba_side_aware_topology_reference currently supports only overlay_seed")
            payload = run_rayjoin_v2_9_numba_side_aware_topology_reference(
                dataset=args.dataset,
                include_rows=include_rows,
            )
        elif args.execution_route == "prepared_optix_compact_grouped_count":
            payload = run_rayjoin_prepared_optix_compact_grouped_count_workload(
                args.workload,
                dataset=args.dataset,
                include_rows=include_rows,
            )
        elif args.execution_route == "prepared_optix_left_id_dense_count":
            payload = run_rayjoin_prepared_optix_left_id_dense_count_workload(
                args.workload,
                dataset=args.dataset,
                include_rows=include_rows,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        elif args.execution_route == "prepared_optix_cupy_refined_pip":
            if args.workload != "pip":
                raise ValueError("prepared_optix_cupy_refined_pip currently supports only --workload pip")
            payload = run_rayjoin_prepared_optix_cupy_refined_pip(
                dataset=args.dataset,
                result_mode=args.result_mode,
                include_rows=include_rows,
                candidate_max_rows=args.candidate_max_rows,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        elif args.execution_route == "prepared_optix_shape_pair_active_count":
            payload = run_rayjoin_prepared_optix_shape_pair_active_count_workload(
                args.workload,
                dataset=args.dataset,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        elif args.execution_route == "prepared_execution_point_location_topology_stream":
            payload = run_rayjoin_prepared_execution_point_location_topology_stream_workload(
                args.workload,
                dataset=args.dataset,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        elif args.execution_route == "prepared_execution_segment_intersection_topology_stream":
            payload = run_rayjoin_prepared_execution_segment_intersection_topology_stream_workload(
                args.workload,
                dataset=args.dataset,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        elif args.execution_route == "prepared_optix":
            payload = run_rayjoin_prepared_optix_workload(
                args.workload,
                dataset=args.dataset,
                result_mode=args.result_mode,
                include_rows=include_rows,
                count_mode=args.pip_count_mode,
                point_order_mode=args.point_order_mode,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
        else:
            payload = run_rayjoin_workload(
                args.workload,
                backend=args.backend,
                dataset=args.dataset,
                include_rows=include_rows,
            )
    print(json.dumps(_json_ready(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
