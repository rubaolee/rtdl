from __future__ import annotations

from .reference import Polygon as _CanonicalPolygon
from .reference import Segment as _CanonicalSegment
from .runtime import _normalize_records
from . import optix_runtime as _optix

_UINT32_MAX = 2**32 - 1


def _require_uint32_id(value: int, label: str) -> int:
    item = int(value)
    if item < 0 or item > _UINT32_MAX:
        raise ValueError(f"{label} IDs must fit uint32 for the current OptiX witness contract")
    return item


def _partner_module(partner: str):
    if partner == "torch":
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("Torch partner adapter requires torch.cuda to be available")

        def count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
            if int(witness_ray_ids.numel()) == 0:
                return torch.zeros_like(segment_ids, dtype=torch.uint32)
            segment_ids_i64 = segment_ids.to(torch.int64)
            ray_ids = witness_ray_ids.to(torch.int64)
            primitive_ids = witness_primitive_ids.to(torch.int64)
            segment_matches = segment_ids_i64.reshape(-1, 1).eq(ray_ids.reshape(1, -1))
            if not bool(torch.all(torch.any(segment_matches, dim=0)).item()):
                raise ValueError("witness ray IDs must be present in segment_ray_columns['ids']")
            segment_positions = torch.argmax(segment_matches.to(torch.int64), dim=0)
            primitive_modulus = torch.max(primitive_ids) + 1
            unique_pairs = torch.unique(segment_positions * primitive_modulus + primitive_ids)
            unique_positions = torch.div(unique_pairs, primitive_modulus, rounding_mode="floor")
            return (
                torch.bincount(unique_positions, minlength=int(segment_ids.numel()))
                .to(torch.uint32)
            )

        return {
            "name": "torch",
            "module": torch,
            "device": torch.device("cuda:0"),
            "uint32": torch.uint32,
            "float64": torch.float64,
            "float32": torch.float32,
            "tensor": lambda values, dtype, device: torch.tensor(values, dtype=dtype, device=device),
            "zeros": lambda shape, dtype, device: torch.zeros(shape, dtype=dtype, device=device),
            "sync": torch.cuda.synchronize,
            "to_host": lambda value: [int(item) for item in value.detach().cpu().tolist()],
            "slice": lambda value, count: value[: int(count)],
            "count_unique_pairs_by_ids": count_unique_pairs_by_ids,
            "greater_equal_uint32": lambda value, threshold: value.to(torch.int64).ge(int(threshold)).to(torch.uint32),
            "invert_binary_uint32": lambda value: (1 - value.to(torch.int64)).to(torch.uint32),
            "fixed_radius_count_threshold_2d": lambda query, search, radius, threshold: _torch_fixed_radius_count_threshold_2d(
                torch,
                query,
                search,
                radius,
                threshold,
            ),
        }
    if partner == "cupy":
        import cupy

        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            raise RuntimeError("CuPy partner adapter requires a CUDA device")

        def count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
            if int(witness_ray_ids.size) == 0:
                return cupy.zeros_like(segment_ids, dtype=cupy.uint32)
            segment_ids_i64 = segment_ids.astype(cupy.int64, copy=False)
            ray_ids = witness_ray_ids.astype(cupy.int64, copy=False)
            primitive_ids = witness_primitive_ids.astype(cupy.int64, copy=False)
            segment_matches = segment_ids_i64.reshape(-1, 1) == ray_ids.reshape(1, -1)
            if not bool(cupy.all(cupy.any(segment_matches, axis=0)).item()):
                raise ValueError("witness ray IDs must be present in segment_ray_columns['ids']")
            segment_positions = cupy.argmax(segment_matches, axis=0).astype(cupy.int64, copy=False)
            primitive_modulus = cupy.max(primitive_ids) + cupy.asarray(1, dtype=cupy.int64)
            unique_pairs = cupy.unique(segment_positions * primitive_modulus + primitive_ids)
            unique_positions = unique_pairs // primitive_modulus
            return cupy.bincount(unique_positions, minlength=int(segment_ids.size)).astype(cupy.uint32, copy=False)

        return {
            "name": "cupy",
            "module": cupy,
            "device": None,
            "uint32": cupy.uint32,
            "float64": cupy.float64,
            "float32": cupy.float32,
            "tensor": lambda values, dtype, device: cupy.asarray(values, dtype=dtype),
            "zeros": lambda shape, dtype, device: cupy.zeros(shape, dtype=dtype),
            "sync": cupy.cuda.runtime.deviceSynchronize,
            "to_host": lambda value: [int(item) for item in cupy.asnumpy(value).tolist()],
            "slice": lambda value, count: value[: int(count)],
            "count_unique_pairs_by_ids": count_unique_pairs_by_ids,
            "greater_equal_uint32": lambda value, threshold: (value >= int(threshold)).astype(cupy.uint32, copy=False),
            "invert_binary_uint32": lambda value: (1 - value).astype(cupy.uint32, copy=False),
            "fixed_radius_count_threshold_2d": lambda query, search, radius, threshold: _cupy_fixed_radius_count_threshold_2d(
                cupy,
                query,
                search,
                radius,
                threshold,
            ),
        }
    raise ValueError("partner must be 'torch' or 'cupy'")


