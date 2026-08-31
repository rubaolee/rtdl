from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


Point2 = tuple[float, float]
Triangle2 = tuple[Point2, Point2, Point2]


@dataclass(frozen=True)
class SimplePolygonOverlayAreaReferenceResult:
    area: float
    left_triangle_count: int
    right_triangle_count: int
    triangle_pair_count: int
    algorithm: str = "ear_clip_triangulation_plus_triangle_pair_convex_clip"


def _clean_vertices(vertices: Sequence[Point2]) -> list[Point2]:
    cleaned = [(float(x), float(y)) for x, y in vertices]
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
        cleaned = cleaned[:-1]
    result: list[Point2] = []
    for point in cleaned:
        if not result or point != result[-1]:
            result.append(point)
    if len(result) >= 2 and result[0] == result[-1]:
        result.pop()
    if len(result) < 3:
        raise ValueError("simple polygon overlay reference requires at least three distinct vertices")
    return result


def _signed_area(vertices: Sequence[Point2]) -> float:
    area2 = 0.0
    count = len(vertices)
    for index, (x0, y0) in enumerate(vertices):
        x1, y1 = vertices[(index + 1) % count]
        area2 += x0 * y1 - x1 * y0
    return 0.5 * area2


def _cross(a: Point2, b: Point2, c: Point2) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _point_in_triangle(point: Point2, triangle: Triangle2, *, eps: float) -> bool:
    a, b, c = triangle
    c0 = _cross(a, b, point)
    c1 = _cross(b, c, point)
    c2 = _cross(c, a, point)
    return c0 >= -eps and c1 >= -eps and c2 >= -eps


def triangulate_simple_polygon_ear_clip(vertices: Sequence[Point2], *, eps: float = 1.0e-12) -> tuple[Triangle2, ...]:
    """Triangulate a simple polygon with deterministic ear clipping.

    This is a CPU reference for future prepared-payload work. It intentionally
    supports simple polygons only; self-intersections, holes, and multipolygons
    belong to the caller's topology normalization layer.
    """

    polygon = _clean_vertices(vertices)
    if _signed_area(polygon) < 0.0:
        polygon = list(reversed(polygon))
    remaining = list(range(len(polygon)))
    triangles: list[Triangle2] = []
    guard = 0
    while len(remaining) > 3:
        guard += 1
        if guard > len(polygon) * len(polygon):
            raise ValueError("ear clipping failed; polygon may be non-simple or numerically degenerate")
        clipped = False
        for position, current in enumerate(tuple(remaining)):
            previous = remaining[position - 1]
            nxt = remaining[(position + 1) % len(remaining)]
            a = polygon[previous]
            b = polygon[current]
            c = polygon[nxt]
            if _cross(a, b, c) <= eps:
                continue
            candidate: Triangle2 = (a, b, c)
            contains_other = False
            for other in remaining:
                if other in (previous, current, nxt):
                    continue
                if _point_in_triangle(polygon[other], candidate, eps=eps):
                    contains_other = True
                    break
            if contains_other:
                continue
            triangles.append(candidate)
            del remaining[position]
            clipped = True
            break
        if not clipped:
            raise ValueError("ear clipping found no ear; polygon may be non-simple or numerically degenerate")
    final: Triangle2 = (polygon[remaining[0]], polygon[remaining[1]], polygon[remaining[2]])
    if abs(_signed_area(final)) <= eps:
        raise ValueError("ear clipping produced a degenerate final triangle")
    triangles.append(final)
    return tuple(triangles)


def _convex_clip(subject: Sequence[Point2], clipper: Sequence[Point2], *, eps: float) -> list[Point2]:
    output = list(subject)
    if _signed_area(clipper) < 0.0:
        clipper = list(reversed(clipper))
    for index, a in enumerate(clipper):
        b = clipper[(index + 1) % len(clipper)]
        input_vertices = output
        output = []
        if not input_vertices:
            break
        previous = input_vertices[-1]
        previous_inside = _cross(a, b, previous) >= -eps
        for current in input_vertices:
            current_inside = _cross(a, b, current) >= -eps
            if current_inside != previous_inside:
                output.append(_line_intersection(previous, current, a, b, eps=eps))
            if current_inside:
                output.append(current)
            previous = current
            previous_inside = current_inside
    return output


def _line_intersection(p0: Point2, p1: Point2, q0: Point2, q1: Point2, *, eps: float) -> Point2:
    px = p1[0] - p0[0]
    py = p1[1] - p0[1]
    qx = q1[0] - q0[0]
    qy = q1[1] - q0[1]
    denom = px * qy - py * qx
    if abs(denom) <= eps:
        return p1
    rx = q0[0] - p0[0]
    ry = q0[1] - p0[1]
    t = (rx * qy - ry * qx) / denom
    return (p0[0] + t * px, p0[1] + t * py)


def convex_polygon_overlap_area(vertices_a: Sequence[Point2], vertices_b: Sequence[Point2], *, eps: float = 1.0e-12) -> float:
    clipped = _convex_clip(vertices_a, vertices_b, eps=eps)
    if len(clipped) < 3:
        return 0.0
    return abs(_signed_area(clipped))


def simple_polygon_overlap_area_by_triangulation(
    left_vertices: Sequence[Point2],
    right_vertices: Sequence[Point2],
    *,
    eps: float = 1.0e-12,
) -> SimplePolygonOverlayAreaReferenceResult:
    left_triangles = triangulate_simple_polygon_ear_clip(left_vertices, eps=eps)
    right_triangles = triangulate_simple_polygon_ear_clip(right_vertices, eps=eps)
    area = 0.0
    for left in left_triangles:
        for right in right_triangles:
            area += convex_polygon_overlap_area(left, right, eps=eps)
    return SimplePolygonOverlayAreaReferenceResult(
        area=area,
        left_triangle_count=len(left_triangles),
        right_triangle_count=len(right_triangles),
        triangle_pair_count=len(left_triangles) * len(right_triangles),
    )


__all__ = [
    "Point2",
    "SimplePolygonOverlayAreaReferenceResult",
    "Triangle2",
    "convex_polygon_overlap_area",
    "simple_polygon_overlap_area_by_triangulation",
    "triangulate_simple_polygon_ear_clip",
]
