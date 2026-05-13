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
        }
    if partner == "cupy":
        import cupy

        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            raise RuntimeError("CuPy partner adapter requires a CUDA device")
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
        }
    raise ValueError("partner must be 'torch' or 'cupy'")


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
    return len(column)  # type: ignore[arg-type]


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
    ray_count = _column_length(segment_ray_columns, "ids")
    triangle_count = _column_length(polygon_triangle_columns, "ids")
    if ray_count == 0 or triangle_count == 0:
        rows: tuple[dict[str, int], ...] = ()
        metadata = {
            "adapter": "segment_polygon_anyhit_rows_optix_partner_columns",
            "partner": partner,
            "app_rows_emitted": 0,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        if return_metadata:
            return {"rows": rows, "metadata": metadata}
        return rows
    if output_capacity is None:
        output_capacity = max(1, ray_count * triangle_count)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")

    runtime = _partner_module(partner)
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