def _torch_fixed_radius_count_threshold_2d(torch, query_columns, search_columns, radius, threshold):
    qx = query_columns["x"].to(torch.float64)
    qy = query_columns["y"].to(torch.float64)
    sx = search_columns["x"].to(torch.float64)
    sy = search_columns["y"].to(torch.float64)
    if int(qx.numel()) == 0:
        return torch.zeros((0,), dtype=torch.uint32, device=qx.device)
    if int(sx.numel()) == 0:
        return torch.zeros_like(query_columns["ids"], dtype=torch.uint32)
    radius_sq = float(radius) * float(radius)
    dx = qx.reshape(-1, 1) - sx.reshape(1, -1)
    dy = qy.reshape(-1, 1) - sy.reshape(1, -1)
    within = (dx * dx + dy * dy).le(radius_sq)
    counts = torch.sum(within.to(torch.int64), dim=1)
    return counts.to(torch.uint32)


def _cupy_fixed_radius_count_threshold_2d(cupy, query_columns, search_columns, radius, threshold):
    qx = query_columns["x"].astype(cupy.float64, copy=False)
    qy = query_columns["y"].astype(cupy.float64, copy=False)
    sx = search_columns["x"].astype(cupy.float64, copy=False)
    sy = search_columns["y"].astype(cupy.float64, copy=False)
    if int(qx.size) == 0:
        return cupy.zeros((0,), dtype=cupy.uint32)
    if int(sx.size) == 0:
        return cupy.zeros_like(query_columns["ids"], dtype=cupy.uint32)
    radius_sq = float(radius) * float(radius)
    dx = qx.reshape(-1, 1) - sx.reshape(1, -1)
    dy = qy.reshape(-1, 1) - sy.reshape(1, -1)
    within = (dx * dx + dy * dy) <= radius_sq
    counts = cupy.sum(within.astype(cupy.int64, copy=False), axis=1)
    return counts.astype(cupy.uint32, copy=False)


def _segment_ray_columns(segments: tuple[_CanonicalSegment, ...], partner: dict) -> dict[str, object]:
    device = partner["device"]
    return {
        "ids": partner["tensor"](
            [_require_uint32_id(segment.id, "segment") for segment in segments],
            partner["uint32"],
            device,
        ),
        "ox": partner["tensor"]([segment.x0 for segment in segments], partner["float64"], device),
        "oy": partner["tensor"]([segment.y0 for segment in segments], partner["float64"], device),
        "dx": partner["tensor"]([segment.x1 - segment.x0 for segment in segments], partner["float64"], device),
        "dy": partner["tensor"]([segment.y1 - segment.y0 for segment in segments], partner["float64"], device),
        "tmax": partner["tensor"]([1.0 for _ in segments], partner["float64"], device),
    }


def _point_columns(points, partner: dict) -> dict[str, object]:
    device = partner["device"]
    return {
        "ids": partner["tensor"](
            [_require_uint32_id(point.id, "point") for point in points],
            partner["uint32"],
            device,
        ),
        "x": partner["tensor"]([point.x for point in points], partner["float64"], device),
        "y": partner["tensor"]([point.y for point in points], partner["float64"], device),
    }


