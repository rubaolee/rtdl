from __future__ import annotations

from pathlib import Path

import numpy as np

from librts_reproduction import load_points, load_polygons
import rtdsl as rt


def load_author_compatible_pip_inputs(
    *,
    polygons_path: Path,
    points_path: Path,
) -> dict[str, object]:
    """Load and lower app-owned PIP inputs before a timed physical route."""

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
    point_rows = tuple((point.x, point.y) for point in points)
    point_matrix = np.asarray(point_rows, dtype=np.float32)
    offsets = [0]
    vertices: list[tuple[float, float]] = []
    for polygon in polygons:
        vertices.append((0.0, 0.0))
        vertices.extend(polygon.vertices)
        vertices.append(polygon.vertices[0])
        vertices.append((0.0, 0.0))
        offsets.append(len(vertices))
    return {
        "polygons": polygons,
        "points": points,
        "boxes": boxes,
        "point_rows": point_rows,
        "point_matrix": point_matrix,
        "vertex_matrix": np.asarray(vertices, dtype=np.float32),
        "offset_array": np.asarray(offsets, dtype=np.int64),
    }


def run_author_compatible_pip_loaded(
    inputs: dict[str, object],
    *,
    execution_mode: str,
    candidate_expansion: float = 1.0e-5,
) -> dict[str, object]:
    """Run the loaded PIP route with compiler-owned candidate placement."""

    if execution_mode != "compiler":
        raise ValueError("author-compatible loaded PIP execution_mode must be compiler")
    polygons = inputs["polygons"]
    points = inputs["points"]
    boxes = inputs["boxes"]
    point_rows = inputs["point_rows"]
    point_matrix = inputs["point_matrix"]
    vertex_matrix = inputs["vertex_matrix"]
    offset_array = inputs["offset_array"]
    candidate_payload = rt.compiler_expanded_aabb_point_membership_rows_2d(
        boxes,
        point_rows,
        indexed_ids=tuple(range(len(polygons))),
        source_ids=tuple(range(len(points))),
        expansions=candidate_expansion,
        row_capacity=len(polygons) * len(points),
    )
    return _refine_author_compatible_pip_candidates(
        polygons=polygons,
        points=points,
        point_matrix=point_matrix,
        vertex_matrix=vertex_matrix,
        offset_array=offset_array,
        candidate_payload=candidate_payload,
        candidate_expansion=candidate_expansion,
    )


def run_author_compatible_pip_rows(
    *,
    polygons_path: Path,
    points_path: Path,
    backend: str = "optix",
    candidate_expansion: float = 1.0e-5,
) -> dict[str, object]:
    inputs = load_author_compatible_pip_inputs(
        polygons_path=polygons_path,
        points_path=points_path,
    )
    return run_author_compatible_pip_loaded_v2(
        inputs,
        backend=backend,
        candidate_expansion=candidate_expansion,
    )


def run_author_compatible_pip_loaded_v2(
    inputs: dict[str, object],
    *,
    backend: str = "optix",
    candidate_expansion: float = 1.0e-5,
) -> dict[str, object]:
    """Run the established V2.x PIP route from already loaded app inputs."""

    polygons = inputs["polygons"]
    points = inputs["points"]
    candidate_payload = rt.expanded_aabb_point_membership_rows_2d(
        inputs["boxes"],
        inputs["point_rows"],
        indexed_ids=tuple(range(len(polygons))),
        source_ids=tuple(range(len(points))),
        expansions=candidate_expansion,
        row_capacity=len(polygons) * len(points),
        backend=backend,
    )
    return _refine_author_compatible_pip_candidates(
        polygons=polygons,
        points=points,
        point_matrix=inputs["point_matrix"],
        vertex_matrix=inputs["vertex_matrix"],
        offset_array=inputs["offset_array"],
        candidate_payload=candidate_payload,
        candidate_expansion=candidate_expansion,
    )


def _refine_author_compatible_pip_candidates(
    *,
    polygons,
    points,
    point_matrix,
    vertex_matrix,
    offset_array,
    candidate_payload,
    candidate_expansion: float,
) -> dict[str, object]:
    from numba import cuda

    candidate_rows = np.asarray(candidate_payload["candidate_id_rows"], dtype=np.int64)
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
        "compiler_plan": candidate_payload.get("compiler_plan"),
        "application_selected_backend": candidate_payload.get("compiler_plan") is None,
    }
