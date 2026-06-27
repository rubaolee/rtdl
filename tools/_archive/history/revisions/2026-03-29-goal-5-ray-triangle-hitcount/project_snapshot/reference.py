from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Segment:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class Point:
    id: int
    x: float
    y: float


@dataclass(frozen=True)
class Polygon:
    id: int
    vertices: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class Triangle:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Ray2D:
    id: int
    ox: float
    oy: float
    dx: float
    dy: float
    tmax: float


def lsi_cpu(left: tuple[Segment, ...], right: tuple[Segment, ...]) -> tuple[dict[str, float | int], ...]:
    hits = []
    for left_seg in left:
        for right_seg in right:
            result = _segment_intersection(left_seg, right_seg)
            if result is None:
                continue
            ix, iy = result
            hits.append(
                {
                    "left_id": left_seg.id,
                    "right_id": right_seg.id,
                    "intersection_point_x": ix,
                    "intersection_point_y": iy,
                }
            )
    return tuple(hits)


def pip_cpu(points: tuple[Point, ...], polygons: tuple[Polygon, ...]) -> tuple[dict[str, int], ...]:
    results = []
    for point in points:
        for polygon in polygons:
            contains = 1 if _point_in_polygon(point.x, point.y, polygon.vertices) else 0
            results.append({"point_id": point.id, "polygon_id": polygon.id, "contains": contains})
    return tuple(results)


def overlay_compose_cpu(
    left_polygons: tuple[Polygon, ...],
    right_polygons: tuple[Polygon, ...],
) -> tuple[dict[str, int], ...]:
    left_segments = _segments_from_polygons(left_polygons)
    right_segments = _segments_from_polygons(right_polygons)
    lsi_hits = lsi_cpu(left_segments, right_segments)

    left_points = tuple(Point(id=polygon.id, x=polygon.vertices[0][0], y=polygon.vertices[0][1]) for polygon in left_polygons)
    right_points = tuple(Point(id=polygon.id, x=polygon.vertices[0][0], y=polygon.vertices[0][1]) for polygon in right_polygons)
    left_in_right = pip_cpu(left_points, right_polygons)
    right_in_left = pip_cpu(right_points, left_polygons)

    results = []
    for left_polygon in left_polygons:
        for right_polygon in right_polygons:
            requires_lsi = 1 if any(hit["left_id"] == left_polygon.id and hit["right_id"] == right_polygon.id for hit in lsi_hits) else 0
            requires_pip = 1 if any(
                (hit["point_id"] == left_polygon.id and hit["polygon_id"] == right_polygon.id and hit["contains"] == 1)
                or (hit["point_id"] == right_polygon.id and hit["polygon_id"] == left_polygon.id and hit["contains"] == 1)
                for hit in (*left_in_right, *right_in_left)
            ) else 0
            results.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_polygon.id,
                    "requires_lsi": requires_lsi,
                    "requires_pip": requires_pip,
                }
            )
    return tuple(results)


def ray_triangle_hit_count_cpu(
    rays: tuple[Ray2D, ...],
    triangles: tuple[Triangle, ...],
) -> tuple[dict[str, int], ...]:
    results = []
    for ray in rays:
        hit_count = 0
        for triangle in triangles:
            if _finite_ray_hits_triangle(ray, triangle):
                hit_count += 1
        results.append({"ray_id": ray.id, "hit_count": hit_count})
    return tuple(results)


def _segments_from_polygons(polygons: tuple[Polygon, ...]) -> tuple[Segment, ...]:
    segments = []
    for polygon in polygons:
        vertices = list(polygon.vertices)
        wrapped = vertices + [vertices[0]]
        for start, end in zip(wrapped, wrapped[1:]):
            segments.append(Segment(id=polygon.id, x0=start[0], y0=start[1], x1=end[0], y1=end[1]))
    return tuple(segments)


def _segment_intersection(left: Segment, right: Segment) -> tuple[float, float] | None:
    px = left.x0
    py = left.y0
    rx = left.x1 - left.x0
    ry = left.y1 - left.y0
    qx = right.x0
    qy = right.y0
    sx = right.x1 - right.x0
    sy = right.y1 - right.y0

    denom = rx * sy - ry * sx
    if abs(denom) < 1.0e-7:
        return None

    qpx = qx - px
    qpy = qy - py
    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * ry - qpy * rx) / denom
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None

    return (px + t * rx, py + t * ry)


def _point_in_polygon(x: float, y: float, vertices: tuple[tuple[float, float], ...]) -> bool:
    inside = False
    j = len(vertices) - 1
    for i, (xi, yi) in enumerate(vertices):
        xj, yj = vertices[j]
        on_crossing = ((yi > y) != (yj > y)) and (
            x <= (xj - xi) * (y - yi) / ((yj - yi) or 1.0e-20) + xi
        )
        if on_crossing:
            inside = not inside
        j = i
    return inside


def _finite_ray_hits_triangle(ray: Ray2D, triangle: Triangle) -> bool:
    triangle_vertices = (
        (triangle.x0, triangle.y0),
        (triangle.x1, triangle.y1),
        (triangle.x2, triangle.y2),
    )
    ex = ray.ox + ray.dx * ray.tmax
    ey = ray.oy + ray.dy * ray.tmax
    ray_segment = Segment(id=ray.id, x0=ray.ox, y0=ray.oy, x1=ex, y1=ey)

    if _point_in_triangle(ray.ox, ray.oy, triangle_vertices):
        return True
    if _point_in_triangle(ex, ey, triangle_vertices):
        return True

    triangle_edges = (
        Segment(id=triangle.id, x0=triangle.x0, y0=triangle.y0, x1=triangle.x1, y1=triangle.y1),
        Segment(id=triangle.id, x0=triangle.x1, y0=triangle.y1, x1=triangle.x2, y1=triangle.y2),
        Segment(id=triangle.id, x0=triangle.x2, y0=triangle.y2, x1=triangle.x0, y1=triangle.y0),
    )
    return any(_segment_intersection(ray_segment, edge) is not None for edge in triangle_edges)


def _point_in_triangle(x: float, y: float, vertices: tuple[tuple[float, float], ...]) -> bool:
    (ax, ay), (bx, by), (cx, cy) = vertices
    v0x = cx - ax
    v0y = cy - ay
    v1x = bx - ax
    v1y = by - ay
    v2x = x - ax
    v2y = y - ay

    dot00 = v0x * v0x + v0y * v0y
    dot01 = v0x * v1x + v0y * v1y
    dot02 = v0x * v2x + v0y * v2y
    dot11 = v1x * v1x + v1y * v1y
    dot12 = v1x * v2x + v1y * v2y

    denom = dot00 * dot11 - dot01 * dot01
    if abs(denom) < 1.0e-7:
        return False

    inv = 1.0 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv
    v = (dot00 * dot12 - dot01 * dot02) * inv
    return u >= 0.0 and v >= 0.0 and (u + v) <= 1.0
