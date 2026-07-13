from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from librts_author_pip_compat import run_author_compatible_pip_rows
from librts_reproduction import load_points, load_polygons, run_pip_rows
import rtdsl as rt


def _load_row_dump(path: Path) -> list[list[int]]:
    rows: list[list[int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        values = line.split(",")
        if len(values) != 2:
            raise ValueError(f"invalid author PIP row: {line!r}")
        rows.append([int(values[0]), int(values[1])])
    rows.sort()
    return rows


def _pnpoly_mask(
    vertices: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
) -> np.ndarray:
    inside = np.zeros(xs.shape[0], dtype=np.bool_)
    j = vertices.shape[0] - 1
    for i in range(vertices.shape[0]):
        xi = vertices[i, 0]
        yi = vertices[i, 1]
        xj = vertices[j, 0]
        yj = vertices[j, 1]
        crosses = (yi > ys) != (yj > ys)
        with np.errstate(divide="ignore", invalid="ignore"):
            crossing_x = (xj - xi) * (ys - yi) / (yj - yi) + xi
        inside ^= crosses & (xs < crossing_x)
        j = i
    return inside


def reference_rows(
    *,
    polygons_path: Path,
    points_path: Path,
    author_sentinel_layout: bool,
) -> list[list[int]]:
    polygons = load_polygons(polygons_path)
    points = load_points(points_path)
    point_matrix = np.asarray([(point.x, point.y) for point in points], dtype=np.float32)
    rows: list[list[int]] = []
    for polygon_id, polygon in enumerate(polygons):
        outer = np.asarray(polygon.vertices, dtype=np.float32)
        closed = np.concatenate((outer, outer[:1]), axis=0)
        min_xy = np.min(closed, axis=0)
        max_xy = np.max(closed, axis=0)
        candidate_ids = np.flatnonzero(
            (point_matrix[:, 0] >= min_xy[0])
            & (point_matrix[:, 0] <= max_xy[0])
            & (point_matrix[:, 1] >= min_xy[1])
            & (point_matrix[:, 1] <= max_xy[1])
        )
        vertices = closed
        if author_sentinel_layout:
            zero = np.zeros((1, 2), dtype=np.float32)
            vertices = np.concatenate((zero, closed, zero), axis=0)
        inside = _pnpoly_mask(
            vertices,
            point_matrix[candidate_ids, 0],
            point_matrix[candidate_ids, 1],
        )
        rows.extend(
            [int(point_id), polygon_id]
            for point_id in candidate_ids[inside]
        )
    rows.sort()
    return rows


def rtdl_candidates_author_compatibility_rows(
    *,
    polygons_path: Path,
    points_path: Path,
    backend: str,
    candidate_expansion: float = 1.0e-5,
) -> tuple[list[list[int]], dict[str, object]]:
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
    candidate_payload = rt.expanded_aabb_point_membership_rows_2d(
        boxes,
        point_rows,
        indexed_ids=tuple(range(len(polygons))),
        source_ids=tuple(range(len(points))),
        expansions=candidate_expansion,
        row_capacity=len(polygons) * len(points),
        backend=backend,
    )
    candidate_rows = np.asarray(candidate_payload["candidate_id_rows"], dtype=np.int64)
    point_matrix = np.asarray(point_rows, dtype=np.float32)
    result: list[list[int]] = []
    zero = np.zeros((1, 2), dtype=np.float32)
    for polygon_id, polygon in enumerate(polygons):
        point_ids = candidate_rows[candidate_rows[:, 1] == polygon_id, 0]
        if point_ids.size == 0:
            continue
        outer = np.asarray(polygon.vertices, dtype=np.float32)
        closed = np.concatenate((outer, outer[:1]), axis=0)
        vertices = np.concatenate((zero, closed, zero), axis=0)
        inside = _pnpoly_mask(
            vertices,
            point_matrix[point_ids, 0],
            point_matrix[point_ids, 1],
        )
        result.extend([int(point_id), polygon_id] for point_id in point_ids[inside])
    result.sort()
    return result, {
        "candidate_contract": candidate_payload["contract"],
        "candidate_count": int(candidate_payload["valid_count"]),
        "candidate_expansion": candidate_expansion,
        "rt_core_accelerated": bool(candidate_payload["rt_core_accelerated"]),
        "native_engine_customization": bool(candidate_payload["native_engine_customization"]),
    }


def _minimum_edge_distance(
    point: tuple[float, float],
    vertices: tuple[tuple[float, float], ...],
) -> float:
    px, py = point
    minimum = math.inf
    for index, (ax, ay) in enumerate(vertices):
        bx, by = vertices[(index + 1) % len(vertices)]
        dx = bx - ax
        dy = by - ay
        denominator = dx * dx + dy * dy
        if denominator == 0.0:
            distance = math.hypot(px - ax, py - ay)
        else:
            scale = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denominator))
            distance = math.hypot(px - (ax + scale * dx), py - (ay + scale * dy))
        minimum = min(minimum, distance)
    return minimum


def _difference_details(
    rows: set[tuple[int, int]],
    *,
    polygons_path: Path,
    points_path: Path,
) -> list[dict[str, object]]:
    polygons = load_polygons(polygons_path)
    points = load_points(points_path)
    details: list[dict[str, object]] = []
    for point_id, polygon_id in sorted(rows):
        point = points[point_id]
        details.append(
            {
                "point_id": point_id,
                "polygon_id": polygon_id,
                "point": [point.x, point.y],
                "minimum_outer_edge_distance": _minimum_edge_distance(
                    (point.x, point.y),
                    polygons[polygon_id].vertices,
                ),
            }
        )
    return details


def build_diagnostic(
    *,
    polygons_path: Path,
    points_path: Path,
    rtdl_backend: str,
    author_rows_path: Path | None = None,
) -> dict[str, object]:
    author_rows = reference_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        author_sentinel_layout=True,
    )
    standard_rows = reference_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        author_sentinel_layout=False,
    )
    rtdl = run_pip_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        backend=rtdl_backend,
    )
    rtdl_rows = rtdl.pop("candidate_id_rows")
    compatibility_rows, compatibility_metadata = rtdl_candidates_author_compatibility_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        backend=rtdl_backend,
    )
    numba_compatibility = run_author_compatible_pip_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        backend=rtdl_backend,
    )
    numba_compatibility_rows = numba_compatibility.pop("candidate_id_rows")
    numba_compatibility_metadata = numba_compatibility
    author_set = {tuple(row) for row in author_rows}
    standard_set = {tuple(row) for row in standard_rows}
    rtdl_set = {tuple(row) for row in rtdl_rows}
    compatibility_set = {tuple(row) for row in compatibility_rows}
    numba_compatibility_set = {tuple(row) for row in numba_compatibility_rows}
    observed_author_rows = (
        _load_row_dump(author_rows_path) if author_rows_path is not None else []
    )
    observed_author_set = {tuple(row) for row in observed_author_rows}
    observed_author_minus_rtdl = observed_author_set - rtdl_set
    rtdl_minus_observed_author = rtdl_set - observed_author_set
    return {
        "schema": "rtdl.paper_reproduction.librts.pip_semantics_diagnostic.v1",
        "author_float32_sentinel_count": len(author_rows),
        "standard_outer_float32_count": len(standard_rows),
        "rtdl_count": int(rtdl["result_count"]),
        "rtdl_candidate_author_compatibility_count": len(compatibility_rows),
        "rtdl_candidate_author_compatibility_metadata": compatibility_metadata,
        "rtdl_candidate_author_numba_compatibility_count": len(numba_compatibility_rows),
        "rtdl_candidate_author_numba_compatibility_metadata": numba_compatibility_metadata,
        "author_minus_rtdl": [list(row) for row in sorted(author_set - rtdl_set)[:20]],
        "rtdl_minus_author": [list(row) for row in sorted(rtdl_set - author_set)[:20]],
        "standard_minus_rtdl": [list(row) for row in sorted(standard_set - rtdl_set)[:20]],
        "rtdl_minus_standard": [list(row) for row in sorted(rtdl_set - standard_set)[:20]],
        "observed_author_row_count": len(observed_author_rows),
        "observed_author_minus_rtdl": [
            list(row) for row in sorted(observed_author_minus_rtdl)[:20]
        ],
        "rtdl_minus_observed_author": [
            list(row) for row in sorted(rtdl_minus_observed_author)[:20]
        ],
        "observed_author_minus_rtdl_details": _difference_details(
            observed_author_minus_rtdl,
            polygons_path=polygons_path,
            points_path=points_path,
        ),
        "rtdl_minus_observed_author_details": _difference_details(
            rtdl_minus_observed_author,
            polygons_path=polygons_path,
            points_path=points_path,
        ),
        "observed_author_matches_rtdl_rows": (
            observed_author_set == rtdl_set if author_rows_path is not None else None
        ),
        "observed_author_matches_rtdl_candidate_author_compatibility_rows": (
            observed_author_set == compatibility_set if author_rows_path is not None else None
        ),
        "observed_author_minus_rtdl_candidate_author_compatibility": [
            list(row) for row in sorted(observed_author_set - compatibility_set)[:20]
        ],
        "rtdl_candidate_author_compatibility_minus_observed_author": [
            list(row) for row in sorted(compatibility_set - observed_author_set)[:20]
        ],
        "observed_author_matches_rtdl_candidate_author_numba_compatibility_rows": (
            observed_author_set == numba_compatibility_set
            if author_rows_path is not None
            else None
        ),
        "observed_author_minus_rtdl_candidate_author_numba_compatibility": [
            list(row) for row in sorted(observed_author_set - numba_compatibility_set)[:20]
        ],
        "rtdl_candidate_author_numba_compatibility_minus_observed_author": [
            list(row) for row in sorted(numba_compatibility_set - observed_author_set)[:20]
        ],
        "author_matches_rtdl_rows": author_set == rtdl_set,
        "standard_matches_rtdl_rows": standard_set == rtdl_set,
        "claim_boundary": {
            "diagnostic_only": True,
            "author_pair_rows_observed": author_rows_path is not None,
            "author_row_dump_is_app_owned_instrumentation": author_rows_path is not None,
            "reference_emulates_pinned_author_source": True,
            "paper_or_performance_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose representative PIP semantics")
    parser.add_argument("--polygons", required=True, type=Path)
    parser.add_argument("--points", required=True, type=Path)
    parser.add_argument("--rtdl-backend", choices=("cpu", "optix"), default="optix")
    parser.add_argument("--author-rows", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = build_diagnostic(
        polygons_path=args.polygons.resolve(),
        points_path=args.points.resolve(),
        rtdl_backend=args.rtdl_backend,
        author_rows_path=args.author_rows.resolve() if args.author_rows else None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