def _polygon_triangle_columns(polygons: tuple[_CanonicalPolygon, ...], partner: dict) -> tuple[dict[str, object], object]:
    ids: list[int] = []
    x0: list[float] = []
    y0: list[float] = []
    x1: list[float] = []
    y1: list[float] = []
    x2: list[float] = []
    y2: list[float] = []
    aabbs: list[list[float]] = []
    for polygon in polygons:
        vertices = tuple((float(x), float(y)) for x, y in polygon.vertices)
        if len(vertices) < 3:
            raise ValueError("polygons must have at least three vertices")
        anchor_x, anchor_y = vertices[0]
        for index in range(1, len(vertices) - 1):
            bx, by = vertices[index]
            cx, cy = vertices[index + 1]
            ids.append(_require_uint32_id(polygon.id, "polygon"))
            x0.append(anchor_x)
            y0.append(anchor_y)
            x1.append(bx)
            y1.append(by)
            x2.append(cx)
            y2.append(cy)
            min_x = min(anchor_x, bx, cx)
            min_y = min(anchor_y, by, cy)
            max_x = max(anchor_x, bx, cx)
            max_y = max(anchor_y, by, cy)
            aabbs.append([min_x, min_y, -1.0e-4, max_x, max_y, 1.0e-4])
    device = partner["device"]
    columns = {
        "ids": partner["tensor"](ids, partner["uint32"], device),
        "x0": partner["tensor"](x0, partner["float64"], device),
        "y0": partner["tensor"](y0, partner["float64"], device),
        "x1": partner["tensor"](x1, partner["float64"], device),
        "y1": partner["tensor"](y1, partner["float64"], device),
        "x2": partner["tensor"](x2, partner["float64"], device),
        "y2": partner["tensor"](y2, partner["float64"], device),
    }
    return columns, partner["tensor"](aabbs, partner["float32"], device)


