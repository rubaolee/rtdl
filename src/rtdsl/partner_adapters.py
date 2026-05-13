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
            ray_ids = witness_ray_ids.to(torch.int64)
            primitive_ids = witness_primitive_ids.to(torch.int64)
            primitive_modulus = torch.max(primitive_ids) + 1
            unique_pairs = torch.unique(ray_ids * primitive_modulus + primitive_ids)
            unique_ray_ids = torch.div(unique_pairs, primitive_modulus, rounding_mode="floor")
            return (
                segment_ids.to(torch.int64).reshape(-1, 1)
                .eq(unique_ray_ids.reshape(1, -1))
                .sum(dim=1)
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
        }
    if partner == "cupy":
        import cupy

        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            raise RuntimeError("CuPy partner adapter requires a CUDA device")

        def count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
            if int(witness_ray_ids.size) == 0:
                return cupy.zeros_like(segment_ids, dtype=cupy.uint32)
            ray_ids = witness_ray_ids.astype(cupy.int64, copy=False)
            primitive_ids = witness_primitive_ids.astype(cupy.int64, copy=False)
            primitive_modulus = cupy.max(primitive_ids) + cupy.asarray(1, dtype=cupy.int64)
            unique_pairs = cupy.unique(ray_ids * primitive_modulus + primitive_ids)
            unique_ray_ids = unique_pairs // primitive_modulus
            return cupy.sum(
                segment_ids.astype(cupy.int64, copy=False).reshape(-1, 1)
                == unique_ray_ids.reshape(1, -1),
                axis=1,
            ).astype(cupy.uint32, copy=False)

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
