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
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from examples.reference.rtdl_language_reference import county_zip_join_reference
from rtdsl.baseline_runner import DatasetCase
from rtdsl.baseline_runner import load_representative_case
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_probe_points
from rtdsl.datasets import chains_to_segment_columns
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb


_WORKLOADS = ("pip", "lsi", "overlay_seed")
_PREPARED_OPTIX_WORKLOADS = ("pip", "lsi", "overlay_seed")
_PIP_BOUNDARY_EVENT_COUNT_MODE = "boundary_event_point_id_count_device_columns"
_PIP_COUNT_MODES = (
    "exact",
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
            "count_mode must be 'exact', 'device_filtered_validated', "
            "'device_filtered_prepared_points_validated', "
            "'point_id_count_device_columns_validated', or "
            f"'{_PIP_BOUNDARY_EVENT_COUNT_MODE}'"
        )
    if count_mode != "exact" and (workload != "pip" or result_mode != "count"):
        raise ValueError("non-exact count_mode is only valid for PIP count workloads")
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
        prepared_point_columns = None
        boundary_event_count_metadata: dict[str, object] | None = None
        boundary_event_columns = None
        boundary_event_count_columns = None
        prepared_point_batch_executor = None
        try:
            if result_mode == "count":
                if count_mode in _PIP_POSITIVE_COUNT_MODES:
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
            native_phase_timings = prepared.last_phase_timings()
        finally:
            if prepared_point_batch_executor is not None:
                prepared_point_batch_executor.close()
            if prepared_point_columns is not None:
                prepared_point_columns.close()
            if boundary_event_count_columns is not None:
                boundary_event_count_columns.close()
            if boundary_event_columns is not None:
                boundary_event_columns.close()
            prepared.close()
        summary = {
            "positive_hit_row_count": row_count if count_mode != _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "positive_assignment_count": row_count if count_mode != _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "boundary_event_row_count": row_count if count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE else None,
            "output_contract": (
                "point_closed_shape_first_boundary_event_count_by_point_id_device_columns"
                if count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE
                else (
                    (
                        "point_to_shape_positive_hit_count_device_filtered_validated"
                        if count_mode == "device_filtered_validated"
                        else (
                            "point_to_shape_positive_hit_count_device_filtered_prepared_points_validated"
                            if count_mode == "device_filtered_prepared_points_validated"
                            else "point_to_shape_positive_hit_count_by_point_id_device_columns_validated"
                        )
                    )
                    if count_mode in _PIP_POSITIVE_COUNT_MODES
                    else "point_to_shape_positive_hit_count"
                )
                if result_mode == "count"
                else "point_to_shape_positive_hit_rows"
            ),
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
        "repeat_protocol": {
            "repeat": int(query_repeat),
            "warmup": int(warmup),
            "measured_query_total_sec": float(phases.get("prepared_query_sec_total_sec", phases["prepared_query_sec"])),
            "reported_query_metric": "prepared_query_median",
        },
        "point_order_mode": point_order_mode if workload == "pip" else None,
        "segment_order_mode": segment_order_mode if workload == "lsi" else None,
        "device_resident_continuation_status": (
            "overlay_seed_prepared_pair_dependency_flags_complete"
            if workload == "overlay_seed"
            else (
                "boundary_event_grouped_count_device_columns_complete: first-boundary-event columns "
                "and grouped point-id counts remain CUDA-resident; this is not a PIP membership contract"
                if workload == "pip" and count_mode == _PIP_BOUNDARY_EVENT_COUNT_MODE
                else (
                "not_complete: prepared query can avoid Python row materialization for counts, "
                "but generic downstream row-stream continuation still needs pod/native work"
                )
            )
        ),
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


class RayJoinOptixShapePairActiveCountPackedLeftShapes:
    """App-layer packed left closed shapes for repeated active-count queries."""

    def __init__(self, left_shapes) -> None:
        phases: dict[str, float] = {}
        from rtdsl.optix_runtime import pack_polygons

        self.packed_polygons = _phase_time(
            phases,
            "left_shape_pack_sec",
            lambda: pack_polygons(records=left_shapes),
        )
        self.pack_seconds = phases["left_shape_pack_sec"]
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
        payload = self.run_packed_left(
            packed_left,
            dataset_note=dataset_note,
            query_repeat=query_repeat,
            warmup=warmup,
        )
        payload["phases_sec"] = {
            "left_shape_pack_sec": packed_left.pack_seconds,
            **payload["phases_sec"],
        }
        payload["packed_left_reuse"] = {
            **payload["packed_left_reuse"],
            "enabled": False,
            "left_shape_pack_paid_in_call": True,
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
        active_count = int(
            _phase_repeat_time(
                phases,
                "prepared_query_sec",
                query_repeat=query_repeat,
                warmup=warmup,
                fn=lambda: self._prepared.count_active_device_continuation(packed_left.packed_polygons),
                stability_value=lambda value: int(value),
            )
        )
        phases["active_count_device_continuation_sec"] = phases["prepared_query_sec"]
        native_phase_timings = self._prepared.last_phase_timings()
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
            "repeat_protocol": {
                "repeat": int(query_repeat),
                "warmup": int(warmup),
                "measured_query_total_sec": float(phases["prepared_query_sec_total_sec"]),
                "reported_query_metric": "prepared_query_median",
            },
            "device_resident_continuation_status": (
                "shape_pair_active_count_device_continuation_probe: generic shape-pair relation "
                "segment flags stay on device, containment and active-count reduction run in a "
                "generic CUDA continuation, and only the scalar count is copied back"
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
        return prepared.run_packed_left(
            packed_left,
            dataset_note=case.note,
            query_repeat=query_repeat,
            warmup=warmup,
        )


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
                query_repeat=query_repeat,
                warmup=warmup,
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
            "v2_6_numba_compact_mask_plan",
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
    if args.workload == "all":
        if args.dataset is not None:
            raise ValueError("--dataset is only valid when --workload is not all")
        if args.execution_route == "v2_6_numba_compact_mask_plan":
            payload = {
                "app": "rayjoin_v2_spatial_join",
                "execution_route": args.execution_route,
                "workloads": {
                    workload: v2_6_numba_compact_mask_plan_payload(workload)
                    for workload in _WORKLOADS
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
        else:
            payload = run_rayjoin_suite(
                backend=args.backend,
                execution_route=args.execution_route,
                result_mode=args.result_mode,
                include_rows=include_rows,
                pip_count_mode=args.pip_count_mode,
                query_repeat=args.repeat,
                warmup=args.warmup,
            )
    else:
        if args.execution_route == "v2_6_numba_compact_mask_plan":
            payload = v2_6_numba_compact_mask_plan_payload(args.workload)
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
        elif args.execution_route == "prepared_optix":
            payload = run_rayjoin_prepared_optix_workload(
                args.workload,
                dataset=args.dataset,
                result_mode=args.result_mode,
                include_rows=include_rows,
                count_mode=args.pip_count_mode,
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
