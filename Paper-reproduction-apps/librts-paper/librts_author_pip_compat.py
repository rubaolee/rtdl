from __future__ import annotations

from pathlib import Path

import numpy as np

from librts_reproduction import load_points, load_polygons
import rtdsl as rt


def run_author_compatible_pip_rows(
    *,
    polygons_path: Path,
    points_path: Path,
    backend: str = "optix",
    candidate_expansion: float = 1.0e-5,
) -> dict[str, object]:
    from numba import cuda

    polygons = load_polygons(polygons_path)
    points = load_points(points_path)
    boxes = tuple(
        (
            min(vertex[0] for vertex in polygon.vertices),
            min(vertex[1] for vertex in polygon.vertices),
            max(vertex[0] for vertex in polygon.vertices),
            max(vertex[1] for vertex in polygon.vertices),
        )
        for polygon in polygons
    )
    point_matrix = np.asarray([(point.x, point.y) for point in points], dtype=np.float32)
    candidate_payload = rt.expanded_aabb_point_membership_rows_2d(
        boxes,
        tuple((point.x, point.y) for point in points),
        indexed_ids=tuple(range(len(polygons))),
        source_ids=tuple(range(len(points))),
        expansions=candidate_expansion,
        row_capacity=len(polygons) * len(points),
        backend=backend,
    )
    candidate_rows = np.asarray(candidate_payload["candidate_id_rows"], dtype=np.int64)
    offsets = [0]
    vertices: list[tuple[float, float]] = []
    for polygon in polygons:
        vertices.append((0.0, 0.0))
        vertices.extend(polygon.vertices)
        vertices.append(polygon.vertices[0])
        vertices.append((0.0, 0.0))
        offsets.append(len(vertices))
    vertex_matrix = np.asarray(vertices, dtype=np.float32)
    offset_array = np.asarray(offsets, dtype=np.int64)
    flags = np.zeros(candidate_rows.shape[0], dtype=np.uint8)

    @cuda.jit(fastmath=True)
    def pnpoly_kernel(candidates, query_points, row_offsets, polygon_vertices, output):
        index = cuda.grid(1)
        if index >= candidates.shape[0]:
            return
        point_id = candidates[index, 0]
        polygon_id = candidates[index, 1]
        testx = query_points[point_id, 0]
        testy = query_points[point_id, 1]
        begin = row_offsets[polygon_id]
        end = row_offsets[polygon_id + 1]
        j = end - 1
        inside = 0
        for i in range(begin, end):
            yi = polygon_vertices[i, 1]
            yj = polygon_vertices[j, 1]
            if ((yi > testy) != (yj > testy)) and (
                testx
                < (polygon_vertices[j, 0] - polygon_vertices[i, 0])
                * (testy - yi)
                / (yj - yi)
                + polygon_vertices[i, 0]
            ):
                inside = 1 - inside
            j = i
        output[index] = inside

    device_candidates = cuda.to_device(candidate_rows)
    device_points = cuda.to_device(point_matrix)
    device_offsets = cuda.to_device(offset_array)
    device_vertices = cuda.to_device(vertex_matrix)
    device_flags = cuda.to_device(flags)
    threads = 256
    blocks = (candidate_rows.shape[0] + threads - 1) // threads
    pnpoly_kernel[blocks, threads](
        device_candidates,
        device_points,
        device_offsets,
        device_vertices,
        device_flags,
    )
    flags = device_flags.copy_to_host()
    rows = candidate_rows[flags == 1, :2].tolist()
    rows.sort()
    return {
        "schema": "rtdl.paper_reproduction.librts.author_compatible_pip_rows.v1",
        "candidate_id_rows": rows,
        "result_count": len(rows),
        "polygon_count": len(polygons),
        "point_count": len(points),
        "candidate_contract": candidate_payload["contract"],
        "candidate_count": int(candidate_payload["valid_count"]),
        "candidate_expansion": candidate_expansion,
        "partner": "numba_cuda",
        "fastmath": True,
        "app_semantics": "pinned_author_pnpoly_float32_sentinel_layout",
        "rt_core_accelerated": bool(candidate_payload["rt_core_accelerated"]),
        "native_engine_customization": bool(candidate_payload["native_engine_customization"]),
    }