def segment_polygon_anyhit_rows_optix_partner(
    segments,
    polygons,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon any-hit rows as a Python+partner+RTDL adapter.

    The native engine sees only generic ray/primitive witness IDs. Polygon
    triangulation, duplicate removal, and row naming live in Python.
    """
    normalized_segments = tuple(
        segments
        if isinstance(segments, tuple) and all(isinstance(item, _CanonicalSegment) for item in segments)
        else _normalize_records("segments", "segments", segments)
    )
    normalized_polygons = tuple(
        polygons
        if isinstance(polygons, tuple) and all(isinstance(item, _CanonicalPolygon) for item in polygons)
        else _normalize_records("polygons", "polygons", polygons)
    )
    if not normalized_segments or not normalized_polygons:
        rows: tuple[dict[str, int], ...] = ()
        metadata = {
            "adapter": "segment_polygon_anyhit_rows_optix_partner",
            "partner": partner,
            "app_rows_emitted": 0,
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        if return_metadata:
            return {"rows": rows, "metadata": metadata}
        return rows
    if output_capacity is None:
        triangle_capacity = sum(max(0, len(polygon.vertices) - 2) for polygon in normalized_polygons)
        output_capacity = max(1, len(normalized_segments) * triangle_capacity)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")

    runtime = _partner_module(partner)
    rays = _segment_ray_columns(normalized_segments, runtime)
    triangles, triangle_aabbs = _polygon_triangle_columns(normalized_polygons, runtime)
    witness_ray_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])
    witness_primitive_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])

    scene = _optix.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        triangles,
        triangle_aabbs,
    )
    try:
        packet = scene.write_device_any_hit_all_witnesses(
            rays,
            witness_ray_ids,
            witness_primitive_ids,
        )
        runtime["sync"]()
    finally:
        scene.close()

    metadata = dict(packet["metadata"])
    emitted_count = int(metadata["emitted_count"])
    if metadata["overflowed"]:
        raise RuntimeError("partner segment/polygon adapter overflowed; increase output_capacity")
    ray_ids = runtime["to_host"](witness_ray_ids)[:emitted_count]
    primitive_ids = runtime["to_host"](witness_primitive_ids)[:emitted_count]
    rows = tuple(
        {"segment_id": segment_id, "polygon_id": polygon_id}
        for segment_id, polygon_id in sorted(set(zip(ray_ids, primitive_ids)))
    )
    metadata.update(
        {
            "adapter": "segment_polygon_anyhit_rows_optix_partner",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def _column_length(columns: dict[str, object], name: str) -> int:
    column = columns[name]
    shape = getattr(column, "shape", None)
    if shape is not None:
        return int(shape[0])
    values = getattr(column, "values", None)
    if values is not None:
        return len(values)
    try:
        return len(column)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ValueError(f"{name} column must expose shape[0] or a length") from exc


def _segment_polygon_all_witness_columns_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
):
    ray_count = _column_length(segment_ray_columns, "ids")
    triangle_count = _column_length(polygon_triangle_columns, "ids")
    runtime = _partner_module(partner)
    if ray_count == 0 or triangle_count == 0:
        metadata = {
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "emitted_count": 0,
            "overflowed": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        empty = runtime["zeros"]((0,), runtime["uint32"], runtime["device"])
        return {
            "runtime": runtime,
            "witness_ray_ids": empty,
            "witness_primitive_ids": empty,
            "emitted_count": 0,
            "metadata": metadata,
        }
    if output_capacity is None:
        output_capacity = max(1, ray_count * triangle_count)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")

    witness_ray_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])
    witness_primitive_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])

    scene = _optix.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        polygon_triangle_columns,
        polygon_triangle_aabbs,
    )
    try:
        packet = scene.write_device_any_hit_all_witnesses(
            segment_ray_columns,
            witness_ray_ids,
            witness_primitive_ids,
        )
        runtime["sync"]()
    finally:
        scene.close()

    metadata = dict(packet["metadata"])
    emitted_count = int(metadata["emitted_count"])
    if metadata["overflowed"]:
        raise RuntimeError("partner segment/polygon column adapter overflowed; increase output_capacity")
    return {
        "runtime": runtime,
        "witness_ray_ids": witness_ray_ids,
        "witness_primitive_ids": witness_primitive_ids,
        "emitted_count": emitted_count,
        "metadata": metadata,
    }


def segment_polygon_anyhit_rows_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon rows from caller-supplied partner CUDA columns.

    The caller owns the GPU-resident ray and triangle columns. The adapter only
    allocates bounded witness output columns, invokes the generic native
    all-witness contract, and names/deduplicates app rows in Python.
    """
    witness_result = _segment_polygon_all_witness_columns_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
    )
    runtime = witness_result["runtime"]
    emitted_count = witness_result["emitted_count"]
    metadata = dict(witness_result["metadata"])
    witness_ray_ids = witness_result["witness_ray_ids"]
    witness_primitive_ids = witness_result["witness_primitive_ids"]
    ray_ids = runtime["to_host"](witness_ray_ids)[:emitted_count]
    primitive_ids = runtime["to_host"](witness_primitive_ids)[:emitted_count]
    rows = tuple(
        {"segment_id": segment_id, "polygon_id": polygon_id}
        for segment_id, polygon_id in sorted(set(zip(ray_ids, primitive_ids)))
    )
    metadata.update(
        {
            "adapter": "segment_polygon_anyhit_rows_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def segment_polygon_hitcount_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon hit counts from caller-supplied partner CUDA columns.

    This is an app-layer adapter over generic ray/primitive witness rows. The
    native engine emits witness IDs only; Python deduplicates polygon hits and
    materializes one hit-count row per input segment ID.
    """
    runtime = _partner_module(partner)
    segment_ids = runtime["to_host"](segment_ray_columns["ids"])
    if not segment_ids:
        rows: tuple[dict[str, int], ...] = ()
        metadata = {
            "adapter": "segment_polygon_hitcount_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": 0,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "none_empty_input",
            "app_count_host_materialization": False,
            "whole_app_true_zero_copy_authorized": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        if return_metadata:
            return {"rows": rows, "metadata": metadata}
        return rows
    witness_result = segment_polygon_anyhit_rows_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
        return_metadata=True,
    )
    counts = {int(segment_id): 0 for segment_id in segment_ids}
    seen_pairs = set()
    for row in witness_result["rows"]:
        pair = (int(row["segment_id"]), int(row["polygon_id"]))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        if pair[0] in counts:
            counts[pair[0]] += 1
    rows = tuple({"segment_id": segment_id, "hit_count": counts[segment_id]} for segment_id in segment_ids)
    metadata = dict(witness_result["metadata"])
    metadata.update(
        {
            "adapter": "segment_polygon_hitcount_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "python_from_generic_witness_pairs",
            "app_count_host_materialization": True,
            "whole_app_true_zero_copy_authorized": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def segment_polygon_hitcount_optix_partner_device_count_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Return partner-owned segment IDs and hit-count columns.

    This adapter keeps the native call on the same generic bounded witness
    contract as the row adapters, then performs duplicate-pair removal and
    per-segment counting with PyTorch/CuPy tensor operations. It avoids
    materializing app hit-count rows on the host.
    """
    witness_result = _segment_polygon_all_witness_columns_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
    )
    runtime = witness_result["runtime"]
    emitted_count = witness_result["emitted_count"]
    metadata = dict(witness_result["metadata"])
    witness_ray_ids = runtime["slice"](witness_result["witness_ray_ids"], emitted_count)
    witness_primitive_ids = runtime["slice"](witness_result["witness_primitive_ids"], emitted_count)
    hit_counts = runtime["count_unique_pairs_by_ids"](
        segment_ray_columns["ids"],
        witness_ray_ids,
        witness_primitive_ids,
    )
    runtime["sync"]()
    columns = {
        "segment_ids": segment_ray_columns["ids"],
        "hit_counts": hit_counts,
    }
    metadata.update(
        {
            "adapter": "segment_polygon_hitcount_optix_partner_device_count_columns",
            "partner": runtime["name"],
            "app_columns_emitted": 2,
            "app_rows_emitted": _column_length(segment_ray_columns, "ids"),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "partner_gpu_from_generic_witness_pairs",
            "app_count_host_materialization": False,
            "whole_app_true_zero_copy_authorized": True,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def road_hazard_priority_flags_optix_partner_device_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    threshold: int = 2,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Return partner-owned road hazard priority columns.

    This app adapter reuses the generic segment/polygon hit-count partner
    column path, then applies the road-hazard priority threshold with the
    selected partner tensor library. The native engine still sees only generic
    ray/primitive witness IDs.
    """
    threshold = int(threshold)
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    hitcount_result = segment_polygon_hitcount_optix_partner_device_count_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    hitcount_columns = hitcount_result["columns"]
    priority_flags = runtime["greater_equal_uint32"](
        hitcount_columns["hit_counts"],
        threshold,
    )
    runtime["sync"]()
    columns = {
        "road_ids": hitcount_columns["segment_ids"],
        "hit_counts": hitcount_columns["hit_counts"],
        "priority_flags": priority_flags,
    }
    metadata = dict(hitcount_result["metadata"])
    metadata.update(
        {
            "adapter": "road_hazard_priority_flags_optix_partner_device_columns",
            "app": "road_hazard_screening",
            "partner": runtime["name"],
            "priority_threshold": threshold,
            "app_priority_materialization": "partner_gpu_threshold_from_hit_counts",
            "app_priority_host_materialization": False,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def fixed_radius_count_threshold_2d_partner_columns(
    query_point_columns: dict[str, object],
    search_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned fixed-radius count and threshold columns.

    This is the protocol-first partner reference path for fixed-radius apps. It
    uses PyTorch/CuPy tensor operations over caller-owned point columns and does
    not call the native RTDL engine yet.
    """
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    neighbor_counts = runtime["fixed_radius_count_threshold_2d"](
        query_point_columns,
        search_point_columns,
        radius,
        threshold,
    )
    threshold_flags = runtime["greater_equal_uint32"](neighbor_counts, threshold)
    runtime["sync"]()
    columns = {
        "query_ids": query_point_columns["ids"],
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_fixed_radius_count_threshold_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "radius": radius,
        "threshold": threshold,
        "app_count_materialization": "partner_gpu_fixed_radius_count_threshold",
        "app_count_host_materialization": False,
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def fixed_radius_count_threshold_2d_optix_partner_device_columns(
    query_point_columns: dict[str, object],
    search_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return OptiX-written fixed-radius count-threshold columns.

    This is the first native RTDL fixed-radius partner bridge: caller-owned
    PyTorch/CuPy point columns are handed directly to OptiX, and OptiX writes
    caller-owned output columns without app-row host materialization.
    """
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    query_count = _column_length(query_point_columns, "ids")
    search_count = _column_length(search_point_columns, "ids")
    neighbor_counts = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    threshold_flags = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    query_ids_out = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])

    if query_count and search_count:
        with _optix.prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
            search_point_columns,
            max_radius=radius,
        ) as prepared:
            native_result = prepared.write_device_count_threshold_columns(
                query_point_columns,
                radius=radius,
                threshold=threshold,
                query_ids_out=query_ids_out,
                neighbor_counts_out=neighbor_counts,
                threshold_flags_out=threshold_flags,
            )
        native_metadata = native_result["metadata"]
    else:
        query_ids_out = query_point_columns["ids"]
        if threshold == 0:
            threshold_flags = runtime["greater_equal_uint32"](neighbor_counts, 0)
        native_metadata = {
            "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy_empty_shortcut",
            "native_symbol": "not_called_empty_input",
            "direct_device_handoff_authorized": True,
            "true_zero_copy_authorized": True,
            "rt_core_speedup_claim_authorized": False,
        }
    runtime["sync"]()
    columns = {
        "query_ids": query_ids_out,
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_optix_partner_device_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
        "app_count_materialization": "native_optix_device_columns",
        "app_count_host_materialization": False,
        "query_count": query_count,
        "search_count": search_count,
        "radius": radius,
        "threshold": threshold,
        "direct_device_handoff_authorized": bool(native_metadata["direct_device_handoff_authorized"]),
        "true_zero_copy_authorized": bool(native_metadata["true_zero_copy_authorized"]),
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "native_metadata": native_metadata,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
    search_point_columns: dict[str, object],
    *,
    max_radius: float,
    partner: str = "torch",
):
    """Prepare a reusable OptiX fixed-radius scene from partner point columns."""
    _partner_module(partner)
    return _optix.prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
        search_point_columns,
        max_radius=max_radius,
    )


def fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
    prepared,
    query_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return fixed-radius columns through a reusable prepared OptiX scene."""
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    query_count = _column_length(query_point_columns, "ids")
    neighbor_counts = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    threshold_flags = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    query_ids_out = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])

    native_result = prepared.write_device_count_threshold_columns(
        query_point_columns,
        radius=radius,
        threshold=threshold,
        query_ids_out=query_ids_out,
        neighbor_counts_out=neighbor_counts,
        threshold_flags_out=threshold_flags,
    )
    runtime["sync"]()
    columns = {
        "query_ids": query_ids_out,
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
        "app_count_materialization": "native_optix_prepared_device_columns",
        "app_count_host_materialization": False,
        "query_count": query_count,
        "radius": radius,
        "threshold": threshold,
        "direct_device_handoff_authorized": bool(native_result["metadata"]["direct_device_handoff_authorized"]),
        "true_zero_copy_authorized": bool(native_result["metadata"]["true_zero_copy_authorized"]),
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "native_metadata": native_result["metadata"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_partner_columns(
    household_point_columns: dict[str, object],
    clinic_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned service coverage flags.

    A household is uncovered when the fixed-radius neighbor count is zero. This
    remains a partner-reference app adapter until fixed-radius native
    device-column handoff exists.
    """
    result = fixed_radius_count_threshold_2d_partner_columns(
        household_point_columns,
        clinic_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_partner_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_fixed_radius_counts",
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_optix_partner_device_columns(
    household_point_columns: dict[str, object],
    clinic_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return native OptiX fixed-radius service coverage columns."""
    result = fixed_radius_count_threshold_2d_optix_partner_device_columns(
        household_point_columns,
        clinic_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_optix_partner_device_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_optix_prepared_partner_device_columns(
    prepared,
    household_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return service coverage columns through a reusable prepared scene."""
    result = fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
        prepared,
        household_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_optix_prepared_partner_device_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_prepared_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_partner_columns(
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned event hotspot flags.

    The self-neighbor is included in the fixed-radius count, so the partner
    threshold is `hotspot_threshold + 1`, matching the existing app summary
    semantics.
    """
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_partner_columns(
        event_point_columns,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_partner_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_fixed_radius_counts",
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_optix_partner_device_columns(
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return native OptiX fixed-radius event hotspot columns."""
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_optix_partner_device_columns(
        event_point_columns,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_optix_partner_device_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_optix_prepared_partner_device_columns(
    prepared,
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return event hotspot columns through a reusable prepared scene."""
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
        prepared,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_optix_prepared_partner_device_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_prepared_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns
