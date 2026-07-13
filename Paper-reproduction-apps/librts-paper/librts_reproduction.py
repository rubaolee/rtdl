from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir()
)
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclass(frozen=True)
class Box2D:
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass(frozen=True)
class Polygon2D:
    vertices: tuple[tuple[float, float], ...]


def _nonempty_lines(path: Path) -> tuple[str, ...]:
    return tuple(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def parse_point_wkt(text: str) -> Point2D:
    value = text.strip()
    if not value.startswith("POINT(") or not value.endswith(")"):
        raise ValueError(f"unsupported point WKT: {text!r}")
    coordinates = value[len("POINT(") : -1].split()
    if len(coordinates) != 2:
        raise ValueError(f"point WKT must contain two coordinates: {text!r}")
    return Point2D(float(coordinates[0]), float(coordinates[1]))


def parse_box_wkt(text: str) -> Box2D:
    value = text.strip()
    if not value.startswith("POLYGON((") or not value.endswith("))"):
        raise ValueError(f"unsupported box WKT: {text!r}")
    points: list[tuple[float, float]] = []
    for pair in value[len("POLYGON((") : -2].split(","):
        coordinates = pair.split()
        if len(coordinates) != 2:
            raise ValueError(f"box WKT coordinate must be 2-D: {text!r}")
        points.append((float(coordinates[0]), float(coordinates[1])))
    if len(points) < 4:
        raise ValueError(f"box WKT requires at least four points: {text!r}")
    xs = tuple(point[0] for point in points)
    ys = tuple(point[1] for point in points)
    return Box2D(min(xs), min(ys), max(xs), max(ys))


def parse_polygon_wkt(text: str) -> Polygon2D:
    value = text.strip()
    compact_prefix = "POLYGON(("
    spaced_prefix = "POLYGON (("
    if value.startswith(compact_prefix) and value.endswith("))"):
        body = value[len(compact_prefix) : -2]
    elif value.startswith(spaced_prefix) and value.endswith("))"):
        body = value[len(spaced_prefix) : -2]
    else:
        raise ValueError(f"unsupported polygon WKT: {text!r}")
    if "),(" in body.replace(" ", ""):
        raise ValueError("bounded LibRTS PIP fixture does not support polygon holes")
    vertices: list[tuple[float, float]] = []
    for pair in body.split(","):
        coordinates = pair.split()
        if len(coordinates) != 2:
            raise ValueError(f"polygon WKT coordinate must be 2-D: {text!r}")
        vertices.append((float(coordinates[0]), float(coordinates[1])))
    if len(vertices) >= 2 and vertices[0] == vertices[-1]:
        vertices.pop()
    if len(vertices) < 3:
        raise ValueError("polygon WKT requires at least three distinct vertices")
    return Polygon2D(tuple(vertices))


def load_boxes(path: Path) -> tuple[Box2D, ...]:
    return tuple(parse_box_wkt(line) for line in _nonempty_lines(path))


def load_points(path: Path) -> tuple[Point2D, ...]:
    return tuple(parse_point_wkt(line) for line in _nonempty_lines(path))


def load_polygons(path: Path) -> tuple[Polygon2D, ...]:
    return tuple(parse_polygon_wkt(line) for line in _nonempty_lines(path))


@rt.kernel(backend="rtdl", precision="float_approx")
def _librts_bounded_pip_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
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


def run_pip_rows(
    *,
    polygons_path: Path,
    points_path: Path,
    backend: str = "cpu",
) -> dict[str, object]:
    if backend not in {"cpu", "optix"}:
        raise ValueError(f"unsupported LibRTS PIP backend: {backend!r}")
    polygons = load_polygons(polygons_path)
    points = load_points(points_path)
    polygon_rows = tuple(
        {"id": index, "vertices": polygon.vertices}
        for index, polygon in enumerate(polygons)
    )
    point_rows = tuple(
        {"id": index, "x": point.x, "y": point.y}
        for index, point in enumerate(points)
    )
    if backend == "cpu":
        raw_rows = rt.run_cpu(
            _librts_bounded_pip_kernel,
            points=point_rows,
            polygons=polygon_rows,
        )
    else:
        raw_rows = rt.run_optix(
            _librts_bounded_pip_kernel,
            points=point_rows,
            polygons=polygon_rows,
        )
    actual_rows = sorted(
        [int(row["point_id"]), int(row["polygon_id"])]
        for row in raw_rows
        if int(row["contains"]) == 1
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.pip_rows.v1",
        "backend": backend,
        "fixture": {
            "polygons_path": str(polygons_path),
            "points_path": str(points_path),
            "polygon_count": len(polygons),
            "point_count": len(points),
        },
        "public_program": "traverse -> point_in_polygon -> emit",
        "result_count": len(actual_rows),
        "candidate_id_rows": actual_rows,
        "rt_core_accelerated": backend == "optix",
        "native_engine_customization": False,
    }


def run_pip(
    *,
    polygons_path: Path | None = None,
    points_path: Path | None = None,
    expected_path: Path | None = None,
    backend: str = "cpu",
) -> dict[str, object]:
    fixture_dir = APP_DIR / "data" / "fixtures"
    resolved_polygons = polygons_path or fixture_dir / "tiny_pip_polygons.wkt"
    resolved_points = points_path or fixture_dir / "tiny_pip_points.wkt"
    resolved_expected = expected_path or fixture_dir / "tiny_pip_expected.json"
    execution = run_pip_rows(
        polygons_path=resolved_polygons,
        points_path=resolved_points,
        backend=backend,
    )
    polygons = load_polygons(resolved_polygons)
    points = load_points(resolved_points)
    expected = json.loads(resolved_expected.read_text(encoding="utf-8"))
    actual_rows = execution["candidate_id_rows"]
    expected_rows = sorted(
        [int(value) for value in row] for row in expected["expected_rows"]
    )
    bbox_only_count = sum(
        1
        for point in points
        for polygon in polygons
        if min(vertex[0] for vertex in polygon.vertices) <= point.x
        <= max(vertex[0] for vertex in polygon.vertices)
        and min(vertex[1] for vertex in polygon.vertices) <= point.y
        <= max(vertex[1] for vertex in polygon.vertices)
    )
    matched = bool(
        actual_rows == expected_rows
        and len(actual_rows) == int(expected["expected_count"])
        and bbox_only_count == int(expected["bbox_only_candidate_count"])
        and bbox_only_count != len(actual_rows)
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.bounded_pip.v1",
        "matched": matched,
        "backend": execution["backend"],
        "fixture": {
            "polygons_path": str(resolved_polygons),
            "points_path": str(resolved_points),
            "expected_path": str(resolved_expected),
            "polygon_count": execution["fixture"]["polygon_count"],
            "point_count": execution["fixture"]["point_count"],
        },
        "public_program": execution["public_program"],
        "result_count": len(actual_rows),
        "candidate_id_rows": actual_rows,
        "expected_rows": expected_rows,
        "bbox_only_candidate_count": bbox_only_count,
        "polygon_refine_discriminating": bbox_only_count != len(actual_rows),
        "rt_core_accelerated": execution["rt_core_accelerated"],
        "native_engine_customization": execution["native_engine_customization"],
        "fixture_boundary_points_used": False,
    }


def _box_rows(boxes: Iterable[Box2D]) -> tuple[tuple[float, float, float, float], ...]:
    return tuple((box.min_x, box.min_y, box.max_x, box.max_y) for box in boxes)


def _point_rows(points: Iterable[Point2D]) -> tuple[tuple[float, float], ...]:
    return tuple((point.x, point.y) for point in points)


def _range_contains_rows(
    boxes: tuple[Box2D, ...], queries: tuple[Box2D, ...]
) -> list[list[int]]:
    return [
        [query_id, box_id]
        for query_id, query in enumerate(queries)
        for box_id, box in enumerate(boxes)
        if query.min_x >= box.min_x
        and query.min_y >= box.min_y
        and query.max_x <= box.max_x
        and query.max_y <= box.max_y
    ]


def run_local_point_contains(
    *,
    boxes_path: Path | None = None,
    points_path: Path | None = None,
    expected_path: Path | None = None,
    backend: str = "cpu",
) -> dict[str, object]:
    if backend not in {"cpu", "optix"}:
        raise ValueError(f"unsupported LibRTS reproduction backend: {backend!r}")
    fixture_dir = APP_DIR / "data" / "fixtures"
    resolved_boxes = boxes_path or fixture_dir / "tiny_boxes.wkt"
    resolved_points = points_path or fixture_dir / "tiny_points.wkt"
    resolved_expected = expected_path or fixture_dir / "tiny_point_contains_expected.json"

    boxes = load_boxes(resolved_boxes)
    points = load_points(resolved_points)
    expected = json.loads(resolved_expected.read_text(encoding="utf-8"))
    payload = rt.expanded_aabb_point_membership_rows_2d(
        _box_rows(boxes),
        _point_rows(points),
        indexed_ids=tuple(range(len(boxes))),
        source_ids=tuple(range(len(points))),
        expansions=0.0,
        row_capacity=len(boxes) * len(points),
        backend=backend,
    )
    actual_rows = [[int(row[0]), int(row[1])] for row in payload["candidate_id_rows"]]
    expected_rows = [[int(value) for value in row] for row in expected["candidate_id_rows"]]
    matched = actual_rows == expected_rows and payload["valid_count"] == expected["valid_count"]

    return {
        "schema": "rtdl.paper_reproduction.librts.local_point_contains_gate.v1",
        "status": (
            "local_rtdl_point_contains_reference_matched"
            if matched
            else "local_rtdl_point_contains_reference_mismatch"
        ),
        "matched": matched,
        "author_comparator_used": False,
        "paper_reproduction_complete": False,
        "fixture": {
            "boxes_path": str(resolved_boxes.relative_to(ROOT)),
            "points_path": str(resolved_points.relative_to(ROOT)),
            "expected_path": str(resolved_expected.relative_to(ROOT)),
            "indexed_box_count": len(boxes),
            "query_point_count": len(points),
        },
        "rtdl": {
            "public_api": "expanded_aabb_point_membership_rows_2d",
            "contract": payload["contract"],
            "backend": payload["backend"],
            "candidate_id_rows": actual_rows,
            "valid_count": payload["valid_count"],
            "rt_core_accelerated": payload["rt_core_accelerated"],
            "native_engine_customization": payload["native_engine_customization"],
        },
        "expected": {
            "candidate_id_rows": expected_rows,
            "valid_count": expected["valid_count"],
        },
        "claim_boundary": {
            "rtdl_only": True,
            "local_reference_only": backend == "cpu",
            "author_same_input_agreement_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_claimed": False,
            "mutable_index_parity_claimed": False,
        },
    }


def run_range_contains(
    *,
    boxes_path: Path | None = None,
    box_queries_path: Path | None = None,
    expected_path: Path | None = None,
    backend: str = "cpu",
) -> dict[str, object]:
    if backend not in {"cpu", "optix"}:
        raise ValueError(f"unsupported LibRTS reproduction backend: {backend!r}")
    fixture_dir = APP_DIR / "data" / "fixtures"
    resolved_boxes = boxes_path or fixture_dir / "tiny_boxes.wkt"
    resolved_queries = box_queries_path or fixture_dir / "tiny_range_queries.wkt"
    resolved_expected = expected_path or fixture_dir / "tiny_range_contains_expected.json"
    boxes = load_boxes(resolved_boxes)
    queries = load_boxes(resolved_queries)
    expected = json.loads(resolved_expected.read_text(encoding="utf-8"))
    exact_rows = _range_contains_rows(boxes, queries)
    payload = rt.query_aabb_index_2d(
        _box_rows(boxes),
        box_queries=_box_rows(queries),
        operation="range_contains",
        backend=backend,
    )
    result_count = int(payload["counts"]["range_contains"])
    expected_rows = [[int(value) for value in row] for row in expected["candidate_id_rows"]]
    matched = bool(
        exact_rows == expected_rows
        and result_count == int(expected["valid_count"])
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.range_contains_gate.v1",
        "status": (
            "rtdl_range_contains_reference_matched"
            if matched
            else "rtdl_range_contains_reference_mismatch"
        ),
        "matched": matched,
        "fixture": {
            "boxes_path": str(resolved_boxes.relative_to(ROOT)),
            "box_queries_path": str(resolved_queries.relative_to(ROOT)),
            "expected_path": str(resolved_expected.relative_to(ROOT)),
            "indexed_box_count": len(boxes),
            "query_box_count": len(queries),
            "reverse_direction_count": int(expected["reverse_direction_count"]),
            "direction_discriminating": (
                int(expected["reverse_direction_count"]) != int(expected["valid_count"])
            ),
        },
        "rtdl": {
            "public_api": "query_aabb_index_2d",
            "contract": payload["contract"],
            "backend": backend,
            "result_count": result_count,
            "pair_rows_exposed": False,
            "rt_core_accelerated": payload["rt_core_accelerated"],
            "native_engine_customization": payload["native_engine_customization"],
        },
        "exact_fixture_oracle": {
            "semantics": "indexed_box_contains_query_box",
            "boundary_policy": "inclusive_min_max",
            "candidate_id_rows": exact_rows,
            "valid_count": len(exact_rows),
        },
        "expected": expected,
        "claim_boundary": {
            "rtdl_only": True,
            "author_same_input_agreement_claimed": False,
            "performance_claimed": False,
        },
    }


def run_range_intersects(
    *,
    boxes_path: Path | None = None,
    box_queries_path: Path | None = None,
    expected_path: Path | None = None,
    backend: str = "cpu",
) -> dict[str, object]:
    if backend not in {"cpu", "optix"}:
        raise ValueError(f"unsupported LibRTS reproduction backend: {backend!r}")
    fixture_dir = APP_DIR / "data" / "fixtures"
    resolved_boxes = boxes_path or fixture_dir / "tiny_boxes.wkt"
    resolved_queries = box_queries_path or fixture_dir / "tiny_range_queries.wkt"
    resolved_expected = expected_path or fixture_dir / "tiny_range_intersects_expected.json"
    boxes = load_boxes(resolved_boxes)
    queries = load_boxes(resolved_queries)
    expected = json.loads(resolved_expected.read_text(encoding="utf-8"))
    box_rows = _box_rows(boxes)
    query_rows = _box_rows(queries)
    count_payload = rt.query_aabb_index_2d(
        box_rows,
        box_queries=query_rows,
        operation="range_intersects",
        backend=backend,
    )
    row_payload = rt.aabb_intersection_pair_rows_2d(
        box_rows,
        query_rows,
        indexed_ids=tuple(range(len(boxes))),
        query_ids=tuple(range(len(queries))),
        backend=backend,
        row_capacity=2 * len(boxes) * len(queries),
    )
    actual_rows = [[int(value) for value in row] for row in row_payload["candidate_id_rows"]]
    expected_rows = [[int(value) for value in row] for row in expected["candidate_id_rows"]]
    result_count = int(count_payload["counts"]["range_intersects"])
    matched = bool(
        actual_rows == expected_rows
        and result_count == int(expected["valid_count"])
        and int(row_payload["valid_count"]) == int(expected["valid_count"])
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.range_intersects_gate.v1",
        "status": (
            "rtdl_range_intersects_rows_matched"
            if matched
            else "rtdl_range_intersects_rows_mismatch"
        ),
        "matched": matched,
        "fixture": {
            "boxes_path": str(resolved_boxes.relative_to(ROOT)),
            "box_queries_path": str(resolved_queries.relative_to(ROOT)),
            "expected_path": str(resolved_expected.relative_to(ROOT)),
            "indexed_box_count": len(boxes),
            "query_box_count": len(queries),
            "range_contains_count": int(expected["range_contains_count"]),
            "predicate_discriminating": (
                int(expected["range_contains_count"]) != int(expected["valid_count"])
            ),
        },
        "rtdl": {
            "count_public_api": "query_aabb_index_2d",
            "row_public_api": "aabb_intersection_pair_rows_2d",
            "count_contract": count_payload["contract"],
            "row_contract": row_payload["contract"],
            "backend": backend,
            "result_count": result_count,
            "candidate_id_rows": actual_rows,
            "rows_exposed": True,
            "complete_candidate_coverage": row_payload["complete_candidate_coverage"],
            "rt_core_accelerated": bool(
                count_payload["rt_core_accelerated"] and row_payload["rt_core_accelerated"]
            ),
            "native_engine_customization": bool(
                count_payload["native_engine_customization"]
                or row_payload["native_engine_customization"]
            ),
        },
        "expected": expected,
        "claim_boundary": {
            "rtdl_only": True,
            "author_same_input_agreement_claimed": False,
            "performance_claimed": False,
        },
    }


def status_payload() -> dict[str, object]:
    manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
    return {
        "schema": "rtdl.paper_reproduction.librts.status.v1",
        "status": manifest["reproduction_scope"]["detail_status"],
        "paper": manifest["paper"],
        "author_artifact": manifest["author_artifact"],
        "rtdl_public_apis": manifest["rtdl_program"]["public_apis_exercised"],
        "boundaries": manifest["boundaries"],
    }


def _write_json(payload: dict[str, object], output: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(text, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bounded LibRTS paper-reproduction entrypoint")
    parser.add_argument(
        "--mode",
        choices=("status", "local-point-contains", "range-contains", "range-intersects", "pip"),
        default="status",
    )
    parser.add_argument("--boxes", type=Path)
    parser.add_argument("--polygons", type=Path)
    parser.add_argument("--points", type=Path)
    parser.add_argument("--box-queries", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--backend", choices=("cpu", "optix"), default="cpu")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if args.mode == "status":
        payload = status_payload()
    elif args.mode == "local-point-contains":
        payload = run_local_point_contains(
            boxes_path=args.boxes,
            points_path=args.points,
            expected_path=args.expected,
            backend=args.backend,
        )
    elif args.mode == "range-contains":
        payload = run_range_contains(
            boxes_path=args.boxes,
            box_queries_path=args.box_queries,
            expected_path=args.expected,
            backend=args.backend,
        )
    elif args.mode == "range-intersects":
        payload = run_range_intersects(
            boxes_path=args.boxes,
            box_queries_path=args.box_queries,
            expected_path=args.expected,
            backend=args.backend,
        )
    else:
        payload = run_pip(
            polygons_path=args.polygons,
            points_path=args.points,
            expected_path=args.expected,
            backend=args.backend,
        )
    _write_json(payload, args.output)
    return 0 if payload.get("matched", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
